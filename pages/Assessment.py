import streamlit as st
from utils.prediction import predict_all


st.set_page_config(
    page_title="ประเมินความเสี่ยงสุขภาพ",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 ระบบประเมินความเสี่ยงสุขภาพ")
st.write("กรอกข้อมูลเบื้องต้นเพื่อประเมินความเสี่ยงของ 5 โรค")

st.divider()


# =========================
# ข้อมูลทั่วไป
# =========================

st.subheader("👤 ข้อมูลทั่วไป")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input(
        "อายุ (ปี)",
        min_value=18,
        max_value=100,
        value=40
    )

with col2:
    sex = st.selectbox(
        "เพศ",
        ["ชาย", "หญิง"]
    )


# =========================
# ข้อมูลร่างกาย
# =========================

st.subheader("📏 ข้อมูลร่างกาย")

col1, col2, col3 = st.columns(3)

with col1:
    height = st.number_input(
        "ส่วนสูง (cm)",
        min_value=100.0,
        max_value=220.0,
        value=170.0
    )

with col2:
    weight = st.number_input(
        "น้ำหนัก (kg)",
        min_value=30.0,
        max_value=200.0,
        value=70.0
    )

with col3:
    bmi = weight / ((height / 100) ** 2)
    st.metric("BMI", f"{bmi:.2f}")


# =========================
# ความดัน
# =========================

st.subheader("❤️ ความดันโลหิต")

col1, col2 = st.columns(2)

with col1:
    systolic = st.number_input(
        "ความดันตัวบน (SBP)",
        min_value=70,
        max_value=250,
        value=120
    )

with col2:
    diastolic = st.number_input(
        "ความดันตัวล่าง (DBP)",
        min_value=40,
        max_value=150,
        value=80
    )


# =========================
# พฤติกรรมสุขภาพ
# =========================

st.subheader("🚬 พฤติกรรมสุขภาพ")

col1, col2, col3 = st.columns(3)

with col1:
    smoking = st.selectbox(
        "สูบบุหรี่หรือไม่",
        ["ไม่สูบ", "สูบ"]
    )

with col2:
    alcohol = st.selectbox(
        "ดื่มแอลกอฮอล์หรือไม่",
        ["ไม่ดื่ม", "ดื่ม"]
    )

with col3:
    activity = st.selectbox(
        "ออกกำลังกายเป็นประจำหรือไม่",
        ["ไม่", "ใช่"]
    )


# =========================
# อาการ
# =========================

st.subheader("🩹 อาการที่พบ")

col1, col2 = st.columns(2)

with col1:
    frequent_thirst = st.checkbox("กระหายน้ำบ่อย")
    frequent_urination = st.checkbox("ปัสสาวะบ่อย")
    fatigue = st.checkbox("เหนื่อยง่าย")
    dizziness = st.checkbox("เวียนศีรษะ")
    numbness = st.checkbox("ชาหรือเสียวมือเท้า")

with col2:
    chest_pain = st.checkbox("เจ็บหน้าอก")
    shortness_breath = st.checkbox("หายใจลำบาก")
    leg_swelling = st.checkbox("ขาบวม")
    slow_wound = st.checkbox("แผลหายช้า")
    abnormal_urination = st.checkbox("ปัสสาวะผิดปกติ")


st.divider()


# =========================
# ปุ่มประเมิน
# =========================

if st.button(
    "🔍 ประเมินความเสี่ยง",
    type="primary",
    use_container_width=True
):

    # อาการฉุกเฉิน
    if chest_pain or shortness_breath:
        st.error(
            "⚠️ หากมีอาการเจ็บหน้าอกหรือหายใจลำบากอย่างรุนแรง "
            "หรือเกิดขึ้นเฉียบพลัน ควรไปโรงพยาบาลหรือขอความช่วยเหลือฉุกเฉิน"
        )

    # เตรียมข้อมูล
    user_data = {
        "age": age,
        "sex": sex,
        "height": height,
        "weight": weight,
        "bmi": bmi,
        "systolic": systolic,
        "diastolic": diastolic,
        "smoking": smoking,
        "alcohol": alcohol,
        "activity": activity,
        "frequent_thirst": frequent_thirst,
        "frequent_urination": frequent_urination,
        "fatigue": fatigue,
        "dizziness": dizziness,
        "numbness": numbness,
        "chest_pain": chest_pain,
        "shortness_breath": shortness_breath,
        "leg_swelling": leg_swelling,
        "slow_wound": slow_wound,
        "abnormal_urination": abnormal_urination
    }

    # เรียก AI
    with st.spinner("กำลังประเมินข้อมูลด้วย AI..."):

        results = predict_all(user_data)

    st.divider()

    st.subheader("📊 ผลการประเมิน")

    disease_names = {
        "diabetes": "🩸 เบาหวาน",
        "hypertension": "❤️ ความดันโลหิตสูง",
        "heart_disease": "🫀 โรคหัวใจ",
        "kidney_disease": "🫘 โรคไต",
        "obesity": "⚖️ โรคอ้วน"
    }

    for disease, result in results.items():

        st.markdown(
            f"### {disease_names[disease]}"
        )

        if result["error"] is not None:

            st.warning(
                "โมเดลไม่สามารถประเมินข้อมูลชุดนี้ได้"
            )

        else:

            probability = result["probability"]

            if probability is not None:

                st.progress(
                    min(int(probability), 100)
                )

                st.write(
                    f"คะแนนจากโมเดล: **{probability:.2f}%**"
                )

            st.write(
                f"ผลการทำนายของโมเดล: **{result['prediction']}**"
            )

    st.info(
        "⚠️ ผลนี้เป็นการประเมินเบื้องต้นจากโมเดล Machine Learning "
        "ไม่ใช่การวินิจฉัยโรค และไม่ควรใช้แทนการตรวจจากแพทย์"
    )