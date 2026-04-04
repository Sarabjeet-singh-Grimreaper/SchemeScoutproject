#!/usr/bin/env python3
"""
SchemeScout - Data Seeding Script
Creates the initial schemes_master.xlsx with Punjab Government schemes
Team: Bit-Wise 4
"""

import pandas as pd
import os
from pathlib import Path
from datetime import datetime, timedelta

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DATA_DIR = PROJECT_ROOT / 'backend' / 'data'

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Punjab Government Welfare Schemes Data
schemes_data = [
    {
        'Scheme Name': 'Mai Bhago Vidya Scheme',
        'Min Age': 6,
        'Max Age': 18,
        'Category': 'All',
        'Income Limit': 200000,
        'Occupation': 'Student',
        'Region': 'All Punjab',
        'Gender': 'Female',
        'Documents Required': 'Aadhar Card, School Certificate, Bank Account, Residence Proof',
        'Description': 'Free bicycles and uniforms for girl students in government schools from Class 6 to 12. Promotes girl child education and reduces dropouts.',
        'Benefits': 'Free bicycle worth Rs. 4,000 and school uniforms. Transportation support for rural girls.',
        'Application Deadline': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
        'Application URL': 'https://punjab.gov.in/mai-bhago-vidya',
        'Status': 'Active'
    },
    {
        'Scheme Name': 'Ashirwad Scheme',
        'Min Age': 18,
        'Max Age': None,
        'Category': 'SC, BC, EWS',
        'Income Limit': 32790,
        'Occupation': 'All',
        'Region': 'All Punjab',
        'Gender': 'Female',
        'Documents Required': 'Aadhar Card, Income Certificate, Caste Certificate, Bank Account, Marriage Card',
        'Description': 'Financial assistance for marriage of daughters from economically weaker sections and SC/BC categories.',
        'Benefits': 'Rs. 51,000 one-time grant for marriage expenses',
        'Application Deadline': (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d'),
        'Application URL': 'https://punjab.gov.in/ashirwad-scheme',
        'Status': 'Active'
    },
    {
        'Scheme Name': 'MMSBY Health Insurance',
        'Min Age': 0,
        'Max Age': None,
        'Category': 'All',
        'Income Limit': 180000,
        'Occupation': 'All',
        'Region': 'All Punjab',
        'Gender': 'All',
        'Documents Required': 'Aadhar Card, Ration Card, Income Certificate, Family Photo',
        'Description': 'Mukhya Mantri Sehat Bima Yojana provides cashless health coverage for hospitalization in empanelled hospitals.',
        'Benefits': 'Health coverage up to Rs. 10 Lakh per family per year. Cashless treatment in 800+ hospitals.',
        'Application Deadline': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
        'Application URL': 'https://sha.punjab.gov.in',
        'Status': 'Active'
    },
    {
        'Scheme Name': 'BOCW Education Stipend',
        'Min Age': 5,
        'Max Age': 25,
        'Category': 'All',
        'Income Limit': 300000,
        'Occupation': 'Construction Worker',
        'Region': 'All Punjab',
        'Gender': 'All',
        'Documents Required': 'BOCW Card, Aadhar Card, School/College Certificate, Bank Account',
        'Description': 'Educational stipend for children of registered construction workers under Building and Other Construction Workers Board.',
        'Benefits': 'Rs. 8,000 to Rs. 12,000 annual stipend based on education level',
        'Application Deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'Application URL': 'https://pblabour.gov.in/bocw',
        'Status': 'Active'
    },
    {
        'Scheme Name': 'Post-Matric Scholarship',
        'Min Age': 15,
        'Max Age': 35,
        'Category': 'SC, BC, OBC',
        'Income Limit': 250000,
        'Occupation': 'Student',
        'Region': 'All Punjab',
        'Gender': 'All',
        'Documents Required': 'Aadhar Card, Caste Certificate, Income Certificate, Previous Marksheet, Bank Account',
        'Description': 'Scholarship for SC/BC students pursuing post-matric education including diploma, degree, and professional courses.',
        'Benefits': 'Full tuition fee reimbursement plus monthly maintenance allowance of Rs. 550-1200',
        'Application Deadline': (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
        'Application URL': 'https://scholarships.punjab.gov.in',
        'Status': 'Active'
    },
    {
        'Scheme Name': 'PM-Kisan Samman Nidhi',
        'Min Age': 18,
        'Max Age': None,
        'Category': 'All',
        'Income Limit': None,
        'Occupation': 'Farmer',
        'Region': 'All Punjab',
        'Gender': 'All',
        'Documents Required': 'Aadhar Card, Land Records (Fard), Bank Account, Mobile Number',
        'Description': 'Central government scheme providing direct income support to farmer families with cultivable land.',
        'Benefits': 'Rs. 6,000 per year in three equal instalments of Rs. 2,000',
        'Application Deadline': (datetime.now() + timedelta(days=120)).strftime('%Y-%m-%d'),
        'Application URL': 'https://pmkisan.gov.in',
        'Status': 'Active'
    },
    {
        'Scheme Name': 'Old Age Pension Scheme',
        'Min Age': 60,
        'Max Age': None,
        'Category': 'All',
        'Income Limit': 60000,
        'Occupation': 'All',
        'Region': 'All Punjab',
        'Gender': 'All',
        'Documents Required': 'Aadhar Card, Age Proof, Income Certificate, Bank Account, BPL Card',
        'Description': 'Monthly pension for senior citizens from Below Poverty Line families and those without other income sources.',
        'Benefits': 'Rs. 1,500 per month pension directly to bank account',
        'Application Deadline': None,
        'Application URL': 'https://punjab.gov.in/old-age-pension',
        'Status': 'Active'
    },
    {
        'Scheme Name': 'Widow Pension Scheme',
        'Min Age': 18,
        'Max Age': None,
        'Category': 'All',
        'Income Limit': 60000,
        'Occupation': 'All',
        'Region': 'All Punjab',
        'Gender': 'Female',
        'Documents Required': 'Aadhar Card, Death Certificate of Husband, Income Certificate, Bank Account',
        'Description': 'Financial assistance for widows from economically weaker sections to support their livelihood.',
        'Benefits': 'Rs. 1,500 per month pension',
        'Application Deadline': None,
        'Application URL': 'https://punjab.gov.in/widow-pension',
        'Status': 'Active'
    },
    {
        'Scheme Name': 'Disability Pension Scheme',
        'Min Age': 18,
        'Max Age': None,
        'Category': 'All',
        'Income Limit': 60000,
        'Occupation': 'All',
        'Region': 'All Punjab',
        'Gender': 'All',
        'Documents Required': 'Aadhar Card, Disability Certificate (40%+), Income Certificate, Bank Account',
        'Description': 'Monthly pension for persons with 40% or more disability from economically weaker sections.',
        'Benefits': 'Rs. 1,500 per month pension',
        'Application Deadline': None,
        'Application URL': 'https://punjab.gov.in/disability-pension',
        'Status': 'Active'
    },
    {
        'Scheme Name': 'Atta Dal Scheme',
        'Min Age': 0,
        'Max Age': None,
        'Category': 'All',
        'Income Limit': 100000,
        'Occupation': 'All',
        'Region': 'All Punjab',
        'Gender': 'All',
        'Documents Required': 'Ration Card (Blue/Yellow), Aadhar Card',
        'Description': 'Subsidized food grains for Below Poverty Line families through Public Distribution System.',
        'Benefits': 'Wheat at Rs. 2/kg and Dal at Rs. 20/kg for eligible families',
        'Application Deadline': None,
        'Application URL': 'https://punjab.gov.in/atta-dal',
        'Status': 'Active'
    },
    {
        'Scheme Name': 'Skill Development Training',
        'Min Age': 18,
        'Max Age': 35,
        'Category': 'All',
        'Income Limit': 300000,
        'Occupation': 'Unemployed, Student',
        'Region': 'All Punjab',
        'Gender': 'All',
        'Documents Required': 'Aadhar Card, Education Certificate, Bank Account',
        'Description': 'Free skill training programs in various trades like IT, healthcare, hospitality, and manufacturing.',
        'Benefits': 'Free training, certification, and placement assistance. Stipend during training period.',
        'Application Deadline': (datetime.now() + timedelta(days=75)).strftime('%Y-%m-%d'),
        'Application URL': 'https://pbssd.punjab.gov.in',
        'Status': 'Active'
    },
    {
        'Scheme Name': 'Kanya Jagriti Jyoti Scheme',
        'Min Age': 6,
        'Max Age': 18,
        'Category': 'SC, BC',
        'Income Limit': 150000,
        'Occupation': 'Student',
        'Region': 'All Punjab',
        'Gender': 'Female',
        'Documents Required': 'Aadhar Card, School Certificate, Caste Certificate, Income Certificate, Bank Account',
        'Description': 'Financial incentive for SC/BC girl students to continue education and prevent dropouts.',
        'Benefits': 'Rs. 2,000 to Rs. 5,000 annual incentive based on class',
        'Application Deadline': (datetime.now() + timedelta(days=50)).strftime('%Y-%m-%d'),
        'Application URL': 'https://punjab.gov.in/kanya-jagriti',
        'Status': 'Active'
    }
]

def create_schemes_master():
    """Create the schemes_master.xlsx file"""
    df = pd.DataFrame(schemes_data)
    output_file = DATA_DIR / 'schemes_master.xlsx'
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"Created: {output_file}")
    print(f"Total schemes: {len(schemes_data)}")
    return output_file

def create_user_submissions():
    """Create an empty user_submissions.xlsx file"""
    columns = [
        'name', 'age', 'gender', 'category', 'annual_income', 
        'occupation', 'region', 'phone', 'email', 'Submission Time'
    ]
    df = pd.DataFrame(columns=columns)
    output_file = DATA_DIR / 'user_submissions.xlsx'
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"Created: {output_file}")
    return output_file

def main():
    print("="*50)
    print("SchemeScout - Data Seeding Script")
    print("="*50)
    print(f"Data directory: {DATA_DIR}")
    print()
    
    # Create schemes master file
    create_schemes_master()
    
    # Create empty submissions file
    create_user_submissions()
    
    print()
    print("Data seeding complete!")
    print("="*50)

if __name__ == '__main__':
    main()
