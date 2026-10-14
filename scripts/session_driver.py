"""JSON-lines CLI relay kept alive by the existing session guardian."""
import json
import io
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import subprocess
import sys


def execute(args, data):
    import cu
    stdout,stderr=io.StringIO(),io.StringIO()
    argv,stdin=sys.argv,sys.stdin
    code=0
    try:
        sys.argv=[str(Path(__file__).with_name('cu.py')),*args]
        sys.stdin=io.StringIO(data)
        with redirect_stdout(stdout),redirect_stderr(stderr):
            try:code=cu.main()
            except SystemExit as exc:
                code=exc.code
                if code:cu.stop_session_on_error()
            except BaseException as exc:
                cu.stop_session_on_error()
                print(json.dumps({'ok':False,'error':str(exc)},ensure_ascii=False),flush=True)
                code=1
    finally:sys.argv,sys.stdin=argv,stdin
    return subprocess.CompletedProcess(args,code,stdout.getvalue(),stderr.getvalue())


def relay(source, sink):
    import cu
    from browser_worker import BrowserWorker
    browser=cu.browser;worker=BrowserWorker()
    try:
        cu.browser=worker.request
        return relay_commands(source,sink)
    finally:
        cu.browser=browser
        worker.close()


REQUEST_LINE_LIMIT=8*1024*1024

def request_lines(source):
    """Read each request in bounded chunks, counting UTF-8 bytes before parsing."""
    source=getattr(source,'buffer',source)
    parts=[];total=0
    while True:
        chunk=source.readline(min(65536,REQUEST_LINE_LIMIT-total+1))
        if not chunk:
            if parts:yield b''.join(parts).decode('utf-8') if isinstance(parts[0],bytes) else ''.join(parts)
            return
        total+=len(chunk.encode('utf-8')) if isinstance(chunk,str) else len(chunk)
        if total>REQUEST_LINE_LIMIT:raise ValueError('driver request line exceeds 8 MiB')
        parts.append(chunk)
        if chunk.endswith(b'\n' if isinstance(chunk,bytes) else '\n'):
            yield b''.join(parts).decode('utf-8') if isinstance(parts[0],bytes) else ''.join(parts)
            parts=[];total=0

def relay_commands(source, sink):
    print(json.dumps({'ok': True, 'driver': 'ready'}), file=sink, flush=True)
    for line in request_lines(source):
        request = json.loads(line)
        if not isinstance(request, dict):
            raise ValueError('request must be an object with args and optional stdin')
        args = request.get('args')
        data = request.get('stdin', '')
        if not isinstance(args, list) or not args or not all(isinstance(a, str) for a in args):
            raise ValueError('args must be a non-empty array of strings')
        if not isinstance(data, str):
            raise ValueError('stdin must be a string')
        if args == ['finish']:
            print(json.dumps({'ok': True, 'driver': 'finished'}), file=sink, flush=True)
            return 0
        if args[0] not in ('observe', 'act', 'windows', 'doctor', 'status', 'browser', 'a11y'):
            raise ValueError('unsupported driver command')
        result = execute(args,data)
        response={'returncode':result.returncode}
        try:response['result']=json.loads(result.stdout)
        except ValueError:response['stdout']=result.stdout
        if result.stderr:response['stderr']=result.stderr
        print(json.dumps(response,ensure_ascii=False,separators=(',',':')), file=sink, flush=True)
        if result.returncode:
            return result.returncode
    return 0  # EOF lets the guardian clean up; never detach a hidden session.
