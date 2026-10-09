"""Session-owned layer surface control; all capture paths use the same fence."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import select
import shutil
import socket
import subprocess
import time


def endpoint(state, token):
    if not isinstance(token, str) or not re.fullmatch(r'[0-9a-f]{32}', token):
        raise RuntimeError('invalid indicator session token')
    return state / ('indicator-' + token + '.sock')


class Native:
    def __init__(self, env):
        binary = shutil.which('computer-use-indicator', path=env.get('PATH'))
        binary = binary or str(Path(__file__).resolve().parents[1] / 'native/indicator')
        self.process = subprocess.Popen([binary], env=env, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, start_new_session=True)
        try:
            self.reply('ready')
        except BaseException:
            self.close()
            raise

    def reply(self, expected):
        deadline = time.monotonic() + 3
        value = bytearray()
        while len(value) < 128:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([self.process.stdout], [], [], remaining)[0]:
                raise RuntimeError('indicator frame acknowledgement timed out')
            byte = os.read(self.process.stdout.fileno(), 1)
            if not byte:
                raise RuntimeError('indicator disconnected')
            if byte == b'\n':
                if value.decode() != expected:
                    raise RuntimeError('unexpected indicator acknowledgement')
                return
            value.extend(byte)
        raise RuntimeError('invalid indicator acknowledgement')

    def command(self, command):
        expected = {'hide': 'hidden', 'show': 'visible'}.get(command, 'ok')
        self.process.stdin.write((command + '\n').encode())
        self.process.stdin.flush()
        self.reply(expected)
        return expected

    def close(self):
        try:
            try:
                self.process.stdin.close()
            except (BrokenPipeError, OSError):
                pass
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                try:
                    self.process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
        finally:
            self.process.stdout.close()


def listen(state, token):
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        server.bind(str(endpoint(state, token)))
        endpoint(state, token).chmod(0o600)
        server.listen(4)
        return server
    except BaseException:
        server.close()
        raise


def serve(server, native, token):
    with server.accept()[0] as client:
        client.settimeout(3)
        data = bytearray()
        while b'\n' not in data and len(data) <= 512:
            chunk = client.recv(512 - len(data) + 1)
            if not chunk:
                raise RuntimeError('indicator request disconnected')
            data.extend(chunk)
        request = json.loads(data)
        command = request.get('command', '')
        if request.get('token') != token or not isinstance(command, str) or len(command) > 200:
            raise RuntimeError('invalid indicator request')
        if command not in ('hide', 'show') and not re.fullmatch(r'move [\w.-]+ [0-9.]+ [0-9.]+', command):
            raise RuntimeError('invalid indicator command')
        reply = native.command(command)
        client.sendall((reply + '\n').encode())


def request(state, command):
    try:
        saved = json.loads((state / 'session.json').read_text())
    except FileNotFoundError:
        if os.environ.get('CU_SESSION_TOKEN'):
            raise RuntimeError('indicator session ended')
        return False
    if saved.get('version') != 3:
        raise RuntimeError('indicator recovery required before capture/input')
    token = saved.get('token')
    if os.environ.get('CU_SESSION_TOKEN', token) != token:
        raise RuntimeError('indicator session changed')
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(4)
        client.connect(str(endpoint(state, token)))
        client.sendall((json.dumps({'token': token, 'command': command}) + '\n').encode())
        reply = bytearray()
        while b'\n' not in reply and len(reply) < 128:
            part = client.recv(128)
            if not part:
                raise RuntimeError('indicator owner disconnected')
            reply.extend(part)
        expected = {'hide': b'hidden\n', 'show': b'visible\n'}.get(command, b'ok\n')
        if reply != expected:
            raise RuntimeError('indicator visibility acknowledgement failed')
    return True


@contextmanager
def capture_clean(state):
    active = request(state, 'hide')
    try:
        yield
    finally:
        if active:
            if not request(state, 'show'):
                raise RuntimeError('indicator session ended during capture')
