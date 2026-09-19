import os
import joblib
import pandas as pd


# =========================================================
# โหลดโมเดล
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")


MODELS = {
    "diabetes": joblib.load(
        os.path.join(MODEL_DIR, "diabetes_model.pkl")
    ),

    "hypertension": joblib.load(
        os.path.join(MODEL_DIR, "hypertension_model.pkl")
    ),

    "heart_disease": joblib.load(
        os.path.join(MODEL_DIR, "heart_disease_model.pkl")
    ),

    "kidney_disease": joblib.load(
        os.path.join(MODEL_DIR, "kidney_disease_model.pkl")
    ),

    "obesity": joblib.load(
        os.path.join(MODEL_DIR, "obesity_model.pkl")
    ),
}


# =========================================================
# สร้างข้อมูลสำหรับ Diabetes
# =========================================================

def make_diabetes_data(data):

    return pd.DataFrame([{
        "Age": data["age"],
        "Gender": data["sex"],

        "Polyuria": data["polyuria"],
        "Polydipsia": data["polydipsia"],
        "sudden weight loss": data["sudden_weight_loss"],
        "weakness": data["weakness"],
        "Polyphagia": data["polyphagia"],
        "Genital thrush": data["genital_thrush"],
        "visual blurring": data["visual_blurring"],
        "Itching": data["itching"],
        "Irritability": data["irritability"],
        "delayed healing": data["delayed_healing"],
        "partial paresis": data["partial_paresis"],
        "muscle stiffness": data["muscle_stiffness"],
        "Alopecia": data["alopecia"],
        "Obesity": data["obesity_symptom"]
    }])


# =========================================================
# สร้างข้อมูลสำหรับ Hypertension
# =========================================================

def make_hypertension_data(data):

    return pd.DataFrame([{
        "age": data["age"],
        "sex": data["sex"],
        "BMI": data["bmi"],
        "Resi": data["resi"],
        "SBP": data["sbp"],
        "DBP": data["dbp"],
        "Smoking": data["smoking"],
        "odisease": data["odisease"],
        "creantine": data["creantine"],
        "BUN": data["bun"],
        "Noofmed": data["noofmed"]
    }])


# =========================================================
# สร้างข้อมูลสำหรับ Heart Disease
# =========================================================

def make_heart_data(data):

    return pd.DataFrame([{
        "age": data["age"],
        "sex": data["sex"],
        "cp": data["cp"],
        "trestbps": data["sbp"],
        "chol": data["chol"],
        "fbs": data["fbs"],
        "restecg": data["restecg"],
        "thalach": data["thalach"],
        "exang": data["exang"],
        "oldpeak": data["oldpeak"],
        "slope": data["slope"],
        "ca": data["ca"],
        "thal": data["thal"]
    }])


# =========================================================
# สร้างข้อมูลสำหรับ Kidney Disease
# =========================================================

def make_kidney_data(data):

    return pd.DataFrame([{
        "age": data["age"],
        "bp": data["sbp"],
        "sg": data["sg"],
        "al": data["al"],
        "su": data["su"],
        "bgr": data["bgr"],
        "bu": data["bu"],
        "sc": data["sc"],
        "sod": data["sod"],
        "pot": data["pot"],
        "hemo": data["hemo"],
        "pcv": data["pcv"],
        "wbcc": data["wbcc"],
        "rbcc": data["rbcc"],
        "rbc": data["rbc"],
        "pc": data["pc"],
        "pcc": data["pcc"],
        "ba": data["ba"],
        "appet": data["appet"],
        "pe": data["pe"],
        "ane": data["ane"],
        "htn": data["hypertension_history"],
        "dm": data["diabetes_history"],
        "cad": data["heart_history"]
    }])


# =========================================================
# สร้างข้อมูลสำหรับ Obesity
# =========================================================

def make_obesity_data(data):

    return pd.DataFrame([{
        "Gender": data["sex"],
        "Age": data["age"],
        "Height": data["height"],
        "Weight": data["weight"],
        "family_history_with_overweight": data["family_history"],
        "FAVC": data["favc"],
        "FCVC": data["fcvc"],
        "NCP": data["ncp"],
        "CAEC": data["caec"],
        "SMOKE": data["smoke"],
        "CH2O": data["ch2o"],
        "SCC": data["scc"],
        "FAF": data["faf"],
        "TUE": data["tue"],
        "CALC": data["calc"],
        "MTRANS": data["mtrans"]
    }])


# =========================================================
# เตรียมข้อมูลให้ตรงกับ columns ของโมเดล
# =========================================================

def prepare_data_for_model(model, data_df):

    try:

        preprocessor = model.named_steps["preprocessor"]

        expected_columns = []

        for _, _, columns in preprocessor.transformers_:

            if columns == "drop":
                continue

            if columns == "passthrough":
                continue

            if isinstance(columns, (list, tuple)):
                expected_columns.extend(columns)

        missing_columns = [
            col for col in expected_columns
            if col not in data_df.columns
        ]

        if missing_columns:

            raise ValueError(
                "ข้อมูลไม่ครบสำหรับโมเดล: "
                + ", ".join(missing_columns)
            )

        data_df = data_df[expected_columns]

        return data_df

    except Exception as e:

        raise ValueError(
            f"ไม่สามารถเตรียมข้อมูลสำหรับโมเดลได้: {str(e)}"
        )


# =========================================================
# ทำนายโรค
# =========================================================

def predict_disease(disease_name, data):

    model = MODELS[disease_name]

    # -----------------------------------------------------
    # โรคที่ต้องใช้ข้อมูลจากผลตรวจสุขภาพเพิ่มเติม
    # -----------------------------------------------------

    medical_required = [
        "hypertension",
        "heart_disease",
        "kidney_disease"
    ]

    medical_data_available = data.get(
        "medical_data_available",
        False
    )

    if (
        disease_name in medical_required
        and not medical_data_available
    ):

        return {
            "prediction": None,
            "probability": None,
            "error": (
                "โรคนี้ต้องใช้ข้อมูลจากผลตรวจสุขภาพเพิ่มเติม "
                "จึงจะสามารถประเมินด้วยโมเดลได้"
            )
        }

    # -----------------------------------------------------
    # สร้างข้อมูลตามโรค
    # -----------------------------------------------------

    if disease_name == "diabetes":

        input_data = make_diabetes_data(data)

    elif disease_name == "hypertension":

        input_data = make_hypertension_data(data)

    elif disease_name == "heart_disease":

        input_data = make_heart_data(data)

    elif disease_name == "kidney_disease":

        input_data = make_kidney_data(data)

    elif disease_name == "obesity":

        input_data = make_obesity_data(data)

    else:

        raise ValueError(
            f"ไม่พบชื่อโรค: {disease_name}"
        )

    # -----------------------------------------------------
    # ตรวจสอบและเรียง columns
    # -----------------------------------------------------

    input_data = prepare_data_for_model(
        model,
        input_data
    )

    # -----------------------------------------------------
    # Predict
    # -----------------------------------------------------

    prediction = model.predict(input_data)[0]

    # -----------------------------------------------------
    # Probability / คะแนนจากโมเดล
    # -----------------------------------------------------

    probability = None

    if hasattr(model, "predict_proba"):

        probabilities = model.predict_proba(input_data)[0]

        probability = float(
            max(probabilities) * 100
        )

    return {
        "prediction": prediction,
        "probability": probability,
        "error": None
    }


# =========================================================
# ทำนายทั้ง 5 โรค
# =========================================================

def predict_all(data):

    results = {}

    diseases = [
        "diabetes",
        "hypertension",
        "heart_disease",
        "kidney_disease",
        "obesity"
    ]

    for disease in diseases:

        try:

            results[disease] = predict_disease(
                disease,
                data
            )

        except Exception as e:

            results[disease] = {
                "prediction": None,
                "probability": None,
                "error": str(e)
            }

    return results