"""lolzteam.__main__ — CLI entrypoint for the code generator."""

import sys
from pathlib import Path

# Add codegen directory to path so generate.py can be imported
sys.path.insert(0, str(Path(__file__).parent.parent / "codegen"))

from codegen.generate import main  # noqa: E402

if __name__ == "__main__":
    main()
