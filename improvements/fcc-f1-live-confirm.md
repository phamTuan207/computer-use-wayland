# F1 Live Confirmation - HTML Sanitization Test

- **Start Wall-clock Time**: 2026-11-22 06:01:51 +07
- **End Wall-clock Time**: 2026-11-22 06:15:00 +07
- **Elapsed Seconds**: 789 seconds
- **Browser Used**: Chromium 130.0.6723.116 (headless mode via `--headless --disable-gpu --dump-dom`)

## Test Page Used
```html
<!DOCTYPE html>
<html>
<body>
  <input type="text" id="t">
  <textarea id="ta"></textarea>
  <script>
    const t = document.getElementById('t');
    const ta = document.getElementById('ta');
    const tests = ['a\nb', 'a\r\nb', 'a\rb', 'a\n\nb', '\nleading', 'trailing\n'];
    const results = {};
    
    tests.forEach(val => {
      t.value = val;
      ta.value = val;
      results[JSON.stringify(val)] = {
        input: JSON.stringify(t.value),
        textarea: JSON.stringify(ta.value)
      };
    });
    
    const pre = document.createElement('pre');
    pre.id = 'result';
    pre.textContent = JSON.stringify(results);
    document.body.appendChild(pre);
  </script>
</body>
</html>
```

## Results Table

| Input (JSON) | Input Read-back (JSON) | Textarea Read-back (JSON) |
| :--- | :--- | :--- |
| "a\nb" | "ab" | "a\nb" |
| "a\r\nb" | "ab" | "a\nb" |
| "a\rb" | "ab" | "a\nb" |
| "a\n\nb" | "ab" | "a\n\nb" |
| "\nleading" | "leading" | "\nleading" |
| "trailing\n" | "trailing" | "trailing\n" |

## Verdict
CONFIRMED (rule holds live)
