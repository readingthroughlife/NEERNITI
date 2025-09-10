import os
import time
import json
from pathlib import Path
import google.generativeai as genai
import cohere
from PyPDF2 import PdfReader
from tqdm import tqdm
import numpy as np
import chromadb

# Standalone RAG implementation using free models (Cohere + Gemini)

# Set API keys
GEMINI_API_KEY = input("Please enter your Google API key for Gemini: ")
COHERE_API_KEY = input("Please enter your Cohere API key (free tier works): ")

# Initialize clients
co = cohere.Client(COHERE_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize ChromaDB
db_dir = Path("./chroma_db")
db_dir.mkdir(exist_ok=True)
chroma_client = chromadb.PersistentClient(path=str(db_dir))

# Create or get collection
collection_name = "text_collection"
try:
    collection = chroma_client.get_collection(collection_name)
    print(f"✅ Loaded existing collection: {collection_name}")
except:
    collection = chroma_client.create_collection(collection_name)
    print(f"✅ Created new collection: {collection_name}")

# Function to extract text from file (PDF or TXT)
def extract_text_from_file(file_path):
    print(f"📄 Extracting text from {file_path}...")
    text = ""
    file_extension = Path(file_path).suffix.lower()
    
    try:
        if file_extension == '.pdf':
            # Handle PDF files
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n"
        elif file_extension == '.txt':
            # Handle TXT files
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
        else:
            print(f"⚠️ Unsupported file format: {file_extension}. Only .pdf and .txt are supported.")
            return ""
            
        return text
    except Exception as e:
        print(f"❌ Error extracting text from file: {e}")
        return ""

# Function to chunk text
def chunk_text(text, chunk_size=1000, overlap=200):
    if not text:
        return []
    
    # Split text by paragraphs first
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If paragraph is very large, split it further
        if len(paragraph) > chunk_size:
            # Add the current chunk if it has content
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            
            # Split large paragraph
            for i in range(0, len(paragraph), chunk_size - overlap):
                chunk = paragraph[i:i + chunk_size]
                if len(chunk) >= 100:  # Only keep chunks with meaningful content
                    chunks.append(chunk)
        else:
            # Check if adding this paragraph would exceed chunk_size
            if len(current_chunk) + len(paragraph) > chunk_size:
                # Add the current chunk if it has meaningful content
                if len(current_chunk) >= 100:
                    chunks.append(current_chunk)
                current_chunk = paragraph
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
    
    # Add the last chunk if it has meaningful content
    if current_chunk and len(current_chunk) >= 100:
        chunks.append(current_chunk)
    
    return chunks

# Function to get embeddings from Cohere
def get_embeddings(texts):
    try:
        response = co.embed(
            texts=texts,
            model="embed-english-v3.0",
            input_type="search_document"
        )
        return response.embeddings
    except Exception as e:
        print(f"❌ Error getting embeddings: {e}")
        return None

# Function to add document to the database
def add_document(file_path, doc_id=None):
    if doc_id is None:
        doc_id = Path(file_path).stem
        
    # Check if document already exists in collection
    existing_ids = collection.get(ids=[doc_id])["ids"]
    if doc_id in existing_ids:
        print(f"⚠️ Document {doc_id} already exists in the collection, skipping...")
        return True
        
    # Extract text from file
    text = extract_text_from_file(file_path)
    if not text:
        return False
        
    # Chunk the text
    chunks = chunk_text(text)
    if not chunks:
        print(f"⚠️ No valid chunks extracted from {file_path}")
        return False
        
    print(f"📊 Created {len(chunks)} chunks from document")
    
    # Get embeddings for chunks
    print("🧠 Generating embeddings with Cohere...")
    embeddings = get_embeddings(chunks)
    if not embeddings:
        return False
        
    # Add chunks to the collection
    chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadata = [{"source": doc_id, "chunk_index": i} for i in range(len(chunks))]
    
    try:
        collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadata
        )
        print(f"✅ Successfully added {len(chunks)} chunks to the collection")
        return True
    except Exception as e:
        print(f"❌ Error adding chunks to collection: {e}")
        return False

# Function to query the database and generate a response
def query(question, top_k=8):
    print(f"🔍 Searching for: {question}")
    
    # Get embedding for the question
    question_embedding = get_embeddings([question])[0]
    
    # Query the collection
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )
    
    if not results["documents"]:
        return "No relevant information found in the documents."
    
    # Prepare context from retrieved documents
    context = ""
    for i, (doc, metadata, distance) in enumerate(zip(
        results["documents"][0], 
        results["metadatas"][0],
        results["distances"][0]
    )):
        relevance = 1 - distance  # Convert distance to similarity score
        source_doc = metadata['source']
        context += f"Source: {source_doc}, Relevance: {relevance:.2f}\n"
        context += f"{doc}\n\n"
    
    # Generate response with Gemini
    prompt = f"""
    Based on the following information from documents:
    
    {context}
    
    Answer this question: {question}
    
    IMPORTANT GUIDELINES:
    1. Provide a clear, concise answer using ONLY the information in the provided context.
    2. If the context has information about multiple districts or taluks, make that clear in your answer.
    3. When providing numerical data (like rainfall or recharge worthy area), always mention the units.
    4. If comparing multiple entities, present the information in a structured way.
    5. If the context doesn't contain relevant information to answer the question, say "I don't have enough information to answer this question."
    6. Cite which source document (output_for_dsrag.txt or district_data.txt) your information comes from.
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return f"Error generating response: {str(e)}"

# Main execution
try:
    # Files to process
    files = [
        "output_for_dsrag.txt",  # Taluk-level data
        "district_data.txt"       # District-level data
    ]
    
    processed_files = []
    
    for file_path in files:
        # Check if file exists, if not, tell the user
        if not Path(file_path).exists():
            print(f"⚠️ File not found: {file_path}")
            continue
            
        print(f"\n📄 Processing {file_path}...")
        if add_document(file_path):
            processed_files.append(file_path)
    
    if processed_files:
        print(f"\n✅ Successfully processed {len(processed_files)} files:")
        for f in processed_files:
            print(f"  - {f}")
        
        # Interactive query loop
        print("\n🔍 Enter your questions (or press Enter with empty input to exit):")
        print("Example questions:")
        print("  - What is the rainfall in district Dang?")
        print("  - What is the total recharge worthy area in taluk Amod?")
        print("  - Which district has the highest rainfall?")
        print("  - Compare the rainfall in Surat and Navsari districts")
        
        while True:
            user_query = input("\nQuestion: ").strip()
            if not user_query:
                break
                
            start_time = time.time()
            answer = query(user_query)
            end_time = time.time()
            
            print(f"\nAnswer (took {end_time - start_time:.2f} seconds):")
            print(answer)
    else:
        print("No documents were successfully processed.")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n💡 Tips:")
print("1. Cohere offers a free tier for embeddings (5,000 requests/month)")
print("2. Gemini offers a free tier for text generation")
print("3. You can store your API keys in environment variables for convenience")
