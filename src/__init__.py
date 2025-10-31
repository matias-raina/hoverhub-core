"""
HoverHub API package initialization.
This module ensures the project root is on sys.path for proper imports.
"""
import sys
from pathlib import Path

# Add project root to sys.path to make 'src' package importable
# This is needed when running with fastapi-cli or uvicorn
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
