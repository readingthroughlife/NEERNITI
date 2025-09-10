import os
import time
from pathlib import Path
import json
from dsrag.knowledge_base import KnowledgeBase
from dsrag.reranker import NoReranker

# Import embedding models - use CohereEmbedding instead of OpenAI
from dsrag.embedding import CohereEmbedding

# Import LLM models - use GeminiAPI instead of OpenAIChat
from dsrag.llm import GeminiAPI

# Get API keys
# Gemini requires GEMINI_API_KEY environment variable
if not os.environ.get("GEMINI_API_KEY"):
    google_api_key = input("Please enter your Google API key for Gemini: ")
    os.environ["GEMINI_API_KEY"] = google_api_key

# Cohere requires CO_API_KEY environment variable
if not os.environ.get("CO_API_KEY"):
    cohere_api_key = input("Please enter your Cohere API key (free tier works): ")
    os.environ["CO_API_KEY"] = cohere_api_key

# Set up models with error handling
try:
    # Using Cohere embedding model (free tier available)
    embedding_model = CohereEmbedding(model="embed-english-v3.0")
    print("✅ Using Cohere embedding model: embed-english-v3.0")
    
    # Use Gemini for LLM
    llm = GeminiAPI(model="gemini-1.5-flash")
    print("✅ Using Google Gemini model: gemini-1.5-flash")
    
    reranker = NoReranker()

    # Create or load a KnowledgeBase with specified embedding model
    kb_id = "my_kb"
    kb = KnowledgeBase(
        kb_id, 
        reranker=reranker, 
        auto_context_model=llm,
        embedding_model=embedding_model
    )

    # Check if the knowledge base directory exists to avoid reprocessing
    kb_dir = Path(f"./{kb_id}")
    files_already_processed = set()
    
    if kb_dir.exists():
        print(f"✅ Loading existing knowledge base: {kb_id}")
    
    # Add PDF documents with retry logic and skipping already processed
    files = ["test_file.pdf", "test_file_2.pdf"]
    
    for f in files:
        if f in files_already_processed:
            print(f"📄 Skipping already processed file: {f}")
            continue
            
        print(f"📄 Adding {f}...")
        try:
            kb.add_document(doc_id=f, file_path=f)
            files_already_processed.add(f)
            print(f"✅ Successfully added {f}")
        except Exception as e:
            print(f"❌ Error adding {f}: {e}")
            print(f"Error type: {type(e).__name__}")

    # Query across PDFs if we have successfully added documents
    if files_already_processed:
        try:
            queries = [
                "What was total rainfall in mm in assam?",
                "What was total rainfall in mm in district DANG taluk AHWA?",
            ]

            print("\n🔍 Running queries...")
            results = kb.query(queries)

            # Print results
            for i, r in enumerate(results):
                print(f"\n---- Result for Query {i+1} ----")
                print(r)
                
        except Exception as e:
            print(f"❌ Error during query: {e}")
            print(f"Error type: {type(e).__name__}")
    else:
        print("No documents were successfully added to the knowledge base.")

except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print(f"Error type: {type(e).__name__}")

print("\n💡 Tips for working with the knowledge base:")
print("1. If you encounter errors with Gemini, check your API key and quota")
print("2. You can hardcode your Google API key in the script for convenience")
print("3. For production, set GOOGLE_API_KEY as an environment variable")
