"""
app.py — หน้าแรก (Home) ของระบบ
รันด้วย: streamlit run app.py
"""

import streamlit as st
from utils import ensure_data_file, load_records

st.set_page_config(
    page_title="ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ",
    page_icon="🩺",
    layout="centered",
)

ensure_data_file()

st.title("🩺 ระบบประเมินการตัดสินใจไปพบแพทย์ของผู้สูงอายุ")
st.caption("โครงงานปี 4 — Elderly Medical Consultation Decision Support System")

st.markdown(
    """
เว็บแอปนี้ช่วยประเมินเบื้องต้นว่าอาการของผู้สูงอายุอยู่ในระดับใด และควรตัดสินใจอย่างไร
ระหว่าง **ไปพบแพทย์ทันที / นัดพบแพทย์เร็วๆ นี้ / เฝ้าระวังอาการที่บ้าน**

เกณฑ์การให้คะแนนออกแบบโดยอิงแนวคิดจาก:
- การคัดกรองสัญญาณอันตราย (Red Flag / Triage)
- ความสามารถในการทำกิจวัตรประจำวัน (ADL/IADL)
- ปัจจัยเสี่ยงการหกล้มในผู้สูงอายุ
- การคัดกรองภาวะอารมณ์/ซึมเศร้าเบื้องต้น
- ปัญหาการใช้ยาและอาการทั่วไป

👉 ใช้เมนูด้านซ้าย เลือก **"แบบประเมิน"** เพื่อเริ่มกรอกข้อมูล
หรือ **"สรุปข้อมูล"** เพื่อดูสถิติจากการเก็บข้อมูลนำร่อง (Pilot Data)
"""
)

st.warning(
    "⚠️ เครื่องมือนี้จัดทำเพื่อการศึกษา/โครงงานวิจัยเท่านั้น ไม่สามารถใช้แทนคำวินิจฉัยของแพทย์ได้ "
    "หากมีอาการรุนแรงหรือฉุกเฉิน ให้โทร 1669 หรือไปโรงพยาบาลทันที"
)

st.divider()

records = load_records()
col1, col2 = st.columns(2)
col1.metric("จำนวนแบบประเมินที่เก็บได้ (Pilot)", f"{len(records)} ชุด")
if records:
    emergency_count = sum(1 for r in records if r["risk_level"] == "emergency")
    col2.metric("จำนวนที่พบสัญญาณอันตราย", f"{emergency_count} ราย")

st.divider()
st.caption(
    "พัฒนาด้วย Streamlit | โครงสร้างข้อมูลถูกเก็บไว้ที่ data/assessments.csv "
    "สำหรับนำไปวิเคราะห์ในบทที่ 4 ของรายงานโครงงาน"
)
