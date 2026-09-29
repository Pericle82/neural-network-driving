"""Genera le tappe del corso dal branch `solution`.

Fonte unica: sul branch `solution` il codice è completo, e ogni parte da far scrivere
allo studente sta tra due marcatori:

    | # BEGIN SOLUTION(step-01) tappa 1: Car.step    (in TypeScript: // BEGIN SOLUTION(...))
    | ...codice della soluzione...
    | # END SOLUTION

Per ogni tappa N lo script produce due commit con tag:
  step-NN-start     blocchi delle tappe < N risolti, blocchi della tappa N (e successive)
                    sostituiti da `raise NotImplementedError("<messaggio>")`
  step-NN-solution  blocchi delle tappe <= N risolti

I file legati a una tappa compaiono solo da quella tappa in poi:
  tests/test_stepNN.py    notebooks/NN_*.py

La catena parte dal tag `step-00` (mai riscritto) e finisce sul branch `main`.
Il contenuto rigenerato per la tappa 0 viene confrontato con `step-00`: se differisce,
lo script lo segnala (le differenze finiranno nel primo commit della tappa 1).

Uso (dal branch solution, a working tree pulito):
    uv run python tools/make_steps.py            # tutte le tappe trovate
    uv run python tools/make_steps.py --dry-run  # mostra cosa farebbe
Poi: git push --force origin main 'refs/tags/step-*'
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BEGIN = re.compile(r"^(?P<indent>\s*)(?P<c>#|//) BEGIN SOLUTION\(step-(?P<step>\d+)\)\s*(?P<msg>.*)$")
END = re.compile(r"^\s*(#|//) END SOLUTION\s*$")
FILE_STEP = [re.compile(r"^tests/test_step(\d+)\.py$"), re.compile(r"^notebooks/(\d+)_.+\.py$")]
SOURCE_BRANCH = "solution"
BASE_TAG = "step-00"


def git(*args: str, cwd: Path | None = None, env: dict | None = None) -> str:
    return subprocess.run(["git", *args], cwd=cwd, env=env, check=True, capture_output=True, text=True).stdout


def file_step(path: str) -> int:
    for rx in FILE_STEP:
        if m := rx.match(path):
            return int(m.group(1))
    return 0


def render(text: str, keep: int, path: str) -> str:
    """Tiene le soluzioni delle tappe <= keep, sostituisce le altre con uno stub."""
    out, block = [], None
    for n, line in enumerate(text.splitlines(keepends=True), 1):
        if block is None and (m := BEGIN.match(line)):
            block = m
            continue
        if block is not None and END.match(line):
            if int(block["step"]) > keep:
                msg = block["msg"] or f"TODO(step-{block['step']})"
                stub = (f'raise NotImplementedError("{msg}")' if block["c"] == "#"
                        else f"throw new Error('{msg}')")
                out.append(f"{block['indent']}{stub}\n")
            block = None
            continue
        if block is None or int(block["step"]) <= keep:
            out.append(line)
    if block is not None:
        sys.exit(f"{path}: BEGIN SOLUTION senza END SOLUTION")
    return "".join(out)


def build_tree(src: Path, dest: Path, keep: int, include_up_to: int) -> None:
    for f in sorted(p for p in src.rglob("*") if p.is_file()):
        rel = f.relative_to(src).as_posix()
        if file_step(rel) > include_up_to:
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if rel.startswith("tools/"):  # gli strumenti del corso si copiano così come sono
            shutil.copy2(f, target)
            continue
        try:
            target.write_text(render(f.read_text(), keep, rel))
        except UnicodeDecodeError:
            shutil.copy2(f, target)


def max_step(src: Path) -> int:
    steps = [0]
    for f in (p for p in src.rglob("*") if p.is_file()):
        rel = f.relative_to(src).as_posix()
        steps.append(file_step(rel))
        try:
            steps += [int(m["step"]) for line in f.read_text().splitlines() if (m := BEGIN.match(line))]
        except UnicodeDecodeError:
            pass
    return max(steps)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    repo = Path(git("rev-parse", "--show-toplevel").strip())
    if git("status", "--porcelain", cwd=repo).strip():
        sys.exit("working tree non pulito: fai commit sul branch solution prima di generare le tappe")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        src = tmp / "src"
        src.mkdir()
        archive = subprocess.run(["git", "archive", SOURCE_BRANCH], cwd=repo, check=True, capture_output=True).stdout
        subprocess.run(["tar", "-x", "-C", str(src)], input=archive, check=True)
        last = max_step(src)
        print(f"tappe trovate su '{SOURCE_BRANCH}': 1..{last}")

        # Controllo di coerenza con la tappa 0 già pubblicata.
        check = tmp / "check0"
        build_tree(src, check, keep=0, include_up_to=0)
        base = tmp / "base"
        base.mkdir()
        subprocess.run(["tar", "-x", "-C", str(base)],
                       input=subprocess.run(["git", "archive", BASE_TAG], cwd=repo, check=True, capture_output=True).stdout,
                       check=True)
        diff = subprocess.run(["diff", "-rq", str(base), str(check)], capture_output=True, text=True).stdout
        if diff.strip():
            print("nota: la tappa 0 rigenerata differisce da step-00 in:")
            for line in diff.strip().splitlines():
                print("   ", line.replace(str(base), "step-00").replace(str(check), "rigenerata"))

        if args.dry_run:
            for n in range(1, last + 1):
                print(f"  step-{n:02d}-start, step-{n:02d}-solution")
            return

        wt = tmp / "wt"
        git("worktree", "add", "--detach", str(wt), BASE_TAG, cwd=repo)
        try:
            base_date = int(git("log", "-1", "--format=%ct", BASE_TAG, cwd=repo))
            for n in range(1, last + 1):
                for kind, keep in (("start", n - 1), ("solution", n)):
                    for p in wt.iterdir():
                        if p.name != ".git":
                            shutil.rmtree(p) if p.is_dir() else p.unlink()
                    build_tree(src, wt, keep=keep, include_up_to=n)
                    git("add", "-A", cwd=wt)
                    # Date fisse: stesso contenuto → stesso hash, niente force-push inutili.
                    stamp = f"{base_date + n * 120 + (60 if kind == 'solution' else 0)} +0000"
                    env = {**__import__("os").environ, "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp}
                    title = f"Tappa {n}: {'punto di partenza' if kind == 'start' else 'soluzione'}"
                    git("commit", "--allow-empty", "-q", "-m", title, cwd=wt, env=env)
                    tag = f"step-{n:02d}-{kind}"
                    git("tag", "-f", "-a", tag, "-m", title, cwd=wt, env=env)
                    print(f"  {tag}  {git('rev-parse', '--short', 'HEAD', cwd=wt).strip()}")
            head = git("rev-parse", "HEAD", cwd=wt).strip()
        finally:
            git("worktree", "remove", "--force", str(wt), cwd=repo)
        git("branch", "-f", "main", head, cwd=repo)
        print(f"main → {head[:7]}.  Pubblica con: git push --force origin main 'refs/tags/step-*'")


if __name__ == "__main__":
    main()
