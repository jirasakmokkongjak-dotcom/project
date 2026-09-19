import os
import joblib
import pandas as pd


# =========================================================
# ตำแหน่งโฟลเดอร์
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)


# =========================================================
# โหลดโมเดล
# =========================================================

MODELS = {
    "diabetes": joblib.load(
        os.path.join(
            MODEL_DIR,
            "diabetes_model.pkl"
        )
    ),

    "hypertension": joblib.load(
        os.path.join(
            MODEL_DIR,
            "hypertension_model.pkl"
        )
    ),

    "heart_disease": joblib.load(
        os.path.join(
            MODEL_DIR,
            "heart_disease_model.pkl"
        )
    ),

    "kidney_disease": joblib.load(
        os.path.join(
            MODEL_DIR,
            "kidney_disease_model.pkl"
        )
    ),

    "obesity": joblib.load(
        os.path.join(
            MODEL_DIR,
            "obesity_model.pkl"
        )
    )
}


# =========================================================
# ฟังก์ชันช่วยดึงข้อมูล
# =========================================================

def get_data(data, *keys, default=None):

    for key in keys:

        if key in data:
            return data[key]

    if default is not None:
        return default

    raise KeyError(
        f"ไม่พบข้อมูลที่ต้องการ: {keys}"
    )


# =========================================================
# Diabetes
# =========================================================

def make_diabetes_data(data):

    return pd.DataFrame([{

        "Age": get_data(
            data,
            "age"
        ),

        "Gender": get_data(
            data,
            "sex"
        ),

        "Polyuria": get_data(
            data,
            "polyuria",
            "frequent_urination"
        ),

        "Polydipsia": get_data(
            data,
            "polydipsia",
            "frequent_thirst"
        ),

        "sudden weight loss": get_data(
            data,
            "sudden_weight_loss"
        ),

        "weakness": get_data(
            data,
            "weakness"
        ),

        "Polyphagia": get_data(
            data,
            "polyphagia",
            "frequent_hunger"
        ),

        "Genital thrush": get_data(
            data,
            "genital_thrush"
        ),

        "visual blurring": get_data(
            data,
            "visual_blurring"
        ),

        "Itching": get_data(
            data,
            "itching"
        ),

        "Irritability": get_data(
            data,
            "irritability"
        ),

        "delayed healing": get_data(
            data,
            "delayed_healing"
        ),

        "partial paresis": get_data(
            data,
            "partial_paresis"
        ),

        "muscle stiffness": get_data(
            data,
            "muscle_stiffness"
        ),

        "Alopecia": get_data(
            data,
            "alopecia"
        ),

        "Obesity": get_data(
            data,
            "obesity_symptom"
        )

    }])


# =========================================================
# Hypertension
# =========================================================

def make_hypertension_data(data):

    return pd.DataFrame([{

        "age": get_data(
            data,
            "age"
        ),

        "sex": get_data(
            data,
            "sex"
        ),

        "BMI": get_data(
            data,
            "bmi"
        ),

        "Resi": get_data(
            data,
            "resi"
        ),

        "SBP": get_data(
            data,
            "sbp"
        ),

        "DBP": get_data(
            data,
            "dbp"
        ),

        "Smoking": get_data(
            data,
            "smoking"
        ),

        "odisease": get_data(
            data,
            "odisease"
        ),

        "creantine": get_data(
            data,
            "creantine"
        ),

        "BUN": get_data(
            data,
            "bun"
        ),

        "Noofmed": get_data(
            data,
            "noofmed"
        )

    }])


# =========================================================
# Heart Disease
# =========================================================

def make_heart_data(data):

    return pd.DataFrame([{

        "age": get_data(
            data,
            "age"
        ),

        "sex": get_data(
            data,
            "sex"
        ),

        "cp": get_data(
            data,
            "cp"
        ),

        "trestbps": get_data(
            data,
            "sbp"
        ),

        "chol": get_data(
            data,
            "chol"
        ),

        "fbs": get_data(
            data,
            "fbs"
        ),

        "restecg": get_data(
            data,
            "restecg"
        ),

        "thalach": get_data(
            data,
            "thalach"
        ),

        "exang": get_data(
            data,
            "exang"
        ),

        "oldpeak": get_data(
            data,
            "oldpeak"
        ),

        "slope": get_data(
            data,
            "slope"
        ),

        "ca": get_data(
            data,
            "ca"
        ),

        "thal": get_data(
            data,
            "thal"
        )

    }])


# =========================================================
# Kidney Disease
# =========================================================

def make_kidney_data(data):

    return pd.DataFrame([{

        "age": get_data(
            data,
            "age"
        ),

        "bp": get_data(
            data,
            "sbp"
        ),

        "sg": get_data(
            data,
            "sg"
        ),

        "al": get_data(
            data,
            "al"
        ),

        "su": get_data(
            data,
            "su"
        ),

        "bgr": get_data(
            data,
            "bgr"
        ),

        "bu": get_data(
            data,
            "bu"
        ),

        "sc": get_data(
            data,
            "sc"
        ),

        "sod": get_data(
            data,
            "sod"
        ),

        "pot": get_data(
            data,
            "pot"
        ),

        "hemo": get_data(
            data,
            "hemo"
        ),

        "pcv": get_data(
            data,
            "pcv"
        ),

        "wbcc": get_data(
            data,
            "wbcc"
        ),

        "rbcc": get_data(
            data,
            "rbcc"
        ),

        "rbc": get_data(
            data,
            "rbc"
        ),

        "pc": get_data(
            data,
            "pc"
        ),

        "pcc": get_data(
            data,
            "pcc"
        ),

        "ba": get_data(
            data,
            "ba"
        ),

        "appet": get_data(
            data,
            "appet"
        ),

        "pe": get_data(
            data,
            "pe"
        ),

        "ane": get_data(
            data,
            "ane"
        ),

        "htn": get_data(
            data,
            "hypertension_history"
        ),

        "dm": get_data(
            data,
            "diabetes_history"
        ),

        "cad": get_data(
            data,
            "heart_history"
        )

    }])


# =========================================================
# Obesity
# =========================================================

def make_obesity_data(data):

    return pd.DataFrame([{

        "Gender": get_data(
            data,
            "sex"
        ),

        "Age": get_data(
            data,
            "age"
        ),

        "Height": get_data(
            data,
            "height"
        ),

        "Weight": get_data(
            data,
            "weight"
        ),

        "family_history_with_overweight":
            get_data(
                data,
                "family_history"
            ),

        "FAVC": get_data(
            data,
            "favc",
            "high_calorie_food"
        ),

        "FCVC": get_data(
            data,
            "fcvc",
            "vegetable_frequency"
        ),

        "NCP": get_data(
            data,
            "ncp",
            "meals_per_day"
        ),

        "CAEC": get_data(
            data,
            "caec",
            "snacking"
        ),

        "SMOKE": get_data(
            data,
            "smoke",
            "smoking"
        ),

        "CH2O": get_data(
            data,
            "ch2o",
            default=2.0
        ),

        "SCC": get_data(
            data,
            "scc",
            "calorie_tracking"
        ),

        "FAF": get_data(
            data,
            "faf",
            "exercise_frequency"
        ),

        "TUE": get_data(
            data,
            "tue",
            "technology_use"
        ),

        "CALC": get_data(
            data,
            "calc",
            "alcohol_frequency"
        ),

        "MTRANS": get_data(
            data,
            "mtrans",
            "transportation"
        )

    }])


# =========================================================
# ตรวจสอบ Column ของ Model
# =========================================================

def prepare_data_for_model(
    model,
    data_df
):

    preprocessor = model.named_steps[
        "preprocessor"
    ]

    expected_columns = []

    for (
        transformer_name,
        transformer,
        columns
    ) in preprocessor.transformers_:

        if transformer == "drop":
            continue

        if transformer == "passthrough":

            if isinstance(
                columns,
                str
            ):
                continue

            expected_columns.extend(
                list(columns)
            )

            continue

        try:

            expected_columns.extend(
                list(columns)
            )

        except Exception:

            pass

    expected_columns = list(
        dict.fromkeys(
            expected_columns
        )
    )

    if not expected_columns:

        raise ValueError(
            "ไม่สามารถอ่านชื่อคอลัมน์จากโมเดลได้"
        )

    missing_columns = [

        col

        for col in expected_columns

        if col not in data_df.columns

    ]

    if missing_columns:

        raise ValueError(
            "ข้อมูลไม่ครบสำหรับโมเดล: "
            + ", ".join(
                missing_columns
            )
        )

    data_df = data_df[
        expected_columns
    ]

    return data_df


# =========================================================
# ทำนายโรค
# =========================================================

def predict_disease(
    disease_name,
    data
):

    if disease_name not in MODELS:

        raise ValueError(
            f"ไม่พบโมเดล: {disease_name}"
        )

    model = MODELS[
        disease_name
    ]

    # =====================================================
    # โรคที่ต้องใช้ผลตรวจเพิ่มเติม
    # =====================================================

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

            "error":
                "ต้องมีผลตรวจสุขภาพเพิ่มเติม"

        }


    # =====================================================
    # สร้างข้อมูล
    # =====================================================

    if disease_name == "diabetes":

        input_data = make_diabetes_data(
            data
        )

    elif disease_name == "hypertension":

        input_data = make_hypertension_data(
            data
        )

    elif disease_name == "heart_disease":

        input_data = make_heart_data(
            data
        )

    elif disease_name == "kidney_disease":

        input_data = make_kidney_data(
            data
        )

    elif disease_name == "obesity":

        input_data = make_obesity_data(
            data
        )

    else:

        raise ValueError(
            f"ไม่พบประเภทโรค: {disease_name}"
        )


    # =====================================================
    # ตรวจสอบและเรียง Column
    # =====================================================

    input_data = prepare_data_for_model(
        model,
        input_data
    )


    # =====================================================
    # Prediction
    # =====================================================

    prediction = model.predict(
        input_data
    )[0]


    # =====================================================
    # Probability
    # =====================================================

    probability = None

    if hasattr(
        model,
        "predict_proba"
    ):

        probabilities = model.predict_proba(
            input_data
        )[0]

        probability = float(
            max(probabilities) * 100
        )


    # =====================================================
    # ผลลัพธ์
    # =====================================================

    return {

        "prediction":
            prediction,

        "probability":
            probability,

        "error":
            None

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

            print(
                f"[ERROR] {disease}: {e}"
            )

            results[disease] = {

                "prediction":
                    None,

                "probability":
                    None,

                "error":
                    str(e)

            }

    return results