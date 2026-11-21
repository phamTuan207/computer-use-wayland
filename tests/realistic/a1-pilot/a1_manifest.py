#!/usr/bin/env python3
"""Generate the sealed A1 pilot manifest (run by Muse, before run 1).

The manifest holds the only copy of the run-id to arm mapping. It lives
OUTSIDE the repo, never committed before unblinding (Council 2 section
9b). This script prints ONLY the sha256 of the manifest file to stdout;
Muse records that hash in the pilot log. Muse reads the manifest file
to issue runs one at a time. The executor never sees the file.

Run order: Case A pairs 1-3, then Case B pairs 1-3. Within each case the
3 run-pairs are assigned start arms by stratified randomization: exactly
2 pairs start on one arm and 1 pair starts on the other, assigned at
random, so learning effects split across arms inside each case instead
of always favouring CODE (plan section 4, synthesis D2).

The held-out draw is sealed here too: one task drawn at random from the
validated pool (pool candidates must already have passed a live run
each, plan section 2). The draw is opened only after the pilot verdict.

started_at is NOT written into the manifest: writing it would change
the file hash mid-pilot and break tamper detection. started_at is
verified at unblinding from the run_start timestamps in the run logs.

Usage:
  python3 a1_manifest.py --pool test-06,test-07,test-08 --out /path/outside/repo/a1-manifest.jsonl
Stdout prints only: sha256 <hex>
No em dash or en dash in this file.
"""

import argparse
import hashlib
import json
import random
import secrets
import sys


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool", required=True,
                        help="comma-separated validated held-out test IDs")
    parser.add_argument("--out", required=True,
                        help="manifest path OUTSIDE the repo")
    args = parser.parse_args(argv)
    pool = [t.strip() for t in args.pool.split(",") if t.strip()]
    if not pool:
        print("empty pool", file=sys.stderr)
        return 2

    seed = secrets.token_hex(8)
    rng = random.Random(int(seed, 16))
    run_ids = set()
    while len(run_ids) < 12:
        run_ids.add(secrets.token_hex(4))
    run_ids = list(run_ids)

    lines = []
    seq = 0
    for case in ("pick4", "f01"):
        # Stratified: exactly 2 pairs start on one arm, 1 on the other.
        starts = ["STEP", "STEP", "CODE"]
        if rng.random() < 0.5:
            starts = ["CODE", "CODE", "STEP"]
        rng.shuffle(starts)
        for pair in range(3):
            first = starts[pair]
            second = "CODE" if first == "STEP" else "STEP"
            for run_number, arm in ((pair + 1, first), (pair + 1, second)):
                seq += 1
                lines.append({
                    "run_id": run_ids[seq - 1],
                    "case": case,
                    "arm": arm,
                    "run_number": run_number,
                    "agent": "one Codex (Luna 6 Max) session",
                    "run_sequence": seq,
                })
    held_out = rng.choice(pool)
    meta = {"seed": seed, "held_out_draw": held_out, "pool": pool}
    with open(args.out, "w") as h:
        for line in lines:
            h.write(json.dumps(line, sort_keys=True) + "\n")
    meta_path = args.out + ".meta.json"
    with open(meta_path, "w") as h:
        json.dump(meta, h, indent=2, sort_keys=True)
    digest = hashlib.sha256(open(args.out, "rb").read()).hexdigest()
    print("sha256 %s" % digest)
    print("meta: %s (seed and held-out draw sealed there)" % meta_path,
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
