import os
import time
from pathlib import Path
import json
import google.generativeai as genai
import cohere
from dsrag.knowledge_base import KnowledgeBase
from dsrag.reranker import NoReranker
from dsrag.embedding import CohereEmbedding

# Simple RAG implementation with free models (Cohere + Gemini)

# Set API keys
GEMINI_API_KEY = input("Please enter your Google API key for Gemini: ")
COHERE_API_KEY = input("Please enter your Cohere API key (free tier works): ")

# We still need a placeholder for OpenAI since dsRAG might check for it
os.environ["OPENAI_API_KEY"] = "placeholder-not-used"
os.environ["CO_API_KEY"] = COHERE_API_KEY
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

try:
    # Initialize the embedding model
    print("Setting up Cohere embedding model...")
    embedding_model = CohereEmbedding(model="embed-english-v3.0")
    print("✅ Cohere embedding model ready")
    
    # Configure our KB with minimal reranker (NoReranker)
    kb_id = "my_kb"
    reranker = NoReranker()
    
    # Custom LLM wrapper for Gemini that mimics the expected interface
    # This works around some issues with the GeminiAPI class
    class CustomGeminiWrapper:
        def __init__(self, api_key):
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
        def get_chat_response(self, messages, **kwargs):
            # Convert message format to what Gemini expects
            gemini_messages = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                gemini_messages.append({"role": role, "parts": [msg["content"]]})
            
            # Get response from Gemini
            response = self.model.generate_content(gemini_messages)
            return response.text
    
    # Create a custom LLM wrapper
    llm = CustomGeminiWrapper(GEMINI_API_KEY)
    print("✅ Gemini model ready")
    
    # Create our knowledge base with NoReranker and custom LLM
    kb = KnowledgeBase(
        kb_id,
        reranker=reranker,
        embedding_model=embedding_model
    )
    
    # Add PDF documents
    files = ["test_file.pdf", "test_file_2.pdf"]
    processed_files = []
    
    for f in files:
        print(f"📄 Adding {f}...")
        try:
            # Add document to KB
            kb.add_document(doc_id=f, file_path=f)
            processed_files.append(f)
            print(f"✅ Successfully added {f}")
        except Exception as e:
            print(f"❌ Error adding {f}: {e}")
    
    # Query the knowledge base if we have documents
    if processed_files:
        print("\n📚 Documents in knowledge base:")
        for doc in processed_files:
            print(f"  - {doc}")
        
        # Get user queries
        print("\n🔍 Enter your queries (one per line, empty line to finish):")
        queries = []
        while True:
            query = input("> ")
            if not query:
                break
            queries.append(query)
        
        if not queries:
            # Use default queries if none provided
            queries = [
                "What was total rainfall in mm in assam?",
                "What was total rainfall in mm in district DANG taluk AHWA?",
            ]
            print("\nUsing default queries:")
            for q in queries:
                print(f"  - {q}")
        
        # Get retrievals from knowledge base
        print("\n🔍 Retrieving relevant chunks...")
        retrievals = kb.retrieve(queries)
        
        # Process each query
        for i, (query, retrieval) in enumerate(zip(queries, retrievals)):
            print(f"\n---- Query {i+1}: {query} ----")
            
            # Show chunks
            print("\nRelevant chunks:")
            for j, chunk in enumerate(retrieval.chunks[:3]):  # Show top 3 chunks
                print(f"\nChunk {j+1} (score: {chunk.score:.4f}):")
                print(f"From: {chunk.doc_id}")
                print(f"Content: {chunk.content[:200]}...")
            
            # Generate answer with Gemini
            prompt = f"""
            Answer the following question based on these excerpts from documents:
            
            {' '.join([chunk.content for chunk in retrieval.chunks[:3]])}
            
            Question: {query}
            
            Provide a concise and accurate answer based only on the information in the excerpts.
            """
            
            print("\nGenerating answer with Gemini...")
            answer = llm.get_chat_response([{"role": "user", "content": prompt}])
            
            print("\nAnswer:")
            print(answer)
            
    else:
        print("No documents were successfully added to the knowledge base.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n💡 Tips:")
print("1. Cohere offers a free tier for embeddings (5,000 requests/month)")
print("2. Gemini offers a free tier for text generation")
print("3. You can store your API keys in environment variables for convenience")
