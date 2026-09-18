import streamlit as st
from utils.prediction import predict_all


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ประเมินความเสี่ยงสุขภาพ",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 ระบบประเมินความเสี่ยงสุขภาพ")
st.write("กรอกข้อมูลเบื้องต้นเพื่อประเมินความเสี่ยงของ 5 โรค")

st.divider()


# =========================================================
# ข้อมูลทั่วไป
# =========================================================

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


# =========================================================
# ข้อมูลร่างกาย
# =========================================================

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

    st.metric(
        "BMI",
        f"{bmi:.2f}"
    )


# =========================================================
# ความดันโลหิต
# =========================================================

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


# =========================================================
# พฤติกรรมสุขภาพ
# =========================================================

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


# =========================================================
# อาการที่เกี่ยวข้องกับเบาหวาน
# =========================================================

st.subheader("🩸 อาการที่เกี่ยวข้องกับเบาหวาน")

col1, col2 = st.columns(2)

with col1:

    frequent_thirst = st.checkbox(
        "กระหายน้ำบ่อย"
    )

    frequent_urination = st.checkbox(
        "ปัสสาวะบ่อย"
    )

    sudden_weight_loss = st.checkbox(
        "น้ำหนักลดกะทันหัน"
    )

    frequent_hunger = st.checkbox(
        "หิวบ่อย"
    )

    visual_blurring = st.checkbox(
        "ตามัว"
    )

    itching = st.checkbox(
        "คันตามผิวหนัง"
    )

    irritability = st.checkbox(
        "หงุดหงิดง่าย"
    )


with col2:

    fatigue = st.checkbox(
        "เหนื่อยง่าย / อ่อนเพลีย"
    )

    slow_wound = st.checkbox(
        "แผลหายช้า"
    )

    numbness = st.checkbox(
        "ชา หรือเสียวมือเท้า"
    )

    muscle_stiffness = st.checkbox(
        "กล้ามเนื้อแข็ง / ตึง"
    )

    hair_loss = st.checkbox(
        "ผมร่วง"
    )

    genital_thrush = st.checkbox(
        "มีเชื้อราในบริเวณอวัยวะเพศ"
    )

    chest_pain = st.checkbox(
        "เจ็บหน้าอก"
    )

    shortness_breath = st.checkbox(
        "หายใจลำบาก"
    )


# =========================================================
# ข้อมูลโรคหัวใจ
# =========================================================

st.subheader("🫀 ข้อมูลเพิ่มเติมสำหรับโรคหัวใจ")

col1, col2 = st.columns(2)

with col1:

    chol = st.number_input(
        "คอเลสเตอรอล (Cholesterol)",
        min_value=0.0,
        max_value=700.0,
        value=200.0
    )

    max_heart_rate = st.number_input(
        "อัตราการเต้นหัวใจสูงสุด",
        min_value=50.0,
        max_value=250.0,
        value=150.0
    )

    oldpeak = st.number_input(
        "ST Depression (Oldpeak)",
        min_value=0.0,
        max_value=10.0,
        value=0.0
    )

    exercise_chest_pain = st.checkbox(
        "เจ็บหน้าอกขณะออกกำลังกาย"
    )


with col2:

    high_blood_sugar = st.checkbox(
        "น้ำตาลในเลือดสูง"
    )

    restecg = st.selectbox(
        "ผลคลื่นไฟฟ้าหัวใจ (Rest ECG)",
        [0, 1, 2]
    )

    slope = st.selectbox(
        "Slope",
        [0, 1, 2]
    )

    ca = st.selectbox(
        "จำนวนหลอดเลือดหลัก (CA)",
        [0, 1, 2, 3, 4]
    )

    thal = st.selectbox(
        "Thal",
        [0, 1, 2, 3]
    )


# =========================================================
# ข้อมูลโรคไต
# =========================================================

st.subheader("🫘 ข้อมูลเพิ่มเติมสำหรับโรคไต")

col1, col2, col3 = st.columns(3)

with col1:

    sg = st.number_input(
        "Specific Gravity (SG)",
        min_value=1.000,
        max_value=1.040,
        value=1.020,
        step=0.001
    )

    al = st.number_input(
        "Albumin (AL)",
        min_value=0,
        max_value=5,
        value=0
    )

    su = st.number_input(
        "Sugar (SU)",
        min_value=0,
        max_value=5,
        value=0
    )

    bgr = st.number_input(
        "Blood Glucose (BGR)",
        min_value=0.0,
        max_value=600.0,
        value=100.0
    )

    bu = st.number_input(
        "Blood Urea (BU)",
        min_value=0.0,
        max_value=300.0,
        value=40.0
    )

    sc = st.number_input(
        "Serum Creatinine (SC)",
        min_value=0.0,
        max_value=20.0,
        value=1.0
    )


with col2:

    sod = st.number_input(
        "Sodium (SOD)",
        min_value=50.0,
        max_value=200.0,
        value=140.0
    )

    pot = st.number_input(
        "Potassium (POT)",
        min_value=1.0,
        max_value=15.0,
        value=4.0
    )

    hemo = st.number_input(
        "Hemoglobin (HEMO)",
        min_value=1.0,
        max_value=25.0,
        value=14.0
    )

    pcv = st.number_input(
        "Packed Cell Volume (PCV)",
        min_value=10.0,
        max_value=70.0,
        value=42.0
    )

    wbcc = st.number_input(
        "White Blood Cell Count",
        min_value=1000.0,
        max_value=30000.0,
        value=8000.0
    )

    rbcc = st.number_input(
        "Red Blood Cell Count",
        min_value=1.0,
        max_value=10.0,
        value=5.0
    )


with col3:

    rbc = st.selectbox(
        "Red Blood Cells",
        ["normal", "abnormal"]
    )

    pc = st.selectbox(
        "Pus Cell",
        ["normal", "abnormal"]
    )

    pcc = st.selectbox(
        "Pus Cell Clumps",
        ["notpresent", "present"]
    )

    ba = st.selectbox(
        "Bacteria",
        ["notpresent", "present"]
    )

    appet = st.selectbox(
        "Appetite",
        ["good", "poor"]
    )

    pe = st.selectbox(
        "Pedal Edema",
        ["no", "yes"]
    )

    ane = st.selectbox(
        "Anemia",
        ["no", "yes"]
    )


# =========================================================
# ประวัติโรคร่วม
# =========================================================

st.subheader("📋 ประวัติโรคร่วม")

col1, col2, col3 = st.columns(3)

with col1:
    hypertension_history = st.checkbox(
        "เคยมีความดันโลหิตสูง"
    )

with col2:
    diabetes_history = st.checkbox(
        "เคยเป็นเบาหวาน"
    )

with col3:
    heart_history = st.checkbox(
        "เคยเป็นโรคหัวใจ"
    )


# =========================================================
# ข้อมูลโรคอ้วน
# =========================================================

st.subheader("⚖️ ข้อมูลเพิ่มเติมสำหรับโรคอ้วน")

col1, col2 = st.columns(2)

with col1:

    family_history_overweight = st.checkbox(
        "มีคนในครอบครัวมีภาวะน้ำหนักเกิน"
    )

    high_calorie_food = st.checkbox(
        "รับประทานอาหารพลังงานสูงเป็นประจำ"
    )

    calorie_monitoring = st.checkbox(
        "ควบคุมหรือคำนวณแคลอรี"
    )

    vegetable_frequency = st.number_input(
        "ความถี่การรับประทานผัก",
        min_value=1.0,
        max_value=3.0,
        value=2.0
    )

    main_meals = st.number_input(
        "จำนวนมื้ออาหารหลักต่อวัน",
        min_value=1.0,
        max_value=5.0,
        value=3.0
    )

    water_intake = st.number_input(
        "ปริมาณน้ำที่ดื่มโดยประมาณ",
        min_value=1.0,
        max_value=5.0,
        value=2.0
    )


with col2:

    food_between_meals = st.selectbox(
        "รับประทานอาหารระหว่างมื้อ",
        ["no", "Sometimes", "Frequently", "Always"]
    )

    exercise_frequency = st.number_input(
        "ความถี่ในการออกกำลังกาย",
        min_value=0.0,
        max_value=3.0,
        value=1.0
    )

    technology_time = st.number_input(
        "เวลาที่ใช้โทรศัพท์/คอมพิวเตอร์ต่อวัน",
        min_value=0.0,
        max_value=5.0,
        value=1.0
    )

    transportation = st.selectbox(
        "วิธีการเดินทางที่ใช้บ่อย",
        [
            "Public_Transportation",
            "Automobile",
            "Walking",
            "Motorbike",
            "Bike"
        ]
    )


# =========================================================
# ข้อมูลเพิ่มเติมความดัน
# =========================================================

st.subheader("❤️ ข้อมูลเพิ่มเติมสำหรับความดันโลหิต")

col1, col2, col3 = st.columns(3)

with col1:

    creantine = st.number_input(
        "Creatinine",
        min_value=0.0,
        max_value=20.0,
        value=1.0
    )

with col2:

    bun = st.number_input(
        "BUN",
        min_value=0.0,
        max_value=300.0,
        value=40.0
    )

with col3:

    noofmed = st.number_input(
        "จำนวนยาที่ใช้ประจำ",
        min_value=0,
        max_value=20,
        value=0
    )

resi = st.number_input(
    "Resi",
    min_value=0.0,
    max_value=100.0,
    value=0.0
)

odisease = st.number_input(
    "จำนวนโรคประจำตัว",
    min_value=0,
    max_value=20,
    value=0
)


# =========================================================
# ปุ่มประเมิน
# =========================================================

st.divider()

if st.button(
    "🔍 ประเมินความเสี่ยง",
    type="primary",
    use_container_width=True
):

    # =====================================================
    # แจ้งเตือนฉุกเฉิน
    # =====================================================

    if chest_pain or shortness_breath:

        st.error(
            "⚠️ หากมีอาการเจ็บหน้าอกหรือหายใจลำบากอย่างรุนแรง "
            "หรือเกิดขึ้นเฉียบพลัน ควรไปโรงพยาบาล "
            "หรือขอความช่วยเหลือฉุกเฉิน"
        )


    # =====================================================
    # รวมข้อมูล
    # =====================================================

    user_data = {

        # -------------------------
        # ข้อมูลทั่วไป
        # -------------------------

        "age": age,
        "sex": sex,

        # -------------------------
        # ร่างกาย
        # -------------------------

        "height": height,
        "weight": weight,
        "bmi": bmi,

        # -------------------------
        # ความดัน
        # -------------------------

        "systolic": systolic,
        "diastolic": diastolic,

        # -------------------------
        # พฤติกรรม
        # -------------------------

        "smoking": smoking,
        "alcohol": alcohol,
        "activity": activity,

        # -------------------------
        # เบาหวาน
        # -------------------------

        "frequent_thirst": frequent_thirst,
        "frequent_urination": frequent_urination,
        "sudden_weight_loss": sudden_weight_loss,
        "frequent_hunger": frequent_hunger,
        "visual_blurring": visual_blurring,
        "itching": itching,
        "irritability": irritability,
        "fatigue": fatigue,
        "slow_wound": slow_wound,
        "numbness": numbness,
        "muscle_stiffness": muscle_stiffness,
        "hair_loss": hair_loss,
        "genital_thrush": genital_thrush,

        # -------------------------
        # อาการฉุกเฉิน / หัวใจ
        # -------------------------

        "chest_pain": chest_pain,
        "shortness_breath": shortness_breath,

        # -------------------------
        # หัวใจ
        # -------------------------

        "chol": chol,
        "max_heart_rate": max_heart_rate,
        "oldpeak": oldpeak,
        "exercise_chest_pain": exercise_chest_pain,
        "high_blood_sugar": high_blood_sugar,
        "restecg": restecg,
        "slope": slope,
        "ca": ca,
        "thal": thal,

        # -------------------------
        # ไต
        # -------------------------

        "sg": sg,
        "al": al,
        "su": su,
        "rbc": rbc,
        "pc": pc,
        "pcc": pcc,
        "ba": ba,
        "bgr": bgr,
        "bu": bu,
        "sc": sc,
        "sod": sod,
        "pot": pot,
        "hemo": hemo,
        "pcv": pcv,
        "wbcc": wbcc,
        "rbcc": rbcc,

        "appet": appet,
        "pe": pe,
        "ane": ane,

        # -------------------------
        # ประวัติโรคร่วม
        # -------------------------

        "hypertension": hypertension_history,
        "diabetes": diabetes_history,
        "heart_disease": heart_history,

        # -------------------------
        # ความดันเพิ่มเติม
        # -------------------------

        "creantine": creantine,
        "bun": bun,
        "noofmed": noofmed,
        "resi": resi,
        "odisease": odisease,

        # -------------------------
        # โรคอ้วน
        # -------------------------

        "family_history_overweight":
            family_history_overweight,

        "high_calorie_food":
            high_calorie_food,

        "calorie_monitoring":
            calorie_monitoring,

        "vegetable_frequency":
            vegetable_frequency,

        "main_meals":
            main_meals,

        "food_between_meals":
            food_between_meals,

        "water_intake":
            water_intake,

        "exercise_frequency":
            exercise_frequency,

        "technology_time":
            technology_time,

        "transportation":
            transportation
    }


    # =====================================================
    # ประเมิน
    # =====================================================

    with st.spinner(
        "กำลังประเมินข้อมูลด้วย AI..."
    ):

        results = predict_all(user_data)


    # =====================================================
    # แสดงผล
    # =====================================================

    st.divider()

    st.subheader("📊 ผลการประเมิน")

    disease_names = {

        "diabetes":
            "🩸 เบาหวาน",

        "hypertension":
            "❤️ ความดันโลหิตสูง",

        "heart_disease":
            "🫀 โรคหัวใจ",

        "kidney_disease":
            "🫘 โรคไต",

        "obesity":
            "⚖️ โรคอ้วน"
    }


    for disease, result in results.items():

        st.markdown(
            f"### {disease_names[disease]}"
        )


        if result["error"] is not None:

            st.warning(
                "โมเดลไม่สามารถประเมินข้อมูลชุดนี้ได้"
            )

            st.code(
                result["error"],
                language="text"
            )

        else:

            probability = result["probability"]

            if probability is not None:

                st.progress(
                    min(int(probability), 100)
                )

                st.write(
                    f"คะแนนจากโมเดล: "
                    f"**{probability:.2f}%**"
                )

            st.write(
                "ผลการทำนายของโมเดล: "
                f"**{result['prediction']}**"
            )


    # =====================================================
    # คำเตือน
    # =====================================================

    st.info(
        "⚠️ ผลนี้เป็นการประเมินเบื้องต้นจากโมเดล "
        "Machine Learning ไม่ใช่การวินิจฉัยโรค "
        "และไม่ควรใช้แทนการตรวจจากแพทย์"
    )