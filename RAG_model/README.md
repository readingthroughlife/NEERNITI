# NEERNITI RAG Model

A standalone Retrieval-Augmented Generation (RAG) system for querying information about districts and taluks in Gujarat using free API services.

## Integration with Your Chatbot Frontend

This RAG model can be easily integrated with any frontend chatbot application. Here's how:

### Direct API Integration

1. Import the query function from the standalone_rag module:
```python
from standalone_rag import query
```

2. Pass user questions to the query function to get answers:
```python
user_question = "What is the rainfall in district Dang?"
answer = query(user_question)
print(answer)
```

### Using as a Service

For more complex integrations, you can wrap the query functionality in a simple API:

1. Install FastAPI and Uvicorn:
```
pip install fastapi uvicorn
```

2. Create an api.py file:
```python
from fastapi import FastAPI
from pydantic import BaseModel
from standalone_rag import query

app = FastAPI()

class Question(BaseModel):
    text: str

@app.post("/ask")
async def ask_question(question: Question):
    answer = query(question.text)
    return {"answer": answer}

# Run with: uvicorn api:app --reload
```

3. Make API calls from your frontend:
```javascript
fetch('http://localhost:8000/ask', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        text: "What is the rainfall in district Dang?"
    }),
})
.then(response => response.json())
.then(data => {
    console.log(data.answer);
});
```

## Features

- **No OpenAI API Required**: Uses free alternatives:
  - **Cohere**: For generating embeddings (free tier: 5,000 requests/month)
  - **Google Gemini**: For text generation (free tier available)
- **Local Vector Database**: Uses ChromaDB to store document embeddings locally
- **Multiple Data Files**: Supports both district-level and taluk-level information
- **Interactive Querying**: Ask questions in natural language about your data

## Setup

1. **Install dependencies**

```
pip install google-generativeai cohere chromadb tqdm numpy
```

2. **API Keys**
   - Get a Google Gemini API key from: https://aistudio.google.com/app/apikey
   - Get a Cohere API key from: https://dashboard.cohere.com/api-keys

3. **Data Files**
   - The system uses these text files:
     - `output_for_dsrag.txt`: Contains taluk-level information
     - `district_data.txt`: Contains district-level information

## Usage

### Running the Main System

```
python standalone_rag.py
```

This will:
1. Prompt you for your API keys
2. Process your text files
3. Start an interactive query session

### Adding More Files

```
python add_file.py new_data.txt another_file.txt
```

### Querying the System

For interactive mode:
```
python query.py
```

For direct queries:
```
python query.py "What is the rainfall in district Dang?"
```

## Example Questions

- What is the rainfall in district Dang?
- What is the total recharge worthy area in taluk Amod?
- Which district has the highest rainfall?
- Compare the rainfall in Surat and Navsari districts
- What is the average annual rainfall in Gujarat?

## Technical Details

- **Embedding Model**: Cohere's embed-english-v3.0
- **Text Generation**: Google's Gemini-1.5-flash
- **Vector Database**: ChromaDB (stored locally in ./chroma_db)
- **Chunking Strategy**: Text is split into chunks with semantic meaning preservation

## Tips

- For better performance, set your API keys as environment variables:
  ```
  set GEMINI_API_KEY=your-key-here
  set COHERE_API_KEY=your-key-here
  ```

- More specific questions tend to yield better results

- You can add multiple text files to expand the knowledge base

## Files in this Project

- `standalone_rag.py`: The main RAG implementation
- `query.py`: Script to query the knowledge base
- `add_file.py`: Script to add new files to the knowledge base
- `api.py`: FastAPI wrapper for integration with frontend
- `output_for_dsrag.txt`: Taluk-level data file
- `district_data.txt`: District-level data file
- `output_district_key_value.txt`: Additional district data
- `gujarat_data.txt`: Supplementary data for Gujarat
- `sample_data.txt`: Sample data for testing
- `requirements.txt`: Dependencies for the project
