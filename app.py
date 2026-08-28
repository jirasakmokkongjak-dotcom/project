import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import warnings

warnings.filterwarnings('ignore')

# ==================== ตั้งค่า LINE Messaging API ====================
# หมายเหตุ: LINE Notify ปิดให้บริการแล้วตั้งแต่ 31 มี.ค. 2025
# ให้ใช้ LINE Messaging API (Official Account) แทน หรือ Telegram Bot ก็ได้
LINE_CHANNEL_ACCESS_TOKEN = "ใส่_CHANNEL_ACCESS_TOKEN_ที่นี่"
LINE_TARGET_USER_ID = "ใส่_USER_ID_ผู้รับแจ้งเตือนที่นี่"  # เช่น ลูกหลาน/ผู้ดูแล

def send_line_message(message: str):
    if LINE_CHANNEL_ACCESS_TOKEN.startswith("ใส่_"):
        return
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": LINE_TARGET_USER_ID,
        "messages": [{"type": "text", "text": message}],
    }
    try:
        requests.post(
            "https://api.line.me/v2/bot/message/push",
            headers=headers, json=payload, timeout=5,
        )
    except Exception:
        pass

# ==================== ไฟล์เก็บข้อมูล ====================
DATA_FILE = "assessment_data.csv"

def save_to_csv(data_dict):
    df_new = pd.DataFrame([data_dict])
    if os.path.exists(DATA_FILE):
        df_new.to_csv(DATA_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(DATA_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, on_bad_lines='skip')
    return pd.DataFrame()

def get_data_count():
    df = load_data()
    return len(df)

# ==================== ตั้งค่าหน้าเว็บ ====================
st.set_page_config(
    page_title="ตรวจอาการง่ายๆ สำหรับผู้สูงอายุ",
    page_icon="🏥",
    layout="centered",  # ไม่ใช้ wide เพื่อไม่ให้ตัวหนังสือกระจายจนตามยาก
    initial_sidebar_state="collapsed",  # ซ่อน sidebar ไว้ก่อน ลดสิ่งที่ทำให้สับสน
)

# ==================== CSS: เน้นใหญ่ ชัด คอนทราสต์สูง ====================
st.markdown("""
<style>
    /* ตัวหนังสือใหญ่ทั้งแอป อ่านง่ายสำหรับผู้สูงอายุ */
    html, body, [class*="css"] { font-size: 22px !important; }
    h1 { font-size: 2.3rem !important; }
    h2 { font-size: 1.9rem !important; }
    h3 { font-size: 1.6rem !important; }

    .stApp { background-color: #FFFFFF; }

    /* ปุ่มใหญ่ กดง่าย ด้วยนิ้วที่ไม่ค่อยแม่นแล้ว */
    .stButton > button {
        font-size: 24px !important;
        padding: 20px 10px !important;
        border-radius: 14px !important;
        min-height: 70px;
        font-weight: 700;
        width: 100%;
    }

    /* ปุ่มหลัก (สีเขียว = ทำต่อ) */
    .stButton > button[kind="primary"] {
        background-color: #1565C0 !important;
        color: white !important;
        border: none !important;
    }

    /* checkbox / radio ให้ตัวใหญ่ขึ้น */
    .stCheckbox label p, .stRadio label p { font-size: 22px !important; }

    /* กล่องข้อความให้อ่านง่าย ตัดขอบให้ชัด ไม่มีเงาเยอะ */
    .simple-box {
        background: #F5F7FA;
        border: 3px solid #1565C0;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        color: #000000;
    }
    .simple-box b { color: #000000; }

    .result-red {
        background: #D32F2F; color: white; padding: 28px; border-radius: 18px;
        text-align: center; font-weight: 800; margin: 16px 0;
    }
    .result-yellow {
        background: #F57C00; color: white; padding: 28px; border-radius: 18px;
        text-align: center; font-weight: 800; margin: 16px 0;
    }
    .result-green {
        background: #2E7D32; color: white; padding: 28px; border-radius: 18px;
        text-align: center; font-weight: 800; margin: 16px 0;
    }
    .result-red h2, .result-yellow h2, .result-green h2 { font-size: 2.2rem; margin: 0 0 10px 0; }
    .result-red p, .result-yellow p, .result-green p { font-size: 1.4rem; margin: 0; }

    /* ปุ่มโทรฉุกเฉิน ลอยอยู่มุมล่างขวาเสมอ */
    .emergency-float {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
    }
    .emergency-float a {
        display: block;
        background: #D32F2F;
        color: white !important;
        text-decoration: none;
        font-size: 22px;
        font-weight: 800;
        padding: 16px 22px;
        border-radius: 50px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
        text-align: center;
    }

    .step-dot {
        display: inline-block; width: 16px; height: 16px; border-radius: 50%;
        margin: 0 6px; background: #CCCCCC;
    }
    .step-dot.active { background: #1565C0; }
</style>
""", unsafe_allow_html=True)

# ปุ่มโทรฉุกเฉินลอยตลอดเวลา ทุกหน้า
st.markdown("""
<div class="emergency-float">
    <a href="tel:1669">🚑 โทร 1669</a>
</div>
""", unsafe_allow_html=True)

# ==================== ข้อมูลอาการ (ยกมาจากเดิม แต่จัดกลุ่มให้เลือกง่ายขึ้น) ====================
SYMPTOMS_DATA = {
    "แดง": {  # ฉุกเฉิน
        "เจ็บหน้าอกร้าวลงแขนซ้าย/กราม": 40,
        "แขนขาอ่อนแรงครึ่งซีก/ปากเบี้ยว": 40,
        "พูดไม่ชัด/สับสนฉับพลัน": 35,
        "หายใจไม่ออก/หอบเหนื่อยขณะพัก": 35,
        "หมดสติ/วูบ/เป็นลม": 40,
        "ปวดศีรษะรุนแรงที่สุดในชีวิต": 35,
        "อาเจียนเป็นเลือด/ถ่ายดำ": 35,
        "ปวดท้องรุนแรงเฉียบพลัน": 30,
    },
    "เหลือง": {  # เฝ้าระวัง
        "ความดันสูงมาก หรือ น้ำตาลในเลือดผิดปกติมาก": 25,
        "น้ำหนักลดลงเร็วผิดปกติ": 20,
        "ใจสั่น/หัวใจเต้นผิดจังหวะ": 18,
        "เวียนศีรษะรุนแรง/ทรงตัวไม่ได้": 18,
        "ขา/ข้อเท้าบวมทั้งสองข้าง": 18,
        "ไข้สูงติดต่อกันเกิน 3 วัน": 15,
        "ปัสสาวะแสบขัด/มีเลือดปน": 15,
    },
    "เขียว": {  # ทั่วไป
        "ปวดเมื่อยตามตัว/ปวดหลัง": 4,
        "ปวดข้อเข่า": 5,
        "นอนไม่หลับ": 4,
        "อ่อนเพลียเล็กน้อย": 4,
        "ไอ/เจ็บคอ": 5,
        "แสบร้อนกลางอกเล็กน้อย": 5,
        "ท้องผูก": 3,
        "ปวดหัวตึงๆ": 5,
    },
}

CATEGORY_LABEL = {
    "แดง": "🔴 อาการรุนแรง (เลือกถ้ามีอาการแบบนี้)",
    "เหลือง": "🟡 อาการที่ควรเฝ้าระวัง",
    "เขียว": "🟢 อาการทั่วไป ไม่รุนแรง",
}

CHRONIC_DISEASES = ["เบาหวาน", "ความดันโลหิตสูง", "โรคหัวใจ", "ไขมันในเลือดสูง", "โรคไต", "ไม่มี"]

# ==================== จัดการ session state สำหรับ wizard ====================
if "step" not in st.session_state:
    st.session_state.step = "home"
if "form" not in st.session_state:
    st.session_state.form = {}

def go_to(step_name):
    st.session_state.step = step_name

def show_progress(current, total, label):
    dots = ""
    for i in range(1, total + 1):
        cls = "step-dot active" if i <= current else "step-dot"
        dots += f'<span class="{cls}"></span>'
    st.markdown(f'<div style="text-align:center; margin-bottom: 10px;">{dots}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center; color:#555;">ขั้นตอนที่ {current} จาก {total} — {label}</p>', unsafe_allow_html=True)

# ==================== หน้าแรก: ทางเลือกใหญ่ๆ แค่ 3 อย่าง ====================
if st.session_state.step == "home":
    st.markdown("<h1 style='text-align:center;'>🏥 ตรวจอาการง่ายๆ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:20px;'>กดปุ่มด้านล่างเพื่อเริ่มต้น</p>", unsafe_allow_html=True)

    if st.button("✅ เริ่มตรวจอาการ", type="primary"):
        st.session_state.form = {}
        go_to("step1")
        st.rerun()

    if st.button("📋 ดูประวัติการตรวจของฉัน"):
        go_to("history")
        st.rerun()

    st.markdown("""
    <div class="simple-box">
        <b>ถ้ามีอาการรุนแรง เช่น เจ็บหน้าอก แขนขาอ่อนแรง พูดไม่ชัด</b><br>
        กดปุ่มสีแดงมุมขวาล่าง เพื่อโทร 1669 ได้ทันที ไม่ต้องรอทำแบบทดสอบ
    </div>
    """, unsafe_allow_html=True)

# ==================== ขั้นตอนที่ 1: ข้อมูลส่วนตัว (สั้นที่สุด) ====================
elif st.session_state.step == "step1":
    show_progress(1, 3, "ข้อมูลของคุณ")
    st.markdown("### 👤 กรุณากรอกข้อมูล")

    name = st.text_input("ชื่อของคุณ", value=st.session_state.form.get("name", ""))
    age = st.number_input("อายุ (ปี)", min_value=40, max_value=120,
                           value=st.session_state.form.get("age", 60))

    st.markdown("**เพศ**")
    gender = st.radio("เพศ", ["ชาย", "หญิง"], horizontal=True, label_visibility="collapsed",
                       index=0 if st.session_state.form.get("gender", "ชาย") == "ชาย" else 1)

    st.markdown("**คุณมีโรคประจำตัวอะไรบ้าง?** (เลือกได้มากกว่า 1)")
    chronic = st.multiselect("โรคประจำตัว", CHRONIC_DISEASES,
                              default=st.session_state.form.get("chronic", []),
                              label_visibility="collapsed")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ กลับหน้าแรก"):
            go_to("home")
            st.rerun()
    with col2:
        if st.button("ถัดไป ➡️", type="primary"):
            if not name.strip():
                st.error("กรุณากรอกชื่อก่อนนะครับ/คะ")
            else:
                st.session_state.form.update({
                    "name": name, "age": age, "gender": gender, "chronic": chronic,
                })
                go_to("step2")
                st.rerun()

# ==================== ขั้นตอนที่ 2: เลือกอาการ (ทีละกลุ่ม ปุ่มใหญ่) ====================
elif st.session_state.step == "step2":
    show_progress(2, 3, "อาการของคุณ")
    st.markdown("### 🤒 วันนี้คุณรู้สึกอย่างไร?")
    st.markdown("แตะเลือกอาการที่ตรงกับตัวคุณตอนนี้ (เลือกได้หลายข้อ)")

    selected_symptoms = st.session_state.form.get("selected_symptoms", [])

    for category, symptoms in SYMPTOMS_DATA.items():
        st.markdown(f"#### {CATEGORY_LABEL[category]}")
        for symptom in symptoms:
            checked = symptom in selected_symptoms
            new_val = st.checkbox(symptom, value=checked, key=f"chk_{symptom}")
            if new_val and symptom not in selected_symptoms:
                selected_symptoms.append(symptom)
            elif not new_val and symptom in selected_symptoms:
                selected_symptoms.remove(symptom)

    st.session_state.form["selected_symptoms"] = selected_symptoms

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ ย้อนกลับ"):
            go_to("step1")
            st.rerun()
    with col2:
        if st.button("ดูผลลัพธ์ ➡️", type="primary"):
            if not selected_symptoms:
                st.warning("กรุณาเลือกอาการอย่างน้อย 1 ข้อก่อนนะครับ/คะ")
            else:
                go_to("result")
                st.rerun()

# ==================== ขั้นตอนที่ 3: แสดงผลแบบง่าย ====================
elif st.session_state.step == "result":
    show_progress(3, 3, "ผลการตรวจ")

    form = st.session_state.form
    name = form.get("name", "")
    age = form.get("age", 0)
    chronic = form.get("chronic", [])
    selected_symptoms = form.get("selected_symptoms", [])

    total_score = 0
    emergency_hit = False
    for category, symptoms in SYMPTOMS_DATA.items():
        for s in selected_symptoms:
            if s in symptoms:
                total_score += symptoms[s]
                if category == "แดง":
                    emergency_hit = True

    risk_multiplier = 1.0
    if age >= 70: risk_multiplier += 0.3
    elif age >= 60: risk_multiplier += 0.2
    if "โรคหัวใจ" in chronic: risk_multiplier += 0.3
    if "โรคไต" in chronic: risk_multiplier += 0.2
    if "เบาหวาน" in chronic: risk_multiplier += 0.1

    final_score = int(total_score * risk_multiplier)

    if emergency_hit or final_score >= 50:
        risk_level = "สูง"
        st.markdown("""
        <div class="result-red">
            <h2>🚨 ควรไปโรงพยาบาลทันที</h2>
            <p>กดปุ่มด้านล่างเพื่อโทรขอความช่วยเหลือเดี๋ยวนี้</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <a href="tel:1669" style="display:block; background:#B71C1C; color:white; text-align:center;
        padding:24px; border-radius:16px; font-size:28px; font-weight:800; text-decoration:none; margin:10px 0;">
        📞 กดโทร 1669 เดี๋ยวนี้
        </a>
        """, unsafe_allow_html=True)
        send_line_message(f"🚨 แจ้งเตือน: {name} อายุ {age} ปี มีอาการเสี่ยงสูง คะแนน {final_score}")
    elif final_score >= 20:
        risk_level = "กลาง"
        st.markdown("""
        <div class="result-yellow">
            <h2>⚠️ ควรไปพบแพทย์ภายใน 1-2 วัน</h2>
            <p>อาการยังไม่ฉุกเฉิน แต่ไม่ควรปล่อยไว้นาน</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        risk_level = "ต่ำ"
        st.markdown("""
        <div class="result-green">
            <h2>✅ ดูแลตัวเองที่บ้านได้</h2>
            <p>พักผ่อนให้เพียงพอ ถ้าอาการแย่ลงให้กลับมาตรวจใหม่</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="simple-box">
        <b>👤 ชื่อ:</b> {name} &nbsp; <b>อายุ:</b> {age} ปี<br>
        <b>🤒 อาการที่เลือก:</b> {' , '.join(selected_symptoms)}
    </div>
    """, unsafe_allow_html=True)

    record = {
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "name": name, "age": age, "gender": form.get("gender", ""),
        "chronic": " | ".join(chronic) if chronic else "ไม่มี",
        "score": final_score, "risk": risk_level,
        "symptoms": " | ".join(selected_symptoms),
    }
    if not st.session_state.get("saved_this_result", False):
        save_to_csv(record)
        st.session_state.saved_this_result = True

    st.success("✅ บันทึกผลเรียบร้อยแล้ว")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 ตรวจอีกครั้ง"):
            st.session_state.form = {}
            st.session_state.saved_this_result = False
            go_to("step1")
            st.rerun()
    with col2:
        if st.button("🏠 กลับหน้าแรก"):
            st.session_state.form = {}
            st.session_state.saved_this_result = False
            go_to("home")
            st.rerun()

# ==================== หน้าประวัติ (แบบง่าย ไม่มีกราฟซับซ้อน) ====================
elif st.session_state.step == "history":
    st.markdown("### 📋 ประวัติการตรวจของคุณ")
    df = load_data()

    if df.empty:
        st.markdown("""
        <div class="simple-box" style="text-align:center;">
            ยังไม่มีประวัติการตรวจ
        </div>
        """, unsafe_allow_html=True)
    else:
        df_sorted = df.sort_values(by="date", ascending=False)
        for _, row in df_sorted.iterrows():
            color = {"สูง": "#D32F2F", "กลาง": "#F57C00", "ต่ำ": "#2E7D32"}.get(row.get("risk", ""), "#555")
            st.markdown(f"""
            <div class="simple-box" style="border-color:{color};">
                <b>📅 {row.get('date','-')}</b><br>
                ชื่อ: {row.get('name','-')} &nbsp; อายุ: {row.get('age','-')} ปี<br>
                ระดับความเสี่ยง: <span style="color:{color}; font-weight:800;">{row.get('risk','-')}</span><br>
                อาการ: {row.get('symptoms','-')}
            </div>
            """, unsafe_allow_html=True)

        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 ดาวน์โหลดประวัติทั้งหมด (ไฟล์ CSV)", data=csv,
                            file_name=f"my_health_data_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv")

    if st.button("🏠 กลับหน้าแรก"):
        go_to("home")
        st.rerun()

# ==================== Footer เตือนความปลอดภัย ====================
st.markdown("---")
st.markdown("""
<p style="text-align:center; color:#777; font-size:16px;">
ระบบนี้เป็นเพียงเครื่องมือช่วยตัดสินใจเบื้องต้น ไม่ใช่การวินิจฉัยของแพทย์<br>
หากไม่แน่ใจ ควรปรึกษาแพทย์หรือโทร 1669
</p>
""", unsafe_allow_html=True)