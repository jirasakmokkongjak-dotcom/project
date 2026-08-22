"""
pages/1_📝_แบบประเมิน.py
หน้าแบบประเมิน — กรอกข้อมูล คำนวณคะแนน และบันทึกลง data/assessments.csv
"""

import streamlit as st
from utils import compute_scores, save_record, new_timestamp, LEVEL_INFO

st.set_page_config(page_title="แบบประเมิน", page_icon="📝", layout="centered")

st.title("📝 แบบประเมินความเสี่ยงและการตัดสินใจไปพบแพทย์")

with st.expander("ℹ️ คำชี้แจงก่อนทำแบบประเมิน (สำหรับผู้เก็บข้อมูลนำร่อง)", expanded=False):
    st.write(
        """
        ข้อมูลที่กรอกจะถูกบันทึกไว้เพื่อวัตถุประสงค์ทางการศึกษา/วิจัยของโครงงานเท่านั้น
        กรุณาใช้ **รหัสผู้ตอบ** แทนชื่อจริง (เช่น P001, P002) เพื่อรักษาความเป็นส่วนตัว
        ของผู้ให้ข้อมูล และควรแจ้งวัตถุประสงค์ให้ผู้ตอบทราบและยินยอมก่อนเก็บข้อมูลทุกครั้ง
        """
    )

st.info(
    "⚠️ แบบประเมินนี้ใช้เพื่อการศึกษาเท่านั้น ไม่สามารถใช้แทนคำวินิจฉัยของแพทย์ได้ "
    "หากมีอาการรุนแรง/ฉุกเฉิน ให้โทร 1669 หรือไปโรงพยาบาลทันที"
)

st.divider()

with st.form("assessment_form"):

    st.subheader("ข้อมูลทั่วไป")
    col1, col2 = st.columns(2)
    with col1:
        respondent_code = st.text_input("รหัสผู้ตอบ (เช่น P001)", "")
        age = st.number_input("อายุ (ปี)", min_value=60, max_value=120, value=70)
    with col2:
        gender = st.selectbox("เพศ", ["ชาย", "หญิง", "ไม่ระบุ"])
        assessor_role = st.selectbox("ผู้กรอกแบบประเมิน", ["ผู้สูงอายุตอบเอง", "ผู้ดูแล/ญาติ", "อสม./เจ้าหน้าที่"])

    st.divider()
    st.subheader("1️⃣ สัญญาณอันตราย (Red Flag Symptoms)")
    red_flags = st.multiselect(
        "เลือกอาการที่พบ (ถ้ามี)",
        [
            "เจ็บแน่นหน้าอก / หายใจลำบากเฉียบพลัน",
            "พูดไม่ชัด / แขนขาอ่อนแรงครึ่งซีกเฉียบพลัน (สงสัยอัมพาต)",
            "หมดสติ หรือซึมลงกะทันหัน",
            "มีเลือดออกไม่หยุด",
            "ไข้สูงมากกว่า 39°C ร่วมกับซึม/สับสน",
            "หกล้มศีรษะกระแทกพื้น",
            "ไม่มีอาการข้างต้น",
        ],
        default=["ไม่มีอาการข้างต้น"],
    )

    st.subheader("2️⃣ ความสามารถในการทำกิจวัตรประจำวัน (ADL/IADL แบบย่อ)")
    st.caption("เลือกกิจกรรมที่ **ทำเองไม่ได้ หรือต้องมีคนช่วยเหลือ** ในช่วง 1 สัปดาห์ที่ผ่านมา")
    adl_labels = ["อาบน้ำ/แต่งตัว", "รับประทานอาหาร", "เข้าห้องน้ำ", "ลุกนั่ง/เดินภายในบ้าน", "ทำกับข้าว/จัดการเรื่องเงินเอง"]
    adl_selected = st.multiselect("กิจกรรมที่ทำเองไม่ได้", adl_labels)
    adl_items = {label: (label in adl_selected) for label in adl_labels}

    st.subheader("3️⃣ ความเสี่ยงการหกล้ม")
    fall_history = st.radio(
        "ประวัติการหกล้มในช่วง 1 เดือนที่ผ่านมา",
        ["ไม่มี", "หกล้มแต่ไม่บาดเจ็บ", "หกล้มและมีอาการบาดเจ็บ/ปวด"],
        horizontal=True,
    )
    col3, col4, col5 = st.columns(3)
    with col3:
        uses_walking_aid = st.checkbox("ใช้ไม้เท้า/walker")
    with col4:
        multiple_meds = st.checkbox("ใช้ยาตั้งแต่ 5 ชนิดขึ้นไป/วัน")
    with col5:
        dizziness = st.checkbox("มีอาการเวียนศีรษะบ่อย")

    st.subheader("4️⃣ สภาพจิตใจและอารมณ์ (คัดกรองเบื้องต้น)")
    st.caption("เลือกข้อที่ตรงกับความรู้สึกใน **2 สัปดาห์ที่ผ่านมา**")
    mood_labels = [
        "รู้สึกเบื่อหน่าย ไม่อยากทำกิจกรรมที่เคยชอบ",
        "รู้สึกเหงา ไม่มีใครพูดคุยด้วย",
        "รู้สึกว่าตัวเองไม่มีคุณค่า/เป็นภาระ",
        "หลงลืมง่ายกว่าเดิมอย่างชัดเจน",
        "นอนไม่หลับ/นอนมากผิดปกติ",
    ]
    mood_selected = st.multiselect("อาการที่ตรงกับความรู้สึก", mood_labels)
    mood_items = {label: (label in mood_selected) for label in mood_labels}

    st.subheader("5️⃣ การใช้ยา")
    col6, col7 = st.columns(2)
    with col6:
        missed_meds = st.checkbox("ลืมกินยา/กินยาผิดขนาดบ่อยครั้ง")
    with col7:
        side_effect = st.checkbox("สงสัยผลข้างเคียงจากยา (เวียนหัว คลื่นไส้ ผื่น)")

    st.subheader("6️⃣ อาการทั่วไป/โรคเรื้อรัง")
    col8, col9 = st.columns(2)
    with col8:
        pain_level = st.slider("ระดับความเจ็บปวด (0-10)", 0, 10, 0)
        fever = st.checkbox("มีไข้")
    with col9:
        symptom_days = st.number_input("มีอาการมาแล้วกี่วัน", min_value=0, max_value=90, value=0)
        chronic_worsen = st.checkbox("โรคประจำตัวกำเริบ (เบาหวาน/ความดัน/หัวใจ ฯลฯ)")

    submitted = st.form_submit_button("📊 ประเมินผลและบันทึกข้อมูล", use_container_width=True)

if submitted:
    if not respondent_code.strip():
        st.error("กรุณาระบุรหัสผู้ตอบก่อนบันทึกข้อมูล")
    else:
        result = compute_scores(
            red_flags=red_flags,
            adl_items=adl_items,
            fall_history=fall_history,
            uses_walking_aid=uses_walking_aid,
            multiple_meds=multiple_meds,
            dizziness=dizziness,
            mood_items=mood_items,
            missed_meds=missed_meds,
            side_effect=side_effect,
            pain_level=pain_level,
            fever=fever,
            symptom_days=symptom_days,
            chronic_worsen=chronic_worsen,
        )
        info = LEVEL_INFO[result["risk_level"]]

        record = {
            "timestamp": new_timestamp(),
            "respondent_code": respondent_code.strip(),
            "age": age,
            "gender": gender,
            "assessor_role": assessor_role,
            "red_flag": any(rf != "ไม่มีอาการข้างต้น" for rf in red_flags),
            **result,
        }
        save_record(record)

        st.divider()
        st.subheader("ผลการประเมิน")
        if result["total_score"] is not None:
            st.metric("คะแนนความเสี่ยงรวม", f"{result['total_score']} คะแนน")

        if info["color"] == "red":
            st.error(info["label"])
        elif info["color"] == "orange":
            st.warning(info["label"])
        else:
            st.success(info["label"])
        st.write(info["advice"])

        if result["adl_score"] is not None:
            st.caption(
                f"รายละเอียดคะแนนย่อย — ADL: {result['adl_score']}, "
                f"ความเสี่ยงหกล้ม: {result['fall_risk_score']}, "
                f"สภาพจิตใจ: {result['mood_score']}, "
                f"การใช้ยา: {result['medication_score']}, "
                f"อาการทั่วไป: {result['symptom_score']}"
            )

        st.success("✅ บันทึกข้อมูลลงระบบเรียบร้อยแล้ว ขอบคุณที่ร่วมทำแบบประเมิน")
