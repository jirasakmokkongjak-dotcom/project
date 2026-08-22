"""
pages/2_📊_สรุปข้อมูล.py
หน้าสรุปข้อมูล/สถิติจากการเก็บข้อมูลนำร่อง (Pilot Data)
"""

import streamlit as st
import pandas as pd
from utils import load_records, DATA_FILE

st.set_page_config(page_title="สรุปข้อมูล", page_icon="📊", layout="centered")

st.title("📊 สรุปข้อมูลจากการเก็บข้อมูลนำร่อง (Pilot Data)")

records = load_records()

if not records:
    st.info("ยังไม่มีข้อมูล — กรุณาไปที่หน้า 'แบบประเมิน' เพื่อเริ่มเก็บข้อมูล")
    st.stop()

df = pd.DataFrame(records)

# แปลงชนิดข้อมูลตัวเลข
numeric_cols = ["age", "adl_score", "fall_risk_score", "mood_score",
                 "medication_score", "symptom_score", "total_score"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

st.subheader("ภาพรวม")
col1, col2, col3 = st.columns(3)
col1.metric("จำนวนกลุ่มตัวอย่างทั้งหมด", f"{len(df)} คน")
col2.metric("อายุเฉลี่ย", f"{df['age'].mean():.1f} ปี")
emergency_pct = (df["risk_level"] == "emergency").mean() * 100
col3.metric("พบสัญญาณอันตราย", f"{emergency_pct:.1f}%")

st.divider()

st.subheader("การกระจายตัวของระดับความเสี่ยง")
level_labels = {
    "emergency": "ฉุกเฉิน",
    "soon": "ควรพบแพทย์เร็วๆ นี้",
    "monitor": "เฝ้าระวังที่บ้าน",
    "low": "ยังไม่จำเป็น",
}
level_counts = df["risk_level"].map(level_labels).value_counts()
st.bar_chart(level_counts)

st.divider()

st.subheader("คะแนนความเสี่ยงรวม แยกตามช่วงอายุ")
df["age_group"] = pd.cut(
    df["age"],
    bins=[59, 69, 79, 89, 120],
    labels=["60-69 ปี", "70-79 ปี", "80-89 ปี", "90 ปีขึ้นไป"],
)
avg_by_age = df.groupby("age_group", observed=True)["total_score"].mean()
st.bar_chart(avg_by_age)

st.divider()

st.subheader("แนวโน้มจำนวนการประเมินตามช่วงเวลา")
df["date"] = pd.to_datetime(df["timestamp"], errors="coerce").dt.date
daily_count = df.groupby("date").size()
st.line_chart(daily_count)

st.divider()

st.subheader("คะแนนเฉลี่ยแยกตามหมวด (เฉพาะกรณีไม่ฉุกเฉิน)")
non_emergency = df[df["risk_level"] != "emergency"]
if not non_emergency.empty:
    category_avg = non_emergency[
        ["adl_score", "fall_risk_score", "mood_score", "medication_score", "symptom_score"]
    ].mean()
    category_avg.index = ["ADL", "ความเสี่ยงหกล้ม", "สภาพจิตใจ", "การใช้ยา", "อาการทั่วไป"]
    st.bar_chart(category_avg)
else:
    st.caption("ยังไม่มีข้อมูลกรณีที่ไม่ฉุกเฉินเพียงพอสำหรับกราฟนี้")

st.divider()

st.subheader("ตารางข้อมูลดิบทั้งหมด")
st.dataframe(df, use_container_width=True)

with open(DATA_FILE, "rb") as f:
    st.download_button(
        "⬇️ ดาวน์โหลดข้อมูลเป็นไฟล์ CSV",
        data=f,
        file_name="elderly_assessment_data.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.caption(
    "💡 นำกราฟและตารางเหล่านี้ไปใช้ประกอบการเขียนบทที่ 4 (ผลการดำเนินงาน) "
    "ของรายงานโครงงานได้โดยตรง"
)
