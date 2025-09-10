#!/usr/bin/env python3

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing imports...")
    import uvicorn
    print("✓ uvicorn imported successfully")
    
    from main import app
    print("✓ main.py imported successfully")
    print(f"✓ App object: {app}")
    
    print("\nTesting server startup...")
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='debug')
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
