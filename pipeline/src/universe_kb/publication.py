"""Serialize directory publication and retain a recoverable prior tree on failure."""

from __future__ import annotations

import fcntl
import logging
import shutil
import tempfile
from pathlib import Path

log = logging.getLogger(__name__)


def publish_directory(staging: Path, destination: Path) -> None:
    """
    Publish a complete sibling staging tree, rolling back a failed final rename.

    The persistent lock inode coordinates cooperating processes. Each invocation owns
    its recovery path, so another publisher cannot erase a failed run's backup.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    lock_path = destination.with_name(f".kb-publish-{destination.name}.lock")
    with lock_path.open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        previous: Path | None = None
        if destination.exists():
            previous = Path(tempfile.mkdtemp(prefix=f".kb-previous-{destination.name}-",
                                             dir=destination.parent))
            previous.rmdir()
            destination.rename(previous)
        try:
            staging.rename(destination)
        except BaseException:
            # Preserve a non-cooperating publisher's completed destination and retain
            # our backup for recovery when replacing it would destroy their result.
            if previous is not None and previous.exists() and not destination.exists():
                try:
                    previous.rename(destination)
                except OSError:
                    log.error("Could not restore prior publication; recovery directory retained")
            raise
        if previous is not None:
            shutil.rmtree(previous)
