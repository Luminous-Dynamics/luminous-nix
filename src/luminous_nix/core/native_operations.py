"""
Compatibility shim for reorganization.
The actual native_operations module has been moved to luminous_nix.nix.native_operations
"""

# Re-export everything from the new location
from luminous_nix.nix.native_operations import *

# Add deprecation warning
import warnings
warnings.warn(
    "Importing from luminous_nix.core.native_operations is deprecated. "
    "Use luminous_nix.nix.native_operations instead.",
    DeprecationWarning,
    stacklevel=2
)