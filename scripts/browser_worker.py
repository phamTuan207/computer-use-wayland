"""One private Node worker owned by an interactive driver; never retries input."""
import json
import os
from pathlib import Path
import select
import subprocess
import time


class BrowserWorker:
    def __init__(self):
        self.process=None
        self.closed=False

    def request(self,request):
        import cu
        if self.closed:raise RuntimeError('browser worker ended; stop this task')
        try:
            cu.check_cancel()
            payload=(json.dumps(request,ensure_ascii=False)+'\n').encode()
            limit=32*1024*1024
            if len(payload)>limit:raise ValueError('browser worker request exceeds 32 MiB')
            if self.process is None:
                # stderr is inherited (None), never DEVNULL: the bridge starts the
                # driver with fd 2 on its private session stderr log, so crashes and
                # node diagnostics from this worker reach that same log. No per-worker
                # file and no pipe to drain — node only writes stderr when it dies.
                self.process=subprocess.Popen(['node',str(Path(__file__).with_name('cdp.mjs')),'--worker'],
                    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=None,bufsize=0)
                os.set_blocking(self.process.stdin.fileno(),False)
            deadline=time.monotonic()+cu.browser_timeout(request)
            sent=0
            while sent<len(payload):
                cu.check_cancel()
                if time.monotonic()>=deadline:raise RuntimeError('browser worker timed out')
                if select.select([], [self.process.stdin], [], .04)[1]:
                    sent+=os.write(self.process.stdin.fileno(),memoryview(payload)[sent:sent+65536])
            response=bytearray()
            while True:
                cu.check_cancel()
                if time.monotonic()>=deadline:raise RuntimeError('browser worker timed out')
                if not select.select([self.process.stdout],[],[],.04)[0]:continue
                chunk=os.read(self.process.stdout.fileno(),65536)
                if not chunk:raise RuntimeError('browser worker exited before response; do not replay input')
                response.extend(chunk)
                if len(response)>limit:raise RuntimeError('browser worker response exceeds 32 MiB')
                if b'\n' in chunk:
                    if response[-1:]!=b'\n' or response.count(b'\n')!=1:
                        raise RuntimeError('invalid browser worker framing')
                    result=json.loads(response)
                    if not isinstance(result,(dict,list)):raise RuntimeError('invalid browser worker response')
                    cu.check_cancel()
                    if isinstance(result,dict) and result.get('ok') is False:self.close()
                    return result
        except BaseException:
            self.close()
            raise

    def close(self):
        self.closed=True
        process=self.process;self.process=None
        if process is None:return
        try:
            try:process.stdin.close()
            except OSError:pass
            try:process.wait(timeout=.5)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:process.wait(timeout=.5)
                except subprocess.TimeoutExpired:process.kill();process.wait()
        finally:process.stdout.close()
