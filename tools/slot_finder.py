import json
from pathlib import Path
from langchain_core.tools import tool

_DATA = Path(__file__).parent.parent / "data" / "slots.json"
_SLOTS: list[dict] = json.loads(_DATA.read_text(encoding="utf-8"))


@tool
def get_slots(doctor_numeric_id: int) -> list[dict]:
    """
    Lấy các khung giờ còn trống của một bác sĩ.

    Args:
        doctor_numeric_id: numeric_id của bác sĩ (lấy từ get_doctors)

    Returns:
        List slot còn chỗ: [{"date", "time", "remaining"}]
        Chỉ trả về slot có remaining > 0, sắp xếp theo time.
        Tối đa 10 slot. Nếu không có → list rỗng.
    """
    available = [
        {"date": s["date"], "time": s["time"], "remaining": s["remaining"]}
        for s in _SLOTS
        if s["doctor_id"] == doctor_numeric_id and s["remaining"] > 0
    ]

    # Sắp xếp theo giờ trong ngày (bỏ qua filter ngày — đây là demo data)
    available.sort(key=lambda x: x["time"])

    return available[:10]