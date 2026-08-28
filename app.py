import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
import os
import requests

warnings.filterwarnings('ignore')

# ==================== ตั้งค่า Line Notify ====================
LINE_NOTIFY_TOKEN = "ใส่_TOKEN_ของคุณที่นี่"

def send_line_notify(message):
    if LINE_NOTIFY_TOKEN == "ใส่_TOKEN_ของคุณที่นี่":
        return
    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    data = {"message": message}
    try:
        requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)
    except Exception:
        pass

# ==================== ตั้งค่าไฟล์เก็บข้อมูล ====================
DATA_FILE = "assessment_data.csv"
TEST_FILE = "test_cases.csv"

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
    if os.path.exists(DATA_FILE):
        try:
            return len(pd.read_csv(DATA_FILE, on_bad_lines='skip'))
        except:
            return 0
    return 0

def get_test_case_count():
    if os.path.exists(TEST_FILE):
        try:
            df_test = pd.read_csv(TEST_FILE, encoding='utf-8-sig')
            return len(df_test)
        except:
            return 0
    return 0

def update_record(index, updated_data):
    df = load_data()
    if 0 <= index < len(df):
        for key, value in updated_data.items():
            df.loc[index, key] = value
        df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
        return True
    return False

def delete_record(index):
    df = load_data()
    if 0 <= index < len(df):
        df = df.drop(index).reset_index(drop=True)
        df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
        return True
    return False

def add_test_case(new_case):
    """ฟังก์ชันกลางสำหรับเพิ่มเคสทดสอบ"""
    if os.path.exists(TEST_FILE):
        try:
            df_test = pd.read_csv(TEST_FILE, encoding='utf-8-sig')
            df_test.columns = [col.strip().lstrip('\ufeff') for col in df_test.columns]
            df_test = pd.concat([df_test, pd.DataFrame([new_case])], ignore_index=True)
        except:
            df_test = pd.DataFrame([new_case])
    else:
        df_test = pd.DataFrame([new_case])
    df_test.to_csv(TEST_FILE, index=False, encoding='utf-8-sig')
    return len(df_test)

# ==================== ตั้งค่าหน้าเว็บ ====================
st.set_page_config(
    page_title="ระบบประเมินสุขภาพส่วนตัว (40+)",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ตกแต่ง ====================
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); background-attachment: fixed; }
    .hero-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 60px 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
    .hero-section h1 { font-size: 3rem; font-weight: 800; margin-bottom: 15px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .page-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
    .page-header h1 { font-size: 2.2rem; font-weight: 700; margin: 0; }
    .metric-card { background: white; padding: 25px; border-radius: 15px; text-align: center; box-shadow: 0 8px 25px rgba(0,0,0,0.1); transition: all 0.3s ease; }
    .metric-card:hover { transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.2); }
    .metric-card h3 { color: #000000 !important; font-size: 1.8rem; font-weight: 700; margin: 10px 0; }
    .metric-card p { color: #000000 !important; font-size: 1rem; margin: 0; font-weight: 500; }
    .emergency-box { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); color: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 8px 25px rgba(255,75,43,0.4); margin: 15px 0; animation: pulse 2s infinite; }
    .emergency-box h3 { font-size: 2.5rem; margin: 10px 0; font-weight: 800; }
    .emergency-box p { font-size: 1.1rem; margin: 5px 0; }
    @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.02); } }
    .risk-high { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); color: white; padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 15px 40px rgba(238,90,111,0.4); animation: pulse 2s infinite; }
    .risk-medium { background: linear-gradient(135deg, #ffa502 0%, #ff7f50 100%); color: white; padding: 30px; border-radius: 20px; text-align: center; }
    .risk-low { background: linear-gradient(135deg, #2ed573 0%, #7bed9f 100%); color: white; padding: 30px; border-radius: 20px; text-align: center; }
    .info-box { background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 25px; border-radius: 15px; border-left: 6px solid #667eea; box-shadow: 0 5px 20px rgba(0,0,0,0.1); margin: 20px 0; color: #000000 !important; }
    .info-box b { color: #000000 !important; }
    .section-title { color: #667eea; font-size: 1.8rem; font-weight: 700; margin: 30px 0 20px 0; padding-bottom: 10px; border-bottom: 3px solid #667eea; display: inline-block; }
    .footer { text-align: center; color: white; padding: 30px; margin-top: 50px; background: rgba(0,0,0,0.2); border-radius: 15px; }
    .stAlert, .stInfo, .element-container .stMarkdown { color: #000000 !important; }
</style>
""", unsafe_allow_html=True)

# ==================== ข้อมูลทางการแพทย์ (NCDs Focus) ====================
SYMPTOMS_DATA = {
    "🚨 อาการฉุกเฉิน (ต้องไปโรงพยาบาลทันที)": {
        "เจ็บหน้าอกร้าวลงแขนซ้าย/กราม": 40,
        "แขนขาอ่อนแรงครึ่งซีก/ปากเบี้ยว": 40,
        "พูดไม่ชัด/สับสนฉับพลัน": 35,
        "หายใจไม่ออก/หอบเหนื่อยขณะพัก": 35,
        "หมดสติ/วูบ/เป็นลม": 40,
        "ปวดศีรษะรุนแรงที่สุดในชีวิต": 35,
        "อาเจียนเป็นเลือด/ถ่ายดำ": 35,
        "ปวดท้องรุนแรงเฉียบพลัน": 30
    },
    "⚠️ อาการที่ต้องเฝ้าระวัง (พบแพทย์ภายใน 24-48 ชม.)": {
        "น้ำหนักลดลงผิดปกติ (>5% ใน 6 เดือน)": 20,
        "ใจสั่น/หัวใจเต้นผิดจังหวะ": 18,
        "เวียนศีรษะรุนแรง/ทรงตัวไม่ได้": 18,
        "บวมที่ขา/ข้อเท้าทั้งสองข้าง": 18,
        "ไข้สูง > 38.5°C ติดต่อกันเกิน 3 วัน": 15,
        "ปัสสาวะแสบขัด/มีเลือดปน": 15
    },
    "✅ อาการทั่วไป (ดูแลตัวเองได้)": {
        "ปวดเมื่อยตามตัว/ปวดหลัง": 4,
        "ปวดข้อเข่า/ข้อเสื่อม": 5,
        "นอนไม่หลับ/หลับไม่สนิท": 4,
        "อ่อนเพลียเล็กน้อย": 4,
        "ไอ/เจ็บคอ/มีน้ำมูก": 5,
        "อาหารไม่ย่อย/แสบร้อนกลางอก": 5,
        "ท้องผูกเล็กน้อย": 3,
        "ปวดศีรษะตึงๆ เป็นบางครั้ง": 5
    }
}

CHRONIC_DISEASES = [
    "เบาหวาน", "ความดันโลหิตสูง", "โรคหัวใจและหลอดเลือด",
    "ไขมันในเลือดสูง", "โรคไตเรื้อรัง", "โรคอ้วน (BMI ≥ 30)",
    "โรคปอดอุดกั้นเรื้อรัง (COPD)", "ไม่มี"
]

FAMILY_HISTORY_OPTIONS = [
    "เบาหวาน", "ความดันโลหิตสูง", "โรคหัวใจและหลอดเลือด", 
    "โรคหลอดเลือดสมอง (Stroke)", "โรคไตเรื้อรัง", "ไม่มี"
]

# ==================== 🧠 ฟังก์ชันคำนวณความเสี่ยงกลาง (Single Source of Truth) ====================
def calculate_risk(age, systolic, diastolic, bs, chronic_list, family_history_list, symptoms_list):
    total_score = 0
    emergency_symptoms = []

    # 1. คะแนนจากอาการ
    for symptom in symptoms_list:
        symptom = symptom.strip()
        for category, symptoms_dict in SYMPTOMS_DATA.items():
            if symptom in symptoms_dict:
                total_score += symptoms_dict[symptom]
                if "ฉุกเฉิน" in category:
                    emergency_symptoms.append(symptom)

    # 2. คะแนนจาก BP
    bp_emergency = False
    if systolic >= 180 or diastolic >= 110:
        total_score += 40
        bp_emergency = True
        emergency_symptoms.append(f"BP {systolic}/{diastolic} mmHg")
    elif systolic >= 140 or diastolic >= 90:
        total_score += 15

    # 3. คะแนนจาก BS
    bs_emergency = False
    if bs < 70:
        total_score += 25
        bs_emergency = True
        emergency_symptoms.append(f"BS {bs} mg/dL (ต่ำ)")
    elif bs > 250:
        total_score += 25
        bs_emergency = True
        emergency_symptoms.append(f"BS {bs} mg/dL (สูง)")
    elif bs >= 126:
        total_score += 10

    # 4. คะแนนจาก Family History
    fh_multiplier_add = 0.0
    for disease in family_history_list:
        d = disease.strip()
        if d and d != "ไม่มี":
            total_score += 5
            fh_multiplier_add += 0.05

    # 5. Risk Multiplier
    risk_multiplier = 1.0 + fh_multiplier_add
    if age >= 70: risk_multiplier += 0.3
    elif age >= 60: risk_multiplier += 0.2
    elif age >= 50: risk_multiplier += 0.1

    for disease in chronic_list:
        d = disease.strip()
        if d == "โรคหัวใจและหลอดเลือด": risk_multiplier += 0.3
        elif d == "โรคไตเรื้อรัง": risk_multiplier += 0.2
        elif d == "เบาหวาน": risk_multiplier += 0.1

    final_score = int(total_score * risk_multiplier)
    is_emergency = len(emergency_symptoms) > 0 or bp_emergency or bs_emergency

    if final_score >= 50 or is_emergency:
        return "สูง", final_score, total_score, risk_multiplier, emergency_symptoms
    elif final_score >= 20:
        return "กลาง", final_score, total_score, risk_multiplier, emergency_symptoms
    else:
        return "ต่ำ", final_score, total_score, risk_multiplier, emergency_symptoms

# ==================== Sidebar ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: white;">
        <h2 style="font-size: 2rem; margin: 0;">🏥</h2>
        <h3 style="font-size: 1.3rem; margin: 10px 0;">Health Check</h3>
        <p style="font-size: 0.9rem; opacity: 0.9;">ระบบประเมินสุขภาพส่วนตัว</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div class="emergency-box">
        <h3>🚑 1669</h3>
        <p><br>เจ็บป่วยฉุกเฉิน</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    elderly_mode = st.checkbox("👓 โหมดตัวหนังสือใหญ่")
    if elderly_mode:
        st.markdown("<style> html { font-size: 125% !important; } </style>", unsafe_allow_html=True)

    menu = st.radio(
        "เมนูหลัก",
        ["🏠 หน้าหลัก", "🩺 ประเมินอาการใหม่", "📋 ประวัติการประเมินของฉัน", 
         " สถิติส่วนตัว", "🧪 ทดสอบความแม่นยำ", "📝 เพิ่มเคสทดสอบ", "ℹ️ เกี่ยวกับ"],
        index=1
    )
    st.markdown("---")
    data_count = get_data_count()
    test_count = get_test_case_count()
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; text-align: center; color: white;">
        <p style="margin: 0; font-size: 0.9rem;">📊 ข้อมูลของคุณ</p>
        <h3 style="margin: 10px 0; font-size: 2rem;">{data_count}</h3>
        <p style="margin: 0; font-size: 0.8rem;">รายการประเมิน</p>
        <p style="margin: 10px 0 0 0; font-size: 0.8rem;">🧪 {test_count} เคสทดสอบ</p>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ==================== หน้า 1: หน้าหลัก ====================
if menu == "🏠 หน้าหลัก":
    st.markdown("""
    <div class="hero-section">
        <h1> ระบบประเมินสุขภาพส่วนตัว</h1>
        <h3>สำหรับวัยกลางคนและผู้สูงอายุ (40+ ปี)</h3>
        <p style="font-size: 1.1rem; margin-top: 20px; opacity: 0.9;">
            ประเมินอาการด้วยตัวเอง • บันทึกข้อมูลส่วนตัว • ติดตามผลสุขภาพ
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="emergency-box">
        <h3>🚑 เบอร์ฉุกเฉินทางการแพทย์</h3>
        <p style="font-size: 2rem; font-weight: bold; margin: 10px 0;">1669</p>
        <p>ศูนย์นเรนทร - เจ็บป่วยฉุกเฉิน ฟรี 24 ชม.</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f'<div class="metric-card"><h3>📋 {get_data_count()}</h3><p>การประเมินของคุณ</p></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="metric-card"><h3>🧪 {test_count}</h3><p>เคสทดสอบ</p></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="metric-card"><h3> ปลอดภัย</h3><p>เก็บในเครื่องคุณ</p></div>', unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-title">📝 วิธีใช้งาน</h2>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    with col_a: st.markdown('<div style="background: rgba(255,255,255,0.95); padding: 20px; border-radius: 12px; color: black;"><b>1. ประเมินอาการ</b><br>- กรอกข้อมูลส่วนตัว<br>- เลือกอาการที่เป็น<br>- ระบบคำนวณความเสี่ยง</div>', unsafe_allow_html=True)
    with col_b: st.markdown('<div style="background: rgba(255,255,255,0.95); padding: 20px; border-radius: 12px; color: black;"><b>2. บันทึกข้อมูล</b><br>- ข้อมูลจะถูกบันทึกอัตโนมัติ<br>- เก็บเป็นไฟล์ CSV<br>- เปิดดูใน Excel ได้</div>', unsafe_allow_html=True)
    with col_c: st.markdown('<div style="background: rgba(255,255,255,0.95); padding: 20px; border-radius: 12px; color: black;"><b>3. ดูประวัติ</b><br>- ดูผลการประเมินย้อนหลัง<br>- เปรียบเทียบผลลัพธ์<br>- ดาวน์โหลดข้อมูล</div>', unsafe_allow_html=True)

# ==================== หน้า 2: ประเมินอาการใหม่ ====================
elif menu == "🩺 ประเมินอาการใหม่":
    st.markdown('<div class="page-header"><h1>🩺 แบบประเมินอาการ</h1></div>', unsafe_allow_html=True)

    with st.form("assessment_form", clear_on_submit=False):
        st.markdown('<h3 class="section-title"> ข้อมูลส่วนตัวของคุณ</h3>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: name = st.text_input("ชื่อ-นามสกุล *", placeholder="กรอกชื่อของคุณ")
        with col2: age = st.number_input("อายุ (ปี) *", min_value=40, max_value=120, value=45)
        with col3: gender = st.selectbox("เพศ *", ["ชาย", "หญิง", "ไม่ระบุ"])

        st.markdown('<h3 class="section-title">🏥 ข้อมูลสุขภาพ</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1: chronic = st.multiselect("โรคประจำตัว", CHRONIC_DISEASES)
        with col2: medications = st.text_input("ยาที่รับประทานประจำ (ถ้ามี)", placeholder="เช่น ยาลดความดัน, ยาเบาหวาน")
        
        st.markdown('<h4 style="color: #667eea; margin-top: 15px;">🩸 ค่าความดันและน้ำตาลในเลือดล่าสุด</h4>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: systolic = st.number_input("ความดันตัวบน (Systolic) mmHg", min_value=70, max_value=300, value=120)
        with col2: diastolic = st.number_input("ความดันตัวล่าง (Diastolic) mmHg", min_value=40, max_value=200, value=80)
        with col3: bs = st.number_input("ระดับน้ำตาลในเลือด (mg/dL)", min_value=0, max_value=600, value=100)

        st.markdown('<h4 style="color: #667eea; margin-top: 15px;"> ประวัติสุขภาพครอบครัว</h4>', unsafe_allow_html=True)
        family_history = st.multiselect("เลือกโรคที่คนในครอบครัวเคยเป็น", FAMILY_HISTORY_OPTIONS)

        st.markdown('<h4 style="color: #667eea; margin-top: 15px;">📏 ส่วนสูงและน้ำหนัก</h4>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1: height = st.number_input("ส่วนสูง (ซม.)", min_value=100, max_value=250, value=160)
        with col2: weight = st.number_input("น้ำหนัก (กก.)", min_value=30, max_value=200, value=60)
        
        bmi = weight / ((height/100) ** 2)
        if bmi < 18.5: bmi_status = "ผอม"
        elif bmi < 23: bmi_status = "ปกติ"
        elif bmi < 25: bmi_status = "ท้วม"
        else: bmi_status = "อ้วน"
        st.info(f" **ค่า BMI ของคุณ:** {bmi:.1f} (**{bmi_status}**)")

        st.markdown('<h3 class="section-title"> อาการที่คุณกำลังประสบอยู่</h3>', unsafe_allow_html=True)
        selected_symptoms = []
        for category, symptoms in SYMPTOMS_DATA.items():
            with st.expander(category, expanded=("ฉุกเฉิน" in category)):
                cols = st.columns(2)
                for i, (symptom, score) in enumerate(symptoms.items()):
                    with cols[i % 2]:
                        if st.checkbox(f"{symptom} (+{score} คะแนน)", key=f"symptom_{symptom}"):
                            selected_symptoms.append(symptom)

        notes = st.text_area("อธิบายอาการเพิ่มเติม (ถ้ามี)", placeholder="เช่น อาการเป็นมา 3 วัน", height=100)
        submitted = st.form_submit_button(" ประเมินผลตอนนี้", type="primary", use_container_width=True)

    if submitted:
        if not name:
            st.error("❌ กรุณากรอกชื่อ-นามสกุล")
        else:
            chronic_clean = [c for c in chronic if c != "ไม่มี"]
            fh_clean = [f for f in family_history if f != "ไม่มี"]
            
            risk_level, final_score, total_score, risk_multiplier, all_emergency = calculate_risk(
                age, systolic, diastolic, bs, chronic_clean, fh_clean, selected_symptoms
            )

            if risk_level == "สูง":
                st.markdown('<div class="risk-high"><h2 style="font-size: 2rem; margin: 0;">🚨 ความเสี่ยงสูง!</h2><p style="font-size: 1.3rem; margin: 10px 0 0 0;">กรุณาไปพบแพทย์ทันที</p></div>', unsafe_allow_html=True)
                st.markdown('<div class="emergency-box"><h3>📞 โทรด่วน 1669</h3><p>บริการฟรี 24 ชั่วโมง</p></div>', unsafe_allow_html=True)
                line_msg = f"🚨 แจ้งเตือนฉุกเฉิน!\nชื่อ: {name}\nอายุ: {age} ปี\nคะแนน: {final_score}\nอาการ/ค่าวิกฤต: {' | '.join(all_emergency)}"
                send_line_notify(line_msg)
            elif risk_level == "กลาง":
                st.markdown('<div class="risk-medium"><h2 style="font-size: 2rem; margin: 0;">⚠️ ความเสี่ยงกลาง</h2><p style="font-size: 1.3rem; margin: 10px 0 0 0;">ควรพบแพทย์ภายใน 24 ชั่วโมง</p></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="risk-low"><h2 style="font-size: 2rem; margin: 0;">✅ ความเสี่ยงต่ำ</h2><p style="font-size: 1.3rem; margin: 10px 0 0 0;">ดูแลตัวเองได้</p></div>', unsafe_allow_html=True)

            st.markdown("---")
            st.markdown('<h3 class="section-title">📊 สรุปผลการประเมิน</h3>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="info-box">
                    <b>👤 ข้อมูลผู้ประเมิน:</b><br>
                    • ชื่อ: {name} | อายุ: {age} ปี | เพศ: {gender}<br>
                    • โรคประจำตัว: {' | '.join(chronic) if chronic else 'ไม่มี'}<br>
                    • ประวัติครอบครัว: {' | '.join(family_history) if family_history else 'ไม่มี'}
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="info-box">
                    <b>📊 ผลการประเมิน:</b><br>
                    • คะแนนดิบ: {total_score} | ตัวคูณ: {risk_multiplier:.2f}x<br>
                    • <b>คะแนนรวม: {final_score}</b> | ระดับ: {risk_level}<br>
                    • BP: {systolic}/{diastolic} mmHg | BS: {bs} mg/dL<br>
                    • BMI: {bmi:.1f} ({bmi_status})
                </div>""", unsafe_allow_html=True)

            if all_emergency:
                st.markdown('<h4 style="color: #ff4b2b;">🚨 ปัจจัยที่กระตุ้นความเสี่ยงสูง:</h4>')
                for item in all_emergency: st.markdown(f"• {item}")
            if selected_symptoms:
                st.markdown(f'<h4>อาการที่เลือก ({len(selected_symptoms)} อาการ)</h4>')
                for s in selected_symptoms: st.markdown(f"• {s}")

            record = {
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "name": name, "age": age, "gender": gender,
                "chronic": " | ".join(chronic) if chronic else "ไม่มี",
                "medications": medications if medications else "ไม่มี",
                "systolic": systolic, "diastolic": diastolic, "bs": bs,
                "family_history": " | ".join(family_history) if family_history else "ไม่มี",
                "bmi": f"{bmi:.1f}", "bmi_status": bmi_status,
                "score": final_score, "risk": risk_level,
                "symptoms": " | ".join(selected_symptoms),
                "notes": notes if notes else "-"
            }
            save_to_csv(record)
            st.success(f"✅ บันทึกเรียบร้อย! (รวม {get_data_count()} รายการ)")

            # ✨ ฟีเจอร์ใหม่: ปุ่มเพิ่มเป็นเคสทดสอบทันทีหลังประเมิน
            st.markdown("---")
            st.markdown("###  ช่วยพัฒนาระบบให้แม่นยำขึ้น")
            st.info("💡 หากท่านเป็นบุคลากรทางการแพทย์ หรือต้องการช่วยทดสอบระบบ กรุณาระบุว่าเคสนี้ควรได้ความเสี่ยงระดับไหน")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                expected_for_test = st.selectbox(
                    "เคสนี้ควรได้ความเสี่ยงระดับไหน? (สำหรับทดสอบระบบ)",
                    ["ต่ำ", "กลาง", "สูง"],
                    key=f"expected_test_{name}_{datetime.now().strftime('%H%M%S')}",
                    index=["ต่ำ", "กลาง", "สูง"].index(risk_level)
                )
            with col2:
                if st.button(" เพิ่มเป็นเคสทดสอบ", key=f"add_test_now_{name}", type="secondary"):
                    new_test_case = {
                        "name": f"{name}_ประเมินใหม่_{datetime.now().strftime('%Y%m%d_%H%M')}",
                        "age": age,
                        "gender": gender,
                        "systolic": systolic,
                        "diastolic": diastolic,
                        "bs": bs,
                        "chronic": " | ".join(chronic) if chronic else "ไม่มี",
                        "family_history": " | ".join(family_history) if family_history else "ไม่มี",
                        "symptoms": " | ".join(selected_symptoms) if selected_symptoms else "ไม่มี",
                        "expected_risk": expected_for_test
                    }
                    
                    total_count = add_test_case(new_test_case)
                    st.success(f"✅ เพิ่มเคสทดสอบเรียบร้อย! (รวม {total_count} เคส)")
                    st.balloons()
                    st.info("🙏 ขอบคุณที่ช่วยพัฒนาระบบให้แม่นยำขึ้น!")

            st.markdown("---")
            if st.button("🖨️ สร้างใบสรุปผลสุขภาพ (สำหรับพิมพ์ / บันทึก PDF)", type="secondary", use_container_width=True):
                st.markdown(f"""
                <div style="background: white; color: black; padding: 30px; border-radius: 10px; border: 2px solid #333; font-family: sans-serif; line-height: 1.6;">
                    <h2 style="text-align: center; color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px;">🏥 ใบสรุปผลการประเมินสุขภาพเบื้องต้น</h2>
                    <p><b>วันที่ประเมิน:</b> {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
                    <hr style="border: 1px solid #ccc;">
                    <p><b>ชื่อ-นามสกุล:</b> {name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>อายุ:</b> {age} ปี &nbsp;&nbsp;|&nbsp;&nbsp; <b>เพศ:</b> {gender}</p>
                    <p><b>โรคประจำตัว:</b> {' | '.join(chronic) if chronic else 'ไม่มี'}</p>
                    <p><b>ประวัติครอบครัว:</b> {' | '.join(family_history) if family_history else 'ไม่มี'}</p>
                    <p><b>ค่า BMI:</b> {bmi:.1f} ({bmi_status}) &nbsp;&nbsp;|&nbsp;&nbsp; <b>ความดัน:</b> {systolic}/{diastolic} mmHg &nbsp;&nbsp;|&nbsp;&nbsp; <b>น้ำตาล:</b> {bs} mg/dL</p>
                    <hr style="border: 1px solid #ccc;">
                    <h3 style="text-align: center; color: {'#d32f2f' if risk_level == 'สูง' else ('#f57c00' if risk_level == 'กลาง' else '#388e3c')};">
                        ผลการประเมิน: ระดับความเสี่ยง "{risk_level}" (คะแนนรวม: {final_score})
                    </h3>
                    <p><b>อาการที่พบ:</b> {' | '.join(selected_symptoms) if selected_symptoms else 'ไม่มีอาการเฉพาะเจาะจง'}</p>
                    <p><b>คำแนะนำ:</b> {' กรุณาไปพบแพทย์ทันที (โทร 1669)' if risk_level == 'สูง' else ('⚠️ ควรพบแพทย์ภายใน 24 ชั่วโมง' if risk_level == 'กลาง' else '✅ ดูแลตัวเองได้ตามปกติ')}</p>
                    {f'<p><b>หมายเหตุ:</b> {notes}</p>' if notes != '-' else ''}
                    <hr style="border: 1px solid #ccc;">
                    <p style="font-size: 0.8em; color: gray; text-align: center; margin-top: 20px;">
                        *เอกสารนี้สร้างขึ้นจากระบบประเมินเบื้องต้น ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้<br>
                        🚑 <b>เบอร์ฉุกเฉิน: 1669</b><br>
                        หากรู้สึกไม่สบาย กรุณาไปพบแพทย์ที่โรงพยาบาลทันที
                    </p>
                </div>
                """, unsafe_allow_html=True)
                st.info("💡 **เคล็ดลับ:** กด `Ctrl + P` (หรือ `Cmd + P` บน Mac) บนคีย์บอร์ด แล้วเลือก 'Save as PDF' (บันทึกเป็น PDF) เพื่อเก็บไฟล์นี้ไว้")

# ==================== หน้า 3: ประวัติ ====================
elif menu == "📋 ประวัติการประเมินของฉัน":
    st.markdown('<div class="page-header"><h1>📋 ประวัติการประเมินของคุณ</h1></div>', unsafe_allow_html=True)
    df = load_data()
    if df.empty:
        st.markdown('<div class="info-box" style="text-align: center; padding: 40px;"><h3 style="color: #667eea; margin: 0;">📭 ยังไม่มีข้อมูล</h3></div>', unsafe_allow_html=True)
    else:
        st.success(f"✅ พบข้อมูล **{len(df)} รายการ**")
        tab1, tab2, tab3 = st.tabs(["👁️ ดูข้อมูล", "✏️ แก้ไข/ลบ", "📥 ดาวน์โหลด"])
        with tab1:
            st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True, height=400)
            if len(df) > 0:
                sel = st.selectbox("เลือกรายการ", range(len(df)), format_func=lambda x: f"{df.iloc[x]['date']} - {df.iloc[x]['name']} ({df.iloc[x]['risk']})")
                if sel is not None:
                    r = df.iloc[sel]
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**ชื่อ:** {r['name']} | **อายุ:** {r['age']} | **เพศ:** {r['gender']}")
                        st.write(f"**โรคประจำตัว:** {r['chronic']}")
                        st.write(f"**BP:** {r.get('systolic','-')}/{r.get('diastolic','-')} | **BS:** {r.get('bs','-')}")
                    with c2:
                        st.write(f"**คะแนน:** {r['score']} | **ความเสี่ยง:** {r['risk']}")
                        st.write(f"**BMI:** {r.get('bmi','-')} ({r.get('bmi_status','-')})")
                        st.write(f"**อาการ:** {r['symptoms']}")
                    
                    # ✨ เพิ่มเป็นเคสทดสอบจากประวัติ
                    st.markdown("---")
                    st.markdown("### 🧪 บันทึกเคสนี้เป็นข้อมูลทดสอบ")
                    st.info("💡 ใช้ฟีเจอร์นี้เพื่อช่วยพัฒนาระบบให้แม่นยำขึ้น")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        expected_risk_test = st.selectbox(
                            "เคสนี้ควรได้ความเสี่ยงระดับไหน? (สำหรับทดสอบระบบ)",
                            ["ต่ำ", "กลาง", "สูง"],
                            key=f"expected_{sel}",
                            index=["ต่ำ", "กลาง", "สูง"].index(r['risk'])
                        )
                    with col2:
                        if st.button("➕ เพิ่มเป็นเคสทดสอบ", key=f"add_test_{sel}", type="secondary"):
                            new_test_case = {
                                "name": f"{r['name']}_{r['date'].replace('/','-').replace(':','-')}",
                                "age": int(r['age']) if pd.notna(r.get('age')) else 45,
                                "gender": r['gender'],
                                "systolic": int(r.get('systolic', 120)) if pd.notna(r.get('systolic')) else 120,
                                "diastolic": int(r.get('diastolic', 80)) if pd.notna(r.get('diastolic')) else 80,
                                "bs": int(r.get('bs', 100)) if pd.notna(r.get('bs')) else 100,
                                "chronic": r['chronic'],
                                "family_history": r.get('family_history', 'ไม่มี'),
                                "symptoms": r['symptoms'],
                                "expected_risk": expected_risk_test
                            }
                            
                            total_count = add_test_case(new_test_case)
                            st.success(f"✅ เพิ่มเคสทดสอบเรียบร้อย! (รวม {total_count} เคส)")
                            st.balloons()
        
        with tab2:
            if len(df) > 0:
                edit_idx = st.selectbox("เลือกรายการ", range(len(df)), format_func=lambda x: f"{df.iloc[x]['date']} - {df.iloc[x]['name']}", key="edit_sel")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🗑️ ลบ", type="secondary"):
                        if delete_record(edit_idx): st.success("ลบแล้ว!"); st.rerun()
                with c2:
                    nr = st.selectbox("แก้ความเสี่ยง", ["ต่ำ", "กลาง", "สูง"], index=["ต่ำ", "กลาง", "สูง"].index(str(df.iloc[edit_idx]['risk'])))
                    if st.button("💾 บันทึก"):
                        update_record(edit_idx, {'risk': nr}); st.success("อัปเดตแล้ว!"); st.rerun()
        with tab3:
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 ดาวน์โหลด CSV", csv, f'health_{datetime.now().strftime("%Y%m%d")}.csv', 'text/csv', use_container_width=True)

# ==================== หน้า 4: สถิติ ====================
elif menu == "📊 สถิติส่วนตัว":
    st.markdown('<div class="page-header"><h1>📊 สถิติการประเมินของคุณ</h1></div>', unsafe_allow_html=True)
    df = load_data()
    if df.empty:
        st.info("💡 ยังไม่มีข้อมูล")
    else:
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="metric-card"><h3>📋 {len(df)}</h3><p>ทั้งหมด</p></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><h3>🚨 {len(df[df["risk"]=="สูง"])}</h3><p>เสี่ยงสูง</p></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><h3> {df["score"].mean():.1f}</h3><p>คะแนนเฉลี่ย</p></div>', unsafe_allow_html=True)
        rc = df['risk'].value_counts().reset_index()
        rc.columns = ['ระดับ', 'จำนวน']
        fig = px.pie(rc, values='จำนวน', names='ระดับ', color='ระดับ', color_discrete_map={'ต่ำ':'#2ed573','กลาง':'#ffa502','สูง':'#ff6b6b'}, hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

# ==================== หน้า 5: ทดสอบความแม่นยำ ====================
elif menu == "🧪 ทดสอบความแม่นยำ":
    st.markdown('<div class="page-header"><h1>🧪 ทดสอบความแม่นยำของระบบ</h1></div>', unsafe_allow_html=True)
    st.info("💡 หน้านี้ใช้ทดสอบว่าระบบประเมินความเสี่ยงได้ตรงกับเกณฑ์ทางการแพทย์หรือไม่")

    if not os.path.exists(TEST_FILE):
        st.error("❌ ไม่พบไฟล์ `test_cases.csv`")
        st.markdown("""
        <div class="info-box">
            <b>📝 วิธีสร้าง:</b><br>
            1. ไปที่หน้า "📝 เพิ่มเคสทดสอบ" เพื่อสร้างเคสทดสอบแรก<br>
            2. หรืออัปโหลดไฟล์ <code>test_cases.csv</code> ผ่าน GitHub
        </div>""", unsafe_allow_html=True)
    else:
        try:
            df_test = pd.read_csv(TEST_FILE, encoding='utf-8-sig')
            df_test.columns = [col.strip().lstrip('\ufeff') for col in df_test.columns]
            st.success(f"✅ โหลดข้อมูลทดสอบ **{len(df_test)} เคส** เรียบร้อยแล้ว")
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์: {str(e)}")
            st.stop()

        if st.button("🚀 เริ่มทดสอบความแม่นยำ", type="primary", use_container_width=True):
            try:
                from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
            except ImportError:
                st.error(" ต้องติดตั้ง scikit-learn: `pip install scikit-learn`")
                st.stop()

            results = []
            for _, row in df_test.iterrows():
                try:
                    chronic_list = [c.strip() for c in str(row['chronic']).split('|')] if pd.notna(row['chronic']) and str(row['chronic']).strip() != 'ไม่มี' else []
                    fh_list = [f.strip() for f in str(row['family_history']).split('|')] if pd.notna(row['family_history']) and str(row['family_history']).strip() != 'ไม่มี' else []
                    sym_list = [s.strip() for s in str(row['symptoms']).split('|')] if pd.notna(row['symptoms']) else []

                    predicted, final_score, raw_score, mult, _ = calculate_risk(
                        int(row['age']), int(row['systolic']), int(row['diastolic']),
                        int(row['bs']), chronic_list, fh_list, sym_list
                    )
                    results.append({
                        'ชื่อ': row['name'],
                        'คำตอบที่ถูกต้อง': str(row['expected_risk']).strip(),
                        'ระบบทำนาย': predicted,
                        'คะแนนรวม': final_score,
                        'ถูกต้อง': str(row['expected_risk']).strip() == predicted
                    })
                except Exception as e:
                    st.warning(f"⚠️ ข้ามเคส {row.get('name', 'Unknown')}: {str(e)}")
                    continue

            if not results:
                st.error("❌ ไม่มีเคสที่ทดสอบได้")
                st.stop()

            df_res = pd.DataFrame(results)
            y_true = df_res['คำตอบที่ถูกต้อง']
            y_pred = df_res['ระบบทำนาย']
            labels = ['ต่ำ', 'กลาง', 'สูง']

            acc = accuracy_score(y_true, y_pred)
            correct_n = df_res['ถูกต้อง'].sum()
            wrong_n = len(df_res) - correct_n

            st.markdown('<h3 class="section-title">📊 ผลการทดสอบ</h3>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(f'<div class="metric-card"><h3>{acc*100:.1f}%</h3><p>Accuracy</p></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card"><h3>{correct_n}/{len(df_res)}</h3><p>ตอบถูก</p></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card"><h3>{wrong_n}</h3><p>ตอบผิด</p></div>', unsafe_allow_html=True)
            with c4: st.markdown(f'<div class="metric-card"><h3>{len(df_res)}</h3><p>เคสทั้งหมด</p></div>', unsafe_allow_html=True)

            st.markdown('<h3 class="section-title">🔥 Confusion Matrix</h3>', unsafe_allow_html=True)
            cm = confusion_matrix(y_true, y_pred, labels=labels)
            fig_cm = go.Figure(data=go.Heatmap(
                z=cm, x=labels, y=labels,
                colorscale='Blues',
                text=cm, texttemplate='%{text}', textfont={"size": 24},
                hoverongaps=False
            ))
            fig_cm.update_layout(
                xaxis_title='ระบบทำนาย (Predicted)',
                yaxis_title='คำตอบที่ถูกต้อง (Expected)',
                height=400, width=500,
                yaxis=dict(autorange='reversed')
            )
            st.plotly_chart(fig_cm, use_container_width=False)

            st.markdown('<h3 class="section-title">📈 รายละเอียดแต่ละระดับ</h3>', unsafe_allow_html=True)
            report = classification_report(y_true, y_pred, labels=labels, target_names=labels, output_dict=True, zero_division=0)
            df_report = pd.DataFrame(report).transpose().round(3)
            st.dataframe(df_report, use_container_width=True)

            wrong_df = df_res[~df_res['ถูกต้อง']]
            if len(wrong_df) > 0:
                st.markdown('<h3 class="section-title">❌ เคสที่ระบบตอบผิด</h3>', unsafe_allow_html=True)
                st.dataframe(wrong_df[['ชื่อ', 'คำตอบที่ถูกต้อง', 'ระบบทำนาย', 'คะแนนรวม']], use_container_width=True)
                st.warning(f"⚠️ ระบบตอบผิด {len(wrong_df)} เคส จาก {len(df_res)} เคส")
            else:
                st.success("🎉 ระบบตอบถูกทุกเคส! (100% Accuracy)")

            st.markdown("---")
            st.markdown('<h3 class="section-title"> สรุปสำหรับเล่มรายงาน</h3>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="info-box">
                <b> ผลการทดสอบความแม่นยำของระบบ (Expert Validation)</b><br><br>
                • จำนวนเคสทดสอบ: <b>{len(df_res)} เคส</b><br>
                • ความแม่นยำรวม (Accuracy): <b>{acc*100:.1f}%</b><br>
                • จำนวนที่ตอบถูก: <b>{correct_n} เคส</b><br>
                • จำนวนที่ตอบผิด: <b>{wrong_n} เคส</b><br><br>
                <b>📌 ผลลัพธ์:</b> ระบบสามารถประเมินระดับความเสี่ยงได้ใกล้เคียงกับเกณฑ์ทางการแพทย์
                {'ในระดับที่น่าพึงพอใจ' if acc >= 0.80 else 'แต่ยังต้องปรับปรุง Logic เพิ่มเติม'}
            </div>""", unsafe_allow_html=True)

# ==================== หน้า 6: เพิ่มเคสทดสอบ ====================
elif menu == " เพิ่มเคสทดสอบ":
    st.markdown('<div class="page-header"><h1> เพิ่มเคสทดสอบใหม่</h1></div>', unsafe_allow_html=True)
    st.info("💡 ใช้หน้านี้เพื่อเพิ่มเคสทดสอบสำหรับประเมินความแม่นยำของระบบ")
    
    with st.form("add_test_case_form"):
        st.markdown('<h3 class="section-title">👤 ข้อมูลเคส</h3>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            test_name = st.text_input("ชื่อเคส", value=f"เคสที่_{get_test_case_count()+1}")
        with col2:
            test_age = st.number_input("อายุ", min_value=40, max_value=120, value=50)
        with col3:
            test_gender = st.selectbox("เพศ", ["ชาย", "หญิง", "ไม่ระบุ"])
        
        st.markdown('<h3 class="section-title">🏥 ข้อมูลสุขภาพ</h3>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            test_systolic = st.number_input("ความดันตัวบน (mmHg)", min_value=70, max_value=300, value=120)
        with col2:
            test_diastolic = st.number_input("ความดันตัวล่าง (mmHg)", min_value=40, max_value=200, value=80)
        with col3:
            test_bs = st.number_input("น้ำตาลในเลือด (mg/dL)", min_value=0, max_value=600, value=100)
        
        test_chronic = st.multiselect("โรคประจำตัว", CHRONIC_DISEASES)
        test_fh = st.multiselect("ประวัติครอบครัว", FAMILY_HISTORY_OPTIONS)
        
        st.markdown('<h3 class="section-title">🤒 อาการ</h3>', unsafe_allow_html=True)
        test_symptoms = []
        for category, symptoms in SYMPTOMS_DATA.items():
            with st.expander(category, expanded=False):
                for symptom in symptoms.keys():
                    if st.checkbox(symptom, key=f"test_{symptom}"):
                        test_symptoms.append(symptom)
        
        expected = st.selectbox("คำตอบที่ถูกต้อง (Expected Risk)", ["ต่ำ", "กลาง", "สูง"])
        
        submitted = st.form_submit_button("💾 บันทึกเป็นเคสทดสอบ", type="primary", use_container_width=True)
        
        if submitted:
            new_case = {
                "name": test_name,
                "age": test_age,
                "gender": test_gender,
                "systolic": test_systolic,
                "diastolic": test_diastolic,
                "bs": test_bs,
                "chronic": " | ".join(test_chronic) if test_chronic else "ไม่มี",
                "family_history": " | ".join(test_fh) if test_fh else "ไม่มี",
                "symptoms": " | ".join(test_symptoms) if test_symptoms else "ไม่มี",
                "expected_risk": expected
            }
            
            total_count = add_test_case(new_case)
            st.success(f"✅ บันทึกเคสทดสอบเรียบร้อย! (รวม {total_count} เคส)")
            st.balloons()
            st.info("🙏 ขอบคุณที่ช่วยพัฒนาระบบให้แม่นยำขึ้น!")

# ==================== หน้า 7: เกี่ยวกับ ====================
elif menu == "ℹ️ เกี่ยวกับ":
    st.markdown('<div class="page-header"><h1>ℹ️ เกี่ยวกับระบบ</h1></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        <b>🎓 ระบบประเมินการตัดสินใจไปพบแพทย์ (40+ ปี)</b><br><br>
        ระบบประเมินอาการสุขภาพด้วยตัวเอง เน้นคัดกรอง NCDs<br>
        <b>✅ ฟีเจอร์:</b> BP/BS แบบเรียลไทม์ + ประวัติครอบครัว + ทดสอบความแม่นยำ + เพิ่มเคสทดสอบ
    </div>""", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box" style="border-left-color: #ff6b6b;">
        <b>⚠️ ข้อจำกัด:</b> <b>ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้</b><br>
        <b>🚑 เบอร์ฉุกเฉิน:</b> 1669
    </div>""", unsafe_allow_html=True)

# ==================== Footer ====================
st.markdown("---")
st.markdown("""
<div class="footer">
    <p style="margin: 0; font-size: 1.1rem;">🏥 ระบบประเมินสุขภาพส่วนตัว (40+ ปี)</p>
    <p style="margin: 10px 0 0 0; font-size: 0.9rem; opacity: 0.8;">Streamlit • Python • Data Visualization</p>
    <p style="margin: 5px 0 0 0; font-size: 0.9rem;">🚑 เบอร์ฉุกเฉิน: 1669</p>
</div>""", unsafe_allow_html=True)