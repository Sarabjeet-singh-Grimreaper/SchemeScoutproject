import os
import threading
from datetime import datetime, timedelta
from typing import Optional
import random

import fastapi
import fastapi.middleware.cors
import pandas as pd
from pydantic import BaseModel

app = fastapi.FastAPI(title="SchemeScout API", version="2.0.0")

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread lock for file operations
file_lock = threading.Lock()

# Data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SCHEMES_FILE = os.path.join(DATA_DIR, "schemes_master.xlsx")
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "user_submissions.xlsx")

# In-memory cache for schemes
schemes_df: Optional[pd.DataFrame] = None


class UserSubmission(BaseModel):
    name: str
    age: int
    category: str
    income: int
    occupation: str
    region: str
    phone: Optional[str] = None
    email: Optional[str] = None


class DocumentStatus(BaseModel):
    doc_name: str
    is_available: bool
    expiry_date: Optional[str] = None
    renewal_link: Optional[str] = None


class UserDocuments(BaseModel):
    user_id: str
    documents: list[DocumentStatus]


class SchemeMatch(BaseModel):
    scheme_name: str
    match_percentage: int
    status: str  # "Eligible", "Potential", "Ineligible"
    min_age: int
    max_age: int
    category: str
    income_limit: int
    occupation: str
    region: str
    documents_required: str
    description: str
    missing_criteria: list[str]
    # New fields for advanced features
    deadline: Optional[str] = None
    days_remaining: Optional[int] = None
    apply_link: Optional[str] = None
    benefit_amount: Optional[str] = None
    beneficiaries_count: Optional[int] = None


class MatchResponse(BaseModel):
    exact_matches: list[SchemeMatch]
    near_matches: list[SchemeMatch]
    submission_id: str
    urgent_schemes: list[SchemeMatch]  # Schemes with deadlines within 30 days


class SimplifyRequest(BaseModel):
    description: str
    scheme_name: str


class SimplifyResponse(BaseModel):
    what_you_get: str
    who_qualifies: str
    how_to_apply: str


class CompareRequest(BaseModel):
    scheme_names: list[str]


class CompareResponse(BaseModel):
    schemes: list[dict]
    recommendation: str


class CommunityStats(BaseModel):
    total_beneficiaries: int
    district_stats: dict[str, int]
    popular_schemes: list[dict]
    recent_success: list[dict]


# Document portal links
DOCUMENT_PORTALS = {
    "Aadhar Card": "https://uidai.gov.in/",
    "Income Certificate": "https://punjab.gov.in/e-district/",
    "Domicile Certificate": "https://punjab.gov.in/e-district/",
    "Caste Certificate": "https://punjab.gov.in/e-district/",
    "Bank Passbook": None,
    "Ration Card": "https://punjab.gov.in/pds/",
    "Land Records": "https://jamabandi.punjab.gov.in/",
    "Death Certificate": "https://punjab.gov.in/e-district/",
    "Disability Certificate": "https://swfrpunjab.gov.in/",
    "Labour Card": "https://bocw.punjab.gov.in/",
    "School Certificate": None,
    "College ID": None,
    "PM-Kisan Registration": "https://pmkisan.gov.in/",
}

# Scheme application portals
SCHEME_PORTALS = {
    "Mai Bhago Vidya Scheme": "https://punjab.gov.in/mai-bhago/",
    "Ashirwad Scheme": "https://punjab.gov.in/ashirwad/",
    "MMSBY Health Insurance": "https://sha.punjab.gov.in/",
    "BOCW Child Stipend": "https://bocw.punjab.gov.in/",
    "PM-Kisan Samman Nidhi": "https://pmkisan.gov.in/",
    "Old Age Pension": "https://punjab.gov.in/pension/",
    "Widow Pension": "https://punjab.gov.in/pension/",
    "Punjab Shagan Scheme": "https://punjab.gov.in/shagan/",
    "Atta Dal Scheme": "https://punjab.gov.in/pds/",
    "Divyangjan Pension": "https://swfrpunjab.gov.in/",
}


def load_schemes() -> pd.DataFrame:
    """Load schemes from Excel file with error handling."""
    global schemes_df
    
    if schemes_df is not None:
        return schemes_df
    
    try:
        if os.path.exists(SCHEMES_FILE):
            schemes_df = pd.read_excel(SCHEMES_FILE, engine="openpyxl")
            # Fill NaN values
            schemes_df = schemes_df.fillna({
                "Min Age": 0,
                "Max Age": 150,
                "Category": "All",
                "Income Limit": 9999999,
                "Occupation": "All",
                "Region": "All",
                "Documents Required": "",
                "Description": ""
            })
            return schemes_df
        else:
            return pd.DataFrame(columns=[
                "Scheme Name", "Min Age", "Max Age", "Category",
                "Income Limit", "Occupation", "Region",
                "Documents Required", "Description"
            ])
    except Exception as e:
        print(f"Error loading schemes: {e}")
        return pd.DataFrame(columns=[
            "Scheme Name", "Min Age", "Max Age", "Category",
            "Income Limit", "Occupation", "Region",
            "Documents Required", "Description"
        ])


def get_scheme_deadline(scheme_name: str) -> tuple[Optional[str], Optional[int]]:
    """Generate realistic scheme deadlines."""
    # Simulated deadlines - in production, these would come from the database
    deadlines = {
        "Mai Bhago Vidya Scheme": 45,
        "Ashirwad Scheme": 120,
        "MMSBY Health Insurance": 90,
        "BOCW Child Stipend": 30,
        "PM-Kisan Samman Nidhi": 60,
        "Old Age Pension": None,  # Rolling applications
        "Widow Pension": None,
        "Punjab Shagan Scheme": 75,
        "Atta Dal Scheme": None,
        "Divyangjan Pension": None,
    }
    
    days = deadlines.get(scheme_name)
    if days is not None:
        deadline_date = datetime.now() + timedelta(days=days)
        return deadline_date.strftime("%Y-%m-%d"), days
    return None, None


def get_benefit_amount(scheme_name: str) -> str:
    """Get benefit amount for schemes."""
    benefits = {
        "Mai Bhago Vidya Scheme": "Free Bicycle + ₹5,000/year",
        "Ashirwad Scheme": "₹51,000 one-time",
        "MMSBY Health Insurance": "₹5,00,000 coverage",
        "BOCW Child Stipend": "₹3,000-9,000/year",
        "PM-Kisan Samman Nidhi": "₹6,000/year",
        "Old Age Pension": "₹1,500/month",
        "Widow Pension": "₹1,500/month",
        "Punjab Shagan Scheme": "₹31,000-51,000",
        "Atta Dal Scheme": "4kg Atta + 1kg Dal/month",
        "Divyangjan Pension": "₹1,500/month",
    }
    return benefits.get(scheme_name, "Variable")


def get_beneficiaries_count(scheme_name: str, region: str) -> int:
    """Get simulated beneficiaries count for social proof."""
    base_counts = {
        "Mai Bhago Vidya Scheme": 15000,
        "Ashirwad Scheme": 8000,
        "MMSBY Health Insurance": 25000,
        "BOCW Child Stipend": 12000,
        "PM-Kisan Samman Nidhi": 50000,
        "Old Age Pension": 30000,
        "Widow Pension": 18000,
        "Punjab Shagan Scheme": 5000,
        "Atta Dal Scheme": 100000,
        "Divyangjan Pension": 10000,
    }
    base = base_counts.get(scheme_name, 5000)
    # Add some randomness per region
    return base + random.randint(0, 2000)


def calculate_match(user: UserSubmission, scheme: pd.Series) -> tuple[int, list[str]]:
    """Calculate match percentage and missing criteria using fuzzy logic."""
    criteria_met = 0
    total_criteria = 3
    missing = []
    
    # Age check
    min_age = int(scheme.get("Min Age", 0))
    max_age = int(scheme.get("Max Age", 150))
    if min_age <= user.age <= max_age:
        criteria_met += 1
    else:
        if user.age < min_age:
            missing.append(f"Age must be at least {min_age} (you are {user.age})")
        else:
            missing.append(f"Age must be at most {max_age} (you are {user.age})")
    
    # Category check
    scheme_category = str(scheme.get("Category", "All")).strip().lower()
    user_category = user.category.strip().lower()
    if scheme_category == "all" or scheme_category == user_category:
        criteria_met += 1
    else:
        missing.append(f"Category must be '{scheme.get('Category', 'N/A')}' (you selected '{user.category}')")
    
    # Income check
    income_limit = int(scheme.get("Income Limit", 9999999))
    if user.income <= income_limit:
        criteria_met += 1
    else:
        missing.append(f"Annual income must be below ₹{income_limit:,} (you entered ₹{user.income:,})")
    
    # Bonus criteria
    bonus_met = 0
    total_bonus = 2
    
    scheme_occupation = str(scheme.get("Occupation", "All")).strip().lower()
    user_occupation = user.occupation.strip().lower()
    if scheme_occupation == "all" or scheme_occupation == user_occupation or user_occupation in scheme_occupation:
        bonus_met += 1
    
    scheme_region = str(scheme.get("Region", "All")).strip().lower()
    user_region = user.region.strip().lower()
    if scheme_region == "all" or scheme_region == "punjab" or scheme_region == user_region:
        bonus_met += 1
    
    main_percentage = (criteria_met / total_criteria) * 80
    bonus_percentage = (bonus_met / total_bonus) * 20
    match_percentage = int(main_percentage + bonus_percentage)
    
    return match_percentage, missing


def save_submission(user: UserSubmission) -> str:
    """Save user submission to Excel file (thread-safe)."""
    submission_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    with file_lock:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            
            if os.path.exists(SUBMISSIONS_FILE):
                df = pd.read_excel(SUBMISSIONS_FILE, engine="openpyxl")
            else:
                df = pd.DataFrame(columns=[
                    "Submission ID", "Timestamp", "Name", "Age", "Category",
                    "Income", "Occupation", "Region", "Phone", "Email"
                ])
            
            new_row = pd.DataFrame([{
                "Submission ID": submission_id,
                "Timestamp": datetime.now().isoformat(),
                "Name": user.name,
                "Age": user.age,
                "Category": user.category,
                "Income": user.income,
                "Occupation": user.occupation,
                "Region": user.region,
                "Phone": user.phone or "",
                "Email": user.email or ""
            }])
            
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(SUBMISSIONS_FILE, index=False, engine="openpyxl")
            
        except Exception as e:
            print(f"Error saving submission: {e}")
    
    return submission_id


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "SchemeScout API v2.0"}


@app.get("/schemes")
async def get_schemes() -> list[dict]:
    """Get all available schemes with enhanced data."""
    df = load_schemes()
    schemes = []
    for _, row in df.iterrows():
        scheme_name = str(row.get("Scheme Name", "Unknown"))
        deadline, days = get_scheme_deadline(scheme_name)
        schemes.append({
            **row.to_dict(),
            "deadline": deadline,
            "days_remaining": days,
            "apply_link": SCHEME_PORTALS.get(scheme_name),
            "benefit_amount": get_benefit_amount(scheme_name),
        })
    return schemes


@app.post("/match", response_model=MatchResponse)
async def match_schemes(user: UserSubmission) -> MatchResponse:
    """Match user profile against all schemes with enhanced data."""
    df = load_schemes()
    
    if df.empty:
        return MatchResponse(
            exact_matches=[],
            near_matches=[],
            urgent_schemes=[],
            submission_id=save_submission(user)
        )
    
    exact_matches = []
    near_matches = []
    urgent_schemes = []
    
    for _, scheme in df.iterrows():
        match_percentage, missing_criteria = calculate_match(user, scheme)
        
        if match_percentage >= 80:
            status = "Eligible"
        elif match_percentage >= 50:
            status = "Potential"
        else:
            status = "Ineligible"
        
        scheme_name = str(scheme.get("Scheme Name", "Unknown"))
        deadline, days_remaining = get_scheme_deadline(scheme_name)
        
        scheme_match = SchemeMatch(
            scheme_name=scheme_name,
            match_percentage=match_percentage,
            status=status,
            min_age=int(scheme.get("Min Age", 0)),
            max_age=int(scheme.get("Max Age", 150)),
            category=str(scheme.get("Category", "All")),
            income_limit=int(scheme.get("Income Limit", 0)),
            occupation=str(scheme.get("Occupation", "All")),
            region=str(scheme.get("Region", "All")),
            documents_required=str(scheme.get("Documents Required", "")),
            description=str(scheme.get("Description", "")),
            missing_criteria=missing_criteria,
            deadline=deadline,
            days_remaining=days_remaining,
            apply_link=SCHEME_PORTALS.get(scheme_name),
            benefit_amount=get_benefit_amount(scheme_name),
            beneficiaries_count=get_beneficiaries_count(scheme_name, user.region)
        )
        
        if status == "Eligible":
            exact_matches.append(scheme_match)
            # Track urgent schemes (within 30 days)
            if days_remaining is not None and days_remaining <= 30:
                urgent_schemes.append(scheme_match)
        elif status == "Potential":
            near_matches.append(scheme_match)
    
    exact_matches.sort(key=lambda x: x.match_percentage, reverse=True)
    near_matches.sort(key=lambda x: x.match_percentage, reverse=True)
    urgent_schemes.sort(key=lambda x: x.days_remaining or 999)
    
    submission_id = save_submission(user)
    
    return MatchResponse(
        exact_matches=exact_matches,
        near_matches=near_matches,
        urgent_schemes=urgent_schemes,
        submission_id=submission_id
    )


@app.post("/simplify", response_model=SimplifyResponse)
async def simplify_scheme(request: SimplifyRequest) -> SimplifyResponse:
    """Simplify scheme description into TL;DR format."""
    # In production, this would call Gemini API
    # For now, we provide structured summaries based on scheme data
    
    scheme_summaries = {
        "Mai Bhago Vidya Scheme": SimplifyResponse(
            what_you_get="Free bicycle + ₹5,000 per year for education expenses",
            who_qualifies="Girls in Class 9-12 from government schools in Punjab",
            how_to_apply="Apply through your school's principal with Aadhar and school certificate"
        ),
        "Ashirwad Scheme": SimplifyResponse(
            what_you_get="₹51,000 one-time financial assistance for marriage",
            who_qualifies="Daughters of SC/ST/BPL families in Punjab",
            how_to_apply="Apply at District Social Welfare Office with required documents"
        ),
        "MMSBY Health Insurance": SimplifyResponse(
            what_you_get="₹5 lakh health insurance coverage for your family",
            who_qualifies="Punjab residents with annual income below ₹1.8 lakh",
            how_to_apply="Visit nearest Sewa Kendra with Aadhar and ration card"
        ),
        "BOCW Child Stipend": SimplifyResponse(
            what_you_get="₹3,000-9,000 annual stipend for children's education",
            who_qualifies="Children of registered construction workers in Punjab",
            how_to_apply="Apply through BOCW portal with labour card and school certificate"
        ),
        "PM-Kisan Samman Nidhi": SimplifyResponse(
            what_you_get="₹6,000 per year in 3 installments (₹2,000 each)",
            who_qualifies="Small and marginal farmers with cultivable land",
            how_to_apply="Register at pmkisan.gov.in or visit Common Service Center"
        ),
        "Old Age Pension": SimplifyResponse(
            what_you_get="₹1,500 monthly pension for daily expenses",
            who_qualifies="Punjab residents aged 58+ with low income",
            how_to_apply="Apply at District Social Welfare Office or e-District portal"
        ),
        "Widow Pension": SimplifyResponse(
            what_you_get="₹1,500 monthly pension for financial support",
            who_qualifies="Widows aged 18+ with annual income below ₹60,000",
            how_to_apply="Apply at District Social Welfare Office with death certificate"
        ),
        "Punjab Shagan Scheme": SimplifyResponse(
            what_you_get="₹31,000-51,000 for daughter's wedding expenses",
            who_qualifies="Punjab families with income below ₹32,790/year",
            how_to_apply="Apply 60 days before marriage at SDM office"
        ),
        "Atta Dal Scheme": SimplifyResponse(
            what_you_get="4kg wheat flour + 1kg dal free every month",
            who_qualifies="BPL families with valid ration card in Punjab",
            how_to_apply="Collect from nearest fair price shop with ration card"
        ),
        "Divyangjan Pension": SimplifyResponse(
            what_you_get="₹1,500 monthly pension for disabled persons",
            who_qualifies="Persons with 40%+ disability, income below ₹60,000/year",
            how_to_apply="Apply at District Social Welfare Office with disability certificate"
        ),
    }
    
    if request.scheme_name in scheme_summaries:
        return scheme_summaries[request.scheme_name]
    
    # Fallback: Extract key points from description
    desc = request.description
    sentences = desc.split(".")
    return SimplifyResponse(
        what_you_get=sentences[0].strip() if sentences else "Contact office for details",
        who_qualifies=sentences[1].strip() if len(sentences) > 1 else "Check eligibility criteria",
        how_to_apply="Visit nearest government office with required documents"
    )


@app.get("/documents")
async def get_document_portals() -> dict[str, Optional[str]]:
    """Get document application/renewal portals."""
    return DOCUMENT_PORTALS


@app.post("/compare", response_model=CompareResponse)
async def compare_schemes(request: CompareRequest) -> CompareResponse:
    """Compare multiple schemes side by side."""
    df = load_schemes()
    schemes = []
    
    for scheme_name in request.scheme_names:
        row = df[df["Scheme Name"] == scheme_name]
        if not row.empty:
            scheme_data = row.iloc[0].to_dict()
            scheme_data["benefit_amount"] = get_benefit_amount(scheme_name)
            scheme_data["apply_link"] = SCHEME_PORTALS.get(scheme_name)
            deadline, days = get_scheme_deadline(scheme_name)
            scheme_data["deadline"] = deadline
            scheme_data["days_remaining"] = days
            schemes.append(scheme_data)
    
    # Generate recommendation based on benefits
    if len(schemes) >= 2:
        # Simple heuristic: recommend scheme with higher income limit (more accessible)
        recommendation = f"Based on accessibility, we recommend applying for the scheme with broader eligibility criteria first."
    else:
        recommendation = "Add more schemes to compare."
    
    return CompareResponse(schemes=schemes, recommendation=recommendation)


@app.get("/community-stats", response_model=CommunityStats)
async def get_community_stats(region: str = "Mohali") -> CommunityStats:
    """Get community statistics for social proof."""
    # Simulated data - in production, this would come from actual database
    district_stats = {
        "Mohali": random.randint(5000, 8000),
        "Ludhiana": random.randint(8000, 12000),
        "Amritsar": random.randint(7000, 10000),
        "Jalandhar": random.randint(6000, 9000),
        "Patiala": random.randint(5000, 7000),
    }
    
    popular_schemes = [
        {"name": "MMSBY Health Insurance", "applications": random.randint(200, 500)},
        {"name": "PM-Kisan Samman Nidhi", "applications": random.randint(300, 600)},
        {"name": "Old Age Pension", "applications": random.randint(150, 300)},
    ]
    
    recent_success = [
        {"name": "Gurpreet Singh", "scheme": "PM-Kisan", "district": region, "days_ago": 2},
        {"name": "Harjit Kaur", "scheme": "MMSBY Health", "district": region, "days_ago": 3},
        {"name": "Balwinder Singh", "scheme": "Old Age Pension", "district": region, "days_ago": 5},
    ]
    
    return CommunityStats(
        total_beneficiaries=sum(district_stats.values()),
        district_stats=district_stats,
        popular_schemes=popular_schemes,
        recent_success=recent_success
    )


@app.get("/stats")
async def get_stats() -> dict:
    """Get submission statistics."""
    try:
        if os.path.exists(SUBMISSIONS_FILE):
            df = pd.read_excel(SUBMISSIONS_FILE, engine="openpyxl")
            return {
                "total_submissions": len(df),
                "categories": df["Category"].value_counts().to_dict() if "Category" in df.columns else {},
                "regions": df["Region"].value_counts().to_dict() if "Region" in df.columns else {}
            }
    except Exception as e:
        print(f"Error getting stats: {e}")
    
    return {"total_submissions": 0, "categories": {}, "regions": {}}
