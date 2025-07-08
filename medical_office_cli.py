#!/usr/bin/env python3
"""
Medical Office CLI - Basic Data Entry System
A simple command-line interface for collecting basic medical office data.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional


class MedicalOfficeData:
    def __init__(self):
        self.data = {
            "patient_info": {},
            "vital_signs": {},
            "symptoms": [],
            "medical_history": {},
            "medications": [],
            "allergies": [],
            "timestamp": None
        }
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        return len(digits_only) >= 10
    
    def get_patient_info(self):
        """Collect basic patient information"""
        print("\n" + "="*50)
        print("PATIENT INFORMATION")
        print("="*50)
        
        # First Name
        while True:
            first_name = input("First Name: ").strip()
            if first_name:
                break
            print("First name is required.")
        
        # Last Name
        while True:
            last_name = input("Last Name: ").strip()
            if last_name:
                break
            print("Last name is required.")
        
        # Date of Birth
        while True:
            dob = input("Date of Birth (MM/DD/YYYY): ").strip()
            try:
                datetime.strptime(dob, '%m/%d/%Y')
                break
            except ValueError:
                print("Please enter date in MM/DD/YYYY format.")
        
        # Gender
        while True:
            gender = input("Gender (M/F/Other): ").strip().upper()
            if gender in ['M', 'F', 'OTHER']:
                break
            print("Please enter M, F, or Other.")
        
        # Phone Number
        while True:
            phone = input("Phone Number: ").strip()
            if self.validate_phone(phone):
                break
            print("Please enter a valid phone number (at least 10 digits).")
        
        # Email (optional)
        email = ""
        email_input = input("Email (optional): ").strip()
        if email_input:
            while not self.validate_email(email_input):
                print("Please enter a valid email address.")
                email_input = input("Email (optional): ").strip()
                if not email_input:
                    break
            email = email_input
        
        # Emergency Contact
        emergency_contact = input("Emergency Contact Name: ").strip()
        emergency_phone = ""
        if emergency_contact:
            while True:
                emergency_phone = input("Emergency Contact Phone: ").strip()
                if self.validate_phone(emergency_phone):
                    break
                print("Please enter a valid phone number for emergency contact.")
        
        self.data["patient_info"] = {
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": dob,
            "gender": gender,
            "phone": phone,
            "email": email,
            "emergency_contact": emergency_contact,
            "emergency_phone": emergency_phone
        }
    
    def get_vital_signs(self):
        """Collect vital signs"""
        print("\n" + "="*50)
        print("VITAL SIGNS")
        print("="*50)
        
        # Blood Pressure
        while True:
            bp_input = input("Blood Pressure (e.g., 120/80): ").strip()
            if re.match(r'^\d{2,3}/\d{2,3}$', bp_input):
                break
            if not bp_input:
                bp_input = "Not recorded"
                break
            print("Please enter blood pressure in format XXX/YY or leave blank.")
        
        # Temperature
        while True:
            temp_input = input("Temperature (°F, e.g., 98.6): ").strip()
            if not temp_input:
                temp_input = "Not recorded"
                break
            try:
                temp = float(temp_input)
                if 90 <= temp <= 110:
                    break
                else:
                    print("Temperature should be between 90°F and 110°F.")
            except ValueError:
                print("Please enter a valid temperature or leave blank.")
        
        # Weight
        while True:
            weight_input = input("Weight (lbs): ").strip()
            if not weight_input:
                weight_input = "Not recorded"
                break
            try:
                weight = float(weight_input)
                if weight > 0:
                    break
                else:
                    print("Weight must be a positive number.")
            except ValueError:
                print("Please enter a valid weight or leave blank.")
        
        # Height
        while True:
            height_input = input("Height (inches or ft'in\", e.g., 68 or 5'8\"): ").strip()
            if not height_input:
                height_input = "Not recorded"
                break
            # Check for feet'inches format
            if "'" in height_input:
                try:
                    parts = height_input.replace('"', '').split("'")
                    feet = int(parts[0])
                    inches = int(parts[1]) if len(parts) > 1 and parts[1] else 0
                    total_inches = feet * 12 + inches
                    if 24 <= total_inches <= 96:
                        height_input = f"{total_inches} inches ({feet}'{inches}\")"
                        break
                    else:
                        print("Height should be reasonable (2' - 8').")
                except:
                    print("Please enter height as inches or ft'in\" format.")
            else:
                try:
                    height = float(height_input)
                    if 24 <= height <= 96:
                        break
                    else:
                        print("Height should be between 24 and 96 inches.")
                except ValueError:
                    print("Please enter a valid height or leave blank.")
        
        # Heart Rate
        while True:
            hr_input = input("Heart Rate (bpm): ").strip()
            if not hr_input:
                hr_input = "Not recorded"
                break
            try:
                hr = int(hr_input)
                if 30 <= hr <= 200:
                    break
                else:
                    print("Heart rate should be between 30 and 200 bpm.")
            except ValueError:
                print("Please enter a valid heart rate or leave blank.")
        
        self.data["vital_signs"] = {
            "blood_pressure": bp_input,
            "temperature": temp_input,
            "weight": weight_input,
            "height": height_input,
            "heart_rate": hr_input
        }
    
    def get_symptoms(self):
        """Collect symptoms and chief complaint"""
        print("\n" + "="*50)
        print("SYMPTOMS & CHIEF COMPLAINT")
        print("="*50)
        
        print("Please describe the main reason for today's visit:")
        chief_complaint = input("Chief Complaint: ").strip()
        
        print("\nAny additional symptoms? (Enter one per line, press Enter twice when done)")
        symptoms = []
        if chief_complaint:
            symptoms.append(chief_complaint)
        
        while True:
            symptom = input("Symptom: ").strip()
            if not symptom:
                break
            symptoms.append(symptom)
        
        # Pain scale if applicable
        pain_level = ""
        if any(word in ' '.join(symptoms).lower() for word in ['pain', 'hurt', 'ache', 'sore']):
            while True:
                pain_input = input("Pain level (0-10 scale, 0=no pain, 10=worst pain): ").strip()
                if not pain_input:
                    break
                try:
                    pain = int(pain_input)
                    if 0 <= pain <= 10:
                        pain_level = str(pain)
                        break
                    else:
                        print("Pain level should be between 0 and 10.")
                except ValueError:
                    print("Please enter a number between 0 and 10.")
        
        self.data["symptoms"] = symptoms
        if pain_level:
            self.data["pain_level"] = pain_level
    
    def get_medical_history(self):
        """Collect basic medical history"""
        print("\n" + "="*50)
        print("MEDICAL HISTORY")
        print("="*50)
        
        # Previous surgeries
        print("Any previous surgeries? (Enter one per line, press Enter twice when done)")
        surgeries = []
        while True:
            surgery = input("Surgery: ").strip()
            if not surgery:
                break
            surgeries.append(surgery)
        
        # Chronic conditions
        print("\nAny chronic conditions or ongoing health issues?")
        conditions = []
        while True:
            condition = input("Condition: ").strip()
            if not condition:
                break
            conditions.append(condition)
        
        # Family history
        family_history = input("\nSignificant family medical history: ").strip()
        
        # Smoking/drinking
        smoking = input("Smoking status (Never/Former/Current): ").strip()
        alcohol = input("Alcohol use (None/Occasional/Regular): ").strip()
        
        self.data["medical_history"] = {
            "surgeries": surgeries,
            "chronic_conditions": conditions,
            "family_history": family_history,
            "smoking_status": smoking,
            "alcohol_use": alcohol
        }
    
    def get_medications_allergies(self):
        """Collect current medications and allergies"""
        print("\n" + "="*50)
        print("MEDICATIONS & ALLERGIES")
        print("="*50)
        
        # Current medications
        print("Current medications (include dosage if known):")
        medications = []
        while True:
            med = input("Medication: ").strip()
            if not med:
                break
            medications.append(med)
        
        # Allergies
        print("\nKnown allergies (medications, foods, environmental):")
        allergies = []
        while True:
            allergy = input("Allergy: ").strip()
            if not allergy:
                break
            allergies.append(allergy)
        
        self.data["medications"] = medications
        self.data["allergies"] = allergies
    
    def display_summary(self):
        """Display a summary of entered data"""
        print("\n" + "="*50)
        print("DATA SUMMARY")
        print("="*50)
        
        # Patient Info
        print(f"Patient: {self.data['patient_info']['first_name']} {self.data['patient_info']['last_name']}")
        print(f"DOB: {self.data['patient_info']['date_of_birth']}")
        print(f"Phone: {self.data['patient_info']['phone']}")
        
        # Vital Signs
        print(f"\nVital Signs:")
        for key, value in self.data['vital_signs'].items():
            if value and value != "Not recorded":
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Symptoms
        if self.data['symptoms']:
            print(f"\nSymptoms:")
            for symptom in self.data['symptoms']:
                print(f"  - {symptom}")
        
        # Medications
        if self.data['medications']:
            print(f"\nCurrent Medications:")
            for med in self.data['medications']:
                print(f"  - {med}")
        
        # Allergies
        if self.data['allergies']:
            print(f"\nAllergies:")
            for allergy in self.data['allergies']:
                print(f"  - {allergy}")
    
    def save_data(self, filename: str = None):
        """Save data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            first_name = self.data['patient_info'].get('first_name', 'Unknown')
            last_name = self.data['patient_info'].get('last_name', 'Patient')
            patient_name = f"{first_name}_{last_name}"
            filename = f"medical_data_{patient_name}_{timestamp}.json"
        
        self.data["timestamp"] = datetime.now().isoformat()
        
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        print(f"\nData saved to: {filename}")
        return filename


def main():
    """Main CLI interface"""
    print("="*50)
    print("MEDICAL OFFICE DATA ENTRY SYSTEM")
    print("="*50)
    print("This system collects basic medical office information.")
    print("Press Ctrl+C at any time to exit.\n")
    
    try:
        medical_data = MedicalOfficeData()
        
        # Collect all data
        medical_data.get_patient_info()
        medical_data.get_vital_signs()
        medical_data.get_symptoms()
        medical_data.get_medical_history()
        medical_data.get_medications_allergies()
        
        # Show summary
        medical_data.display_summary()
        
        # Save option
        print("\n" + "="*50)
        save_choice = input("Save this data? (y/N): ").strip().lower()
        if save_choice in ['y', 'yes']:
            filename = medical_data.save_data()
            print("Data collection complete!")
        else:
            print("Data not saved. Session complete!")
    
    except KeyboardInterrupt:
        print("\n\nSession cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()