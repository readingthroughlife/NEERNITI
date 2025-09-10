import os
import sys
import time
from pathlib import Path

# Check if we have already created a standalone_rag.py file
if not Path("standalone_rag.py").exists():
    print("Error: standalone_rag.py not found. Please create it first.")
    sys.exit(1)

# Import functions from standalone_rag.py
print("Loading RAG system...")
from standalone_rag import add_document

# Print header
def print_header():
    print("\n" + "=" * 60)
    print("📄 NEERNITI RAG File Addition Tool 📄".center(60))
    print("=" * 60)
    print("\nThis tool adds new text files to the RAG system.")
    print("Supported file formats: .txt files")
    print("\n" + "-" * 60)

print_header()

# Check if files were provided as command line arguments
if len(sys.argv) < 2:
    print("Usage: python add_file.py <file1.txt> [file2.txt] [file3.txt] ...")
    print("Example: python add_file.py mydata.txt anotherfile.txt")
    sys.exit(1)

# Process each file
processed_files = []
failed_files = []

for file_path in sys.argv[1:]:
    if not Path(file_path).exists():
        print(f"⚠️ File not found: {file_path}")
        failed_files.append(file_path)
        continue
        
    # Check file extension
    if not file_path.lower().endswith('.txt'):
        print(f"⚠️ Unsupported file format: {file_path}")
        print("Only .txt files are supported.")
        failed_files.append(file_path)
        continue
        
    print(f"\n📄 Processing {file_path}...")
    start_time = time.time()
    success = add_document(file_path)
    end_time = time.time()
    
    if success:
        processed_files.append(file_path)
        print(f"✅ Successfully added {file_path} (took {end_time - start_time:.2f} seconds)")
    else:
        failed_files.append(file_path)
        print(f"❌ Failed to add {file_path}")

# Summary
if processed_files:
    print(f"\n✅ Successfully processed {len(processed_files)} files:")
    for f in processed_files:
        print(f"  - {f}")

if failed_files:
    print(f"\n❌ Failed to process {len(failed_files)} files:")
    for f in failed_files:
        print(f"  - {f}")

print("\n💡 You can now use query.py to ask questions about your documents")
print("Example: python query.py \"What is the rainfall in district Dang?\"")
print("Or run in interactive mode: python query.py")
