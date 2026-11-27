"""S0 tests: persistent SSH multiplexing (FINAL direction e05fc58).

No live SSH is needed for any test here: the runner is injected, so
every test runs offline on the VM. Live timing is measured separately
by the worker log (fresh vs mux, master death, idle survival); these
tests pin the construction rules PROBE-S0 measured, so a later edit
cannot silently reintroduce `ssh -f`, drop ServerAliveInterval, or
retry a remote failure.
"""
import importlib.util
import json
import pathlib
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "ssh_mux", ROOT / "scripts" / "ssh_mux.py")
ssh_mux = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ssh_mux)


class FakeProc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _runner_for(calls, script):
    """Fake subprocess.run: pops (argv, kwargs) answers from script."""
    def runner(argv, **kwargs):
        calls.append(argv)
        return script.pop(0)
    return runner


class ConstructionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mux = ssh_mux.SshMux(host="testuser@192.0.2.1",
                                  state_dir=self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_ssh_f_anywhere(self):
        """PROBE-S0 F1: ssh -f masters refuse mux sessions and die in
        1-2 min. No argv this module builds may contain -f."""
        for argv in (self.mux.master_argv(), self.mux.client_argv(["true"]),
                     self.mux.check_argv(), self.mux.exit_argv()):
            self.assertNotIn("-f", argv)

    def test_master_uses_setsid_form_options(self):
        argv = self.mux.master_argv()
        self.assertEqual(argv[0], "ssh")
        self.assertIn("-N", argv)
        opts = " ".join(argv)
        self.assertIn("ControlMaster=yes", opts)
        self.assertIn("ServerAliveCountMax=3", opts)
        self.assertIn("ControlPersist=600", opts)
        self.assertIn("/tmp/cm-s0-", opts)
        self.assertNotIn("/tmp/cm-probe-", opts)
        self.assertNotIn("/tmp/cm-soakb-", opts)

    def test_client_is_controlmaster_auto(self):
        opts = " ".join(self.mux.client_argv(["echo", "hi"]))
        self.assertIn("ControlMaster=auto", opts)
        self.assertIn("ControlPath=/tmp/cm-s0-", opts)
        self.assertIn("ServerAliveInterval=15", opts)

    def test_base_options_match_ssh_laptop_sh(self):
        """Same host, key, proxy, and timeouts as ~/workspace/ssh-laptop.sh."""
        opts = " ".join(self.mux.client_argv(["true"]))
        self.assertIn("testuser@192.0.2.1", opts)
        self.assertIn(str(pathlib.Path.home() / ".ssh" / "id_ed25519"), opts)
        self.assertIn("tailscale-proxy.py", opts)
        self.assertIn("BatchMode=yes", opts)
        self.assertIn("ConnectTimeout=25", opts)


class FailureClassificationTest(unittest.TestCase):
    def test_markers_are_connection_failures(self):
        for err in ("Control socket connect: No such file or directory",
                    "Master refused session request: Permission denied",
                    "ssh: connect to host 192.0.2.1 port 22: "
                    "Connection refused",
                    "Connection timed out during banner exchange"):
            proc = FakeProc(255, "", err)
            self.assertTrue(ssh_mux.SshMux._is_connection_failure(proc),
                            err)

    def test_remote_255_is_not_a_connection_failure(self):
        """ssh passes a remote exit status of 255 through unchanged.
        Treating rc 255 alone as a connection failure would retry a
        command that already ran."""
        proc = FakeProc(255, "remote output\n", "")
        self.assertFalse(ssh_mux.SshMux._is_connection_failure(proc))

    def test_remote_nonzero_is_not_a_connection_failure(self):
        proc = FakeProc(3, "", "remote: something failed\n")
        self.assertFalse(ssh_mux.SshMux._is_connection_failure(proc))


class EnsureMasterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mux = ssh_mux.SshMux(host="testuser@192.0.2.1",
                                  state_dir=self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_alive_master_is_not_restarted(self):
        calls = []
        runner = _runner_for(calls, [
            FakeProc(0, "", "Master running (pid=12345)\n")])
        self.mux._runner = runner
        with mock.patch.object(self.mux, "start_master") as start:
            status = self.mux.ensure_master()
        start.assert_not_called()
        self.assertEqual(status, {"alive": True, "pid": 12345,
                                  "restarted": False,
                                  "death_logged": False})

    def test_dead_master_logs_death_and_restarts(self):
        calls = []
        runner = _runner_for(calls, [
            FakeProc(255, "", "Control socket connect: "
                     "No such file or directory\n")])
        self.mux._runner = runner
        self.mux._write_state(master_pid=11111)
        with mock.patch.object(
                self.mux, "start_master",
                return_value=(True, 22222)) as start:
            status = self.mux.ensure_master()
        start.assert_called_once()
        self.assertTrue(status["alive"])
        self.assertTrue(status["restarted"])
        self.assertTrue(status["death_logged"])
        self.assertEqual(status["pid"], 22222)
        rows = [json.loads(line) for line in
                (pathlib.Path(self.tmp.name) / "ssh-mux.jsonl"
                 ).read_text().splitlines()]
        death = [r for r in rows if r["event"] == "master_death"]
        restart = [r for r in rows if r["event"] == "master_restart"]
        self.assertEqual(len(death), 1)
        self.assertEqual(death[0]["previous_pid"], 11111)
        self.assertEqual(death[0]["check_rc"], 255)
        self.assertEqual(len(restart), 1)
        self.assertEqual(restart[0]["new_pid"], 22222)


class RunRetryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mux = ssh_mux.SshMux(host="testuser@192.0.2.1",
                                  state_dir=self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_connection_failure_retries_once(self):
        calls = []
        script = [
            FakeProc(0, "", "Master running (pid=12345)\n"),  # ensure check
            FakeProc(255, "", "Control socket connect: "
                     "No such file or directory\n"),  # client fails
            FakeProc(0, "", "Master running (pid=12345)\n"),  # retry ensure
            FakeProc(0, "ALIVE\n", ""),  # retry client succeeds
            FakeProc(0, "", "Master running (pid=12345)\n"),  # final check
        ]
        self.mux._runner = _runner_for(calls, script)
        result = self.mux.run(["echo", "ALIVE"])
        self.assertEqual(result["rc"], 0)
        self.assertEqual(result["stdout"], "ALIVE\n")
        self.assertTrue(result["restarted"])
        client_calls = [c for c in calls if "echo" in c]
        self.assertEqual(len(client_calls), 2)

    def test_remote_failure_is_never_retried(self):
        calls = []
        script = [
            FakeProc(0, "", "Master running (pid=12345)\n"),
            FakeProc(3, "", "remote: something failed\n"),
            FakeProc(0, "", "Master running (pid=12345)\n"),
        ]
        self.mux._runner = _runner_for(calls, script)
        result = self.mux.run(["false-ish-remote"])
        self.assertEqual(result["rc"], 3)
        client_calls = [c for c in calls if "false-ish-remote" in c]
        self.assertEqual(len(client_calls), 1)


class WatchdogTest(unittest.TestCase):
    def test_watchdog_is_ensure(self):
        with tempfile.TemporaryDirectory() as tmp:
            mux = ssh_mux.SshMux(host="testuser@192.0.2.1", state_dir=tmp)
            with mock.patch.object(
                    mux, "ensure_master",
                    return_value={"alive": True, "pid": 1,
                                  "restarted": False,
                                  "death_logged": False}) as ensure:
                self.assertEqual(mux.watchdog()["alive"], True)
                ensure.assert_called_once()


if __name__ == "__main__":
    unittest.main()
