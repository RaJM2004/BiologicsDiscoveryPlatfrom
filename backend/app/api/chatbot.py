from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from groq import Groq

router = APIRouter()

# Initialize Groq Client
API_KEY = os.getenv("GROQ_API_KEY", "YOUR_API_KEY_HERE")

try:
    from groq import Groq
    client = Groq(api_key=API_KEY)
except ImportError:
    print("Groq library not found. Install with `pip install groq`.")
    client = None
except Exception as e:
    print(f"Failed to initialize Groq client: {e}")
    client = None

class ChatRequest(BaseModel):
    message: str
    context: str = "" # Optional context from the page the user is on

@router.post("/ask")
async def ask_chatbot(request: ChatRequest):
    if not client:
        raise HTTPException(status_code=503, detail="Chat service unavailable (API Key Error).")

    system_prompt = """You are 'BioAssist', an advanced AI assistant embedded in the Biologics Discovery Platform. 
Your goal is to help scientists navigate the platform and answer complex biological/pharma questions.

PLATFORM NAVIGATION GUIDE:
1. Target Explorer: Search for targets (proteins/genes) and view 3D structures.
2. Hit Screening: Upload .smi files to screen millions of compounds using XGBoost.
3. Lead Optimization: Use Genetic Algorithms to evolve/mutate a hit into a better candidate.
4. Wet-Lab Validation: Generate protocols (OT-2) for physical testing.
5. Blinded Results: Review data without bias.

SCIENTIFIC PERSONA:
- You are an expert in Computational Biology, Medicinal Chemistry, and Pharmacology.
- Be concise, professional, and helpful.
- If the user is stuck, suggest the next step in the workflow (e.g., "After screening, you should optimize your top hits.").
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Using a currently supported model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {request.context}\n\nUser Question: {request.message}"}
            ],
            temperature=0.7,
            max_tokens=500,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        return {"response": completion.choices[0].message.content}

    except Exception as e:
        print(f"Groq API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
