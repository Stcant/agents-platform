#!/usr/bin/env bash
# Create disposable copies; add git history only to scenarios that need it.
# The source fixtures in this repository contain no .git directory.

set -eu

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
dest="${TMPDIR:-/tmp}/opencode/dev-brain-evals"
name="dev-brain eval"
email="dev-brain@example.invalid"

rm -rf "$dest"
mkdir -p "$dest"
cp -R "$here/fixtures/." "$dest/"

commit() {
  dir="$1"
  message="$2"
  git -C "$dir" add -A
  git -C "$dir" -c user.name="$name" -c user.email="$email" commit -qm "$message"
}

init() {
  dir="$1"
  rm -rf "$dir/.git"
  git -C "$dir" init -q
  git -C "$dir" symbolic-ref HEAD refs/heads/main
}

init "$dest/bugfix"
commit "$dest/bugfix" "fixture: failing discount test"

init "$dest/explain"
commit "$dest/explain" "fixture: order flow"

# resume: first commit with add only and a stale state, then subtract without updating state
init "$dest/resume"
cat > "$dest/resume/calc.py" <<'EOF'
def add(a, b):
    return a + b
EOF
cat > "$dest/resume/test_calc.py" <<'EOF'
import unittest

from calc import add


class CalcTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)


if __name__ == "__main__":
    unittest.main()
EOF
cat > "$dest/resume/.dev-brain/STATE.md" <<'EOF'
# State — calc
Updated: 2026-10-21 · Branch: main

## Goal
Add and subtract integers — acceptance: `python3 -m unittest -v` passes.

## Done (latest first, max 5)
- `add` implemented — evidence: `python3 -m unittest -v` PASS

## In progress / blockers
- none

## Known pre-existing failures
- none

## Next (max 3)
1. Implement `subtract` in `calc.py` and add a test.
EOF
commit "$dest/resume" "add with test and state"

cat > "$dest/resume/calc.py" <<'EOF'
def add(a, b):
    return a + b


def subtract(a, b):
    return a - b
EOF
cat > "$dest/resume/test_calc.py" <<'EOF'
import unittest

from calc import add, subtract


class CalcTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_subtract(self):
        self.assertEqual(subtract(5, 3), 2)


if __name__ == "__main__":
    unittest.main()
EOF
commit "$dest/resume" "implement subtract with test (state not updated)"

echo "fixtures ready in $dest:"
for dir in "$dest"/*/; do
  if [ -d "$dir/.git" ]; then
    echo "  $(basename "$dir"): $(git -C "$dir" log --oneline | wc -l) commit(s)"
  else
    echo "  $(basename "$dir"): no git history needed"
  fi
done
