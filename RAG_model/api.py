from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sys
from pathlib import Path

# Check if we have already created a standalone_rag.py file
if not Path("standalone_rag.py").exists():
    raise ImportError("standalone_rag.py not found. Please make sure you're running this from the correct directory.")

# Check if text files exist
required_files = ["output_for_dsrag.txt", "district_data.txt"]
missing_files = []

for file in required_files:
    if not Path(file).exists():
        missing_files.append(file)

if missing_files:
    raise ImportError(f"Missing required files: {', '.join(missing_files)}")

# Import functions from standalone_rag.py
print("Loading RAG system...")
from standalone_rag import query

app = FastAPI(
    title="NEERNITI RAG API",
    description="API for querying Gujarat district and taluk data using the NEERNITI RAG model",
    version="1.0.0"
)

class Question(BaseModel):
    text: str

class AnswerResponse(BaseModel):
    answer: str
    query_time_seconds: float
    source_files: list[str]

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(question: Question):
    """
    Ask a question about Gujarat districts and taluks.
    
    Example questions:
    - What is the rainfall in district Dang?
    - What is the total recharge worthy area in taluk Amod?
    - Which district has the highest rainfall?
    """
    import time
    
    if not question.text or len(question.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    start_time = time.time()
    try:
        answer = query(question.text)
        end_time = time.time()
        
        return {
            "answer": answer,
            "query_time_seconds": round(end_time - start_time, 2),
            "source_files": required_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying RAG model: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "NEERNITI RAG API is running. Use the /ask endpoint to query the model.",
        "documentation": "/docs",
        "example_questions": [
            "What is the rainfall in district Dang?",
            "What is the total recharge worthy area in taluk Amod?",
            "Which district has the highest rainfall?",
            "Compare the rainfall in Surat and Navsari districts"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
