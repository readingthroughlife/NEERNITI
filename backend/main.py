    
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import requests

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Excel data at startup
DISTRICT_FILE = os.path.join(os.path.dirname(__file__), '../cleaned_file_district_Gujarat.xlsx')
TALUKA_FILE = os.path.join(os.path.dirname(__file__), '../cleaned_taluka24-25 (1).xlsx')

district_df = pd.DataFrame()
taluka_df = pd.DataFrame()

def load_and_process_data():
    global district_df, taluka_df
    
    try:
        # Load taluka data - data starts from row 8, headers at rows 5-7
        taluka_raw = pd.read_excel(TALUKA_FILE, header=None, engine='openpyxl')
        
        # Create proper column headers for taluka data
        taluka_columns = ['S.No', 'STATE', 'DISTRICT', 'TALUK', 'Rainfall_C', 'Rainfall_NC', 'Rainfall_PQ', 'Rainfall_Total', 
                         'Total_Geographical_Area', 'Recharge_Worthy_Area_C', 'Recharge_Worthy_Area_NC', 'Recharge_Worthy_Area_PQ', 
                         'Recharge_Worthy_Area_Total', 'Col13', 'Col14', 'Col15', 'Col16', 'Col17', 'Col18', 'Col19', 'Col20']
        
        # Extract data rows (starting from row 8)
        taluka_data_rows = taluka_raw.iloc[8:].copy()
        taluka_data_rows.columns = range(len(taluka_data_rows.columns))
        
        # Create DataFrame with proper columns (take only available columns)
        num_cols = min(len(taluka_columns), taluka_data_rows.shape[1])
        taluka_df = pd.DataFrame(taluka_data_rows.iloc[:, :num_cols].values, 
                                columns=taluka_columns[:num_cols])
        
        # Clean data - remove rows where TALUK is NaN
        taluka_df = taluka_df.dropna(subset=['TALUK'])
        
        print(f"Successfully loaded taluka data with {len(taluka_df)} rows")
        print(f"Sample talukas: {taluka_df['TALUK'].head().tolist()}")
        
    except Exception as e:
        print(f"Error loading taluka Excel file: {e}")
        taluka_df = pd.DataFrame()

    try:
        # Load district data - data starts from row 9, headers at rows 6-8
        district_raw = pd.read_excel(DISTRICT_FILE, header=None, engine='openpyxl')
        
        # Create proper column headers for district data
        district_columns = ['S.No', 'STATE', 'DISTRICT', 'Rainfall_C', 'Rainfall_NC', 'Rainfall_PQ', 'Rainfall_Total',
                           'Total_Geographical_Area', 'Recharge_Worthy_Area_C', 'Recharge_Worthy_Area_NC', 'Recharge_Worthy_Area_PQ',
                           'Recharge_Worthy_Area_Total', 'Col12', 'Col13', 'Col14', 'Col15', 'Col16', 'Col17', 'Col18', 'Col19']
        
        # Extract data rows (starting from row 9)
        district_data_rows = district_raw.iloc[9:].copy()
        district_data_rows.columns = range(len(district_data_rows.columns))
        
        # Create DataFrame with proper columns
        num_cols = min(len(district_columns), district_data_rows.shape[1])
        district_df = pd.DataFrame(district_data_rows.iloc[:, :num_cols].values, 
                                  columns=district_columns[:num_cols])
        
        # Clean data - remove rows where DISTRICT is NaN
        district_df = district_df.dropna(subset=['DISTRICT'])
        
        print(f"Successfully loaded district data with {len(district_df)} rows")
        print(f"Sample districts: {district_df['DISTRICT'].head().tolist()}")
        
    except Exception as e:
        print(f"Error loading district Excel file: {e}")
        district_df = pd.DataFrame()

# Load the data
load_and_process_data()

# Gemini API setup
GEMINI_API_KEY = "AIzaSyCjMlosHSgduLkBPWtOMP_f4ckVh8Nt1lQ"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY

def detect_language(user_message: str) -> str:
    """Detect if the message is in Hindi or English"""
    # Check for Hindi (Devanagari) characters
    hindi_chars = any('\u0900' <= char <= '\u097F' for char in user_message)
    
    # Hindi keywords that might be written in English
    hindi_keywords_english = [
        'kisan', 'kheti', 'fasal', 'paani', 'baarish', 'kuan', 'aam', 
        'gaon', 'zila', 'taluka', 'sarkar', 'yojana', 'bhujal'
    ]
    
    # Hindi keywords in Devanagari
    hindi_keywords_devanagari = [
        'किसान', 'खेती', 'फसल', 'पानी', 'बारिश', 'कुआं', 'गांव',
        'जिला', 'तालुका', 'सरकार', 'योजना', 'भूजल', 'सिंचाई'
    ]
    
    has_hindi_keywords = (
        any(keyword in user_message.lower() for keyword in hindi_keywords_english) or
        any(keyword in user_message for keyword in hindi_keywords_devanagari)
    )
    
    if hindi_chars or has_hindi_keywords:
        return "hindi"
    else:
        return "english"

def create_bilingual_prompt(user_message: str, search_results, user_type: str, language: str) -> str:
    """Create bilingual prompt for Hindi/English responses"""
    
    has_location_data = search_results and search_results.get("has_location_data", False)
    
    if has_location_data:
        # Use Excel data for location-specific questions
        base_prompt = f"""
You are a groundwater data specialist for Gujarat, India with access to official government data.

SPECIFIC LOCATION DATA FOUND - USE THIS DATA TO ANSWER:

User Type: {user_type}
User Question: {user_message}

REAL DATA FROM GOVERNMENT RECORDS:
District Data: {search_results.get('district_data', [])}
Taluka Data: {search_results.get('taluka_data', [])}
Locations Found: {search_results.get('found_locations', [])}

MANDATORY: Use the exact numbers, rainfall data, geographical area, and measurements from above. Give specific, data-driven answers.
"""
    else:
        # Use Gemini's general knowledge for generic questions
        base_prompt = f"""
You are a helpful groundwater expert and agricultural advisor for India.

GENERAL GROUNDWATER QUESTION - USE YOUR KNOWLEDGE TO HELP:

User Type: {user_type}
User Question: {user_message}

INSTRUCTIONS: 
- Provide helpful, educational information about groundwater, irrigation, farming, or water management
- Give practical advice and best practices
- Be informative and useful even without specific local data
- Focus on general principles that apply broadly
- Include actionable suggestions when possible
"""
    
    if language == "hindi":
        hindi_instructions = """

IMPORTANT: RESPOND IN HINDI (हिंदी में उत्तर दें)

HINDI RESPONSE GUIDELINES:
- उत्तर हिंदी में दें (Devanagari script में)
- सरल और स्पष्ट भाषा का उपयोग करें
- अंक और माप की इकाइयां अंग्रेजी में रख सकते हैं

USER TYPE GUIDELINES:"""

        if has_location_data:
            if user_type == "farmer":
                hindi_instructions += """
- किसान के लिए: डेटा से वास्तविक संख्याओं का उपयोग करें (20-40 शब्दों में)
- व्यावहारिक सलाह दें - वर्षा, क्षेत्रफल डेटा के साथ
- हां/नहीं में जवाब दें जहाँ संभव हो

उदाहरण: "अहवा में वर्षा 2354 mm है, क्षेत्रफल 53133 ha है। खेती के लिए उपयुक्त है।"
"""
            elif user_type == "planner":
                hindi_instructions += """
- योजनाकार के लिए: सभी वास्तविक आंकड़े शामिल करें (60-100 शब्दों में)
- तकनीकी डेटा का विस्तृत उल्लेख करें
- योजना संबंधी सुझाव दें
"""
        else:
            if user_type == "farmer":
                hindi_instructions += """
- किसान के लिए: व्यावहारिक सामान्य सलाह (20-40 शब्दों में)
- भूजल संरक्षण के तरीके बताएं
- सिंचाई की बेहतर विधियां सुझाएं

उदाहरण: "ड्रिप सिंचाई से पानी बचाएं। बारिश का पानी इकट्ठा करें। मिट्टी की जांच कराएं।"
"""
            elif user_type == "planner":
                hindi_instructions += """
- योजनाकार के लिए: व्यापक जल प्रबंधन सलाह (60-100 शब्दों में)
- नीतिगत सुझाव और रणनीति दें
- दीर्घकालिक समाधान बताएं

उदाहरण: "भूजल प्रबंधन के लिए रेन वाटर हार्वेस्टिंग बढ़ाएं। सामुदायिक जल संरक्षण योजना बनाएं।"
"""
        
        base_prompt += hindi_instructions
    
    else:  # English
        base_prompt += """

LANGUAGE: Respond in ENGLISH

RESPONSE GUIDELINES:"""
        
        if has_location_data:
            base_prompt += """
- Use the exact data provided to give specific, factual answers
- Reference actual numbers, locations, and measurements
"""
            if user_type == "farmer":
                base_prompt += """
- For Farmers: Simple language with actual data (20-40 words)
- Give practical advice using real rainfall, area data
- Provide clear yes/no answers when possible

Example: "AHWA has 2354mm rainfall and 53133 hectares. Good for farming."
"""
            elif user_type == "planner":
                base_prompt += """
- For Planners: Detailed analysis with all data (60-100 words)
- Include specific statistics and technical information
- Provide planning recommendations based on data
"""
        else:
            base_prompt += """
- Provide helpful general knowledge and best practices
- Be educational and actionable
- Focus on practical solutions
"""
            if user_type == "farmer":
                base_prompt += """
- For Farmers: Practical general advice (20-40 words)
- Focus on water conservation and efficient irrigation
- Give actionable farming tips

Example: "Use drip irrigation to save water. Collect rainwater. Test soil regularly for better crop planning."
"""
            elif user_type == "planner":
                base_prompt += """
- For Planners: Comprehensive water management advice (60-100 words)
- Include policy suggestions and strategies
- Provide long-term solutions

Example: "Implement rainwater harvesting policies. Develop community water conservation programs. Monitor groundwater levels regularly."
"""
    
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
    if not district_df.empty:
        district_mask = district_df['DISTRICT'].astype(str).str.lower().str.contains('|'.join(user_lower.split()), na=False)
        
        if district_mask.any():
            matching_rows = district_df[district_mask].head(3)
            results["district_data"] = matching_rows.to_dict(orient="records")
            results["has_location_data"] = True
            
            # Add found locations
            for _, row in matching_rows.iterrows():
                if pd.notna(row['DISTRICT']):
                    results["found_locations"].append(f"{row['DISTRICT']} (District)")
    
    # Always return results - let the prompt decide how to handle
    return results

def query_excel(user_message):
    """Legacy function for backwards compatibility - now uses search_groundwater_data"""
    return search_groundwater_data(user_message)

def ask_gemini(prompt, context_data=None):
    # Compose the prompt for Gemini
    if context_data:
        prompt = f"User question: {prompt}\nRelevant groundwater data: {context_data}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(GEMINI_API_URL, json=payload)
    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return "Sorry, I couldn't parse Gemini's response."
    else:
        return f"Gemini API error: {response.text}"

@app.get("/data/summary")
def get_data_summary():
    summary = {
        "district_data": {
            "columns": list(district_df.columns) if not district_df.empty else [],
            "rows": len(district_df) if not district_df.empty else 0
        },
        "taluka_data": {
            "columns": list(taluka_df.columns) if not taluka_df.empty else [],
            "rows": len(taluka_df) if not taluka_df.empty else 0
        }
    }
    return summary

@app.get("/search-locations/{location}")
def search_specific_location(location: str):
    """Search for a specific location in the data"""
    results = search_groundwater_data(location)
    return {
        "location": location,
        "found": bool(results and (results.get("district_data") or results.get("taluka_data"))),
        "data": results
    }

@app.get("/sample-queries")
def get_sample_queries():
    """Get sample input queries for different user types in Hindi and English"""
    
    # Extract actual talukas and districts from loaded data
    sample_talukas = []
    sample_districts = []
    
    if not taluka_df.empty and 'TALUK' in taluka_df.columns:
        sample_talukas = taluka_df['TALUK'].dropna().head(5).tolist()
    
    if not district_df.empty and 'DISTRICT' in district_df.columns:
        sample_districts = district_df['DISTRICT'].dropna().head(5).tolist()
    
    return {
        "farmer_queries": {
            "english": [
                "What is the groundwater level in AHWA for farming?",
                "Is AHWA taluka suitable for farming?",
                "How much rainfall does AHWA get?",
                "Is groundwater good for crops in DANG district?",
                "Tell me about groundwater discharge in AHWA"
            ],
            "hindi": [
                "अहवा में खेती के लिए भूजल स्तर क्या है?",
                "क्या अहवा तालुका खेती के लिए उपयुक्त है?",
                "अहवा में कितनी बारिश होती है?",
                "क्या डांग जिले में भूजल फसल के लिए अच्छा है?",
                "अहवा में भूजल स्राव के बारे में बताएं"
            ]
        },
        "planner_queries": {
            "english": [
                "What are the groundwater trends in DANG district for water policy planning?",
                "What is the rainfall data for AHWA taluka?",
                "What is the recharge potential analysis for AHWA?",
                "How should water allocation be planned for DANG district?",
                "What are the geographical area statistics for AHWA?"
            ],
            "hindi": [
                "जल नीति योजना के लिए डांग जिले में भूजल के रुझान क्या हैं?",
                "अहवा तालुका के लिए वर्षा डेटा क्या है?",
                "अहवा के लिए रिचार्ज क्षमता विश्लेषण क्या है?",
                "डांग जिले के लिए जल आवंटन की योजना कैसे बनाई जाए?",
                "अहवा के लिए भौगोलिक क्षेत्र के आंकड़े क्या हैं?"
            ]
        },
        "sample_locations": {
            "talukas": sample_talukas,
            "districts": sample_districts
        },
        "usage_tips": {
            "english": [
                "Mention your role (farmer/planner) for better responses",
                "Ask about specific locations like AHWA, DANG for detailed data",
                "Use keywords: groundwater, irrigation, farming, rainfall, discharge"
            ],
            "hindi": [
                "बेहतर उत्तर के लिए अपनी भूमिका (किसान/योजनाकार) का उल्लेख करें",
                "विस्तृत डेटा के लिए अहवा, डांग जैसे विशिष्ट स्थानों के बारे में पूछें",
                "मुख्य शब्द का उपयोग करें: भूजल, सिंचाई, खेती, वर्षा, स्राव"
            ]
        }
    }

@app.post("/chat")
async def chat_endpoint(request: Request):
    body = await request.json()
    user_message = body.get("message", "")
    language = body.get("language", "english")
    user_type = body.get("user_type", "farmer")
    
    # Only auto-detect language if user hasn't explicitly selected one
    # Priority: User selection > Auto-detection
    detected_lang = detect_language(user_message)
    
    # Keep the user's selected language unless they want auto-detection
    # You can add auto-detection logic here if needed, but for now respect user choice
    
    # Search for relevant groundwater data
    search_results = search_groundwater_data(user_message)
    
    # Create bilingual prompt (always returns results, never None)
    bilingual_prompt = create_bilingual_prompt(user_message, search_results, user_type, language)
    
    # Ask Gemini with context
    gemini_response = ask_gemini(bilingual_prompt)
    
    return {
        "response": gemini_response,
        "selected_language": language,
        "detected_language": detected_lang,
        "user_type": user_type,
        "data_found": search_results.get("has_location_data", False),
        "found_locations": search_results.get("found_locations", [])
    }
