import os
import joblib
import pandas as pd


# =========================
# ตำแหน่งโฟลเดอร์ models
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")


# =========================
# โหลดโมเดล
# =========================

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
    )
}


# =========================
# ฟังก์ชันแปลงข้อมูล
# =========================

def prepare_data(data):
    """
    รับข้อมูลจากหน้าเว็บ
    แล้วเตรียมเป็น DataFrame
    """

    df = pd.DataFrame([data])

    return df


# =========================
# ฟังก์ชันประเมินโรค
# =========================

def predict_disease(disease, data):

    if disease not in MODELS:
        return None

    model = MODELS[disease]

    df = prepare_data(data)

    try:

        prediction = model.predict(df)[0]

        probability = None

        if hasattr(model, "predict_proba"):

            probabilities = model.predict_proba(df)[0]

            probability = float(max(probabilities)) * 100

        return {
            "prediction": prediction,
            "probability": probability,
            "error": None
        }

    except Exception as e:

        return {
            "prediction": None,
            "probability": None,
            "error": str(e)
        }


# =========================
# ประเมินทั้ง 5 โรค
# =========================

def predict_all(data):

    results = {}

    for disease in MODELS:

        results[disease] = predict_disease(
            disease,
            data
        )

    return results