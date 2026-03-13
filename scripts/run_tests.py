"""
Ejecuta la suite de tests.
Uso: python -m scripts.run_tests [args para pytest]
"""

import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent


def main():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"] + sys.argv[1:],
        cwd=_PROJECT_ROOT,
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
