"""
Matching Engine - The "Bit-Wise" Eligibility Matching Logic
Implements exact matching and fuzzy/partial matching for near-miss suggestions
"""

from typing import Dict, Any, List, Tuple
from .excel_service import load_schemes
import pandas as pd


def calculate_match_score(user_data: Dict[str, Any], scheme: Dict[str, Any]) -> Tuple[int, List[str], List[str]]:
    """
    Calculate match score between user data and a scheme
    Returns: (score_percentage, matched_criteria, missing_criteria)
    """
    matched = []
    missing = []
    total_criteria = 0
    matched_count = 0
    
    # Age matching
    if scheme.get('Min Age') is not None or scheme.get('Max Age') is not None:
        total_criteria += 1
        user_age = user_data.get('age', 0)
        min_age = scheme.get('Min Age', 0) or 0
        max_age = scheme.get('Max Age', 150) or 150
        
        # Handle NaN values
        if pd.notna(min_age) and pd.notna(max_age):
            if min_age <= user_age <= max_age:
                matched.append(f"Age ({user_age} years)")
                matched_count += 1
            else:
                if user_age < min_age:
                    missing.append(f"Age: Need to be at least {min_age} years (you are {user_age})")
                else:
                    missing.append(f"Age: Must be under {max_age} years (you are {user_age})")
        else:
            matched.append(f"Age ({user_age} years)")
            matched_count += 1
    
    # Category matching
    if scheme.get('Category'):
        total_criteria += 1
        scheme_categories = str(scheme['Category']).lower().split(',')
        scheme_categories = [c.strip() for c in scheme_categories]
        user_category = str(user_data.get('category', '')).lower().strip()
        
        if user_category in scheme_categories or 'all' in scheme_categories or 'general' in scheme_categories:
            matched.append(f"Category ({user_data.get('category', 'N/A')})")
            matched_count += 1
        else:
            missing.append(f"Category: Scheme requires {scheme['Category']}")
    
    # Income matching
    if scheme.get('Income Limit') is not None:
        total_criteria += 1
        user_income = user_data.get('annual_income', 0) or 0
        income_limit = scheme.get('Income Limit', float('inf')) or float('inf')
        
        # Handle NaN values
        if pd.notna(income_limit) and income_limit != float('inf'):
            if user_income <= income_limit:
                matched.append(f"Income (Rs. {user_income:,} annual)")
                matched_count += 1
            else:
                missing.append(f"Income: Must be below Rs. {income_limit:,} (yours is Rs. {user_income:,})")
        else:
            matched.append(f"Income (Rs. {user_income:,} annual)")
            matched_count += 1
    
    # Occupation matching
    if scheme.get('Occupation'):
        total_criteria += 1
        scheme_occupations = str(scheme['Occupation']).lower().split(',')
        scheme_occupations = [o.strip() for o in scheme_occupations]
        user_occupation = str(user_data.get('occupation', '')).lower().strip()
        
        if user_occupation in scheme_occupations or 'all' in scheme_occupations or 'any' in scheme_occupations:
            matched.append(f"Occupation ({user_data.get('occupation', 'N/A')})")
            matched_count += 1
        else:
            missing.append(f"Occupation: Scheme is for {scheme['Occupation']}")
    
    # Region matching
    if scheme.get('Region'):
        total_criteria += 1
        scheme_regions = str(scheme['Region']).lower().split(',')
        scheme_regions = [r.strip() for r in scheme_regions]
        user_region = str(user_data.get('region', '')).lower().strip()
        
        if user_region in scheme_regions or 'all punjab' in scheme_regions or 'all' in scheme_regions:
            matched.append(f"Region ({user_data.get('region', 'N/A')})")
            matched_count += 1
        else:
            missing.append(f"Region: Scheme available in {scheme['Region']}")
    
    # Gender matching
    if scheme.get('Gender'):
        total_criteria += 1
        scheme_gender = str(scheme['Gender']).lower().strip()
        user_gender = str(user_data.get('gender', '')).lower().strip()
        
        if scheme_gender == 'all' or scheme_gender == user_gender:
            matched.append(f"Gender ({user_data.get('gender', 'N/A')})")
            matched_count += 1
        else:
            missing.append(f"Gender: Scheme is for {scheme['Gender']} only")
    
    # Calculate percentage
    if total_criteria > 0:
        score = int((matched_count / total_criteria) * 100)
    else:
        score = 100  # No specific criteria means everyone qualifies
    
    return score, matched, missing


def get_eligibility_status(score: int) -> str:
    """Determine eligibility status based on score"""
    if score >= 100:
        return "Eligible"
    elif score >= 70:
        return "Potential"
    elif score >= 50:
        return "Partial Match"
    else:
        return "Ineligible"


def find_matching_schemes(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Find all matching schemes for a user
    Returns schemes sorted by match score
    """
    df = load_schemes()
    if df.empty:
        return []
    
    results = []
    
    for _, row in df.iterrows():
        scheme = row.to_dict()
        score, matched, missing = calculate_match_score(user_data, scheme)
        
        # Include schemes with at least some match (score > 0) or all schemes for discovery
        result = {
            'scheme_name': str(scheme.get('Scheme Name', 'Unknown')),
            'match_score': int(score),
            'status': get_eligibility_status(score),
            'matched_criteria': matched,
            'missing_criteria': missing,
            'benefits': str(scheme.get('Benefits', '')),
            'description': str(scheme.get('Description', '')),
            'documents_required': str(scheme.get('Documents Required', '')),
            'application_deadline': str(scheme.get('Application Deadline', '')) if scheme.get('Application Deadline') and pd.notna(scheme.get('Application Deadline')) else None,
            'application_url': str(scheme.get('Application URL', '')),
            'income_limit': scheme.get('Income Limit') if pd.notna(scheme.get('Income Limit')) else None,
            'min_age': scheme.get('Min Age') if pd.notna(scheme.get('Min Age')) else None,
            'max_age': scheme.get('Max Age') if pd.notna(scheme.get('Max Age')) else None,
            'category': str(scheme.get('Category', '')),
            'occupation': str(scheme.get('Occupation', '')),
            'region': str(scheme.get('Region', ''))
        }
        results.append(result)
    
    # Sort by match score (highest first)
    results.sort(key=lambda x: x['match_score'], reverse=True)
    
    return results


def get_document_checklist(user_documents: List[str], scheme_name: str) -> Dict[str, Any]:
    """
    Compare user's documents against scheme requirements
    Returns what they have and what they need
    """
    df = load_schemes()
    scheme = df[df['Scheme Name'].str.lower() == scheme_name.lower()]
    
    if scheme.empty:
        return {'error': 'Scheme not found'}
    
    required_docs_str = scheme.iloc[0].get('Documents Required', '')
    if not required_docs_str:
        return {
            'scheme_name': scheme_name,
            'required_documents': [],
            'available_documents': [],
            'missing_documents': [],
            'completion_percentage': 100
        }
    
    # Parse required documents
    required_docs = [doc.strip().lower() for doc in str(required_docs_str).split(',')]
    user_docs_lower = [doc.lower() for doc in user_documents]
    
    available = []
    missing = []
    
    for doc in required_docs:
        if any(user_doc in doc or doc in user_doc for user_doc in user_docs_lower):
            available.append(doc.title())
        else:
            missing.append(doc.title())
    
    completion = int((len(available) / len(required_docs)) * 100) if required_docs else 100
    
    return {
        'scheme_name': scheme_name,
        'required_documents': [doc.title() for doc in required_docs],
        'available_documents': available,
        'missing_documents': missing,
        'completion_percentage': completion
    }


def get_gap_analysis(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Perform gap analysis for near-match schemes
    Identifies what specific changes would make user eligible
    """
    df = load_schemes()
    if df.empty:
        return []
    
    gap_analysis = []
    
    for _, row in df.iterrows():
        scheme = row.to_dict()
        score, matched, missing = calculate_match_score(user_data, scheme)
        
        # Only include schemes that are close (50-99% match)
        if 50 <= score < 100:
            gap_analysis.append({
                'scheme_name': scheme.get('Scheme Name', 'Unknown'),
                'current_score': score,
                'matched_criteria': matched,
                'gaps': missing,
                'potential_benefit': scheme.get('Benefits', ''),
                'recommendation': generate_recommendation(missing)
            })
    
    return gap_analysis


def generate_recommendation(missing_criteria: List[str]) -> str:
    """Generate actionable recommendations based on missing criteria"""
    recommendations = []
    
    for criteria in missing_criteria:
        criteria_lower = criteria.lower()
        
        if 'age' in criteria_lower:
            recommendations.append("This scheme has age restrictions. Check back when you meet the age criteria, or explore similar schemes without age limits.")
        elif 'income' in criteria_lower:
            recommendations.append("Consider obtaining an updated Income Certificate from your local Tehsil office to verify your eligibility.")
        elif 'category' in criteria_lower:
            recommendations.append("Ensure your caste/category certificate is up to date. Visit the nearest SDM office if you need to apply for one.")
        elif 'occupation' in criteria_lower:
            recommendations.append("This scheme targets specific occupations. You may find similar benefits under schemes for your occupation category.")
        elif 'region' in criteria_lower:
            recommendations.append("This scheme is region-specific. Check if similar schemes are available in your area.")
        elif 'gender' in criteria_lower:
            recommendations.append("This scheme is gender-specific. Explore other schemes that may offer similar benefits.")
    
    return " ".join(recommendations) if recommendations else "Review the scheme criteria carefully and gather required documents."
