from importlib.metadata import version, PackageNotFoundError

# Get version form pyproject.toml
try:
    __version__: str = version(__name__)
except PackageNotFoundError:
    # fallback 
    __version__ = "0.0.0+local"

# Public API
from .config import Config    
from .anonymizer import Anonymizer

# Methods to be imported by `from textwash import *` 
# (also silences profiler warnings)
__all__ = ["Config", "Anonymizer", "__version__"]