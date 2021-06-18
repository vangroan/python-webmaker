import contextlib
import os
from typing import Generator


@contextlib.contextmanager
def cd(target_dir: str) -> Generator[None, None, None]:
    """Change directory, and change it back to its original value."""
    cwd = os.getcwd()
    try:
        os.chdir(target_dir)
        yield
    finally:
        os.chdir(cwd)
