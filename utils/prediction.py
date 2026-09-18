import os
import joblib
import pandas as pd


# ==================================================
# ตำแหน่งโมเดล
# ==================================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")


# ==================================================
# โหลดโมเดล
# ==================================================

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


# ==================================================
# ข้อมูลเบาหวาน
# ==================================================

def make_diabetes_data(data):

    return {
        "Age": data["age"],
        "Gender": "Male" if data["sex"] == "ชาย" else "Female",

        "Polyuria":
            "Yes" if data["frequent_urination"] else "No",

        "Polydipsia":
            "Yes" if data["frequent_thirst"] else "No",

        "sudden weight loss":
            "Yes" if data["sudden_weight_loss"] else "No",

        "weakness":
            "Yes" if data["fatigue"] else "No",

        "Polyphagia":
            "Yes" if data["frequent_hunger"] else "No",

        "Genital thrush":
            "Yes" if data["genital_thrush"] else "No",

        "visual blurring":
            "Yes" if data["visual_blurring"] else "No",

        "Itching":
            "Yes" if data["itching"] else "No",

        "Irritability":
            "Yes" if data["irritability"] else "No",

        "delayed healing":
            "Yes" if data["slow_wound"] else "No",

        "partial paresis":
            "Yes" if data["numbness"] else "No",

        "muscle stiffness":
            "Yes" if data["muscle_stiffness"] else "No",

        "Alopecia":
            "Yes" if data["hair_loss"] else "No",

        "Obesity":
            "Yes" if data["bmi"] >= 25 else "No"
    }


# ==================================================
# ข้อมูลความดันโลหิต
# ==================================================

def make_hypertension_data(data):

    return {
        "age": data["age"],

        "sex":
            1 if data["sex"] == "ชาย" else 0,

        "BMI":
            data["bmi"],

        "Resi":
            data["resi"],

        "SBP":
            data["systolic"],

        "DBP":
            data["diastolic"],

        "Smoking":
            1 if data["smoking"] == "สูบ" else 0,

        "odisease":
            data["odisease"],

        "creantine":
            data["creantine"],

        "BUN":
            data["bun"],

        "Noofmed":
            data["noofmed"]
    }


# ==================================================
# ข้อมูลโรคหัวใจ
# ==================================================

def make_heart_data(data):

    return {
        "age": data["age"],

        "sex":
            1 if data["sex"] == "ชาย" else 0,

        "cp":
            1 if data["chest_pain"] else 0,

        "trestbps":
            data["systolic"],

        "chol":
            data["chol"],

        "fbs":
            1 if data["high_blood_sugar"] else 0,

        "restecg":
            data["restecg"],

        "thalach":
            data["max_heart_rate"],

        "exang":
            1 if data["exercise_chest_pain"] else 0,

        "oldpeak":
            data["oldpeak"],

        "slope":
            data["slope"],

        "ca":
            data["ca"],

        "thal":
            data["thal"]
    }


# ==================================================
# ข้อมูลโรคไต
# ==================================================

def make_kidney_data(data):

    return {
        "age":
            data["age"],

        "bp":
            data["systolic"],

        "sg":
            data["sg"],

        "al":
            data["al"],

        "su":
            data["su"],

        "bgr":
            data["bgr"],

        "bu":
            data["bu"],

        "sc":
            data["sc"],

        "sod":
            data["sod"],

        "pot":
            data["pot"],

        "hemo":
            data["hemo"],

        "pcv":
            data["pcv"],

        "wbcc":
            data["wbcc"],

        "rbcc":
            data["rbcc"],

        "rbc":
            data["rbc"],

        "pc":
            data["pc"],

        "pcc":
            data["pcc"],

        "ba":
            data["ba"],

        "htn":
            "yes" if data["hypertension"] else "no",

        "dm":
            "yes" if data["diabetes"] else "no",

        "cad":
            "yes" if data["heart_disease"] else "no",

        "appet":
            data["appet"],

        "pe":
            data["pe"],

        "ane":
            data["ane"]
    }


# ==================================================
# ข้อมูลโรคอ้วน
# ==================================================

def make_obesity_data(data):

    return {
        "Age":
            data["age"],

        "Height":
            data["height"] / 100,

        "Weight":
            data["weight"],

        "FCVC":
            data["vegetable_frequency"],

        "NCP":
            data["main_meals"],

        "CH2O":
            data["water_intake"],

        "FAF":
            data["exercise_frequency"],

        "TUE":
            data["technology_time"],

        "Gender":
            "Male" if data["sex"] == "ชาย" else "Female",

        "family_history_with_overweight":
            "yes"
            if data["family_history_overweight"]
            else "no",

        "FAVC":
            "yes"
            if data["high_calorie_food"]
            else "no",

        "CAEC":
            data["food_between_meals"],

        "SMOKE":
            "yes"
            if data["smoking"] == "สูบ"
            else "no",

        "SCC":
            "yes"
            if data["calorie_monitoring"]
            else "no",

        "CALC":
            "Sometimes"
            if data["alcohol"] == "ดื่ม"
            else "no",

        "MTRANS":
            data["transportation"]
    }


# ==================================================
# เตรียมข้อมูลให้ตรงกับ Dataset
# ==================================================

def prepare_data_for_model(model, data):

    df = pd.DataFrame([data])

    try:

        preprocessor = model.named_steps["preprocessor"]

        required_columns = []

        for name, transformer, columns in preprocessor.transformers_:

            if columns is None:
                continue

            if isinstance(columns, str):

                required_columns.append(columns)

            elif hasattr(columns, "tolist"):

                required_columns.extend(columns.tolist())

            else:

                required_columns.extend(list(columns))

    except Exception as e:

        raise ValueError(
            f"ไม่สามารถอ่านคอลัมน์ของโมเดลได้: {e}"
        )

    missing_columns = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "คอลัมน์ที่โมเดลต้องการแต่ไม่มีข้อมูล: "
            + str(missing_columns)
        )

    df = df[required_columns]

    return df


# ==================================================
# ทำนายโรค
# ==================================================

def predict_disease(disease, data):

    if disease not in MODELS:

        return {
            "prediction": None,
            "probability": None,
            "error": "ไม่พบโมเดล"
        }

    model = MODELS[disease]

    try:

        if disease == "diabetes":

            model_data = make_diabetes_data(data)

        elif disease == "hypertension":

            model_data = make_hypertension_data(data)

        elif disease == "heart_disease":

            model_data = make_heart_data(data)

        elif disease == "kidney_disease":

            model_data = make_kidney_data(data)

        elif disease == "obesity":

            model_data = make_obesity_data(data)

        else:

            model_data = data


        df = prepare_data_for_model(
            model,
            model_data
        )


        prediction = model.predict(df)[0]


        probability = None

        if hasattr(model, "predict_proba"):

            probabilities = model.predict_proba(df)[0]

            probability = float(
                max(probabilities)
            ) * 100


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


# ==================================================
# ประเมินทั้ง 5 โรค
# ==================================================

def predict_all(data):

    results = {}

    for disease in MODELS:

        results[disease] = predict_disease(
            disease,
            data
        )

    return results