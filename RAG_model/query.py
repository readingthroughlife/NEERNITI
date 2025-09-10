import sys
import os
import time
from pathlib import Path

# Check if we have already created a standalone_rag.py file
if not Path("standalone_rag.py").exists():
    print("Error: standalone_rag.py not found. Please create it first.")
    sys.exit(1)

# Check if text files exist
required_files = ["output_for_dsrag.txt", "district_data.txt"]
missing_files = []

for file in required_files:
    if not Path(file).exists():
        missing_files.append(file)

if missing_files:
    print("Error: The following required files are missing:")
    for file in missing_files:
        print(f"  - {file}")
    print("Please make sure these files exist in the current directory.")
    sys.exit(1)

# Import functions from standalone_rag.py
print("Loading RAG system...")
from standalone_rag import query

# Set environment variables for API keys if needed
if "GEMINI_API_KEY" in os.environ and "COHERE_API_KEY" in os.environ:
    print("Using API keys from environment variables")
else:
    print("NOTE: For convenience, you can set GEMINI_API_KEY and COHERE_API_KEY environment variables")

# Print header
def print_header():
    print("\n" + "=" * 60)
    print("🔍 NEERNITI RAG Query System 🔍".center(60))
    print("=" * 60)
    print("\nThis system can answer questions about:")
    print("- District-level data (rainfall, geographic info)")
    print("- Taluk-level data (recharge worthy area, etc.)")
    print("\nExample questions:")
    print("  - What is the rainfall in district Dang?")
    print("  - What is the total recharge worthy area in taluk Amod?")
    print("  - Which district has the highest rainfall?")
    print("  - Compare the rainfall in Surat and Navsari districts")
    print("\n" + "-" * 60)

# Check if a query was provided as command line argument
if len(sys.argv) > 1:
    print_header()
    user_query = " ".join(sys.argv[1:])
    print(f"\nQuestion: {user_query}")
    
    start_time = time.time()
    answer = query(user_query)
    end_time = time.time()
    
    print(f"\nAnswer (took {end_time - start_time:.2f} seconds):")
    print(answer)
    sys.exit(0)

# Interactive mode
print_header()
print("🔍 Enter your questions (or press Enter with empty input to exit):")

try:
    while True:
        user_query = input("\nQuestion: ").strip()
        if not user_query:
            break
            
        start_time = time.time()
        answer = query(user_query)
        end_time = time.time()
        
        print(f"\nAnswer (took {end_time - start_time:.2f} seconds):")
        print(answer)
        
    print("\nThank you for using the NEERNITI RAG Query System!")
except KeyboardInterrupt:
    print("\n\nExiting...")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
