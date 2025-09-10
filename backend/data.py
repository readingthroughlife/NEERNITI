from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Excel data
EXCEL_PATH = os.path.join(os.path.dirname(__file__), '../CentralReport1757410209484.xlsx')
data_df = pd.read_excel(EXCEL_PATH)

@app.get("/data/summary")
def get_data_summary():
    return {"columns": list(data_df.columns), "rows": len(data_df)}
