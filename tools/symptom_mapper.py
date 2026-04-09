import json
import re
from pathlib import Path
from langchain_core.tools import tool
from unidecode import unidecode

_DATA = Path(__file__).parent.parent / "data" / "specialties.json"
_SPECIALTIES: list[dict] = json.loads(_DATA.read_text(encoding="utf-8"))

_FEMALE_ONLY = {"san-phu-khoa", "trung-tam-benh-ly-tuyen-vu"}
_PEDIATRIC = {"nhi"}
_ADULT_ONLY = {"san-phu-khoa"}
_EXCLUDE_FROM_AUTO = {"trung-tam-ung-buou", "tiem-chung-vac-xin", "y-hoc-co-truyen"}


def _normalize(text: str) -> str:
    return unidecode(text.lower())


def _match(keyword: str, text_norm: str) -> bool:
    kw_norm = _normalize(keyword)
    if len(kw_norm.replace(" ", "")) <= 3:
        return bool(re.search(r'\b' + re.escape(kw_norm) + r'\b', text_norm))
    return kw_norm in text_norm


@tool
def map_symptoms(symptom_text: str, age: int = 0, gender: str = "") -> list[dict]:
    """
    Gợi ý tối đa 2 chuyên khoa phù hợp dựa trên triệu chứng, tuổi, giới tính.
    Hỗ trợ input có dấu và không dấu.

    Args:
        symptom_text: Mô tả triệu chứng (ngôn ngữ tự nhiên)
        age: Tuổi bệnh nhân (0 = không biết)
        gender: 'nam' | 'nữ' | ''

    Returns:
        List tối đa 2 dict: [{"id", "name", "score", "reason"}]
        Nếu không match → trả về Nội tổng quát làm fallback.
    """
    text_norm = _normalize(symptom_text)
    scores: dict[str, int] = {}

    for spec in _SPECIALTIES:
        spec_id = spec["id"]

        if spec_id in _EXCLUDE_FROM_AUTO:
            continue
        if spec_id in _FEMALE_ONLY and gender == "nam":
            continue
        if spec_id == "nam-khoa" and gender == "nữ":
            continue
        if spec_id in _PEDIATRIC and age >= 18 and age != 0:
            continue
        if spec_id in _ADULT_ONLY and 0 < age < 18:
            continue

        match_count = sum(
            1 for kw in spec.get("keywords", [])
            if _match(kw, text_norm)
        )
        if match_count > 0:
            scores[spec_id] = match_count

    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]

    if not top:
        fallback = next(
            (s for s in _SPECIALTIES if s["id"] == "kham-suc-khoe-tong-quat-nguoi-lon"),
            None,
        )
        if fallback:
            return [{
                "id": fallback["id"],
                "name": fallback["name"],
                "score": 0,
                "reason": "Không xác định được chuyên khoa rõ ràng — Sức khoẻ tổng quát sẽ đánh giá ban đầu.",
            }]
        return []

    spec_map = {s["id"]: s for s in _SPECIALTIES}
    return [
        {
            "id": spec_id,
            "name": spec_map[spec_id]["name"],
            "score": score,
            "reason": f"Khớp {score} triệu chứng liên quan.",
        }
        for spec_id, score in top
        if spec_id in spec_map
    ]