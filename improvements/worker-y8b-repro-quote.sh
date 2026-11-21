#!/bin/bash
# Reproduce the executor quoting trap on A2's live tab (read-only evals).
echo "=== A: executor exact quoting (single quotes inside JS) ==="
/tmp/e1/step.sh '{"cmd":"eval","js":"return (function(){var cc=document.querySelector('#contacts-count');return cc?cc.textContent.trim():null;})()"}'
echo "=== B: fixed quoting (double quotes in JS) ==="
/tmp/e1/step.sh '{"cmd":"eval","js":"return (function(){var cc=document.querySelector(\"#contacts-count\");return cc?cc.textContent.trim():null;})()"}'
