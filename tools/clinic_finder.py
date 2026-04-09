import json
from pathlib import Path
from langchain_core.tools import tool

_DATA = Path(__file__).parent.parent / "data" / "hospitals.json"
_HOSPITALS: list[dict] = json.loads(_DATA.read_text(encoding="utf-8"))


@tool
def find_clinics(speciality_id: str, user_location: str = "") -> list[dict]:
    """
    Tìm các cơ sở Vinmec có chuyên khoa yêu cầu.
    LLM sẽ dùng user_location để suy ra cơ sở nào gần nhất.

    Args:
        speciality_id: ID chuyên khoa cần tìm (từ map_symptoms hoặc user chọn)
        user_location: Địa chỉ / khu vực của bệnh nhân (VD: "Cầu Giấy, Hà Nội")

    Returns:
        List các cơ sở phù hợp: [{"id", "name", "address", "has_speciality": True}]
        Trả về tối đa 5 cơ sở. Nếu không có cơ sở nào → list rỗng.
    """
    result = []
    for hospital in _HOSPITALS:
        if speciality_id in hospital.get("specialities", []):
            result.append(
                {
                    "id": hospital["id"],
                    "name": hospital["name"],
                    "address": hospital["address"],
                    "has_speciality": True,
                }
            )

    # Sắp xếp ưu tiên: Hà Nội lên trên nếu user ở Hà Nội
    if user_location:
        loc_lower = user_location.lower()
        hanoi_keywords = ["hà nội", "ha noi", "hn", "hoàn kiếm", "cầu giấy",
                          "đống đa", "hai bà trưng", "hoàng mai", "thanh xuân",
                          "nam từ liêm", "bắc từ liêm", "long biên", "gia lâm"]
        hcm_keywords = ["hồ chí minh", "ho chi minh", "hcm", "sài gòn", "sai gon",
                        "quận 1", "quận 2", "quận 3", "bình thạnh", "thủ đức"]

        def priority(h):
            if any(kw in loc_lower for kw in hanoi_keywords):
                return 0 if "hà nội" in h["address"].lower() or "times-city" in h["id"] or "smart-city" in h["id"] else 1
            if any(kw in loc_lower for kw in hcm_keywords):
                return 0 if "hồ chí minh" in h["address"].lower() or "central-park" in h["id"] else 1
            return 1

        result.sort(key=priority)

    return result[:5]