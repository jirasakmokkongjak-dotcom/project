import os
import json
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


# =========================
# ตั้งค่าโฟลเดอร์
# =========================

DATA_DIR = "DATA"
MODEL_DIR = "models"

os.makedirs(MODEL_DIR, exist_ok=True)


# =========================
# ฟังก์ชันสร้างโมเดล
# =========================

def train_model(df, target_column, model_name, binary_target=False):
    print("\n" + "=" * 50)
    print(f"กำลังฝึกโมเดล: {model_name}")
    print("=" * 50)

    # ลบแถวที่ไม่มีค่า Target
    df = df.dropna(subset=[target_column]).copy()

    # สำหรับ Heart Disease:
    # target 0 = ไม่มีโรค
    # target 1-4 = มีโรค
    if binary_target:
        df[target_column] = (
            pd.to_numeric(df[target_column], errors="coerce") > 0
        ).astype(int)

    X = df.drop(columns=[target_column])
    y = df[target_column]

    # แปลงคอลัมน์ที่เป็นตัวเลข
    for col in X.columns:
        converted = pd.to_numeric(X[col], errors="coerce")

        # ถ้าแปลงเป็นตัวเลขได้เกือบทั้งหมด ให้ใช้เป็น numeric
        if converted.notna().mean() > 0.8:
            X[col] = converted

    numeric_features = X.select_dtypes(
        include=["int64", "float64", "int32", "float32"]
    ).columns.tolist()

    categorical_features = X.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    # Numeric
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median"))
    ])

    # Categorical
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False
        ))
    ])

    # รวมการเตรียมข้อมูล
    preprocessor = ColumnTransformer([
        ("numeric", numeric_pipeline, numeric_features),
        ("categorical", categorical_pipeline, categorical_features)
    ])

    # Random Forest
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    # แบ่งข้อมูล Train / Test
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # ฝึกโมเดล
    pipeline.fit(X_train, y_train)

    # ทำนาย
    y_pred = pipeline.predict(X_test)

    # คำนวณประสิทธิภาพ
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )
    recall = recall_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )
    f1 = f1_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")

    # บันทึกโมเดล
    model_path = os.path.join(
        MODEL_DIR,
        f"{model_name}_model.pkl"
    )

    joblib.dump(pipeline, model_path)

    print(f"บันทึกโมเดลแล้ว → {model_path}")

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }


# =========================
# 1. Diabetes
# =========================

diabetes = pd.read_csv(
    os.path.join(DATA_DIR, "diabetes.csv")
)

diabetes_result = train_model(
    diabetes,
    "class",
    "diabetes"
)


# =========================
# 2. Hypertension
# =========================

hypertension = pd.read_csv(
    os.path.join(DATA_DIR, "hypertension.csv")
)

hypertension_result = train_model(
    hypertension,
    "level",
    "hypertension"
)


# =========================
# 3. Heart Disease
# =========================

heart = pd.read_csv(
    os.path.join(DATA_DIR, "heart_disease.csv")
)

heart_result = train_model(
    heart,
    "target",
    "heart_disease",
    binary_target=True
)


# =========================
# 4. Kidney Disease
# =========================

kidney = pd.read_csv(
    os.path.join(DATA_DIR, "kidney_disease.csv")
)

kidney_result = train_model(
    kidney,
    "class",
    "kidney_disease"
)


# =========================
# 5. Obesity
# =========================

obesity = pd.read_csv(
    os.path.join(DATA_DIR, "obesity.csv")
)

obesity_result = train_model(
    obesity,
    "NObeyesdad",
    "obesity"
)


# =========================
# บันทึกผลทั้งหมด
# =========================

results = {
    "diabetes": diabetes_result,
    "hypertension": hypertension_result,
    "heart_disease": heart_result,
    "kidney_disease": kidney_result,
    "obesity": obesity_result
}

with open(
    os.path.join(MODEL_DIR, "model_metrics.json"),
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        results,
        f,
        indent=4,
        ensure_ascii=False
    )

print("\n" + "=" * 50)
print("ฝึกโมเดลทั้ง 5 โรคเสร็จแล้ว!")
print("=" * 50)