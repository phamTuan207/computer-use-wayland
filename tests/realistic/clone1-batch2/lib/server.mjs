// Loopback static file server for the realistic test fixtures.
// Serves one directory on 127.0.0.1 on an ephemeral port. No outside
// network is used. Fixtures are plain files, so the server only reads
// from the given root and never follows paths outside it.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const MIME = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.mjs': 'text/javascript',
  '.json': 'application/json',
  '.css': 'text/css',
  '.txt': 'text/plain',
  '.md': 'text/plain',
  '.mp4': 'video/mp4',
  '.vtt': 'text/vtt',
};

export function serveDir(rootDir) {
  const root = path.resolve(rootDir);
  const server = http.createServer((req, res) => {
    const urlPath = decodeURIComponent(req.url.split('?')[0]);
    const fp = path.join(root, urlPath === '/' ? 'fixture.html' : urlPath);
    if (!fp.startsWith(root)) {
      res.writeHead(403);
      res.end('forbidden');
      return;
    }
    fs.readFile(fp, (err, data) => {
      if (err) {
        res.writeHead(404);
        res.end('not found');
        return;
      }
      const type = MIME[path.extname(fp)] || 'application/octet-stream';
      const range = req.headers.range;
      if (range && /^bytes=\d*-\d*$/.test(range)) {
        const [startStr, endStr] = range.replace('bytes=', '').split('-');
        const start = startStr ? Number(startStr) : 0;
        const end = endStr ? Math.min(Number(endStr), data.length - 1) : data.length - 1;
        if (start >= data.length || start > end) {
          res.writeHead(416, { 'Content-Range': 'bytes */' + data.length });
          res.end();
          return;
        }
        res.writeHead(206, {
          'Content-Type': type,
          'Accept-Ranges': 'bytes',
          'Content-Range': 'bytes ' + start + '-' + end + '/' + data.length,
          'Content-Length': end - start + 1,
        });
        res.end(data.subarray(start, end + 1));
        return;
      }
      res.writeHead(200, {
        'Content-Type': type,
        'Accept-Ranges': 'bytes',
        'Content-Length': data.length,
      });
      res.end(data);
    });
  });
  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => {
      resolve({
        url: `http://127.0.0.1:${server.address().port}`,
        close: () => new Promise((r) => server.close(r)),
      });
    });
  });
}
