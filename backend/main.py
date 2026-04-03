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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Initialize FastAPI app
app = FastAPI(
    title="SchemeScout API",
    description="Punjab Government Welfare Schemes Eligibility Checker",
    version="1.0.0"
)

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


@app.get("/api/schemes")
async def get_schemes():
    """Get all available schemes"""
    try:
        schemes = get_all_schemes()
        return {
            "success": True,
            "count": len(schemes),
            "schemes": schemes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schemes/{scheme_name}")
async def get_scheme(scheme_name: str):
    """Get a specific scheme by name"""
    scheme = get_scheme_by_name(scheme_name)
    if scheme:
        return {"success": True, "scheme": scheme}
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
        
        return {
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
        }
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
            return {
                "success": True,
                "simplified": {
                    "summary": request.text[:200] + "..." if len(request.text) > 200 else request.text,
                    "key_points": ["Please set GEMINI_API_KEY for AI-powered summaries"],
                    "ai_powered": False
                }
            }
        
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Simplify this government scheme description into easy-to-understand language. 
        Provide:
        1. A 2-3 sentence summary
        2. Three key points: What you get, Who qualifies, How to apply
        
        Scheme: {request.scheme_name if request.scheme_name else 'Government Scheme'}
        Description: {request.text}
        
        Format your response as:
        SUMMARY: [Your summary]
        WHAT YOU GET: [Benefit details]
        WHO QUALIFIES: [Eligibility criteria]
        HOW TO APPLY: [Application process]
        """
        
        response = model.generate_content(prompt)
        
        return {
            "success": True,
            "simplified": {
                "raw_response": response.text,
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
