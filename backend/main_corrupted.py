    
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import requests
import json
from typing import Dict, List, Optional

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load both datasets at startup
print("Loading datasets...")

# Dataset 1: Original CentralReport
central_df = pd.DataFrame()
CENTRAL_PATH = os.path.join(os.path.dirname(__file__), '../CentralReport1757410209484.xlsx')
try:
    central_df = pd.read_excel(CENTRAL_PATH, engine='openpyxl')
    print(f"Successfully loaded CentralReport data with {len(central_df)} rows")
except Exception as e:
    print(f"Error loading CentralReport file: {e}")

# Dataset 2: Cleaned Taluka Dataset
taluka_df = pd.DataFrame()
TALUKA_PATH = os.path.join(os.path.dirname(__file__), '../cleaned_taluka24-25 (1).xlsx')
try:
    # Load with proper headers (row 5 contains the actual column headers)
    taluka_df = pd.read_excel(TALUKA_PATH, header=5, engine='openpyxl')
    # Clean up any empty columns
    taluka_df = taluka_df.dropna(axis=1, how='all')
    # Remove rows with all NaN values
    taluka_df = taluka_df.dropna(axis=0, how='all')
    print(f"Successfully loaded Taluka data with {len(taluka_df)} rows and columns: {list(taluka_df.columns)[:5]}...")
except Exception as e:
    print(f"Error loading Taluka file: {e}")

# Dataset 3: Cleaned District Dataset
district_df = pd.DataFrame()
DISTRICT_PATH = os.path.join(os.path.dirname(__file__), '../cleaned_file_district_Gujarat.xlsx')
try:
    # Load with proper headers (row 5 contains the actual column headers)
    district_df = pd.read_excel(DISTRICT_PATH, header=5, skiprows=[6, 7], engine='openpyxl')
    # Clean up any empty columns
    district_df = district_df.dropna(axis=1, how='all')
    # Remove rows with all NaN values
    district_df = district_df.dropna(axis=0, how='all')
    print(f"Successfully loaded District data with {len(district_df)} rows and columns: {list(district_df.columns)[:5]}...")
except Exception as e:
    print(f"Error loading District file: {e}")

# Combine datasets for comprehensive search
all_data = {
    'central': central_df,
    'taluka': taluka_df,
    'district': district_df
}

# Gemini API setup
GEMINI_API_KEY = "AIzaSyDVeFvBen77ocY_Vbk1DD6z2bihDdBg0JM"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY

def detect_user_type(user_message: str) -> str:
    """Detect user type based on message content and keywords"""
    user_message_lower = user_message.lower()
    
    # Farmer keywords
    farmer_keywords = [
        "crop", "farming", "irrigation", "water for crops", "bore well", "tube well",
        "field", "agriculture", "harvest", "planting", "seeds", "fertilizer",
        "my farm", "my field", "my crops", "water shortage", "drought",
        "rainfall for farming", "when to irrigate", "water availability"
    ]
    
    # Planner keywords  
    planner_keywords = [
        "policy", "planning", "district", "taluka", "state", "government",
        "water management", "resource allocation", "budget", "scheme",
        "water conservation", "aquifer management", "recharge projects",
        "water policy", "district planning", "resource planning",
        "groundwater assessment", "monitoring", "survey data"
    ]
    
    # Researcher/Technical keywords
    researcher_keywords = [
        "data analysis", "trends", "statistical", "research", "study",
        "correlation", "technical", "methodology", "analysis",
        "water table depth", "aquifer characteristics", "hydrogeology"
    ]
    
    # Count keyword matches
    farmer_score = sum(1 for keyword in farmer_keywords if keyword in user_message_lower)
    planner_score = sum(1 for keyword in planner_keywords if keyword in user_message_lower)
    researcher_score = sum(1 for keyword in researcher_keywords if keyword in user_message_lower)
    
    # Determine user type
    if farmer_score > 0 and farmer_score >= planner_score:
        return "farmer"
    elif planner_score > 0 and planner_score >= farmer_score:
        return "planner"
    elif researcher_score > 0:
        return "researcher"
    else:
        return "general"

def search_datasets(user_message: str) -> Dict:
    """Enhanced search focused on Excel datasets (Taluka and District) with precise location matching"""
    results = {}
    user_message_lower = user_message.lower()
    
    # Enhanced location search patterns
    location_patterns = {
        'bardoli': ['bardoli'],
        'surat': ['surat'],
        'gujarat': ['gujarat'],
        'ahmedabad': ['ahmedabad'],
        'vadodara': ['vadodara'],
        'rajkot': ['rajkot']
    }
    
    # Groundwater related keywords
    groundwater_keywords = [
        "groundwater", "water level", "recharge", "extraction", "farming", "irrigation",
        "bore well", "rainfall", "assessment", "suitable", "availability"
    ]
    
    # Check if query is relevant
    is_relevant = any(keyword in user_message_lower for keyword in groundwater_keywords) or \
                  any(location in user_message_lower for locations in location_patterns.values() for location in locations)
    
    if not is_relevant:
        return {"relevant": False, "message": "Please ask questions related to groundwater data or specific locations."}
    
    # Search Taluka dataset with precise location matching
    if not taluka_df.empty:
        try:
            # Direct location search - exact and partial matches
            location_matches = None
            for location_name, patterns in location_patterns.items():
                for pattern in patterns:
                    if pattern in user_message_lower:
                        location_matches = taluka_df[
                            taluka_df['TALUK'].str.contains(pattern, case=False, na=False) |
                            taluka_df['DISTRICT'].str.contains(pattern, case=False, na=False) |
                            taluka_df['STATE'].str.contains(pattern, case=False, na=False)
                        ]
                        if not location_matches.empty:
                            break
                if location_matches is not None and not location_matches.empty:
                    break
            
            # If specific location found, get detailed data
            if location_matches is not None and not location_matches.empty:
                # Get relevant columns for the location
                relevant_data = []
                for _, row in location_matches.iterrows():
                    location_data = {
                        'STATE': row.get('STATE', ''),
                        'DISTRICT': row.get('DISTRICT', ''),
                        'TALUK': row.get('TALUK', ''),
                        'Rainfall (mm)': row.get('Rainfall (mm)', 0),
                        'Ground Water Recharge (ham)': row.get('Ground Water Recharge (ham)', 0),
                        'Annual Ground water Recharge (ham)': row.get('Annual Ground water Recharge (ham)', 0),
                        'Annual Extractable Ground water Resource (ham)': row.get('Annual Extractable Ground water Resource (ham)', 0),
                        'Stage of Ground Water Extraction (%)': row.get('Stage of Ground Water Extraction (%)', 0),
                        'Categorization of Assessment Unit': row.get('Categorization of Assessment Unit', ''),
                        'Pre Monsoon of GW Trend': row.get('Pre Monsoon of GW Trend', ''),
                        'Post Monsoon of GW Trend': row.get('Post Monsoon of GW Trend', ''),
                        'Net Annual Ground Water Availability for Future Use (ham)': row.get('Net Annual Ground Water Availability for Future Use (ham)', 0)
                    }
                    # Only include non-null, non-zero values
                    filtered_data = {k: v for k, v in location_data.items() if v and str(v) != '0' and str(v) != '0.0'}
                    relevant_data.append(filtered_data)
                
                results['taluka_data'] = relevant_data
                results['taluka_summary'] = f"Found {len(relevant_data)} location matches in Taluka dataset"
            
            # If no location match but groundwater keywords present, get sample data
            elif any(keyword in user_message_lower for keyword in groundwater_keywords):
                sample_data = taluka_df.head(2)
                sample_records = []
                for _, row in sample_data.iterrows():
                    sample_record = {
                        'STATE': row.get('STATE', ''),
                        'DISTRICT': row.get('DISTRICT', ''),
                        'TALUK': row.get('TALUK', ''),
                        'Rainfall (mm)': row.get('Rainfall (mm)', 0),
                        'Ground Water Recharge (ham)': row.get('Ground Water Recharge (ham)', 0),
                        'Categorization of Assessment Unit': row.get('Categorization of Assessment Unit', '')
                    }
                    filtered_record = {k: v for k, v in sample_record.items() if v and str(v) != '0'}
                    sample_records.append(filtered_record)
                
                results['taluka_data'] = sample_records
                results['taluka_summary'] = f"Sample data from Taluka dataset ({len(taluka_df)} total records)"
                
        except Exception as e:
            print(f"Error searching taluka data: {e}")
    
    # Search District dataset
    if not district_df.empty:
        try:
            # Similar location-based search for district data
            district_matches = None
            for location_name, patterns in location_patterns.items():
                for pattern in patterns:
                    if pattern in user_message_lower:
                        district_matches = district_df[
                            district_df['DISTRICT'].str.contains(pattern, case=False, na=False) |
                            district_df['STATE'].str.contains(pattern, case=False, na=False)
                        ]
                        if not district_matches.empty:
                            break
                if district_matches is not None and not district_matches.empty:
                    break
            
            if district_matches is not None and not district_matches.empty:
                district_data = []
                for _, row in district_matches.iterrows():
                    district_record = {
                        'STATE': row.get('STATE', ''),
                        'DISTRICT': row.get('DISTRICT', ''),
                        'Rainfall (mm)': row.get('Rainfall (mm)', 0)
                    }
                    filtered_record = {k: v for k, v in district_record.items() if v and str(v) != '0'}
                    district_data.append(filtered_record)
                
                results['district_data'] = district_data
                results['district_summary'] = f"Found {len(district_data)} district matches"
                
        except Exception as e:
            print(f"Error searching district data: {e}")
    
    # Add metadata
    results['relevant'] = True
    results['datasets_available'] = {
        'taluka': len(taluka_df) if not taluka_df.empty else 0,
        'district': len(district_df) if not district_df.empty else 0
    }
    
    return results

def create_user_specific_prompt(user_message: str, search_results: Dict, user_type: str) -> str:
    """Create user-specific prompt for Gemini with tailored context"""
    
    if not search_results.get('relevant', False):
        return f"""You are NEERNITI, an AI assistant for groundwater resource assessment in Gujarat, India. 
        
User asked: "{user_message}"

This question doesn't seem related to groundwater or water resources. Please respond politely and redirect them to ask about:
- Groundwater levels and assessment
- Water table data
- Rainfall and recharge information
- District/Taluka wise water data
- Water quality and monitoring
- Irrigation and water management

Keep your response helpful and professional."""

    # User-specific response guidelines
    user_guidelines = {
        "farmer": """
RESPONSE GUIDELINES FOR FARMER:
- Keep answers VERY SHORT and PRACTICAL (1-2 sentences max, under 40 words)
- Focus ONLY on actionable farming advice
- Use SIMPLE language, avoid technical terms
- Mention practical solutions like water depth, irrigation timing, crop suitability
- Give direct YES/NO answers when possible
- Focus on immediate farming concerns and solutions""",
        
        "planner": """
RESPONSE GUIDELINES FOR PLANNER:
- Provide DETAILED technical and policy information (4-6 sentences, up to 120 words)
- Include specific data points, percentages, and measurements
- Focus on district/taluka level statistics and trends
- Include resource allocation insights and planning implications
- Use official terminology and provide comprehensive analysis
- Mention categorization status, extraction stages, and future projections
- Address policy and planning recommendations""",
        
        "researcher": """
RESPONSE GUIDELINES FOR RESEARCHER:
- Provide BRIEF technical analysis (3-4 sentences, up to 80 words)
- Include relevant data points and trends
- Mention methodology or data limitations if relevant
- Use appropriate technical terms but stay concise
- Focus on analytical insights""",
        
        "general": """
RESPONSE GUIDELINES FOR GENERAL USER:
- Keep answers SHORT and INFORMATIVE (2-3 sentences, under 60 words)
- Use simple, clear language
- Provide basic information without overwhelming detail
- Focus on key facts and practical information"""
    }

    prompt = f"""You are NEERNITI, an AI assistant for groundwater resource assessment in Gujarat, India.

USER TYPE: {user_type.upper()}
USER QUESTION: "{user_message}"

{user_guidelines.get(user_type, user_guidelines["general"])}

AVAILABLE DATASETS:"""
    
    # Add dataset information
    datasets_info = search_results.get('datasets_available', {})
    if datasets_info.get('taluka', 0) > 0:
        prompt += f"\n- Taluka Dataset: {datasets_info['taluka']} records (2024-25 latest cleaned data)"
    if datasets_info.get('district', 0) > 0:
        prompt += f"\n- District Dataset: {datasets_info['district']} records (2024-25 latest cleaned data)"
    
    # Add relevant data found
    if 'taluka_data' in search_results and search_results['taluka_data']:
        prompt += f"\n\nRELEVANT TALUKA DATA FOUND:"
        for i, record in enumerate(search_results['taluka_data'][:2]):  # Show max 2 records
            prompt += f"\nLocation {i+1}: "
            # Show key fields in a clean format
            key_info = []
            if record.get('TALUK'): key_info.append(f"Taluka: {record['TALUK']}")
            if record.get('DISTRICT'): key_info.append(f"District: {record['DISTRICT']}")
            if record.get('Rainfall (mm)'): key_info.append(f"Rainfall: {record['Rainfall (mm)']} mm")
            if record.get('Ground Water Recharge (ham)'): key_info.append(f"GW Recharge: {record['Ground Water Recharge (ham)']} ham")
            if record.get('Annual Extractable Ground water Resource (ham)'): key_info.append(f"Extractable Resource: {record['Annual Extractable Ground water Resource (ham)']} ham")
            if record.get('Stage of Ground Water Extraction (%)'): key_info.append(f"Extraction Stage: {record['Stage of Ground Water Extraction (%)']}%")
            if record.get('Categorization of Assessment Unit'): key_info.append(f"Category: {record['Categorization of Assessment Unit']}")
            if record.get('Pre Monsoon of GW Trend'): key_info.append(f"Pre-monsoon Trend: {record['Pre Monsoon of GW Trend']}")
            if record.get('Post Monsoon of GW Trend'): key_info.append(f"Post-monsoon Trend: {record['Post Monsoon of GW Trend']}")
            
            prompt += ", ".join(key_info)
    
    if 'district_data' in search_results and search_results['district_data']:
        prompt += f"\n\nRELEVANT DISTRICT DATA FOUND:"
        for i, record in enumerate(search_results['district_data'][:1]):  # Show max 1 district record
            prompt += f"\nDistrict {i+1}: "
            district_info = []
            if record.get('DISTRICT'): district_info.append(f"District: {record['DISTRICT']}")
            if record.get('STATE'): district_info.append(f"State: {record['STATE']}")
            if record.get('Rainfall (mm)'): district_info.append(f"Rainfall: {record['Rainfall (mm)']} mm")
            
            prompt += ", ".join(district_info)

    prompt += f"""

CRITICAL INSTRUCTIONS:
- Use the EXACT data provided above in your response
- For FARMER: Give direct answer in under 40 words with practical advice
- For PLANNER: Give detailed technical response in 100-120 words with specific data
- If data shows "safe" category and good recharge, mention it's suitable for farming
- If asking about specific location like BARDOLI, use the exact data found
- Always mention the key metrics: recharge rate, extraction stage, categorization
- Be specific about numbers and trends found in the data"""

    return prompt
    
    prompt += f"""

INSTRUCTIONS:
1. Analyze the user's question in the context of groundwater resource assessment
2. Use the provided data to give specific, accurate answers
3. If the data contains relevant information, cite specific values, locations, or trends
4. If the user asks about specific districts/talukas, provide localized information
5. For general questions, provide comprehensive insights from the available data
6. Always maintain a professional, helpful tone
7. If you need more specific information, suggest what additional details would be helpful
8. Format numbers clearly and use appropriate units (mm, ha, etc.)

RESPONSE GUIDELINES:
- Be specific and data-driven when possible
- Explain technical terms in simple language
- Provide actionable insights
- Mention data sources when relevant
- Keep responses concise but comprehensive

Please provide a detailed, informative response based on the available groundwater data."""

    return prompt

def ask_gemini(prompt: str) -> str:
    """Enhanced Gemini API interaction with better error handling"""
    try:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1000,
                "topP": 0.8,
                "topK": 40
            }
        }
        
        response = requests.post(GEMINI_API_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    return content
                else:
                    return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
            except (KeyError, IndexError) as e:
                return "I encountered an issue processing the response. Please try again."
        else:
            print(f"Gemini API error: {response.status_code} - {response.text}")
            return "I'm currently experiencing technical difficulties. Please try again in a moment."
            
    except requests.exceptions.Timeout:
        return "The request took too long to process. Please try again."
    except requests.exceptions.ConnectionError:
        return "I'm having trouble connecting to the AI service. Please check your internet connection and try again."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "An unexpected error occurred. Please try again."

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

def create_bilingual_prompt(user_message: str, search_results: Dict, user_type: str, language: str) -> str:
    """Create bilingual prompt for Hindi/English responses"""
    
    # Get the base prompt
    base_prompt = create_user_specific_prompt(user_message, search_results, user_type)
    
    if language == "hindi":
        hindi_instructions = """

IMPORTANT: RESPOND IN HINDI (हिंदी में उत्तर दें)

HINDI RESPONSE GUIDELINES:
- उत्तर हिंदी में दें (Devanagari script में)
- सरल और स्पष्ट भाषा का उपयोग करें
- तकनीकी शब्दों के साथ हिंदी अर्थ भी दें
- अंक और माप की इकाइयां अंग्रेजी में रख सकते हैं (जैसे: 25 mm, 100 ham)

HINDI USER TYPE SPECIFIC GUIDELINES:"""

        if user_type == "farmer":
            hindi_instructions += """
- किसान के लिए: बहुत सरल भाषा (20-30 शब्दों में)
- व्यावहारिक सलाह दें (सिंचाई, फसल के लिए उपयुक्त या नहीं)
- हां/नहीं में जवाब दें जहाँ संभव हो"""
        
        elif user_type == "planner":
            hindi_instructions += """
- योजनाकार के लिए: विस्तृत जानकारी (80-100 शब्दों में)
- तकनीकी डेटा और आंकड़े शामिल करें
- नीति और योजना से संबंधित सुझाव दें"""
        
        base_prompt += hindi_instructions + """

उदाहरण हिंदी उत्तर:
- "बारडोली में भूजल रिचार्ज 150 ham है। खेती के लिए उपयुक्त है।"
- "सूरत जिले में बारिश 850 mm है। सिंचाई के लिए पानी उपलब्ध है।"
"""
    
    else:  # English
        base_prompt += """

LANGUAGE: Respond in ENGLISH"""
    
    return base_prompt

@app.get("/")
def read_root():
    return {"message": "NEERNITI Backend API is running", "status": "ok"}

@app.get("/")
def read_root():
    return {
        "message": "NEERNITI Groundwater Assessment API",
        "version": "2.0",
        "datasets": {
            "taluka_records": len(taluka_df) if not taluka_df.empty else 0,
            "central_records": len(central_df) if not central_df.empty else 0
        },
        "endpoints": ["/chat", "/data/summary", "/health"]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "datasets_loaded": {
            "taluka": not taluka_df.empty,
            "central": not central_df.empty
        }
    }

@app.get("/data/summary")
def get_data_summary():
    summary = {
        "taluka_dataset": {
            "rows": len(taluka_df) if not taluka_df.empty else 0,
            "columns": list(taluka_df.columns) if not taluka_df.empty else [],
            "description": "Gujarat Taluka-wise groundwater data for 2024-25"
        },
        "district_dataset": {
            "rows": len(district_df) if not district_df.empty else 0,
            "columns": list(district_df.columns) if not district_df.empty else [],
            "description": "Gujarat District-wise groundwater data for 2024-25"
        },
        "central_dataset": {
            "rows": len(central_df) if not central_df.empty else 0,
            "columns": list(central_df.columns) if not central_df.empty else [],
            "description": "Central groundwater assessment report"
        }
    }
    return summary

@app.get("/sample-queries")
def get_sample_queries():
    """Get sample input queries for different user types in Hindi and English"""
    
    # Extract actual talukas from the dataset
    sample_talukas = []
    sample_districts = []
    
    if not taluka_df.empty and 'TALUK' in taluka_df.columns:
        sample_talukas = taluka_df['TALUK'].dropna().unique()[:5].tolist()
    
    if not district_df.empty and 'DISTRICT' in district_df.columns:
        sample_districts = district_df['DISTRICT'].dropna().unique()[:5].tolist()
    
    return {
        "farmer_queries": {
            "english": [
                "What is the groundwater level in my area for farming?",
                "Is BARDOLI taluka suitable for farming?",
                "How much water is available for irrigation in Surat district?",
                "Is groundwater good for crops in my village?",
                "When should I irrigate my crops based on water levels?"
            ],
            "hindi": [
                "मेरे क्षेत्र में खेती के लिए भूजल स्तर क्या है?",
                "क्या बारडोली तालुका खेती के लिए उपयुक्त है?",
                "सूरत जिले में सिंचाई के लिए कितना पानी उपलब्ध है?",
                "क्या मेरे गांव में भूजल फसलों के लिए अच्छा है?",
                "पानी के स्तर के आधार पर मुझे अपनी फसलों में कब सिंचाई करनी चाहिए?"
            ]
        },
        "planner_queries": {
            "english": [
                "What is the district-wise groundwater extraction stage in Gujarat?",
                "Show me groundwater recharge trends for BARDOLI taluka",
                "What are the policy recommendations for water management in Surat?",
                "Analyze groundwater categorization for planning purposes",
                "What are the future water availability projections for this region?"
            ],
            "hindi": [
                "गुजरात में जिलेवार भूजल निकासी चरण क्या है?",
                "बारडोली तालुका के लिए भूजल रिचार्ज रुझान दिखाएं",
                "सूरत में जल प्रबंधन के लिए नीतिगत सिफारिशें क्या हैं?",
                "योजना उद्देश्यों के लिए भूजल वर्गीकरण का विश्लेषण करें",
                "इस क्षेत्र के लिए भविष्य की जल उपलब्धता के अनुमान क्या हैं?"
            ]
        },
        "sample_locations": {
            "talukas": sample_talukas,
            "districts": sample_districts
        },
        "usage_tips": {
            "english": [
                "Mention your role (farmer/planner) for better responses",
                "Ask about specific locations for detailed data",
                "Use keywords: groundwater, irrigation, farming, water level"
            ],
            "hindi": [
                "बेहतर उत्तर के लिए अपनी भूमिका (किसान/योजनाकार) का उल्लेख करें",
                "विस्तृत डेटा के लिए विशिष्ट स्थानों के बारे में पूछें",
                "मुख्य शब्द का उपयोग करें: भूजल, सिंचाई, खेती, जल स्तर"
            ]
        }
    }

@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        body = await request.json()
        user_message = body.get("message", "").strip()
        
        # Add debugging
        print(f"DEBUG: Received message: '{user_message}'")
        
        if not user_message:
            return {"response": "Please ask me something about groundwater data or water resources in Gujarat. / कृपया गुजरात में भूजल डेटा या जल संसाधनों के बारे में कुछ पूछें।"}
        
        # Detect language (Hindi/English)
        language = detect_language(user_message)
        print(f"DEBUG: Detected language: {language}")
        
        # Detect user type
        user_type = detect_user_type(user_message)
        print(f"DEBUG: Detected user type: {user_type}")
        
        # Search datasets for relevant information
        search_results = search_datasets(user_message)
        print(f"DEBUG: Search results relevance: {search_results.get('relevant', False)}")
        
        # Create bilingual user-specific prompt with context
        user_prompt = create_bilingual_prompt(user_message, search_results, user_type, language)
        print(f"DEBUG: Created prompt (first 100 chars): {user_prompt[:100]}...")
        
        # Get response from Gemini
        gemini_response = ask_gemini(user_prompt)
        print(f"DEBUG: Gemini response (first 100 chars): {gemini_response[:100]}...")
        
        return {
            "response": gemini_response,
            "user_type": user_type,
            "language": language,
            "data_context": {
                "relevant": search_results.get('relevant', False),
                "datasets_searched": search_results.get('datasets_available', {}),
                "records_found": {
                    "taluka": len(search_results.get('taluka_data', [])),
                    "district": len(search_results.get('district_data', [])),
                    "central": len(search_results.get('central_data', []))
                }
            }
        }
        
    except Exception as e:
        print(f"ERROR in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return {
            "response": "I apologize, but I encountered an error processing your request. Please try again. / मुझे खेद है, लेकिन आपके अनुरोध को संसाधित करने में त्रुटि हुई। कृपया पुनः प्रयास करें।",
            "error": str(e)
        }
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading datasets...")

# --- Smarter Data Loading ---
def load_and_clean_taluka_data(path: str) -> pd.DataFrame:
    """Loads taluka data, handling the multi-level header structure."""
    try:
        # Load the raw data to inspect the headers
        raw_df = pd.read_excel(path, header=None, engine='openpyxl', nrows=10)
       
        # Manually identify the row with the most meaningful headers
        # Based on the provided CSV content, row 5 (0-indexed) has good headers.
        # Let's also create a combined header for better context.
        header_row_main = raw_df.iloc[5]
        header_row_sub = raw_df.iloc[6]

        # Combine headers for clarity, e.g., 'Ground Water Extraction for all uses (ha.m) - C'
        combined_headers = []
        current_main_header = ''
        for i, (main_h, sub_h) in enumerate(zip(header_row_main, header_row_sub)):
            # Use the main header if no sub-header exists
            if pd.isna(main_h) or str(main_h).lower() in ['s.no', 'state', 'district', 'taluk']:
                new_header = str(sub_h).strip() if pd.notna(sub_h) else str(header_row_main.iloc[i]).strip()
            else:
                # Handle cases where the main header spans multiple sub-headers
                if pd.notna(main_h):
                    current_main_header = str(main_h).strip()
                if pd.notna(sub_h):
                    new_header = f"{current_main_header} - {str(sub_h).strip()}"
                else:
                    new_header = current_main_header
            combined_headers.append(new_header)
       
        # Load the full dataset with the combined headers
        df = pd.read_excel(path, header=None, skiprows=[0, 1, 2, 3, 4, 6, 7], engine='openpyxl')
        df.columns = combined_headers[:len(df.columns)]
       
        # Clean up empty columns and rows
        df = df.dropna(axis=1, how='all')
        df = df.dropna(axis=0, how='all')
       
        # Rename columns to be more search-friendly
        rename_map = {
            'S.No': 'S.No',
            'STATE': 'STATE',
            'DISTRICT': 'DISTRICT',
            'TALUK': 'TALUK',
            'Rainfall (mm)': 'Rainfall (mm)',
            'Annual Extractable Ground water Resource (ham)': 'Annual Extractable Ground water Resource (ham)',
            'Stage of Ground Water Extraction (%)': 'Stage of Ground Water Extraction (%)',
            'Categorization of Assessment Unit': 'Categorization of Assessment Unit',
            'Pre Monsoon of GW Trend': 'Pre Monsoon of GW Trend',
            'Post Monsoon of GW Trend': 'Post Monsoon of GW Trend',
            'Ground Water Recharge (ham)': 'Ground Water Recharge (ham)',
            'Net Annual Ground Water Availability for Future Use (ham)': 'Net Annual Ground Water Availability for Future Use (ham)'
        }
        df = df.rename(columns=rename_map)

        print(f"Successfully loaded Taluka data with {len(df)} rows and columns: {list(df.columns)[:10]}...")
        return df
    except Exception as e:
        print(f"Error loading Taluka file: {e}")
        return pd.DataFrame()

def load_and_clean_district_data(path: str) -> pd.DataFrame:
    """Loads district data, similar to the taluka data."""
    try:
        df = pd.read_excel(path, header=5, skiprows=[6, 7], engine='openpyxl')
        df = df.dropna(axis=1, how='all')
        df = df.dropna(axis=0, how='all')
        print(f"Successfully loaded District data with {len(df)} rows and columns: {list(df.columns)[:5]}...")
        return df
    except Exception as e:
        print(f"Error loading District file: {e}")
        return pd.DataFrame()

# File paths
TALUKA_PATH = os.path.join(os.path.dirname(__file__), '../cleaned_taluka24-25 (1).xlsx')
DISTRICT_PATH = os.path.join(os.path.dirname(__file__), '../cleaned_file_district_Gujarat.xlsx')

taluka_df = load_and_clean_taluka_data(TALUKA_PATH)
district_df = load_and_clean_district_data(DISTRICT_PATH)

# Dummy Central Report for API example
central_df = pd.DataFrame()
CENTRAL_PATH = os.path.join(os.path.dirname(__file__), '../CentralReport1757410209484.xlsx')
try:
    central_df = pd.read_excel(CENTRAL_PATH, engine='openpyxl')
    print(f"Successfully loaded CentralReport data with {len(central_df)} rows")
except Exception as e:
    print(f"Error loading CentralReport file: {e}")

all_data = {
    'central': central_df,
    'taluka': taluka_df,
    'district': district_df
}

# --- Semantic Search & Mapping ---
# A dictionary to map user-friendly keywords to actual column names
COLUMN_MAPPING = {
    'groundwater': ['Ground Water Recharge (ham)', 'Annual Ground water Recharge (ham)', 'Annual Extractable Ground water Resource (ham)', 'Stage of Ground Water Extraction (%)', 'Categorization of Assessment Unit', 'Ground Water Extraction for all uses (ha.m)'],
    'water level': ['Pre Monsoon of GW Trend', 'Post Monsoon of GW Trend'],
    'rainfall': ['Rainfall (mm)'],
    'irrigation': ['Ground Water Extraction for all uses (ha.m)', 'Ground Water Extraction for all uses (ha.m) - Irrigation'],
    'farming': ['Ground Water Extraction for all uses (ha.m)', 'Ground Water Extraction for all uses (ha.m) - Irrigation'],
    'recharge': ['Ground Water Recharge (ham)', 'Annual Ground water Recharge (ham)'],
    'availability': ['Net Annual Ground Water Availability for Future Use (ham)', 'Annual Extractable Ground water Resource (ham)'],
    'extraction': ['Stage of Ground Water Extraction (%)', 'Ground Water Extraction for all uses (ha.m)']
}

def find_relevant_columns(user_message: str) -> List[str]:
    """Finds the best matching columns based on user message keywords."""
    found_columns = set()
    user_message_lower = user_message.lower()
   
    # Use fuzzy matching for better keyword detection
    all_keywords = list(COLUMN_MAPPING.keys())
    matches = process.extractBests(user_message_lower, all_keywords, score_cutoff=70)
   
    for match, score in matches:
        found_columns.update(COLUMN_MAPPING[match])
       
    return list(found_columns)

def search_datasets(user_message: str) -> Dict:
    """Enhanced search focused on Excel datasets with improved column and location matching."""
    results = {"relevant": False, "datasets_available": {}}
    user_message_lower = user_message.lower()
   
    # Check for locations
    location_patterns = {
        'bardoli': ['bardoli'],
        'surat': ['surat', 'chorasi'],
        'gujarat': ['gujarat'],
        'ahmedabad': ['ahmedabad', 'bavla', 'dholera', 'dholka'],
        'vadodara': ['vadodara', 'padra', 'karjan', 'vaghodiya', 'sinor'],
        'rajkot': ['rajkot', 'gondal', 'lodhika', 'jetpur'],
        'kachchh': ['kachchh', 'abdasa', 'anjar', 'bhuj', 'gandhidham', 'lakhpat', 'mandvi', 'mundra', 'nakhatrana', 'rapar']
    }
   
    found_location = None
    for location_name, patterns in location_patterns.items():
        for pattern in patterns:
            if pattern in user_message_lower:
                found_location = location_name
                break
        if found_location:
            break

    relevant_columns = find_relevant_columns(user_message)
   
    if not found_location and not relevant_columns:
        return {"relevant": False, "message": "Please ask questions related to groundwater data or specific locations."}
   
    results['relevant'] = True
   
    # Search Taluka dataset
    if not taluka_df.empty:
        results['datasets_available']['taluka'] = len(taluka_df)
        taluka_matches = pd.DataFrame()
        if found_location:
            taluka_matches = taluka_df[taluka_df['TALUK'].str.contains(found_location, case=False, na=False) | taluka_df['DISTRICT'].str.contains(found_location, case=False, na=False)]
       
        if not taluka_matches.empty:
            results['taluka_data'] = taluka_matches.to_dict('records')
            results['taluka_summary'] = f"Found {len(taluka_matches)} location matches in Taluka dataset for {found_location}"
        elif relevant_columns:
            # If no location but relevant keywords, return sample data with relevant columns
            sample_data = taluka_df.head(2)
            results['taluka_data'] = sample_data.to_dict('records')
            results['taluka_summary'] = f"Sample data from Taluka dataset ({len(taluka_df)} total records)"
           
    # Search District dataset
    if not district_df.empty:
        results['datasets_available']['district'] = len(district_df)
        district_matches = pd.DataFrame()
        if found_location:
            district_matches = district_df[district_df['DISTRICT'].str.contains(found_location, case=False, na=False)]
       
        if not district_matches.empty:
            results['district_data'] = district_matches.to_dict('records')
            results['district_summary'] = f"Found {len(district_matches)} district matches for {found_location}"

    return results

def detect_user_type(user_message: str) -> str:
    """Detect user type based on message content and keywords"""
    user_message_lower = user_message.lower()
   
    farmer_keywords = ["crop", "farming", "irrigation", "water for crops", "bore well", "field", "agriculture", "harvest", "planting", "my farm", "my field", "water shortage", "drought"]
    planner_keywords = ["policy", "planning", "district", "taluka", "state", "government", "water management", "resource allocation", "budget", "scheme", "water conservation", "aquifer management", "recharge projects"]
    researcher_keywords = ["data analysis", "trends", "statistical", "research", "study", "correlation", "technical", "methodology", "analysis", "water table depth", "aquifer characteristics", "hydrogeology"]
   
    farmer_score = sum(1 for keyword in farmer_keywords if keyword in user_message_lower)
    planner_score = sum(1 for keyword in planner_keywords if keyword in user_message_lower)
    researcher_score = sum(1 for keyword in researcher_keywords if keyword in user_message_lower)
   
    if farmer_score > 0 and farmer_score >= planner_score:
        return "farmer"
    elif planner_score > 0 and planner_score >= farmer_score:
        return "planner"
    elif researcher_score > 0:
        return "researcher"
    else:
        return "general"

def create_user_specific_prompt(user_message: str, search_results: Dict, user_type: str) -> str:
    """Create user-specific prompt for Gemini with tailored context, using a consistent format."""
   
    if not search_results.get('relevant', False):
        return f"""You are NEERNITI, an AI assistant for groundwater resource assessment in Gujarat, India.
User asked: "{user_message}"
This question doesn't seem related to groundwater or water resources. Please respond politely and redirect them to ask about:
- Groundwater levels and assessment
- Water table data
- Rainfall and recharge information
- District/Taluka wise water data
- Water quality and monitoring
- Irrigation and water management
Keep your response helpful and professional."""

    # User-specific response guidelines
    user_guidelines = {
        "farmer": """
RESPONSE GUIDELINES FOR FARMER:
- Keep answers VERY SHORT and PRACTICAL (1-2 sentences max, under 40 words)
- Focus ONLY on actionable farming advice
- Use SIMPLE language, avoid technical terms
- Mention practical solutions like water depth, irrigation timing, crop suitability
- Give direct YES/NO answers when possible
- Focus on immediate farming concerns and solutions""",
       
        "planner": """
RESPONSE GUIDELINES FOR PLANNER:
- Provide DETAILED technical and policy information (4-6 sentences, up to 120 words)
- Include specific data points, percentages, and measurements
- Focus on district/taluka level statistics and trends
- Include resource allocation insights and planning implications
- Use official terminology and provide comprehensive analysis
- Mention categorization status, extraction stages, and future projections
- Address policy and planning recommendations""",
       
        "researcher": """
RESPONSE GUIDELINES FOR RESEARCHER:
- Provide BRIEF technical analysis (3-4 sentences, up to 80 words)
- Include relevant data points and trends
- Mention methodology or data limitations if relevant
- Use appropriate technical terms but stay concise
- Focus on analytical insights""",
       
        "general": """
RESPONSE GUIDELINES FOR GENERAL USER:
- Keep answers SHORT and INFORMATIVE (2-3 sentences, under 60 words)
- Use simple, clear language
- Provide basic information without overwhelming detail
- Focus on key facts and practical information"""
    }

    prompt = f"""You are NEERNITI, an AI assistant for groundwater resource assessment in Gujarat, India.

USER TYPE: {user_type.upper()}
USER QUESTION: "{user_message}"

{user_guidelines.get(user_type, user_guidelines["general"])}

AVAILABLE DATASETS:"""
   
    datasets_info = search_results.get('datasets_available', {})
    if datasets_info.get('taluka', 0) > 0:
        prompt += f"\n- Taluka Dataset: {datasets_info['taluka']} records (2024-25 latest cleaned data)"
    if datasets_info.get('district', 0) > 0:
        prompt += f"\n- District Dataset: {datasets_info['district']} records (2024-25 latest cleaned data)"

    # Add relevant data found
    if 'taluka_data' in search_results and search_results['taluka_data']:
        prompt += "\n\nRELEVANT TALUKA DATA FOUND (JSON FORMAT):"
        prompt += "\n" + json.dumps(search_results['taluka_data'][:3], indent=2)  # Use JSON for clarity
   
    if 'district_data' in search_results and search_results['district_data']:
        prompt += "\n\nRELEVANT DISTRICT DATA FOUND (JSON FORMAT):"
        prompt += "\n" + json.dumps(search_results['district_data'][:3], indent=2)

    prompt += f"""

CRITICAL INSTRUCTIONS:
- Use the EXACT data provided above in your response, referring to the JSON content.
- Tailor your response according to the specific user type guidelines provided.
- If data shows "safe" categorization, mention it is a good sign for water availability.
- If asking about specific location like BARDOLI, use the exact data found for that location.
- Always mention the key metrics found in the data, such as recharge rate, extraction stage, and categorization.
- Be specific about numbers and trends found in the data (e.g., rainfall in mm, extraction in %).
- If the data is not specific enough to fully answer the user's question, state that you are providing the most relevant data available."""

    return prompt

def ask_gemini(prompt: str) -> str:
    """Enhanced Gemini API interaction with better error handling."""
    # Gemini API setup - Replace with your actual key and URL
    GEMINI_API_KEY = "AIzaSyDVeFvBen77ocY_Vbk1DD6z2bihDdBg0JM"
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY

    try:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1000,
                "topP": 0.8,
                "topK": 40
            }
        }
       
        response = requests.post(GEMINI_API_URL, json=payload, timeout=30)
       
        if response.status_code == 200:
            try:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    return content
                else:
                    return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
            except (KeyError, IndexError) as e:
                return "I encountered an issue processing the response. Please try again."
        else:
            print(f"Gemini API error: {response.status_code} - {response.text}")
            return "I'm currently experiencing technical difficulties. Please try again in a moment."
           
    except requests.exceptions.Timeout:
        return "The request took too long to process. Please try again."
    except requests.exceptions.ConnectionError:
        return "I'm having trouble connecting to the AI service. Please check your internet connection and try again."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "An unexpected error occurred. Please try again."

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {
        "message": "NEERNITI Groundwater Assessment API",
        "version": "2.0",
        "datasets": {
            "taluka_records": len(taluka_df) if not taluka_df.empty else 0,
            "district_records": len(district_df) if not district_df.empty else 0,
            "central_records": len(central_df) if not central_df.empty else 0
        },
        "endpoints": ["/chat", "/data/summary", "/health"]
    }
