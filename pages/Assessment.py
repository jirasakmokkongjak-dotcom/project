import streamlit as st

from utils.prediction import predict_all


# =========================================================
# ตั้งค่าหน้า
# =========================================================

st.set_page_config(
    page_title="ระบบประเมินความเสี่ยงสุขภาพ",
    page_icon="🏥",
    layout="wide"
)


# =========================================================
# หัวข้อ
# =========================================================

st.title("🏥 ระบบประเมินความเสี่ยงสุขภาพ")

st.write(
    "ระบบประเมินความเสี่ยงเบื้องต้นจากข้อมูลสุขภาพ "
    "โดยใช้ Machine Learning"
)

st.warning(
    "⚠️ ระบบนี้ใช้สำหรับการประเมินเบื้องต้นเท่านั้น "
    "ไม่ใช่การวินิจฉัยโรค และไม่สามารถใช้แทนแพทย์ได้"
)


# =========================================================
# ข้อมูลทั่วไป
# =========================================================

st.header("👤 ข้อมูลทั่วไป")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input(
        "อายุ (ปี)",
        min_value=1,
        max_value=120,
        value=22
    )

with col2:
    sex = st.selectbox(
        "เพศ",
        ["Male", "Female"]
    )

with col3:
    height = st.number_input(
        "ส่วนสูง (เมตร)",
        min_value=0.5,
        max_value=2.5,
        value=1.72,
        step=0.01
    )


col1, col2, col3 = st.columns(3)

with col1:
    weight = st.number_input(
        "น้ำหนัก (กิโลกรัม)",
        min_value=1.0,
        max_value=300.0,
        value=75.0,
        step=0.1
    )

with col2:
    # คำนวณ BMI จากส่วนสูงและน้ำหนัก
    calculated_bmi = weight / (height ** 2)

    bmi = st.number_input(
        "BMI",
        min_value=5.0,
        max_value=80.0,
        value=round(calculated_bmi, 1),
        step=0.1
    )

with col3:
    sbp = st.number_input(
        "ความดันตัวบน SBP (mmHg)",
        min_value=50,
        max_value=300,
        value=120
    )


dbp = st.number_input(
    "ความดันตัวล่าง DBP (mmHg)",
    min_value=30,
    max_value=200,
    value=80
)


# =========================================================
# พฤติกรรมสุขภาพ
# =========================================================

st.header("🚬 พฤติกรรมสุขภาพ")

col1, col2, col3 = st.columns(3)

with col1:
    smoking = st.selectbox(
        "สูบบุหรี่",
        ["No", "Yes"]
    )

with col2:
    smoke = smoking

with col3:
    alcohol = st.selectbox(
        "ดื่มแอลกอฮอล์",
        ["No", "Yes"]
    )


activity = st.selectbox(
    "กิจกรรมทางกาย",
    [
        "ไม่ค่อยออกกำลังกาย",
        "ออกกำลังกายเล็กน้อย",
        "ออกกำลังกายปานกลาง",
        "ออกกำลังกายมาก"
    ]
)


# =========================================================
# อาการที่เกี่ยวข้องกับ Diabetes
# =========================================================

st.header("🩸 อาการที่เกี่ยวข้องกับเบาหวาน")

col1, col2, col3 = st.columns(3)

with col1:

    polyuria = st.checkbox(
        "ปัสสาวะบ่อย (Polyuria)"
    )

    polydipsia = st.checkbox(
        "กระหายน้ำบ่อย (Polydipsia)"
    )

    sudden_weight_loss = st.checkbox(
        "น้ำหนักลดลงอย่างรวดเร็ว"
    )

    weakness = st.checkbox(
        "อ่อนเพลีย / อ่อนแรง"
    )

    polyphagia = st.checkbox(
        "หิวบ่อย / กินจุ"
    )


with col2:

    genital_thrush = st.checkbox(
        "เชื้อราบริเวณอวัยวะเพศ"
    )

    visual_blurring = st.checkbox(
        "ตามัว"
    )

    itching = st.checkbox(
        "คันตามร่างกาย"
    )

    irritability = st.checkbox(
        "หงุดหงิดง่าย"
    )

    delayed_healing = st.checkbox(
        "แผลหายช้า"
    )


with col3:

    partial_paresis = st.checkbox(
        "กล้ามเนื้อบางส่วนอ่อนแรง"
    )

    muscle_stiffness = st.checkbox(
        "กล้ามเนื้อแข็ง / ตึง"
    )

    alopecia = st.checkbox(
        "ผมร่วง"
    )

    obesity_symptom = st.checkbox(
        "มีภาวะอ้วน / น้ำหนักเกิน"
    )

    emergency_symptoms = st.checkbox(
        "มีอาการผิดปกติรุนแรง เช่น "
        "เจ็บหน้าอกหรือหายใจลำบาก"
    )


# =========================================================
# ประวัติโรค
# =========================================================

st.header("📋 ประวัติสุขภาพ")

col1, col2, col3 = st.columns(3)

with col1:
    hypertension_history = st.selectbox(
        "เคยมีประวัติความดันโลหิตสูง",
        ["no", "yes"]
    )

with col2:
    diabetes_history = st.selectbox(
        "เคยมีประวัติเบาหวาน",
        ["no", "yes"]
    )

with col3:
    heart_history = st.selectbox(
        "เคยมีประวัติโรคหัวใจ",
        ["no", "yes"]
    )


# =========================================================
# ผลตรวจสุขภาพเพิ่มเติม
# =========================================================

st.header("🧪 ผลตรวจสุขภาพเพิ่มเติม")

medical_data_available = st.radio(
    "คุณมีผลตรวจสุขภาพหรือข้อมูลจากโรงพยาบาลเพิ่มเติมหรือไม่?",
    [
        "ไม่มีผลตรวจเพิ่มเติม",
        "มีผลตรวจเพิ่มเติม"
    ],
    horizontal=True
)

medical_data_available = (
    medical_data_available == "มีผลตรวจเพิ่มเติม"
)


# =========================================================
# ค่าเริ่มต้น
# =========================================================

# Obesity
family_history = "no"
favc = "no"
fcvc = 2.0
ncp = 3.0
caec = "Sometimes"
scc = "no"
faf = 1.0
tue = 1.0
calc = "no"
mtrans = "Public_Transportation"

# Hypertension
resi = "No"
odisease = "No"
creantine = 1.0
bun = 15.0
noofmed = 0

# Heart
cp = 0
chol = 200
fbs = 0
restecg = 0
thalach = 150
exang = 0
oldpeak = 0.0
slope = 0
ca = 0
thal = 0

# Kidney
sg = 1.020
al = 0
su = 0
bgr = 100.0
bu = 20.0
sc = 1.0
sod = 140.0
pot = 4.5
hemo = 14.0
pcv = 45.0
wbcc = 8000.0
rbcc = 5.0
rbc = "normal"
pc = "normal"
pcc = "notpresent"
ba = "notpresent"
appet = "good"
pe = "no"
ane = "no"


# =========================================================
# ถ้ามีผลตรวจ
# =========================================================

if medical_data_available:

    st.success(
        "✅ ระบบจะใช้ข้อมูลผลตรวจเพิ่มเติม "
        "เพื่อประเมิน Hypertension, Heart Disease และ CKD"
    )

    # =====================================================
    # Hypertension
    # =====================================================

    st.subheader("🩺 ข้อมูลสำหรับ Hypertension")

    col1, col2, col3 = st.columns(3)

    with col1:
        resi = st.selectbox(
            "มีภาวะดื้อต่ออินซูลิน (Resi)",
            ["No", "Yes"]
        )

    with col2:
        odisease = st.selectbox(
            "มีโรคอื่นร่วม (odisease)",
            ["No", "Yes"]
        )

    with col3:
        noofmed = st.number_input(
            "จำนวนยาที่ใช้",
            min_value=0,
            max_value=20,
            value=0
        )

    col1, col2 = st.columns(2)

    with col1:
        creantine = st.number_input(
            "Creatinine",
            min_value=0.0,
            max_value=20.0,
            value=1.0,
            step=0.1
        )

    with col2:
        bun = st.number_input(
            "BUN",
            min_value=0.0,
            max_value=200.0,
            value=15.0,
            step=0.1
        )


    # =====================================================
    # Heart Disease
    # =====================================================

    st.subheader("❤️ ข้อมูลสำหรับ Heart Disease")

    col1, col2, col3 = st.columns(3)

    with col1:
        cp = st.number_input(
            "Chest Pain Type (cp)",
            min_value=0,
            max_value=3,
            value=0
        )

    with col2:
        chol = st.number_input(
            "Cholesterol (chol)",
            min_value=0,
            max_value=700,
            value=200
        )

    with col3:
        thalach = st.number_input(
            "Maximum Heart Rate (thalach)",
            min_value=50,
            max_value=250,
            value=150
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        fbs = st.selectbox(
            "Fasting Blood Sugar > 120",
            [0, 1]
        )

    with col2:
        restecg = st.number_input(
            "Resting ECG (restecg)",
            min_value=0,
            max_value=2,
            value=0
        )

    with col3:
        exang = st.selectbox(
            "Exercise Induced Angina",
            [0, 1]
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        oldpeak = st.number_input(
            "ST Depression (oldpeak)",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.1
        )

    with col2:
        slope = st.number_input(
            "Slope",
            min_value=0,
            max_value=2,
            value=0
        )

    with col3:
        ca = st.number_input(
            "Number of Major Vessels (ca)",
            min_value=0,
            max_value=4,
            value=0
        )

    thal = st.number_input(
        "Thal",
        min_value=0,
        max_value=3,
        value=0
    )


    # =====================================================
    # Kidney Disease
    # =====================================================

    st.subheader("🧪 ข้อมูลสำหรับ Kidney Disease")

    col1, col2, col3 = st.columns(3)

    with col1:
        sg = st.number_input(
            "Specific Gravity (sg)",
            min_value=1.000,
            max_value=1.050,
            value=1.020,
            step=0.001,
            format="%.3f"
        )

    with col2:
        al = st.number_input(
            "Albumin (al)",
            min_value=0,
            max_value=5,
            value=0
        )

    with col3:
        su = st.number_input(
            "Sugar (su)",
            min_value=0,
            max_value=5,
            value=0
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        bgr = st.number_input(
            "Blood Glucose Random (bgr)",
            min_value=0.0,
            max_value=1000.0,
            value=100.0
        )

    with col2:
        bu = st.number_input(
            "Blood Urea (bu)",
            min_value=0.0,
            max_value=300.0,
            value=20.0
        )

    with col3:
        sc = st.number_input(
            "Serum Creatinine (sc)",
            min_value=0.0,
            max_value=30.0,
            value=1.0,
            step=0.1
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        sod = st.number_input(
            "Sodium (sod)",
            min_value=0.0,
            max_value=200.0,
            value=140.0
        )

    with col2:
        pot = st.number_input(
            "Potassium (pot)",
            min_value=0.0,
            max_value=20.0,
            value=4.5,
            step=0.1
        )

    with col3:
        hemo = st.number_input(
            "Hemoglobin (hemo)",
            min_value=0.0,
            max_value=30.0,
            value=14.0,
            step=0.1
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        pcv = st.number_input(
            "Packed Cell Volume (pcv)",
            min_value=0.0,
            max_value=100.0,
            value=45.0
        )

    with col2:
        wbcc = st.number_input(
            "White Blood Cell Count (wbcc)",
            min_value=0.0,
            max_value=30000.0,
            value=8000.0
        )

    with col3:
        rbcc = st.number_input(
            "Red Blood Cell Count (rbcc)",
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.1
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        rbc = st.selectbox(
            "Red Blood Cells (rbc)",
            ["normal", "abnormal"]
        )

    with col2:
        pc = st.selectbox(
            "Pus Cell (pc)",
            ["normal", "abnormal"]
        )

    with col3:
        pcc = st.selectbox(
            "Pus Cell Clumps (pcc)",
            ["notpresent", "present"]
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        ba = st.selectbox(
            "Bacteria (ba)",
            ["notpresent", "present"]
        )

    with col2:
        appet = st.selectbox(
            "Appetite",
            ["good", "poor"]
        )

    with col3:
        pe = st.selectbox(
            "Pedal Edema (pe)",
            ["no", "yes"]
        )

    ane = st.selectbox(
        "Anemia (ane)",
        ["no", "yes"]
    )

else:

    st.info(
        "ℹ️ หากไม่มีผลตรวจสุขภาพเพิ่มเติม "
        "ระบบจะไม่บังคับให้กรอกค่าผลเลือด "
        "และจะประเมินเฉพาะโรคที่สามารถใช้ข้อมูลทั่วไปได้"
    )


# =========================================================
# ข้อมูลสำหรับ Obesity
# =========================================================

st.header("⚖️ ข้อมูลพฤติกรรมสำหรับ Obesity")

col1, col2, col3 = st.columns(3)

with col1:
    family_history = st.selectbox(
        "คนในครอบครัวมีประวัติน้ำหนักเกิน",
        ["no", "yes"]
    )

with col2:
    favc = st.selectbox(
        "รับประทานอาหารแคลอรีสูงบ่อย",
        ["no", "yes"]
    )

with col3:
    fcvc = st.number_input(
        "ความถี่รับประทานผัก",
        min_value=1.0,
        max_value=3.0,
        value=2.0,
        step=0.1
    )

col1, col2, col3 = st.columns(3)

with col1:
    ncp = st.number_input(
        "จำนวนมื้ออาหารต่อวัน",
        min_value=1.0,
        max_value=6.0,
        value=3.0,
        step=0.1
    )

with col2:
    caec = st.selectbox(
        "รับประทานอาหารระหว่างมื้อ",
        [
            "no",
            "Sometimes",
            "Frequently",
            "Always"
        ]
    )

with col3:
    scc = st.selectbox(
        "ติดตาม/ควบคุมปริมาณแคลอรี",
        ["no", "yes"]
    )

col1, col2, col3 = st.columns(3)

with col1:
    faf = st.number_input(
        "ความถี่ออกกำลังกาย",
        min_value=0.0,
        max_value=3.0,
        value=1.0,
        step=0.1
    )

with col2:
    tue = st.number_input(
        "เวลาที่ใช้กับอุปกรณ์เทคโนโลยี",
        min_value=0.0,
        max_value=3.0,
        value=1.0,
        step=0.1
    )

with col3:
    calc = st.selectbox(
        "ดื่มแอลกอฮอล์",
        [
            "no",
            "Sometimes",
            "Frequently",
            "Always"
        ]
    )

mtrans = st.selectbox(
    "การเดินทางหลัก",
    [
        "Public_Transportation",
        "Automobile",
        "Walking",
        "Motorbike",
        "Bike"
    ]
)


# =========================================================
# สร้างข้อมูลสำหรับโมเดล
# =========================================================

user_data = {

    # ข้อมูลทั่วไป
    "age": age,
    "sex": sex,
    "height": height,
    "weight": weight,
    "bmi": bmi,

    # ความดัน
    "sbp": sbp,
    "dbp": dbp,

    # พฤติกรรม
    "smoking": smoking,
    "smoke": smoke,
    "alcohol": alcohol,
    "activity": activity,

    # Diabetes
    "polyuria": "Yes" if polyuria else "No",
    "polydipsia": "Yes" if polydipsia else "No",
    "sudden_weight_loss":
        "Yes" if sudden_weight_loss else "No",
    "weakness":
        "Yes" if weakness else "No",
    "polyphagia":
        "Yes" if polyphagia else "No",
    "genital_thrush":
        "Yes" if genital_thrush else "No",
    "visual_blurring":
        "Yes" if visual_blurring else "No",
    "itching":
        "Yes" if itching else "No",
    "irritability":
        "Yes" if irritability else "No",
    "delayed_healing":
        "Yes" if delayed_healing else "No",
    "partial_paresis":
        "Yes" if partial_paresis else "No",
    "muscle_stiffness":
        "Yes" if muscle_stiffness else "No",
    "alopecia":
        "Yes" if alopecia else "No",
    "obesity_symptom":
        "Yes" if obesity_symptom else "No",

    # ประวัติโรค
    "hypertension_history":
        hypertension_history,
    "diabetes_history":
        diabetes_history,
    "heart_history":
        heart_history,

    # Obesity
    "family_history":
        family_history,
    "favc":
        favc,
    "fcvc":
        fcvc,
    "ncp":
        ncp,
    "caec":
        caec,
    "smoke":
        smoke,
    "ch2o":
        2.0,
    "scc":
        scc,
    "faf":
        faf,
    "tue":
        tue,
    "calc":
        calc,
    "mtrans":
        mtrans,

    # ตรวจว่ามีผลตรวจหรือไม่
    "medical_data_available":
        medical_data_available
}


# =========================================================
# เพิ่มผลตรวจ
# =========================================================

if medical_data_available:

    user_data.update({

        # Hypertension
        "resi":
            resi,
        "odisease":
            odisease,
        "creantine":
            creantine,
        "bun":
            bun,
        "noofmed":
            noofmed,

        # Heart
        "cp":
            cp,
        "chol":
            chol,
        "fbs":
            fbs,
        "restecg":
            restecg,
        "thalach":
            thalach,
        "exang":
            exang,
        "oldpeak":
            oldpeak,
        "slope":
            slope,
        "ca":
            ca,
        "thal":
            thal,

        # Kidney
        "sg":
            sg,
        "al":
            al,
        "su":
            su,
        "bgr":
            bgr,
        "bu":
            bu,
        "sc":
            sc,
        "sod":
            sod,
        "pot":
            pot,
        "hemo":
            hemo,
        "pcv":
            pcv,
        "wbcc":
            wbcc,
        "rbcc":
            rbcc,
        "rbc":
            rbc,
        "pc":
            pc,
        "pcc":
            pcc,
        "ba":
            ba,
        "appet":
            appet,
        "pe":
            pe,
        "ane":
            ane
    })


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
    # อาการฉุกเฉิน
    # =====================================================

    if emergency_symptoms:

        st.error(
            "🚨 หากกำลังมีอาการเจ็บหน้าอก หายใจลำบาก "
            "หมดสติ หรืออาการรุนแรงเฉียบพลัน "
            "ควรไปโรงพยาบาลหรือขอความช่วยเหลือฉุกเฉินทันที "
            "ไม่ควรรอผลจากระบบนี้"
        )


    # =====================================================
    # ประเมิน
    # =====================================================

    with st.spinner(
        "กำลังประเมินข้อมูล..."
    ):

        results = predict_all(
            user_data
        )


    # =====================================================
    # ผลการประเมิน
    # =====================================================

    st.divider()

    st.header("📊 ผลการประเมิน")


    # =====================================================
    # Diabetes
    # =====================================================

    diabetes_result = results[
        "diabetes"
    ]

    st.subheader(
        "🩸 Diabetes"
    )

    if diabetes_result[
        "prediction"
    ] is not None:

        prediction = str(
            diabetes_result[
                "prediction"
            ]
        ).strip().lower()

        if prediction == "negative":

            st.success(
                "ผลการจำแนกของโมเดล: Negative"
            )

        else:

            st.warning(
                "ผลการจำแนกของโมเดล: Positive"
            )

        if diabetes_result[
            "probability"
        ] is not None:

            st.caption(
                f"คะแนนจากโมเดล: "
                f"{diabetes_result['probability']:.2f}%"
            )

    else:

        st.warning(
            "โมเดลไม่สามารถประเมินได้"
        )

        if diabetes_result.get(
            "error"
        ):

            st.error(
                "รายละเอียด: "
                + str(
                    diabetes_result[
                        "error"
                    ]
                )
            )


    # =====================================================
    # Hypertension
    # =====================================================

    st.subheader(
        "🩺 Hypertension"
    )

    hypertension_result = results[
        "hypertension"
    ]

    if hypertension_result[
        "prediction"
    ] is None:

        st.info(
            "ℹ️ ยังไม่ประเมินโรคนี้ "
            "เนื่องจากไม่ได้ระบุว่ามีผลตรวจสุขภาพเพิ่มเติม"
        )

    else:

        hypertension_prediction = str(
            hypertension_result[
                "prediction"
            ]
        ).strip()

        hypertension_text = {

            "Stage 1":
                "Stage 1",

            "Stage 2":
                "Stage 2",

            "hypertensive crisis":
                "Hypertensive Crisis"
        }

        display_prediction = (
            hypertension_text.get(
                hypertension_prediction,
                hypertension_prediction
            )
        )

        st.info(
            "ผลการจำแนกของโมเดล: "
            + display_prediction
        )

        if hypertension_result[
            "probability"
        ] is not None:

            st.caption(
                f"คะแนนจากโมเดล: "
                f"{hypertension_result['probability']:.2f}%"
            )


    # =====================================================
    # Heart Disease
    # =====================================================

    st.subheader(
        "❤️ Heart Disease"
    )

    heart_result = results[
        "heart_disease"
    ]

    if heart_result[
        "prediction"
    ] is None:

        st.info(
            "ℹ️ ยังไม่ประเมินโรคนี้ "
            "เนื่องจากไม่ได้ระบุว่ามีผลตรวจสุขภาพเพิ่มเติม"
        )

    else:

        heart_prediction = (
            heart_result[
                "prediction"
            ]
        )

        if int(
            heart_prediction
        ) == 0:

            st.success(
                "ผลการจำแนกของโมเดล: 0 "
                "(กลุ่มไม่พบโรคตามข้อมูลของโมเดล)"
            )

        else:

            st.warning(
                "ผลการจำแนกของโมเดล: 1 "
                "(กลุ่มพบโรคตามข้อมูลของโมเดล)"
            )

        if heart_result[
            "probability"
        ] is not None:

            st.caption(
                f"คะแนนจากโมเดล: "
                f"{heart_result['probability']:.2f}%"
            )


    # =====================================================
    # Kidney Disease
    # =====================================================

    st.subheader(
        "🧪 Kidney Disease"
    )

    kidney_result = results[
        "kidney_disease"
    ]

    if kidney_result[
        "prediction"
    ] is None:

        st.info(
            "ℹ️ ยังไม่ประเมินโรคนี้ "
            "เนื่องจากไม่ได้ระบุว่ามีผลตรวจสุขภาพเพิ่มเติม"
        )

    else:

        kidney_prediction = str(
            kidney_result[
                "prediction"
            ]
        ).strip().lower()

        if kidney_prediction == "notckd":

            st.success(
                "ผลการจำแนกของโมเดล: ไม่พบ CKD "
                "ตามข้อมูลของโมเดล"
            )

        else:

            st.warning(
                "ผลการจำแนกของโมเดล: CKD "
                "ตามข้อมูลของโมเดล"
            )

        if kidney_result[
            "probability"
        ] is not None:

            st.caption(
                f"คะแนนจากโมเดล: "
                f"{kidney_result['probability']:.2f}%"
            )


    # =====================================================
    # Obesity
    # =====================================================

    st.subheader(
        "⚖️ Obesity"
    )

    obesity_result = results[
        "obesity"
    ]

    if obesity_result[
        "prediction"
    ] is not None:

        obesity_prediction = str(
            obesity_result[
                "prediction"
            ]
        ).strip()

        obesity_labels = {

            "Insufficient_Weight":
                "น้ำหนักต่ำกว่าเกณฑ์",

            "Normal_Weight":
                "น้ำหนักปกติ",

            "Overweight_Level_I":
                "น้ำหนักเกินระดับ I",

            "Overweight_Level_II":
                "น้ำหนักเกินระดับ II",

            "Obesity_Type_I":
                "โรคอ้วนประเภท I",

            "Obesity_Type_II":
                "โรคอ้วนประเภท II",

            "Obesity_Type_III":
                "โรคอ้วนประเภท III"
        }

        display_obesity = obesity_labels.get(
            obesity_prediction,
            obesity_prediction.replace(
                "_",
                " "
            )
        )

        st.info(
            "ผลการจำแนกของโมเดล: "
            + display_obesity
        )

        if obesity_result[
            "probability"
        ] is not None:

            st.caption(
                f"คะแนนจากโมเดล: "
                f"{obesity_result['probability']:.2f}%"
            )

    else:

        st.warning(
            "โมเดลไม่สามารถประเมินได้"
        )

        if obesity_result.get(
            "error"
        ):

            st.error(
                "รายละเอียด: "
                + str(
                    obesity_result[
                        "error"
                    ]
                )
            )


# =========================================================
# หมายเหตุท้ายหน้า
# =========================================================

st.divider()

st.info(
    "⚠️ ผลการประเมินทั้งหมดเป็นผลจาก Machine Learning "
    "โดยใช้ข้อมูลที่ผู้ใช้กรอกและข้อมูลผลตรวจเพิ่มเติม "
    "ผลลัพธ์เป็นเพียงการประเมินเบื้องต้น "
    "ไม่ใช่การวินิจฉัยโรค และไม่ควรใช้แทนการตรวจจากแพทย์"
)