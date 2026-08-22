import streamlit as st
st.set_page_config(page_title="ระบบประเมิน", page_icon="", layout="wide")
st.title(" ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ")
st.markdown("---")
name = st.text_input("ชื่อ-นามสกุล")
age = st.number_input("อายุ (ปี)", min_value=60, max_value=120, value=65)
gender = st.selectbox("เพศ", ["ชาย", "หญิง", "ไม่ระบุ"])
st.subheader("อาการที่พบ")
symptoms = st.multiselect("เลือกอาการ", ["เจ็บหน้าอก", "หายใจไม่ออก", "ไข้สูง", "เวียนศีรษะ", "ปวดเมื่อย", "นอนไม่หลับ"])
if st.button("ประเมินผล", type="primary"):
    if name and symptoms:
        st.success(f"✅ บันทึกข้อมูล: {name}, อายุ {age} ปี, เพศ {gender}")
        st.info(f"อาการที่เลือก: {', '.join(symptoms)}")
        if "เจ็บหน้าอก" in symptoms or "หายใจไม่ออก" in symptoms:
            st.error("🚨 ความเสี่ยงสูง! กรุณาไปพบแพทย์ทันที")
        elif len(symptoms) >= 3:
            st.warning("⚠️ ความเสี่ยงกลาง ควรพบแพทย์ภายใน 24 ชั่วโมง")
        else:
            st.success("✅ ความเสี่ยงต่ำ ดูแลตัวเองได้")
    else:
        st.error("❌ กรุณากรอกชื่อและเลือกอาการอย่างน้อย 1 รายการ")
