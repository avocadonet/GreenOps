#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Добавляем src в sys.path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import pytest

if __name__ == "__main__":
    # Аргументы для pytest
    args = [
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-v",
        "tests/",
    ]

    exit_code = pytest.main(args)
    sys.exit(exit_code)
