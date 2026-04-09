import json
from pathlib import Path
from langchain_core.tools import tool

_DATA = Path(__file__).parent.parent / "data" / "red_flags.json"
_RED_FLAGS: list[dict] = json.loads(_DATA.read_text(encoding="utf-8"))


@tool
def check_red_flag(symptom_text: str, age: int = 0, gender: str = "") -> dict:
    """
    Kiểm tra xem triệu chứng có phải red flag nguy hiểm không.
    Chạy bắt buộc trước khi gợi ý chuyên khoa.

    Args:
        symptom_text: Mô tả triệu chứng của bệnh nhân (ngôn ngữ tự nhiên)
        age: Tuổi bệnh nhân (0 = không biết)
        gender: Giới tính ('nam' | 'nữ' | '')

    Returns:
        {
            "is_red_flag": bool,
            "urgent": bool,           # True = cần xử lý ngay hôm nay
            "recommend_er": bool,     # True = nên gọi 115 / vào cấp cứu
            "warning": str,           # Thông báo hiển thị cho user
            "speciality_hint": str,   # Khoa gợi ý nếu không vào cấp cứu
            "matched_id": str         # ID của red flag matched
        }
    """
    text_lower = symptom_text.lower()

    # Tuổi cao → hạ ngưỡng cảnh báo cho một số red flag
    high_risk_age = age >= 55 or age == 0  # không biết tuổi = cẩn thận hơn

    for flag in _RED_FLAGS:
        for pattern in flag["patterns"]:
            if pattern.lower() in text_lower:
                result = {
                    "is_red_flag": True,
                    "urgent": flag.get("urgent", True),
                    "recommend_er": flag.get("recommend_er", False),
                    "warning": flag["warning"],
                    "speciality_hint": flag.get("speciality_hint", ""),
                    "matched_id": flag["id"],
                }

                # Nâng mức độ cảnh báo theo tuổi/giới tính
                if flag["id"] == "cancer-weight-loss" and high_risk_age:
                    result["urgent"] = True
                    result["warning"] += " Đặc biệt quan trọng ở độ tuổi của bạn."

                if flag["id"] == "dvt-warning" and high_risk_age:
                    result["recommend_er"] = True
                    result["warning"] += " Ở độ tuổi này, nguy cơ biến chứng cao hơn."

                # Phụ khoa chỉ áp dụng cho nữ
                if flag["id"] == "cancer-bleeding" and gender == "nam":
                    # Với nam giới bỏ qua triệu chứng xuất huyết âm đạo
                    female_only = ["xuất huyết âm đạo sau mãn kinh"]
                    if all(p in text_lower for p in female_only):
                        continue

                return result

    return {"is_red_flag": False}