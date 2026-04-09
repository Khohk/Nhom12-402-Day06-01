import json
from pathlib import Path
from langchain_core.tools import tool

_DATA = Path(__file__).parent.parent / "data" / "specialties.json"
_SPECIALTIES: list[dict] = json.loads(_DATA.read_text(encoding="utf-8"))

# Khoa chỉ dành cho nữ
_FEMALE_ONLY = {"san-phu-khoa", "trung-tam-benh-ly-tuyen-vu"}

# Khoa chỉ dành cho trẻ em (dưới 18)
_PEDIATRIC = {"nhi"}

# Khoa người lớn không nên gợi ý cho trẻ em
_ADULT_ONLY = {"san-phu-khoa", "nam-khoa"}


@tool
def map_symptoms(symptom_text: str, age: int = 0, gender: str = "") -> list[dict]:
    """
    Gợi ý tối đa 2 chuyên khoa phù hợp dựa trên triệu chứng, tuổi, giới tính.
    Dùng keyword matching + heuristics theo độ tuổi và giới tính.

    Args:
        symptom_text: Mô tả triệu chứng (ngôn ngữ tự nhiên)
        age: Tuổi bệnh nhân (0 = không biết)
        gender: 'nam' | 'nữ' | ''

    Returns:
        List tối đa 2 dict: [{"id": str, "name": str, "score": int, "reason": str}]
        Sắp xếp theo score giảm dần.
        Nếu không match được → trả về Nội tổng quát làm fallback.
    """
    text_lower = symptom_text.lower()
    scores: dict[str, int] = {}

    for spec in _SPECIALTIES:
        spec_id = spec["id"]

        # Filter theo giới tính
        if spec_id in _FEMALE_ONLY and gender == "nam":
            continue
        if spec_id == "nam-khoa" and gender == "nữ":
            continue

        # Filter theo tuổi
        if spec_id in _PEDIATRIC and age >= 18 and age != 0:
            continue
        if spec_id in _ADULT_ONLY and 0 < age < 18:
            continue

        # Keyword matching
        match_count = 0
        for kw in spec.get("keywords", []):
            if kw.lower() in text_lower:
                match_count += 1

        if match_count > 0:
            scores[spec_id] = match_count

    # Sắp xếp và lấy top 2
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]

    if not top:
        # Fallback: Nội tổng quát nếu không match được gì
        fallback = next(
            (s for s in _SPECIALTIES if s["id"] == "kham-suc-khoe-tong-quat-nguoi-lon"),
            None,
        )
        if fallback:
            return [
                {
                    "id": fallback["id"],
                    "name": fallback["name"],
                    "score": 0,
                    "reason": "Không xác định được chuyên khoa rõ ràng — Sức khoẻ tổng quát có thể đánh giá ban đầu.",
                }
            ]
        return []

    result = []
    spec_map = {s["id"]: s for s in _SPECIALTIES}
    for spec_id, score in top:
        spec = spec_map.get(spec_id)
        if spec:
            result.append(
                {
                    "id": spec_id,
                    "name": spec["name"],
                    "score": score,
                    "reason": f"Khớp {score} triệu chứng liên quan.",
                }
            )

    return result