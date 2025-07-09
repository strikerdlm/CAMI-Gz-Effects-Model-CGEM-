# Medical Office CLI - Basic Data Entry System

A simple command-line interface for collecting basic medical office data during patient visits.

## Features

This CLI tool collects the following basic medical information:

- **Patient Information**: Name, date of birth, contact details, emergency contact
- **Vital Signs**: Blood pressure, temperature, weight, height, heart rate
- **Symptoms**: Chief complaint, additional symptoms, pain level assessment
- **Medical History**: Previous surgeries, chronic conditions, family history, lifestyle factors
- **Medications & Allergies**: Current medications and known allergies

## Requirements

- Python 3.6 or higher
- No external dependencies required (uses only Python standard library)

## Usage

1. Make the script executable (optional):
   ```bash
   chmod +x medical_office_cli.py
   ```

2. Run the application:
   ```bash
   python3 medical_office_cli.py
   ```

3. Follow the interactive prompts to enter patient data

4. Review the summary and choose to save the data as a JSON file

## Data Validation

The tool includes validation for:
- Email format
- Phone number format (minimum 10 digits)
- Date of birth format (MM/DD/YYYY)
- Vital sign ranges (reasonable medical values)
- Pain scale (0-10)

## Data Storage

- Data is saved as JSON files with timestamps
- Files are named: `medical_data_{FirstName}_{LastName}_{timestamp}.json`
- All entered information is preserved in structured format

## Navigation

- Press `Enter` on empty fields to skip optional information
- Press `Ctrl+C` at any time to exit the application
- Most fields allow empty input except required patient identification

## Sample Data Structure

```json
{
  "patient_info": {
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "01/15/1980",
    "gender": "M",
    "phone": "555-123-4567",
    "email": "john.doe@email.com"
  },
  "vital_signs": {
    "blood_pressure": "120/80",
    "temperature": "98.6",
    "weight": "175",
    "height": "70 inches (5'10\")"
  },
  "symptoms": ["Headache", "Fatigue"],
  "medications": ["Ibuprofen 200mg"],
  "allergies": ["Penicillin"]
}
```

## Security Note

This tool is designed for basic data collection and does not include encryption or HIPAA compliance features. For production medical use, additional security measures would be required.
