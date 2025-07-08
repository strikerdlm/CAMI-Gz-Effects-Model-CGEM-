#!/usr/bin/env python3
"""
Demo example showing the structure of data collected by the Medical Office CLI
"""

import json
from datetime import datetime

def create_sample_data():
    """Create sample medical office data to demonstrate the structure"""
    
    sample_data = {
        "patient_info": {
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": "03/15/1985",
            "gender": "F",
            "phone": "555-987-6543",
            "email": "jane.smith@email.com",
            "emergency_contact": "John Smith",
            "emergency_phone": "555-987-6544"
        },
        "vital_signs": {
            "blood_pressure": "118/75",
            "temperature": "98.4",
            "weight": "140",
            "height": "65 inches (5'5\")",
            "heart_rate": "72"
        },
        "symptoms": [
            "Persistent cough for 3 days",
            "Mild fever",
            "Fatigue"
        ],
        "pain_level": "3",
        "medical_history": {
            "surgeries": [
                "Appendectomy (2010)"
            ],
            "chronic_conditions": [
                "Seasonal allergies"
            ],
            "family_history": "Diabetes (mother), Heart disease (father)",
            "smoking_status": "Never",
            "alcohol_use": "Occasional"
        },
        "medications": [
            "Birth control pill (daily)",
            "Claritin 10mg (as needed)"
        ],
        "allergies": [
            "Shellfish",
            "Latex"
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    return sample_data

def display_sample_data():
    """Display the sample data in a formatted way"""
    
    data = create_sample_data()
    
    print("="*60)
    print("SAMPLE MEDICAL OFFICE DATA")
    print("="*60)
    
    # Patient Information
    print("\n📋 PATIENT INFORMATION:")
    patient = data['patient_info']
    print(f"   Name: {patient['first_name']} {patient['last_name']}")
    print(f"   DOB: {patient['date_of_birth']}")
    print(f"   Gender: {patient['gender']}")
    print(f"   Phone: {patient['phone']}")
    print(f"   Email: {patient['email']}")
    print(f"   Emergency Contact: {patient['emergency_contact']} ({patient['emergency_phone']})")
    
    # Vital Signs
    print("\n🩺 VITAL SIGNS:")
    vitals = data['vital_signs']
    for key, value in vitals.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Symptoms
    print("\n🤒 SYMPTOMS & COMPLAINTS:")
    for symptom in data['symptoms']:
        print(f"   • {symptom}")
    if 'pain_level' in data:
        print(f"   Pain Level: {data['pain_level']}/10")
    
    # Medical History
    print("\n📋 MEDICAL HISTORY:")
    history = data['medical_history']
    if history['surgeries']:
        print("   Previous Surgeries:")
        for surgery in history['surgeries']:
            print(f"     • {surgery}")
    
    if history['chronic_conditions']:
        print("   Chronic Conditions:")
        for condition in history['chronic_conditions']:
            print(f"     • {condition}")
    
    print(f"   Family History: {history['family_history']}")
    print(f"   Smoking Status: {history['smoking_status']}")
    print(f"   Alcohol Use: {history['alcohol_use']}")
    
    # Medications
    print("\n💊 CURRENT MEDICATIONS:")
    for med in data['medications']:
        print(f"   • {med}")
    
    # Allergies
    print("\n⚠️  ALLERGIES:")
    for allergy in data['allergies']:
        print(f"   • {allergy}")
    
    print(f"\n📅 Data collected: {data['timestamp']}")
    print("="*60)

def save_sample_json():
    """Save sample data to a JSON file"""
    data = create_sample_data()
    filename = "sample_medical_data.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Sample data saved to: {filename}")
    return filename

if __name__ == "__main__":
    print("Medical Office CLI - Demo Example")
    print("This shows the type of data collected by the CLI tool.\n")
    
    display_sample_data()
    save_sample_json()
    
    print("\n" + "="*60)
    print("To use the interactive CLI tool, run:")
    print("python3 medical_office_cli.py")
    print("="*60)