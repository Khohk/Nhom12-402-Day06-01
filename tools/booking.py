"""Appointment booking utilities."""

def book_appointment(patient_info, doctor_id, slot_id):
    """Create a booking for the patient."""
    return {
        "status": "success",
        "patient": patient_info,
        "doctor_id": doctor_id,
        "slot_id": slot_id,
    }
