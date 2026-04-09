import json
from pathlib import Path
from langchain_core.tools import tool

_DATA = Path(__file__).parent.parent / "data" / "doctors.json"
_DOCTORS: list[dict] = json.loads(_DATA.read_text(encoding="utf-8"))


@tool
def get_doctors(clinic_id: str, speciality_id: str) -> list[dict]:
    """
    Lấy danh sách bác sĩ tại một cơ sở theo chuyên khoa.

    Args:
        clinic_id: ID cơ sở (từ find_clinics)
        speciality_id: ID chuyên khoa

    Returns:
        List bác sĩ: [{"id", "numeric_id", "name", "title"}]
        numeric_id dùng để tra lịch trống trong get_slots.
        Tối đa 5 bác sĩ. Nếu không có → list rỗng.
    """
    result = [
        {
            "id": d["id"],
            "numeric_id": d["numeric_id"],
            "name": d["name"],
            "title": d["title"],
        }
        for d in _DOCTORS
        if d["clinic_id"] == clinic_id and d["speciality_id"] == speciality_id
    ]

    return result[:5]