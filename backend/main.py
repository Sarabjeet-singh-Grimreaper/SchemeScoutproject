"""
SchemeScout Backend - FastAPI Server
Handles eligibility matching, Excel operations, and AI integration
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
from dotenv import load_dotenv
import math

# Load environment variables
load_dotenv()

# Custom JSON encoder to handle NaN values
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float):
            if math.isnan(obj):
                return None
            elif math.isinf(obj):
                return None
        return super().default(obj)

def custom_json_response(data: Any, status_code: int = 200):
    """Create JSON response with custom encoder"""
    return JSONResponse(
        content=json.loads(json.dumps(data, cls=CustomJSONEncoder)),
        status_code=status_code
    )

# Import services
from services.excel_service import (
    get_all_schemes,
    get_scheme_by_name,
    log_user_submission,
    get_unique_categories,
    get_unique_occupations,
    get_unique_regions,
    get_schemes_by_deadline
)
from services.matching_engine import (
    find_matching_schemes,
    get_document_checklist,
    get_gap_analysis
)

# Initialize FastAPI app with custom JSON response
app = FastAPI(
    title="SchemeScout API",
    description="Punjab Government Welfare Schemes Eligibility Checker",
    version="1.0.0",
    default_response_class=JSONResponse
)

# Custom JSON response middleware
@app.middleware("http")
async def json_cleanup_middleware(request, call_next):
    response = await call_next(request)
    
    # Only modify JSON responses
    if response.headers.get("content-type") == "application/json":
        # Read the original response
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        
        try:
            # Parse and clean JSON
            import json
            data = json.loads(body.decode())
            cleaned_data = json.loads(json.dumps(data, cls=CustomJSONEncoder))
            
            # Return cleaned response
            return JSONResponse(
                content=cleaned_data,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except:
            # If JSON parsing fails, return original
            return response
    
    return response

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "detail": "An unexpected error occurred. Please try again."
        }
    )


# Pydantic models for request/response
class UserProfile(BaseModel):
    name: str
    age: int
    gender: str
    category: str
    annual_income: Optional[float] = 0
    occupation: str
    region: str
    phone: Optional[str] = None
    email: Optional[str] = None


class DocumentCheckRequest(BaseModel):
    scheme_name: str
    user_documents: List[str]


class SimplifyRequest(BaseModel):
    text: str
    scheme_name: Optional[str] = None


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "service": "SchemeScout API",
        "version": "1.0.0",
        "team": "Bit-Wise 4"
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return custom_json_response({
        "test": "working",
        "data": [1, 2, 3],
        "nested": {"a": 1, "b": None}
    })


@app.get("/api/schemes")
async def get_schemes():
    """Get all available schemes"""
    try:
        schemes = get_all_schemes()
        return custom_json_response({
            "success": True,
            "count": len(schemes),
            "schemes": schemes
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schemes/{scheme_name}")
async def get_scheme(scheme_name: str):
    """Get a specific scheme by name"""
    scheme = get_scheme_by_name(scheme_name)
    if scheme:
        return custom_json_response({"success": True, "scheme": scheme})
    raise HTTPException(status_code=404, detail="Scheme not found")


@app.post("/api/check-eligibility")
async def check_eligibility(user: UserProfile):
    """
    Check user eligibility against all schemes
    Returns matched schemes with scores and gap analysis
    """
    try:
        user_data = user.model_dump()
        
        # Log the submission
        log_user_submission(user_data)
        
        # Find matching schemes
        matches = find_matching_schemes(user_data)
        
        # Separate by eligibility status
        eligible = [m for m in matches if m['status'] == 'Eligible']
        potential = [m for m in matches if m['status'] == 'Potential']
        partial = [m for m in matches if m['status'] == 'Partial Match']
        
        return custom_json_response({
            "success": True,
            "user_profile": {
                "name": user.name,
                "age": user.age,
                "category": user.category
            },
            "summary": {
                "total_schemes": len(matches),
                "eligible_count": len(eligible),
                "potential_count": len(potential),
                "partial_count": len(partial)
            },
            "eligible_schemes": eligible,
            "potential_schemes": potential,
            "partial_matches": partial,
            "all_results": matches
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/document-check")
async def check_documents(request: DocumentCheckRequest):
    """Check user documents against scheme requirements"""
    try:
        result = get_document_checklist(request.user_documents, request.scheme_name)
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        return {"success": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/deadline-alerts")
async def get_deadline_alerts(days: int = 30):
    """Get schemes with approaching deadlines"""
    try:
        urgent_schemes = get_schemes_by_deadline(days)
        return {
            "success": True,
            "alert_period_days": days,
            "count": len(urgent_schemes),
            "urgent_schemes": urgent_schemes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/filters")
async def get_filter_options():
    """Get available filter options for the form"""
    try:
        return {
            "success": True,
            "categories": get_unique_categories(),
            "occupations": get_unique_occupations(),
            "regions": get_unique_regions(),
            "genders": ["Male", "Female", "Other"],
            "age_ranges": [
                {"label": "0-18", "min": 0, "max": 18},
                {"label": "18-35", "min": 18, "max": 35},
                {"label": "35-60", "min": 35, "max": 60},
                {"label": "60+", "min": 60, "max": 150}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/gap-analysis")
async def analyze_gaps(user: UserProfile):
    """Get detailed gap analysis for near-match schemes"""
    try:
        user_data = user.model_dump()
        gaps = get_gap_analysis(user_data)
        return {
            "success": True,
            "count": len(gaps),
            "gap_analysis": gaps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/simplify")
async def simplify_text(request: SimplifyRequest):
    """
    Use AI to simplify scheme descriptions
    Requires GEMINI_API_KEY environment variable
    """
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            # Return a formatted summary without AI if no API key
            # Create basic TL;DR points from the description
            text = request.text[:200] + "..." if len(request.text) > 200 else request.text
            tldr_points = [
                f"WHAT YOU GET: Financial and educational support for eligible beneficiaries",
                f"WHO QUALIFIES: Students/residents meeting specific eligibility criteria", 
                f"HOW TO APPLY: Submit application through official government portal with required documents"
            ]
            
            return {
                "success": True,
                "simplified": {
                    "tldr_points": tldr_points,
                    "raw_response": text,
                    "ai_powered": False
                }
            }
        
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Simplify this government scheme description into a clear, concise TL;DR format.
        
        Scheme: {request.scheme_name if request.scheme_name else 'Government Scheme'}
        Description: {request.text}
        
        Provide exactly 3 bullet points:
        1. WHAT YOU GET: The main benefits in simple terms
        2. WHO QUALIFIES: Eligibility criteria in simple terms  
        3. HOW TO APPLY: Application process in simple terms
        
        Format your response as exactly 3 lines, each starting with the bullet point symbol:
        • WHAT YOU GET: [benefit details]
        • WHO QUALIFIES: [eligibility details]
        • HOW TO APPLY: [application details]
        
        Keep each point under 50 words. Use simple, everyday language.
        """
        
        response = model.generate_content(prompt)
        
        # Parse the response to extract the three bullet points
        response_text = response.text.strip()
        bullet_points = []
        
        # Split by bullet points and clean up
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-'):
                # Remove bullet symbol and clean up
                clean_line = line[1:].strip()
                if clean_line:
                    bullet_points.append(clean_line)
        
        # Ensure we have exactly 3 points
        if len(bullet_points) < 3:
            # Fallback: split response into parts
            parts = response_text.split('\n')
            bullet_points = [part.strip() for part in parts[:3] if part.strip()]
        
        return {
            "success": True,
            "simplified": {
                "tldr_points": bullet_points,
                "raw_response": response_text,
                "ai_powered": True
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "simplified": {
                "summary": request.text[:200] + "..." if len(request.text) > 200 else request.text,
                "ai_powered": False
            }
        }


# Run with: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
