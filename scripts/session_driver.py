"""JSON-lines CLI relay kept alive by the existing session guardian."""
import json
from pathlib import Path
import subprocess
import sys


def relay(source, sink):
    print(json.dumps({'ok': True, 'driver': 'ready'}), file=sink, flush=True)
    for line in source:
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
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('cu.py')), *args],
                                input=data, capture_output=True, text=True)
        response={'returncode':result.returncode}
        try:response['result']=json.loads(result.stdout)
        except ValueError:response['stdout']=result.stdout
        if result.stderr:response['stderr']=result.stderr
        print(json.dumps(response,ensure_ascii=False,separators=(',',':')), file=sink, flush=True)
        if result.returncode:
            return result.returncode
    return 0  # EOF lets the guardian clean up; never detach a hidden session.
