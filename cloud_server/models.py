from pydantic import BaseModel, Field
from typing import List, Optional

class DoctorLogin(BaseModel):
    email: str
    password: str

class DoctorCreate(BaseModel):
    full_name: str
    email: str
    password: str
    status: Optional[str] = 'pending'

class PatientCreate(BaseModel):
    doctor_id: str
    full_name: str
    dob: str
    medical_id: str
    affiliation: str
    diagnosis_notes: str

class PatientReassign(BaseModel):
    doctor_id: str

class TelemetryData(BaseModel):
    patient_id: str
    device_id: str
    sensor_type: str
    value: float
    unit: str
