from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, cast

DATE_FMT = "%Y-%m-%d"
FILENAME_DATETIME_FMT = "%Y-%m-%dT%H_%M_%S"
PREV_LINK = "prev"


def main(args_: Optional[Args] = None):
    if args_ is None:
        args = Args.parse_args(argparser())
    else:
        args = args_

    # - when we log on / every day, check for the latest day in the repo.
    #
    # other stuff:
    # - can we make git know where the repo is?
    # - journald logging?

    date = datetime.now().strftime(DATE_FMT)
    day_dir = args.repo_path / date
    day_dir_is_ok = day_dir.exists()
    working_path_is_ok = ensure_symlink_to(args.working_path, day_dir)
    if day_dir_is_ok and working_path_is_ok:
        # We're good, print a message and quit
        print(f"{day_dir} already exists, nothing to do.")

    if args.full or not day_dir_is_ok or not working_path_is_ok:
        # Commit our work to the git repo.
        # Don't worry about empty directories; git doesn't track those.
        git_commit(args.repo_path)

        remove_empty_dirs(args.repo_path, other_than=[day_dir])

        latest = latest_day_dir(args.repo_path)

        # Make a new day folder for today.
        if not day_dir_is_ok:
            print(f"Creating {day_dir}")
            day_dir.mkdir(exist_ok=True, parents=True)

        # If we have a previous day, make a link to it.
        if latest is not None:
            print(f"Previous working path was {latest}")
            prev_link = args.working_path / PREV_LINK
            ensure_symlink_to(prev_link, latest)


def ensure_symlink_to(path: Path, dest: Path) -> bool:
    """Ensure ``path`` is a symlink to ``dest``.

    Returns ``True`` if work was done.
    """
    if not path.parent.exists():
        print("Creating {path.parent}")
        path.parent.mkdir(parents=True)

    if path.is_symlink():
        actual_dest = path.parent / os.readlink(path)
        if actual_dest == dest:
            print(f"{path} is already a link to {dest}")
            return False
        else:
            print(f"{path} is a link to {actual_dest} instead of {dest}")
            path.unlink()
    elif path.exists():
        backup = backup_path(path)
        print(f"Renaming {path} to {backup}")
        path.rename(backup)

    print(f"Linking {path} to {dest}")
    path.symlink_to(dest)
    return True


def backup_path(path: Path) -> Path:
    basename = path.name + "-" + datetime.now().strftime(FILENAME_DATETIME_FMT)
    new_path = path.with_name(basename)
    if new_path.exists():
        raise ValueError(f"Backup path {new_path} already exists")
    return new_path


def remove_empty_dirs(path: Path, other_than: List[Path] = []) -> None:
    """Removes empty child directories of a ``Path``.
    """
    for child in path.iterdir():
        if child in other_than:
            continue

        if not child.is_dir():
            continue

        contents = [path for path in child.iterdir() if path.name != PREV_LINK]
        if contents:
            continue

        print(f"{child} is empty, removing")
        child.rmdir()


def git_commit(repo: Path):
    if repo.exists():
        changes = any(path.name != PREV_LINK for _, path in git_changes(repo))
        if changes:
            print(f"{repo} has local changes, comitting")
            date = datetime.now().strftime(DATE_FMT)
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    date,
                    "-m",
                    f"Temporary / scratch work until {date}",
                ],
                cwd=repo,
                check=True,
            )
        else:
            print(f"{repo} has no local changes")
    else:
        print(f"{repo} doesn't exist, creating")
        repo.mkdir(parents=True)
        print(f"Running `git init` in {repo}")
        subprocess.run(["git", "init"], cwd=repo, check=True)


def git_changes(repo: Path) -> List[Tuple[str, Path]]:
    proc = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files"],
        capture_output=True,
        encoding="utf-8",
        check=True,
        cwd=repo,
    )
    return [(line[:2], repo / line[3:]) for line in proc.stdout.strip().splitlines()]


def latest_day_dir(path: Path) -> Optional[Path]:
    """Gets the latest day in YYYY-mm-dd format.
    """

    # Safety: This program will never be run before the year 1900.
    # If you set your computer's time to a year before 1900, eat shit.
    sentinel = datetime(1900, 1, 1)
    latest = sentinel
    latest_path = path
    for subdir in path.iterdir():
        try:
            date = datetime.strptime(subdir.name, DATE_FMT)
        except ValueError as e:
            continue

        if date > latest:
            latest = date
            latest_path = subdir

    if latest == sentinel:
        return None
    else:
        return latest_path


@dataclass
class Args:
    repo_path: Path
    working_path: Path
    full: bool

    @classmethod
    def parse_args(cls, parser: argparse.ArgumentParser) -> Args:
        args = parser.parse_args()
        return cls(
            repo_path=args.repo_path, working_path=args.working_path, full=args.full,
        )


def argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage a daily scratch directory.")
    parser.add_argument("--repo-path", type=Path, help="Path to the main repository.")
    parser.add_argument(
        "--working-path", type=Path, help="Path to the daily temporary directory."
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="""Perform a full check; this removes empty directories, makes a
        git commit if there's new work, etc. even if today's directory already
        exists.""",
    )

    return parser


if __name__ == "__main__":
    main()
