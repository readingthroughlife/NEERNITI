from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pandas as pd
import requests
import json
import os
import threading
import time
from map_generator import generate_map_for_location, extract_locations_from_message

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for DataFrames
taluka_df = pd.DataFrame()
district_df = pd.DataFrame()

# Load datasets at startup
def load_data():
    global taluka_df, district_df
    try:
        # Load taluka data
        taluka_path = "/Users/atharvaranjan/Desktop/NEERNITI /Neerniti/cleaned_taluka24-25 (1).xlsx"
        if os.path.exists(taluka_path):
            taluka_df = pd.read_excel(taluka_path)
            print(f"Loaded taluka data: {len(taluka_df)} rows")
        
        # Load district data
        district_path = "/Users/atharvaranjan/Desktop/NEERNITI /Neerniti/cleaned_file_district_Gujarat.xlsx"
        if os.path.exists(district_path):
            district_df = pd.read_excel(district_path)
            print(f"Loaded district data: {len(district_df)} rows")
            
    except Exception as e:
        print(f"Error loading data: {e}")

# Load data on startup
load_data()

class ChatRequest(BaseModel):
    message: str
    language: str = "english"
    user_type: str = "general"

def create_bilingual_prompt(user_message, data_results, language="english", user_type="general"):
    """Create a bilingual prompt based on available data and user preferences"""
    
    # Check if we have location-specific data
    has_location_data = data_results["has_location_data"]
    
    # Base prompt with data emphasis
    base_prompt = f"""You are NEERNITI, a Gujarat Groundwater Management Chatbot. You have access to comprehensive groundwater data from Gujarat.

USER MESSAGE: {user_message}

CRITICAL INSTRUCTIONS:
1. **DATA PRIORITY**: If location data is available below, YOU MUST use specific numbers from the Excel data
2. **LANGUAGE**: Respond in {'HINDI' if language == 'hindi' else 'ENGLISH'}
3. **USER TYPE**: Tailor response for {user_type}
4. **MAP GENERATION**: If user asks about maps or visualization, mention that a map can be generated

"""
    
    if has_location_data:
        base_prompt += "\\n**AVAILABLE DATA (USE THIS INFORMATION):**\\n"
        
        # Add taluka data
        if data_results["taluka_data"]:
            base_prompt += "\\nTALUKA DATA:\\n"
            for idx, row in enumerate(data_results["taluka_data"], 1):
                base_prompt += f"Location {idx}: {row.get('TALUK', 'N/A')} - District: {row.get('DISTRICT', 'N/A')}\\n"
                base_prompt += f"  Annual Rainfall: {row.get('Annual Rainfall (mm)', 'N/A')} mm\\n"
                base_prompt += f"  Geographical Area: {row.get('Geographical Area (ha)', 'N/A')} hectares\\n"
                if 'Irrigated Area (ha)' in row:
                    base_prompt += f"  Irrigated Area: {row.get('Irrigated Area (ha)', 'N/A')} hectares\\n"
                base_prompt += "\\n"
        
        # Add district data
        if data_results["district_data"]:
            base_prompt += "DISTRICT DATA:\\n"
            for idx, row in enumerate(data_results["district_data"], 1):
                base_prompt += f"District {idx}: {row.get('DISTRICT', 'N/A')}\\n"
                base_prompt += f"  Annual Rainfall: {row.get('Annual Rainfall (mm)', 'N/A')} mm\\n"
                base_prompt += f"  Geographical Area: {row.get('Geographical Area (ha)', 'N/A')} hectares\\n"
                base_prompt += "\\n"
    else:
        base_prompt += "\\n**NO SPECIFIC LOCATION DATA FOUND** - Provide general groundwater advice\\n"
    
    # Add language and user type specific instructions
    if language == "hindi":
        base_prompt += "\\n**हिंदी में उत्तर दें** - भूजल डेटा का उपयोग करके उत्तर दें\\n"
        if user_type.lower() == "farmer":
            base_prompt += "किसान के लिए: 30-50 शब्दों में व्यावहारिक सलाह दें\\n"
        elif user_type.lower() == "planner":
            base_prompt += "योजनाकार के लिए: 80-120 शब्दों में विस्तृत विश्लेषण दें\\n"
        else:
            base_prompt += "सामान्य उपयोगकर्ता के लिए: 50-70 शब्दों में संतुलित जानकारी दें\\n"
    else:
        base_prompt += "\\n**Respond in English** - Use groundwater data to provide specific advice\\n"
        if user_type.lower() == "farmer":
            base_prompt += "For Farmers: Provide practical advice in 30-50 words\\n"
        elif user_type.lower() == "planner":
            base_prompt += "For Planners: Provide detailed analysis in 80-120 words\\n"
        else:
            base_prompt += "For General Users: Provide balanced information in 50-70 words\\n"
    
    return base_prompt

def search_groundwater_data(user_message):
    """Search through both district and taluka data for relevant information"""
    user_lower = user_message.lower()
    results = {
        "district_data": [],
        "taluka_data": [],
        "found_locations": [],
        "has_location_data": False
    }
    
    # Search in taluka data
    if not taluka_df.empty:
        # Search for location names in TALUK and DISTRICT columns
        taluk_mask = taluka_df['TALUK'].astype(str).str.lower().str.contains('|'.join(user_lower.split()), na=False)
        district_mask = taluka_df['DISTRICT'].astype(str).str.lower().str.contains('|'.join(user_lower.split()), na=False)
        
        combined_mask = taluk_mask | district_mask
        
        if combined_mask.any():
            matching_rows = taluka_df[combined_mask].head(3)
            results["taluka_data"] = matching_rows.to_dict(orient="records")
            results["has_location_data"] = True
            
            # Add found locations
            for _, row in matching_rows.iterrows():
                if pd.notna(row['TALUK']):
                    results["found_locations"].append(f"{row['TALUK']} (Taluka)")
                if pd.notna(row['DISTRICT']):
                    results["found_locations"].append(f"{row['DISTRICT']} (District)")
    
    # Search in district data
    if not district_df.empty and not results["has_location_data"]:
        district_mask = district_df['DISTRICT'].astype(str).str.lower().str.contains('|'.join(user_lower.split()), na=False)
        
        if district_mask.any():
            matching_rows = district_df[district_mask].head(3)
            results["district_data"] = matching_rows.to_dict(orient="records")
            results["has_location_data"] = True
            
            # Add found locations
            for _, row in matching_rows.iterrows():
                if pd.notna(row['DISTRICT']):
                    results["found_locations"].append(f"{row['DISTRICT']} (District)")
    
    return results

def generate_map_async(user_message):
    """Generate map in background thread"""
    try:
        locations = extract_locations_from_message(user_message)
        print(f"Extracted locations for mapping: {locations}")
        
        if locations:
            success = generate_map_for_location(locations[0])
            if success:
                print(f"Map generated successfully for {locations[0]}")
                # Open map in browser
                import webbrowser
                map_path = "/Users/atharvaranjan/Desktop/NEERNITI /Neerniti/backend/templates/map.html"
                if os.path.exists(map_path):
                    webbrowser.open(f"file://{map_path}")
            else:
                print(f"Failed to generate map for {locations[0]}")
    except Exception as e:
        print(f"Error in map generation: {e}")

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        print(f"Received request: {request.message}, Language: {request.language}, User Type: {request.user_type}")
        
        # Search for data first
        data_results = search_groundwater_data(request.message)
        print(f"Search results: Found {len(data_results['taluka_data'])} taluka matches, {len(data_results['district_data'])} district matches")
        
        # Check if map generation is needed
        map_keywords = ["map", "मानचित्र", "show map", "generate map", "visualization", "visualize"]
        if any(keyword in request.message.lower() for keyword in map_keywords):
            # Start map generation in background
            threading.Thread(target=generate_map_async, args=(request.message,), daemon=True).start()
        
        # Create bilingual prompt
        prompt = create_bilingual_prompt(
            request.message, 
            data_results, 
            request.language, 
            request.user_type
        )
        
        # Call Gemini API
        api_key = "AIzaSyDva7blUmTKmUL1Hi7TQXn1l4Pp8QmsoFU"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            data = response.json()
            if "candidates" in data and data["candidates"]:
                bot_response = data["candidates"][0]["parts"][0]["text"]
                
                # Add map availability notice
                map_message = ""
                if any(keyword in request.message.lower() for keyword in map_keywords):
                    if request.language == "hindi":
                        map_message = "\\n\\n🗺️ मानचित्र तैयार हो रहा है और ब्राउज़र में खुल जाएगा।"
                    else:
                        map_message = "\\n\\n🗺️ Map is being generated and will open in your browser."
                
                return {
                    "response": bot_response + map_message,
                    "data_found": data_results["has_location_data"],
                    "locations": data_results["found_locations"]
                }
            else:
                raise HTTPException(status_code=500, detail="No response from AI model")
        else:
            print(f"API Error: {response.status_code}, {response.text}")
            raise HTTPException(status_code=500, detail=f"AI API error: {response.status_code}")
            
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/map.html")
async def serve_map():
    """Serve the generated map HTML file"""
    map_path = "/Users/atharvaranjan/Desktop/NEERNITI /Neerniti/backend/templates/map.html"
    
    if os.path.exists(map_path):
        with open(map_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="""
        <html>
            <body>
                <h2>No map available</h2>
                <p>Ask about a location (like AHWA, DANG, etc.) to generate a map!</p>
            </body>
        </html>
        """)

@app.get("/")
async def root():
    return {"message": "NEERNITI Groundwater Chatbot API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
