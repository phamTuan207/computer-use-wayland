#!/usr/bin/env python3
"""Stateful MCP bridge for one computer-use driver session."""
import json
import os
import base64
import subprocess
import sys
import time
from pathlib import Path
import uuid

CU = os.environ.get("CU_EXECUTABLE") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "cu.py")

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import mcp_bridge_transport as transport

# Monotonic deadlines in seconds; tests inject short values by patching
# these module globals before exercising the bridge.
STARTUP_TIMEOUT = transport.DEFAULT_STARTUP_TIMEOUT
REQUEST_TIMEOUT = transport.DEFAULT_REQUEST_TIMEOUT
# The driver reads ONE JSON request per line and refuses lines over 8 MiB
# (scripts/session_driver.py REQUEST_LINE_LIMIT, counting the newline), so
# oversized requests are validated here BEFORE any byte reaches the pipe.
REQUEST_LINE_LIMIT = 8 * 1024 * 1024
# Cleanup waits (seconds): graceful stdin-EOF drain, then SIGTERM, then
# SIGKILL. Injectable for tests; production keeps the original values.
REAP_WAIT = 10.0          # close_session graceful drain after stdin EOF
TERMINATE_WAIT = 5.0      # close_session wait after terminate()
FAIL_DRAIN_WAIT = 3.0     # uncertain-request drain after stdin EOF
FAIL_TERMINATE_WAIT = 5.0 # uncertain-request wait after terminate()

proc = None
LOG_DIR = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home()/'.cache'))) / 'agent-computer-use'
session_ended = None
session_log = None
stderr_log = None
last_command = None
# Reader borrowing the LIVE driver stdout object for the whole session;
# created once per start, reset only by close_session.
driver_reader = None
request_count = 0


def log_event(event):
    if session_log:
        try:
            with session_log.open('a', encoding='utf-8') as stream:
                stream.write(json.dumps({'time':time.time(), **event}, ensure_ascii=False)+'\n')
        except OSError:
            pass  # diagnostics must never mask the failure being handled


def remember_end(reason):
    """Record the first end-of-session reason; later calls never erase it.

    Fields:
    - 'exit_code' (legacy): in the command-failure path this is the driver
      command's exit code (session_ended.exit_code, falling back to the
      response's returncode); otherwise it is the reaped child process exit
      status when known. None when unknown.
    - 'child_exit_code': exit status of the reaped child process only.
    - 'command_exit_code': exit code the driver reported for its failing
      command; None for pure transport failures where no command completed.
    """
    global session_ended
    child_exit_code = proc.poll() if proc else None
    details={'reason':reason,'exit_code':child_exit_code,
             'child_exit_code':child_exit_code,'command_exit_code':None,
             'last_command':last_command,'ended_at':time.time()}
    try:
        # Preserve a bounded tail of the child's private stderr BEFORE the
        # log handles are closed.
        if stderr_log:
            stderr_log.flush()
            with open(stderr_log.name, 'rb') as stream:
                stream.seek(0,2)
                stream.seek(max(0,stream.tell()-8192))
                details['stderr']=stream.read().decode(errors='replace')
        elif proc and proc.poll() is not None and proc.stderr:
            details['stderr']=proc.stderr.read(8192)
    except Exception:
        pass  # stderr is diagnostic; keep the recorded reason intact
    if session_log:details['log']=str(session_log)
    if session_ended is not None:
        # A repeated end (e.g. a late 'driver exited before finish') must not
        # erase the first failure record; only fill in an unknown child status.
        if session_ended.get('child_exit_code') is None and child_exit_code is not None:
            session_ended['child_exit_code']=child_exit_code
            if session_ended.get('exit_code') is None:
                session_ended['exit_code']=child_exit_code
        return session_ended
    session_ended=details
    log_event({'session_ended':details})
    return details


def ended_error(reason):
    details=remember_end(reason)
    return _session_ended_error(details)


def _session_ended_error(details):
    return RuntimeError('computer-use session ended: '+json.dumps(details,ensure_ascii=False)+
                        '; start a new session and observe current state; do not replay input')


GUI_KEYS = {
    "XDG_RUNTIME_DIR", "WAYLAND_DISPLAY", "DISPLAY", "HYPRLAND_INSTANCE_SIGNATURE",
    "DBUS_SESSION_BUS_ADDRESS", "XDG_CURRENT_DESKTOP", "XDG_SESSION_DESKTOP",
    "XDG_SESSION_TYPE", "XDG_SEAT", "XDG_VTNR", "USER", "HOME", "LOGNAME",
    "PATH", "GDK_BACKEND", "QT_QPA_PLATFORM", "ELECTRON_OZONE_PLATFORM_HINT",
    "MOZ_ENABLE_WAYLAND",
}


def gui_environment():
    # Agent daemons may inherit a stale Hyprland signature from an earlier login.
    # Read the live compositor shell's environment for every new session.
    for entry in os.scandir("/proc"):
        if not entry.name.isdigit():
            continue
        try:
            if open(f"/proc/{entry.name}/comm").read().strip() != "quickshell":
                continue
            # Serpantinum runs another Quickshell in the host PID namespace.
            # Its Wayland display belongs to nested Sway, not host Hyprland.
            if b"/usr/share/omarchy/shell" not in open(f"/proc/{entry.name}/cmdline", "rb").read():
                continue
            env = {}
            for item in open(f"/proc/{entry.name}/environ", "rb").read().split(b"\0"):
                key, sep, value = item.partition(b"=")
                if sep and key.decode(errors="ignore") in GUI_KEYS:
                    env[key.decode()] = value.decode(errors="surrogateescape")
            sig = env.get("HYPRLAND_INSTANCE_SIGNATURE", "")
            if (env.get("WAYLAND_DISPLAY") and env.get("XDG_RUNTIME_DIR") and sig
                    and os.path.isdir(os.path.join(env["XDG_RUNTIME_DIR"], "hypr", sig))):
                return {**os.environ, **env}
        except (OSError, PermissionError):
            continue
    raise RuntimeError("no live Hyprland GUI environment found; start Quickshell or log into Hyprland")


def read_message():
    line = sys.stdin.buffer.readline(8 * 1024 * 1024 + 1)
    if not line:
        return None
    if len(line) > 8 * 1024 * 1024 or not line.endswith(b"\n"):
        raise ValueError("invalid MCP message size or framing")
    return json.loads(line)


def write_message(value):
    data = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode() + b"\n"
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()


def close_session():
    """Close every owned handle and reap the owned child exactly once.

    This is the ONLY place that closes the session's streams or the stderr
    log, and the only place that tears the session down. It never raises:
    cleanup trouble is collected in the returned outcome instead of masking
    the failure a caller is already handling. Stream objects own their fds;
    they are closed through the object, never via a raw fd, and only once
    (guarded by .closed).

    Returns the cleanup outcome dict:
    {'ok': bool, 'errors': [str, ...], 'escalated': bool,
     'child_exit_code': int | None}
    'ok' is True ONLY when teardown was confirmed clean: every handle closed
    without error, no escalation to SIGTERM/SIGKILL was needed, and the
    reaped child (if any) exited 0. When a teardown actually ran and a
    session end record exists, the outcome is attached to
    session_ended['cleanup'] and a FINAL session_ended event is appended to
    the session log, so the last log entry always matches the finalized
    record (reason, command/child exit codes, cleanup outcome). AFTER the
    reap the bounded child-stderr tail is refreshed into the end record, so
    a SIGTERM handler's late diagnostic written during teardown is not
    lost.
    """
    global proc, stderr_log, driver_reader
    driver_reader = None
    child, proc = proc, None
    errors=[]
    escalated=False
    child_exit_code=None
    if child is not None:
        try:
            stdin = getattr(child, 'stdin', None)
            if stdin and not stdin.closed:stdin.close()
        except Exception as exc:
            errors.append('stdin close failed: %s' % exc)
        try:
            child.wait(timeout=REAP_WAIT)
        except Exception:
            escalated=True
            try:
                child.terminate()
                try:
                    child.wait(timeout=TERMINATE_WAIT)
                except Exception:
                    child.kill()
                    child.wait()
            except Exception as exc:
                errors.append('child termination failed: %s' % exc)
        for name in ('stdin','stdout','stderr'):
            stream = getattr(child, name, None)
            try:
                if stream and not stream.closed:stream.close()
            except Exception as exc:
                errors.append('%s close failed: %s' % (name, exc))
        try:
            child_exit_code = child.poll()
        except Exception:
            child_exit_code = None
    if stderr_log is not None:
        if session_ended is not None:
            # Refresh the bounded stderr tail AFTER the reap but BEFORE the
            # log file is closed: a child SIGTERM handler can emit its real
            # cleanup diagnostic (e.g. 'guardian cleanup failed') during the
            # teardown above, long after remember_end sampled an empty tail.
            # Without this refresh the finalized record would carry a stale
            # stderr while exit code and cleanup are already correct.
            try:
                stderr_log.flush()
                with open(stderr_log.name, 'rb') as stream:
                    stream.seek(0, 2)
                    stream.seek(max(0, stream.tell() - 8192))
                    session_ended['stderr'] = stream.read().decode(errors='replace')
            except Exception:
                pass  # the refresh must never mask the handled failure
        try:
            stderr_log.close()
        except Exception as exc:
            errors.append('stderr log close failed: %s' % exc)
        stderr_log=None
    outcome={'ok': not errors and not escalated and child_exit_code in (0, None),
             'errors': errors, 'escalated': escalated,
             'child_exit_code': child_exit_code}
    if child is not None:
        if session_ended is not None:
            try:
                if session_ended.get('child_exit_code') is None and child_exit_code is not None:
                    session_ended['child_exit_code']=child_exit_code
                    if session_ended.get('exit_code') is None:
                        session_ended['exit_code']=child_exit_code
                session_ended['cleanup']=outcome
            except Exception:
                pass
            # Append the FINAL end event now that reason, command/child exit
            # codes and the cleanup outcome are all finalized, so the last
            # log record always matches what the caller reports.
            log_event({'session_ended':session_ended})
    return outcome


def terminate_and_reap():
    """Terminate and reap the owned child exactly once (uncertain outcome).

    Used when a request outcome is uncertain (partial write, stalled or
    dead driver): the child is stopped and reaped here so close_session()
    afterwards is a pure handle teardown. Never raises.
    """
    child=proc
    if child is None:
        return
    try:
        if child.poll() is None:
            try:
                child.terminate()
            except Exception:
                pass
            try:
                child.wait(timeout=FAIL_TERMINATE_WAIT)
            except Exception:
                try:
                    child.kill()
                    child.wait()
                except Exception:
                    pass
    except Exception:
        pass


def fail_request(reason):
    """Stop an uncertain request before accepting another one; never replay it.

    Terminates and reaps the owned child FIRST, then preserves the failure
    reason and a bounded tail of the child's private stderr BEFORE closing
    log handles, closes every owned handle exactly once, and raises the
    ended-session error. The raised message carries BOTH the primary reason
    AND the secondary cleanup outcome recorded by close_session.
    """
    terminate_and_reap()
    try:
        remember_end(reason)  # record + first log while handles are open
    finally:
        close_session()  # attaches cleanup outcome + appends the final log
    details=session_ended if isinstance(session_ended,dict) else {'reason':reason}
    raise _session_ended_error(details)


def envelope_protocol_error(args, result):
    """Return a bounded reason string when `result` is not a recognized
    driver response shape for `args`, else None.

    Recognized shapes (the scripts/session_driver.py contract):
    - finish acknowledgement: {'ok': True, 'driver': 'finished'};
    - regular command: an integer `returncode` (bool is NOT an integer here)
      plus a boolean `session_continues`. A fatal response (nonzero
      returncode, continuation refused) additionally carries `session_ended`
      with a non-empty `reason`. Contradictory metadata — returncode 0 with
      session_continues false, or session_continues true together with
      session_ended — is a protocol failure too.
    The startup handshake ('driver': 'ready') is its own shape, validated by
    the start operation before any command is sent.

    A JSON object alone is never good enough: a missing returncode used to
    default to 0 and let an arbitrary envelope pass as a successful command.
    """
    if args == ['finish']:
        if result.get('ok') is not True or result.get('driver') != 'finished':
            return ('driver finish response is not a finish acknowledgement '
                    '(ok=%r, driver=%r)' % (result.get('ok'),
                                            str(result.get('driver'))[:120]))
        return None
    code=result.get('returncode')
    if isinstance(code,bool) or not isinstance(code,int):
        return ('driver response is missing an integer command returncode '
                '(got %s)'%type(code).__name__)
    continues=result.get('session_continues')
    if not isinstance(continues,bool):
        return ('driver response is missing a boolean session_continues flag '
                '(got %s)'%type(continues).__name__)
    if code==0 and continues is False:
        return ('driver response is contradictory: returncode 0 with '
                'session_continues false')
    if continues and 'session_ended' in result:
        return ('driver response is contradictory: session_continues true '
                'with session_ended metadata')
    if code and not continues:
        detail=result.get('session_ended')
        if not isinstance(detail,dict) or not isinstance(detail.get('reason'),str) \
                or not detail['reason'].strip():
            return ('driver fatal response is missing session_ended reason '
                    'metadata')
    return None


def session_call(args, data="", image_policy="auto"):
    global last_command, request_count
    if proc is None:
        if session_ended:
            raise RuntimeError('computer-use session ended: '+json.dumps(session_ended,ensure_ascii=False)+
                               '; start a new session and observe current state; do not replay input')
        raise RuntimeError("no live computer-use session; call start first")
    if proc.poll() is not None:
        remember_end('driver exited between requests')
        close_session()
        details=session_ended if isinstance(session_ended,dict) else {'reason':'driver exited between requests'}
        raise _session_ended_error(details)
    # Do not persist typed text or action bodies in diagnostic logs.
    last_command=args[0]+(' '+args[1] if args[0] in ('browser','a11y') and len(args)>1 else '')
    log_event({'command':last_command})
    payload=json.dumps({"args": args, "stdin": data, "image_policy": image_policy},
                       ensure_ascii=False).encode('utf-8')+b'\n'
    if len(payload)>REQUEST_LINE_LIMIT:
        # Refuse BEFORE writing a single byte: nothing was sent, nothing is
        # uncertain, so the session stays active and no replay question exists.
        raise ValueError('request is %d bytes; the driver refuses request lines over %d bytes (8 MiB)'
                         % (len(payload), REQUEST_LINE_LIMIT))
    # Exactly ONE send attempt per command: an uncertain outcome is never
    # replayed, so the count for the failed command stays at one.
    request_count+=1
    # ONE monotonic deadline covers writing AND reading this request.
    deadline=time.monotonic()+REQUEST_TIMEOUT
    try:
        transport.write_request(proc.stdin, payload, deadline)
        line=driver_reader.read_line(deadline=deadline)
        result=transport.decode_message(line)
    except Exception as exc:
        fail_request(str(exc) or exc.__class__.__name__)
    # A decoded JSON object is not automatically a valid driver response.
    # Validate the shape BEFORE consuming any field so a malformed envelope
    # can never pass as a successful command.
    protocol_error=envelope_protocol_error(args,result)
    if protocol_error:
        # Missing/wrong-type/contradictory response metadata is a
        # transport/protocol failure: the envelope cannot be trusted, so the
        # uncertain request is stopped here — terminate, reap, preserve the
        # reason, close — and is NEVER replayed.
        fail_request(protocol_error)
    if args==['finish']:
        # The validated finish ACK carries no command envelope: there is no
        # continuation metadata to interpret for it.
        return result
    detail=result.get('session_ended')
    if not isinstance(detail,dict):detail={}
    inner=result.get('result',{})
    # The DRIVER owns the continuation decision: a failed command keeps the
    # session only when its response envelope carries the top-level boolean
    # `session_continues: true` (internal typed-refusal provenance or the
    # exact transient matcher inside the driver). Any 'recoverable' flag
    # inside the backend payload (result.result) is never trusted, and a
    # failed command without valid continuation metadata is fail-closed:
    # the session ends.
    continues=result['session_continues']
    if result['returncode'] and not continues:
        reason=detail.get('reason') or (inner.get('error') if isinstance(inner,dict) else None) or result.get('stderr') or 'driver command failed'
        try:
            proc.wait(timeout=FAIL_DRAIN_WAIT)
        except Exception:
            pass
        ended=remember_end(reason)
        # Legacy 'exit_code' is the driver COMMAND exit code: prefer the
        # driver-reported session_ended.exit_code, fall back to the
        # response's returncode. It may differ from the reaped child process
        # exit status, which stays in 'child_exit_code'.
        command_code=detail.get('exit_code', result.get('returncode'))
        ended['exit_code']=command_code
        if ended.get('command_exit_code') is None:
            ended['command_exit_code']=command_code
        result['session_ended']=ended
        result['session_ended']['next_step']='Start a new session and observe current state; never replay uncertain input.'
        close_session()  # attaches cleanup outcome + appends the FINAL log event
    return result


def tool_call(arguments):
    global proc, session_ended, session_log, stderr_log, last_command
    global driver_reader, request_count
    operation = arguments.get("operation")
    if operation == "start":
        if proc is not None and proc.poll() is None:
            raise RuntimeError("computer-use session is already active")
        close_session()
        session_ended=None
        last_command=None
        request_count=0
        LOG_DIR.mkdir(parents=True,exist_ok=True,mode=0o700)
        ident=f"{time.time_ns()}-{uuid.uuid4().hex[:8]}"
        session_log=LOG_DIR/f'session-{ident}.log'
        session_log.touch(mode=0o600)
        stderr_path=LOG_DIR/f'session-{ident}.stderr.log'
        stderr_log=open(stderr_path,'x',opener=lambda path,flags:os.open(path,flags,0o600))
        try:
            gui_env=gui_environment()
        except Exception:
            close_session()
            raise
        try:
            # Binary, unbuffered pipes: every driver read below is a raw byte
            # read through the LineReader; buffered readline is never mixed in.
            proc = subprocess.Popen(
                [CU, "session", "--", CU, "session-driver"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr_log,
                bufsize=0, env=gui_env,
            )
        except Exception as exc:
            # Popen/exec failure: close all owned handles, surface the
            # ORIGINAL cause.
            remember_end('driver process could not be started: %s' % (str(exc) or exc.__class__.__name__))
            close_session()
            raise
        try:
            driver_reader = transport.LineReader(proc.stdout, timeout=STARTUP_TIMEOUT)
            envelope = transport.decode_message(driver_reader.read_line())
        except Exception as exc:
            # Handshake read/decode failure (timeout, EOF, malformed
            # envelope): record the truth, close all owned handles, and
            # surface a failed-start error that carries the FINALIZED
            # session_ended record — primary transport cause, child exit
            # status, bounded stderr tail, log paths and the cleanup
            # outcome — because the main MCP layer can only return
            # str(exc). The original exception stays as __cause__.
            if isinstance(exc, transport.ResponseTimeoutError):
                reason='session startup timed out'
            else:
                reason='could not start session: %s' % (str(exc) or exc.__class__.__name__)
            ended=remember_end(reason)
            close_session()
            raise RuntimeError('could not start session: '+json.dumps(ended,ensure_ascii=False)) from exc
        if envelope.get("driver") != "ready":
            ended=remember_end('could not start session: unexpected handshake payload')
            # Retain the payload cause as a bounded diagnostic: the raw
            # envelope is folded into the end record (which close_session
            # finalizes and reports), never dumped unbounded.
            payload=json.dumps(envelope,ensure_ascii=False)
            if len(payload)>2048:payload=payload[:2048]+' [truncated]'
            ended['handshake']=payload
            close_session()
            raise RuntimeError('could not start session: '+json.dumps(ended,ensure_ascii=False))
        return {"ok": True, "session": "active", "driver": "ready", "log":str(session_log)}
    if operation == "request":
        args = arguments.get("args")
        if not isinstance(args, list) or not args or not all(isinstance(x, str) for x in args):
            raise ValueError("args must be a non-empty string array")
        if args[0] not in {"observe", "act", "windows", "doctor", "status", "browser", "a11y"}:
            raise ValueError("unsupported command")
        data = arguments.get("stdin", "")
        if not isinstance(data, str):
            raise ValueError("stdin must be a string")
        policy = arguments.get("image_policy", "auto")
        if policy not in ("auto", "always"):
            raise ValueError("image_policy must be auto or always")
        return session_call(args, data, policy)
    if operation == "finish":
        if proc is None:
            # A repeated finish is an inactive no-op and must keep any earlier
            # failure record (and its cleanup outcome) untouched.
            return {'ok':True,'session':'inactive','already_finished':True,'session_ended':session_ended}
        if proc.poll() is not None:
            remember_end('driver exited before finish')
            close_session()
            return {'ok':True,'session':'inactive','already_finished':True,'session_ended':session_ended}
        try:
            # The driver acknowledges finish and exits by itself. Neither its
            # ACK nor exit 0 is proof of successful native restoration; the
            # result below reports exactly what was observed.
            ack = session_call(['finish'])
        except RuntimeError:
            ended = session_ended if isinstance(session_ended, dict) else {}
            close_session()  # idempotent; attaches cleanup + final log if open
            if ended.get('reason') == 'driver exited between requests':
                # The driver died before finish could be sent: an inactive
                # no-op that retains its death details.
                return {'ok':True,'session':'inactive','already_finished':True,'session_ended':ended}
            # A timeout/cleanup failure during an ACTIVE finish stays an error
            # even though the failure path has now made the session inactive.
            raise
        outcome = close_session()
        if outcome.get('ok'):
            # Teardown confirmed clean: handles closed, no escalation, child
            # reaped with exit status 0.
            return ack
        if session_ended is None:
            # Record why this finish is not a clean success, then finalize the
            # record so the last log event matches the response below.
            ended=remember_end('finish acknowledged but teardown did not confirm clean')
            ended['child_exit_code']=outcome.get('child_exit_code')
            ended['cleanup']=outcome
            log_event({'session_ended':ended})
            ack['session_ended']=ended
        # The driver ACKed, but teardown did NOT confirm clean (nonzero child
        # status, escalation, or close errors). Keep the ACK details visible
        # AND surface the cleanup outcome; this finish is not a success.
        ack['ok']=False
        ack['cleanup']=outcome
        child_code=outcome.get('child_exit_code')
        if isinstance(child_code,int) and child_code!=0:
            ack['returncode']=child_code  # the child's real exit status
        return ack
    if operation == "status":
        if proc is not None and proc.poll() is not None:
            remember_end('driver exited between requests')
            close_session()
        return {"ok": True, "session_active": proc is not None and proc.poll() is None,
                'session_ended':session_ended,'log':str(session_log) if session_log else None}
    raise ValueError("operation must be start, request, finish, or status")


def image_paths(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "image" and isinstance(child, str) and child.endswith(".png"):
                yield child
            yield from image_paths(child)
    elif isinstance(value, list):
        for child in value:
            yield from image_paths(child)


def main():
    while True:
        message = read_message()
        if message is None:
            break
        method = message.get("method")
        ident = message.get("id")
        try:
            if method == "initialize":
                result = {"protocolVersion": message["params"].get("protocolVersion", "2024-11-05"),
                          "capabilities": {"tools": {}},
                          "serverInfo": {"name": "computer-use-session", "version": "1.0.0"}}
            elif method == "notifications/initialized" or method == "notifications/cancelled":
                continue
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": [{
                    "name": "computer_use_session",
                    "description": "Start and control one persistent computer-use session. Start once, send commands through request, and finish at task end. For predictable UI, inspect once, batch all known actions in one request, then inspect the final result. Extra observations must resolve a specific unknown or failure. Auto delivery omits exact duplicate desktop images; use image_policy always to force a repeated image. Native pressed/checked/selected/expanded flags can verify supported controls without images.",
                    "inputSchema": {"type": "object", "properties": {
                        "operation": {"type": "string", "enum": ["start", "request", "finish", "status"]},
                        "args": {"type": "array", "items": {"type": "string"}},
                        "stdin": {"type": "string"},
                        "image_policy": {"type": "string", "enum": ["auto", "always"], "default": "auto", "description": "auto omits exact duplicate desktop images in this session; always forces delivery"}}, "required": ["operation"]}}]}
            elif method == "tools/call":
                value = tool_call(message["params"].get("arguments", {}))
                content = [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}]
                visual = value.get("visual", {})
                suppressed = visual.get("path") if visual.get("status") == "unchanged" and not value.get("returncode", 0) else None
                for path in dict.fromkeys(image_paths(value)):
                    if path == suppressed:
                        continue
                    with open(path, "rb") as image:
                        content.append({"type": "image", "data": base64.b64encode(image.read()).decode("ascii"), "mimeType": "image/png"})
                result = {"content": content}
                # A failure must never be framed as a successful tool call:
                # a nonzero returncode, a tool result whose own ok is False,
                # or a CURRENT cleanup failure all set isError. An
                # inactive/repeated finish (ok true) stays a successful no-op
                # even when historical death details remain in its payload.
                cleanup = value.get("cleanup")
                if value.get("returncode", 0) or value.get("ok") is False or (
                        isinstance(cleanup, dict) and cleanup.get("ok") is False):
                    result["isError"] = True
            else:
                if ident is None:
                    continue
                raise ValueError("unknown method: " + str(method))
            if ident is not None:
                write_message({"jsonrpc": "2.0", "id": ident, "result": result})
        except Exception as exc:
            if ident is not None:
                write_message({"jsonrpc": "2.0", "id": ident, "error": {"code": -32000, "message": str(exc)}})
    close_session()


if __name__ == "__main__":
    try:
        main()
    finally:
        close_session()
