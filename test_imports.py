#!/usr/bin/env python3
"""
Test imports for debugging
"""
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("Testing imports...")

try:
    from lex_multimodal_processor import multimodal_processor
    print("✓ Multimodal processor imported")
except Exception as e:
    print(f"✗ Multimodal processor import failed: {e}")
    print("  This is likely because dependencies are missing inside Docker")

try:
    from lex_orchestrated import OrchestratedLEX
    print("✓ OrchestratedLEX imported")
    lex = OrchestratedLEX()
    print("✓ OrchestratedLEX instantiated")
except Exception as e:
    print(f"✗ OrchestratedLEX failed: {e}")
    import traceback
    traceback.print_exc()