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
    # INTERNAL PROVENANCE: True only when cu.main raised the exact typed
    # cu.PreflightRefusal exception (validation failed before focus or input).
    # It is never inferred from any printed/backend JSON, so a forged
    # 'recoverable' flag inside a result payload can never keep a session
    # alive. The printed envelope keeps its legacy 'recoverable':true field
    # for compatibility, but continuation decisions read only this attribute.
    refusal=False
    try:
        sys.argv=[str(Path(__file__).with_name('cu.py')),*args]
        sys.stdin=io.StringIO(data)
        with redirect_stdout(stdout),redirect_stderr(stderr):
            try:code=cu.main()
            except SystemExit as exc:
                code=exc.code
                if code:cu.stop_session_on_error()
            except cu.PreflightRefusal as exc:
                refusal=True
                print(json.dumps({'ok':False,'completed':0,'recoverable':True,'error':str(exc),
                                  'next_step':'Correct the request; if the observation expired, observe again. No input was sent.'}),flush=True)
                code=1
            except BaseException as exc:
                cu.stop_session_on_error()
                print(json.dumps({'ok':False,'error':str(exc)},ensure_ascii=False),flush=True)
                code=1
    finally:sys.argv,sys.stdin=argv,stdin
    result=subprocess.CompletedProcess(args,code,stdout.getvalue(),stderr.getvalue())
    result.preflight_refusal=refusal
    return result


def continuation_reason(result, body):
    """Bounded single-line reason for a fatal command's session_ended envelope.

    Prefers the backend result's own error string, then the first stderr
    line; whitespace-collapsed and capped at 400 chars like every other
    driver diagnostic.
    """
    error=body.get('error') if isinstance(body,dict) else None
    if not isinstance(error,str) or not error.strip():
        stderr=(result.stderr or '').strip().splitlines()
        error=stderr[0] if stderr else 'driver command failed'
    return ' '.join(str(error).split())[:400]


def relay(source, sink):
    import cu
    from browser_worker import BrowserWorker
    browser=cu.browser;worker=BrowserWorker()
    # The browser endpoint default is session state, scoped exactly like the
    # browser executor above: one serial relay session starts from the
    # standalone CLI default (9222) and never inherits a previous session's
    # retained endpoint; the enclosing process default is restored in the
    # finally block even when a command raises. No concurrent relay support.
    endpoint=cu.BROWSER_ENDPOINT
    try:
        cu.browser=worker.request
        cu.BROWSER_ENDPOINT='http://127.0.0.1:9222'
        return relay_commands(source,sink)
    finally:
        cu.browser=browser
        cu.BROWSER_ENDPOINT=endpoint
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
    from visual_delivery import VisualCheckpoint
    checkpoint = VisualCheckpoint()
    print(json.dumps({'ok': True, 'driver': 'ready'}), file=sink, flush=True)
    for line in request_lines(source):
        request = json.loads(line)
        if not isinstance(request, dict):
            raise ValueError('request must be an object with args and optional stdin')
        args = request.get('args')
        data = request.get('stdin', '')
        policy = request.get('image_policy', 'always')
        if policy not in ('auto', 'always'):
            raise ValueError('image_policy must be auto or always')
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
        if policy == 'auto':
            visual = checkpoint.assess(response)
            if visual is not None:response['visual'] = visual
        else:
            checkpoint.clear()
        import cu
        body=response.get('result')
        # ONE continuation decision per command. A failed command continues
        # only on INTERNAL provenance (the typed PreflightRefusal exception)
        # or the exact transient matcher (returncode 1, command `act`,
        # desktop refusal envelope, all co-error exclusions). Any
        # 'recoverable' flag inside the backend payload is never trusted, and
        # missing/invalid metadata is fail-closed: the session ends.
        continues=result.returncode==0 or (
            result.returncode==1 and
            (getattr(result,'preflight_refusal',False) or
             (args[0]=='act' and cu.is_transient_refusal(body))))
        # Envelope shape: EVERY command response carries the top-level
        # boolean `session_continues` (True for successes too); a fatal
        # command additionally carries `session_ended` with the bounded
        # `reason` and the failing command's `exit_code`.
        response['session_continues']=continues
        if result.returncode and not continues:
            response['session_ended']={'reason':continuation_reason(result,body),
                                       'exit_code':result.returncode}
        print(json.dumps(response,ensure_ascii=False,separators=(',',':')), file=sink, flush=True)
        if result.returncode and not continues:
            return result.returncode
    return 0  # EOF lets the guardian clean up; never detach a hidden session.
