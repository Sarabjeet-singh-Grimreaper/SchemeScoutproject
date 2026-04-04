"""
Excel Service - Handles all Excel file operations for SchemeScout
Thread-safe operations for reading schemes and logging user submissions
"""

import pandas as pd
import os
from datetime import datetime
import threading
from typing import List, Dict, Any, Optional

# Thread lock for safe Excel writes
excel_lock = threading.Lock()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
SCHEMES_FILE = os.path.join(DATA_DIR, 'schemes_master.xlsx')
SUBMISSIONS_FILE = os.path.join(DATA_DIR, 'user_submissions.xlsx')


def ensure_data_dir():
    """Ensure the data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_schemes() -> pd.DataFrame:
    """
    Load schemes from Excel file
    Returns empty DataFrame with correct columns if file doesn't exist
    """
    try:
        if os.path.exists(SCHEMES_FILE):
            df = pd.read_excel(SCHEMES_FILE, engine='openpyxl')
            # Replace NaN values with None to avoid JSON serialization issues
            df = df.replace({float('nan'): None})
            return df
        else:
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=[
                'Scheme Name', 'Min Age', 'Max Age', 'Category', 
                'Income Limit', 'Occupation', 'Region', 'Gender',
                'Documents Required', 'Description', 'Benefits',
                'Application Deadline', 'Application URL', 'Status'
            ])
    except Exception as e:
        print(f"Error loading schemes: {e}")
        return pd.DataFrame()


def get_all_schemes() -> List[Dict[str, Any]]:
    """Get all schemes as a list of dictionaries"""
    df = load_schemes()
    # Replace NaN with None for JSON serialization
    df = df.where(pd.notnull(df), None)
    # Convert any remaining problematic values
    df = df.fillna('')
    return df.to_dict(orient='records')


def get_scheme_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get a specific scheme by name"""
    df = load_schemes()
    scheme = df[df['Scheme Name'].str.lower() == name.lower()]
    if not scheme.empty:
        scheme_dict = scheme.iloc[0].to_dict()
        # Replace NaN values with None
        return {k: (v if pd.notna(v) else None) for k, v in scheme_dict.items()}
    return None


def log_user_submission(submission_data: Dict[str, Any]) -> bool:
    """
    Log a user submission to the Excel file
    Thread-safe operation
    """
    ensure_data_dir()
    
    with excel_lock:
        try:
            # Add timestamp
            submission_data['Submission Time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Load existing submissions or create new DataFrame
            if os.path.exists(SUBMISSIONS_FILE):
                df = pd.read_excel(SUBMISSIONS_FILE, engine='openpyxl')
            else:
                df = pd.DataFrame()
            
            # Append new submission
            new_row = pd.DataFrame([submission_data])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save back to Excel
            df.to_excel(SUBMISSIONS_FILE, index=False, engine='openpyxl')
            return True
            
        except Exception as e:
            print(f"Error logging submission: {e}")
            return False


def get_unique_categories() -> List[str]:
    """Get unique categories from schemes"""
    df = load_schemes()
    if 'Category' in df.columns:
        return df['Category'].dropna().unique().tolist()
    return []


def get_unique_occupations() -> List[str]:
    """Get unique occupations from schemes"""
    df = load_schemes()
    if 'Occupation' in df.columns:
        return df['Occupation'].dropna().unique().tolist()
    return []


def get_unique_regions() -> List[str]:
    """Get unique regions from schemes"""
    df = load_schemes()
    if 'Region' in df.columns:
        return df['Region'].dropna().unique().tolist()
    return []


def get_schemes_by_deadline(days: int = 30) -> List[Dict[str, Any]]:
    """Get schemes with deadlines within specified days"""
    df = load_schemes()
    if 'Application Deadline' not in df.columns:
        return []
    
    today = datetime.now()
    df['Application Deadline'] = pd.to_datetime(df['Application Deadline'], errors='coerce')
    
    # Filter schemes with deadlines within the specified days
    mask = (df['Application Deadline'] >= today) & \
           (df['Application Deadline'] <= today + pd.Timedelta(days=days))
    
    urgent_schemes = df[mask].copy()
    urgent_schemes = urgent_schemes.where(pd.notnull(urgent_schemes), None)
    
    # Convert deadline back to string for JSON
    urgent_schemes['Application Deadline'] = urgent_schemes['Application Deadline'].dt.strftime('%Y-%m-%d')
    
    return urgent_schemes.to_dict(orient='records')
