"""
utils.py
โมดูลกลาง: ตรรกะการให้คะแนน (scoring logic) และฟังก์ชันจัดการข้อมูล (CSV)
ใช้ร่วมกันระหว่างหน้า "แบบประเมิน" และหน้า "สรุปข้อมูล"

หมายเหตุด้านที่มาของเกณฑ์ (สำหรับอ้างอิงในรายงานโปรเจกต์):
- กลุ่มสัญญาณอันตราย (Red Flag) : อ้างอิงหลักการคัดกรองความฉุกเฉิน (Triage) ทั่วไป
- กลุ่มความสามารถในการทำกิจวัตรประจำวัน : แนวคิดจาก ADL/IADL (Activities of Daily Living)
- กลุ่มความเสี่ยงหกล้ม : แนวคิดจากปัจจัยเสี่ยงหกล้มในผู้สูงอายุที่ใช้ในงานประเมินทางเวชศาสตร์ผู้สูงอายุ
  (เช่น ประวัติหกล้ม, การใช้อุปกรณ์ช่วยเดิน, จำนวนยาที่ใช้)
- กลุ่มสภาพจิตใจ : แนวคิดจากการคัดกรองภาวะซึมเศร้าในผู้สูงอายุเบื้องต้น (ปรับคำถามให้เข้าใจง่าย)

*** ข้อควรทำต่อสำหรับโปรเจกต์จริง ***
ควรนำเกณฑ์นี้ไปให้อาจารย์ที่ปรึกษา/ผู้เชี่ยวชาญด้านเวชศาสตร์ผู้สูงอายุตรวจสอบความเหมาะสม (content validity)
ก่อนนำไปเก็บข้อมูลกับกลุ่มตัวอย่างจริง และควรอ้างอิงเครื่องมือมาตรฐานฉบับเต็มในบทที่ 2 (ทบทวนวรรณกรรม)
"""

import os
import csv
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "assessments.csv")

CSV_COLUMNS = [
    "timestamp", "respondent_code", "age", "gender", "assessor_role",
    "red_flag", "adl_score", "fall_risk_score", "mood_score",
    "medication_score", "symptom_score", "total_score", "risk_level",
]

LEVEL_INFO = {
    "emergency": {
        "label": "🚨 ควรไปพบแพทย์ / ห้องฉุกเฉินทันที",
        "color": "red",
        "advice": "พบสัญญาณอันตราย ควรนำผู้สูงอายุส่งโรงพยาบาลทันที หรือโทรแจ้งหน่วยกู้ชีพ 1669",
    },
    "soon": {
        "label": "🟠 ควรนัดพบแพทย์ภายใน 1-2 วัน",
        "color": "orange",
        "advice": "อาการมีความเสี่ยงระดับปานกลาง แนะนำให้นัดหมายพบแพทย์เพื่อตรวจประเมินเพิ่มเติม",
    },
    "monitor": {
        "label": "🟡 เฝ้าระวังอาการที่บ้าน",
        "color": "orange",
        "advice": "อาการยังไม่รุนแรง ควรสังเกตอาการต่อเนื่อง 24-48 ชั่วโมง หากแย่ลงให้รีบไปพบแพทย์",
    },
    "low": {
        "label": "🟢 ยังไม่มีความจำเป็นต้องพบแพทย์",
        "color": "green",
        "advice": "ความเสี่ยงต่ำ ดูแลตามอาการที่บ้านได้ และติดตามอาการอย่างสม่ำเสมอ",
    },
}


def ensure_data_file():
    """สร้างโฟลเดอร์/ไฟล์ CSV ถ้ายังไม่มี"""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)


def compute_scores(
    red_flags,
    adl_items,       # dict: {"อาบน้ำ": True/False (True = ทำเองไม่ได้), ...}
    fall_history,     # str
    uses_walking_aid,
    multiple_meds,    # ใช้ยา >= 5 ชนิด/วัน
    dizziness,
    mood_items,       # dict: {"เบื่อหน่ายไม่อยากทำกิจกรรม": True/False, ...}
    missed_meds,
    side_effect,
    pain_level,
    fever,
    symptom_days,
    chronic_worsen,
):
    """คำนวณคะแนนย่อยแต่ละกลุ่มและคะแนนรวม คืนค่าเป็น dict"""

    has_red_flag = any(rf != "ไม่มีอาการข้างต้น" for rf in red_flags)
    if has_red_flag:
        return {
            "adl_score": None, "fall_risk_score": None, "mood_score": None,
            "medication_score": None, "symptom_score": None,
            "total_score": 100, "risk_level": "emergency",
        }

    # 1) ADL/IADL-lite: ยิ่งทำเองไม่ได้หลายอย่าง ยิ่งเสี่ยง
    adl_score = sum(5 for v in adl_items.values() if v)

    # 2) ความเสี่ยงหกล้ม
    fall_risk_score = 0
    if fall_history == "หกล้มแต่ไม่บาดเจ็บ":
        fall_risk_score += 10
    elif fall_history == "หกล้มและมีอาการบาดเจ็บ/ปวด":
        fall_risk_score += 20
    fall_risk_score += 8 if uses_walking_aid else 0
    fall_risk_score += 8 if multiple_meds else 0
    fall_risk_score += 6 if dizziness else 0

    # 3) สภาพจิตใจ/อารมณ์ (คัดกรองเบื้องต้น)
    mood_score = sum(4 for v in mood_items.values() if v)

    # 4) การใช้ยา
    medication_score = (8 if missed_meds else 0) + (10 if side_effect else 0)

    # 5) อาการทั่วไป/โรคเรื้อรัง
    symptom_score = (
        pain_level * 2
        + (8 if fever else 0)
        + min(symptom_days, 10) * 1.2
        + (15 if chronic_worsen else 0)
    )

    total = adl_score + fall_risk_score + mood_score + medication_score + symptom_score
    total = round(total, 1)

    if total >= 45:
        level = "soon"
    elif total >= 20:
        level = "monitor"
    else:
        level = "low"

    return {
        "adl_score": adl_score,
        "fall_risk_score": fall_risk_score,
        "mood_score": mood_score,
        "medication_score": medication_score,
        "symptom_score": round(symptom_score, 1),
        "total_score": total,
        "risk_level": level,
    }


def save_record(record: dict):
    """บันทึกผลการประเมิน 1 รายการลง CSV"""
    ensure_data_file()
    with open(DATA_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writerow(record)


def load_records():
    """โหลดข้อมูลทั้งหมดเป็น list of dict"""
    ensure_data_file()
    with open(DATA_FILE, "r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def new_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
