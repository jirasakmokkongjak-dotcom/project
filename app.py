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

def save_to_csv(data_dict):
    df_new = pd.DataFrame([data_dict])
    if os.path.exists(DATA_FILE):
        df_new.to_csv(DATA_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(DATA_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

def get_data_count():
    if os.path.exists(DATA_FILE):
        return len(pd.read_csv(DATA_FILE))
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

# ==================== ตั้งค่าหน้าเว็บ ====================
st.set_page_config(
    page_title="ระบบประเมินสุขภาพส่วนตัว (40+)",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ตกแต่งแบบ Modern UX/UI ====================
st.markdown("""
<style>
    /* ===== Global Styles ===== */
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background-color: #f4f7f6;
        font-family: 'Prompt', sans-serif;
    }
    
    /* ===== Headers ===== */
    .hero-section, .page-header {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        color: white;
        padding: 2.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 40px rgba(0, 131, 176, 0.25);
    }
    
    .hero-section h1, .page-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .hero-section h3, .page-header h3 {
        font-size: 1.2rem;
        font-weight: 400;
        opacity: 0.9;
        margin-top: 10px;
    }
    
    /* ===== Cards ===== */
    .metric-card, .info-box {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.03);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0, 131, 176, 0.15);
        border-color: #00b4db;
    }
    
    .metric-card h3 {
        color: #0083b0;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .metric-card p {
        color: #6c757d;
        font-size: 0.95rem;
        margin: 0;
        font-weight: 500;
    }
    
    /* ===== Risk Cards ===== */
    .risk-high {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(255, 75, 43, 0.3);
        animation: pulse 2s infinite;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(247, 151, 30, 0.3);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(17, 153, 142, 0.3);
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* ===== Info Box ===== */
    .info-box {
        background: linear-gradient(to right, #ffffff, #f8f9fa);
        border-left: 5px solid #00b4db;
    }
    
    .info-box b {
        color: #0083b0;
    }
    
    /* ===== Section Title ===== */
    .section-title {
        color: #0083b0;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #e0f2f1;
        display: inline-block;
    }
    
    /* ===== Buttons ===== */
    .stButton>button {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 131, 176, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 131, 176, 0.4);
    }
    
    .stButton>button[kind="secondary"] {
        background: #f8f9fa;
        color: #495057;
        border: 1px solid #dee2e6;
        box-shadow: none;
    }
    
    /* ===== Form Elements ===== */
    .stTextInput>div>div>input, 
    .stNumberInput>div>div>input, 
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        background-color: #fafafa;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, 
    .stNumberInput>div>div>input:focus, 
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #00b4db;
        background-color: white;
        box-shadow: 0 0 0 3px rgba(0, 180, 219, 0.15);
        outline: none;
    }
    
    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    /* ===== Tabs ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 2px solid #e0f2f1;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 500;
        color: #6c757d;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #e0f2f1;
        color: #0083b0;
        font-weight: 600;
    }
    
    /* ===== Footer ===== */
    .footer {
        text-align: center;
        color: #6c757d;
        padding: 2rem;
        margin-top: 4rem;
        background: white;
        border-radius: 20px 20px 0 0;
        box-shadow: 0 -5px 20px rgba(0,0,0,0.03);
    }
    
    /* ===== Scrollbar ===== */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: #00b4db; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #0083b0; }
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
        "ความดันโลหิตตัวบน ≥ 180 หรือตัวล่าง ≥ 110": 25,
        "ระดับน้ำตาลในเลือด < 70 หรือ > 250 mg/dL": 25,
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

# ==================== Sidebar ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem; color: #0083b0;">
        <div style="font-size: 3.5rem; margin-bottom: 10px;">🏥</div>
        <h2 style="font-size: 1.5rem; margin: 0; font-weight: 700;">Health Check</h2>
        <p style="font-size: 0.9rem; color: #6c757d; margin-top: 5px;">ระบบประเมินสุขภาพส่วนตัว</p>
        <p style="font-size: 0.8rem; color: #00b4db; font-weight: 600; background: #e0f2f1; display: inline-block; padding: 4px 12px; border-radius: 20px; margin-top: 10px;">สำหรับวัย 40+ ปี</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    elderly_mode = st.checkbox("👓 โหมดตัวหนังสือใหญ่", help="เพิ่มขนาดตัวอักษรสำหรับผู้สูงอายุ")
    if elderly_mode:
        st.markdown("<style> html { font-size: 125% !important; } </style>", unsafe_allow_html=True)
    
    menu = st.radio(
        "เมนูหลัก",
        ["🏠 หน้าหลัก", "🩺 ประเมินอาการ", "📋 ประวัติ", "📊 สถิติ", "ℹ️ เกี่ยวกับ"],
        index=1
    )
    
    st.markdown("---")
    
    data_count = get_data_count()
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%); padding: 1.5rem; border-radius: 16px; text-align: center; color: white; box-shadow: 0 8px 20px rgba(0, 131, 176, 0.3);">
        <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">ข้อมูลของคุณ</p>
        <h3 style="margin: 10px 0; font-size: 2.5rem; font-weight: 700;">{data_count}</h3>
        <p style="margin: 0; font-size: 0.85rem; opacity: 0.9;">รายการประเมิน</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ==================== หน้าที่ 1: หน้าหลัก ====================
if menu == "🏠 หน้าหลัก":
    st.markdown("""
    <div class="hero-section">
        <h1>🏥 ระบบประเมินสุขภาพส่วนตัว</h1>
        <h3>สำหรับวัยกลางคนและผู้สูงอายุ (40+ ปี)</h3>
        <p style="font-size: 1.1rem; margin-top: 20px; opacity: 0.95;">
            ประเมินอาการด้วยตัวเอง • บันทึกข้อมูลส่วนตัว • ติดตามผลสุขภาพ
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2.5rem;">📋</div>
            <h3>{get_data_count()}</h3>
            <p>การประเมินของคุณ</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2.5rem;">👤</div>
            <h3>ส่วนตัว</h3>
            <p>ข้อมูลเป็นของคุณ</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2.5rem;">🔒</div>
            <h3>ปลอดภัย</h3>
            <p>เก็บในเครื่องคุณ</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-title">📝 วิธีใช้งาน</h2>', unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""
        <div class="info-box">
            <h4 style="color: #0083b0; margin-top: 0;">1️⃣ ประเมินอาการ</h4>
            <ul style="margin: 10px 0; padding-left: 20px; color: #495057; line-height: 1.6;">
                <li>กรอกข้อมูลส่วนตัว</li>
                <li>เลือกอาการที่เป็น</li>
                <li>ระบบคำนวณความเสี่ยง</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="info-box">
            <h4 style="color: #0083b0; margin-top: 0;">2️⃣ บันทึกข้อมูล</h4>
            <ul style="margin: 10px 0; padding-left: 20px; color: #495057; line-height: 1.6;">
                <li>ข้อมูลจะถูกบันทึกอัตโนมัติ</li>
                <li>เก็บเป็นไฟล์ CSV</li>
                <li>เปิดดูใน Excel ได้</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown("""
        <div class="info-box">
            <h4 style="color: #0083b0; margin-top: 0;">3️⃣ ดูประวัติ</h4>
            <ul style="margin: 10px 0; padding-left: 20px; color: #495057; line-height: 1.6;">
                <li>ดูผลการประเมินย้อนหลัง</li>
                <li>เปรียบเทียบผลลัพธ์</li>
                <li>ดาวน์โหลดข้อมูล</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box" style="margin-top: 40px; padding: 2rem; border-left-color: #ff4b2b;">
        <b>⚠️ หมายเหตุสำคัญ:</b> ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น 
        <b>ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้</b> หากมีอาการรุนแรงหรือกังวลใจ 
        ควรปรึกษาแพทย์หรือบุคลากรทางการแพทย์โดยตรง
    </div>
    """, unsafe_allow_html=True)

# ==================== หน้าที่ 2: ประเมินอาการใหม่ ====================
elif menu == "🩺 ประเมินอาการ":
    st.markdown('<div class="page-header"><h1>🩺 แบบประเมินอาการ</h1></div>', unsafe_allow_html=True)

    with st.form("assessment_form", clear_on_submit=False):
        st.markdown('<h3 class="section-title">👤 ข้อมูลส่วนตัวของคุณ</h3>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: 
            name = st.text_input("ชื่อ-นามสกุล *", placeholder="กรอกชื่อของคุณ")
        with col2: 
            age = st.number_input("อายุ (ปี) *", min_value=40, max_value=120, value=45)
        with col3: 
            gender = st.selectbox("เพศ *", ["ชาย", "หญิง", "ไม่ระบุ"])

        st.markdown('<h3 class="section-title">🏥 ข้อมูลสุขภาพ</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            chronic = st.multiselect("โรคประจำตัว", CHRONIC_DISEASES)
        with col2:
            medications = st.text_input("ยาที่รับประทานประจำ (ถ้ามี)", placeholder="เช่น ยาลดความดัน, ยาเบาหวาน")
        
        col1, col2 = st.columns(2)
        with col1:
            bp = st.text_input("ความดันโลหิตล่าสุด", placeholder="เช่น 120/80")
        with col2:
            bs = st.number_input("ระดับน้ำตาลในเลือด (mg/dL)", min_value=0, max_value=600, value=100)
        
        st.markdown('<h3 class="section-title">🤒 อาการที่คุณกำลังประสบอยู่</h3>', unsafe_allow_html=True)
        st.info("💡 **คำแนะนำ:** เลือกอาการที่คุณกำลังเป็นอยู่ในขณะนี้ สามารถเลือกได้มากกว่า 1 อาการ", icon="💡")
        
        total_score = 0
        selected_symptoms = []
        emergency_symptoms = []

        for category, symptoms in SYMPTOMS_DATA.items():
            with st.expander(category, expanded=True):
                cols = st.columns(2)
                for i, (symptom, score) in enumerate(symptoms.items()):
                    with cols[i % 2]:
                        if st.checkbox(f"{symptom} (+{score} คะแนน)", key=f"symptom_{symptom}"):
                            total_score += score
                            selected_symptoms.append(symptom)
                            if "ฉุกเฉิน" in category: 
                                emergency_symptoms.append(symptom)

        st.markdown('<h3 class="section-title">📝 หมายเหตุเพิ่มเติม</h3>', unsafe_allow_html=True)
        notes = st.text_area(
            "อธิบายอาการเพิ่มเติม (ถ้ามี)", 
            placeholder="เช่น อาการเป็นมา 3 วัน, มีไข้ร่วมด้วย, เคยเป็นมาก่อน, ฯลฯ",
            height=100
        )

        submitted = st.form_submit_button("🔍 ประเมินผลตอนนี้", type="primary", use_container_width=True)

    if submitted:
        if not name:
            st.error("⚠️ กรุณากรอกชื่อ-นามสกุล")
        elif not selected_symptoms:
            st.warning("⚠️ กรุณาเลือกอาการอย่างน้อย 1 รายการ")
        else:
            risk_multiplier = 1.0
            
            if age >= 70: risk_multiplier += 0.3
            elif age >= 60: risk_multiplier += 0.2
            elif age >= 50: risk_multiplier += 0.1
            
            if "โรคหัวใจและหลอดเลือด" in chronic: risk_multiplier += 0.3
            if "โรคไตเรื้อรัง" in chronic: risk_multiplier += 0.2
            if "เบาหวาน" in chronic: risk_multiplier += 0.1
            
            final_score = int(total_score * risk_multiplier)
            
            if final_score >= 50 or len(emergency_symptoms) > 0:
                risk_level, risk_class = "สูง", "risk-high"
                st.markdown(f'<div class="{risk_class}"><h2 style="font-size: 2.5rem; margin: 0; font-weight: 700;">🚨 ความเสี่ยงสูง!</h2><p style="font-size: 1.3rem; margin: 15px 0 0 0; font-weight: 500;">กรุณาไปพบแพทย์ทันที</p></div>', unsafe_allow_html=True)
                
                line_msg = f"🚨 แจ้งเตือนฉุกเฉิน!\nชื่อ: {name}\nอายุ: {age} ปี\nคะแนน: {final_score}\nอาการ: {', '.join(selected_symptoms)}"
                send_line_notify(line_msg)
                
            elif final_score >= 20:
                risk_level, risk_class = "กลาง", "risk-medium"
                st.markdown(f'<div class="{risk_class}"><h2 style="font-size: 2.5rem; margin: 0; font-weight: 700;">⚠️ ความเสี่ยงกลาง</h2><p style="font-size: 1.3rem; margin: 15px 0 0 0; font-weight: 500;">ควรพบแพทย์ภายใน 24 ชั่วโมง</p></div>', unsafe_allow_html=True)
            else:
                risk_level, risk_class = "ต่ำ", "risk-low"
                st.markdown(f'<div class="{risk_class}"><h2 style="font-size: 2.5rem; margin: 0; font-weight: 700;">✅ ความเสี่ยงต่ำ</h2><p style="font-size: 1.3rem; margin: 15px 0 0 0; font-weight: 500;">ดูแลตัวเองได้</p></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown('<h3 class="section-title">📊 สรุปผลการประเมินของคุณ</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="info-box">
                    <h4 style="color: #0083b0; margin-top: 0;">👤 ข้อมูลผู้ประเมิน</h4>
                    <p style="margin: 8px 0;"><b>ชื่อ:</b> {name}</p>
                    <p style="margin: 8px 0;"><b>อายุ:</b> {age} ปี</p>
                    <p style="margin: 8px 0;"><b>เพศ:</b> {gender}</p>
                    <p style="margin: 8px 0;"><b>โรคประจำตัว:</b> {', '.join(chronic) if chronic else 'ไม่มี'}</p>
                    <p style="margin: 8px 0;"><b>ยาที่รับประทาน:</b> {medications if medications else 'ไม่มี'}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="info-box">
                    <h4 style="color: #0083b0; margin-top: 0;">📊 ผลการประเมิน</h4>
                    <p style="margin: 8px 0;"><b>คะแนนดิบ:</b> {total_score}</p>
                    <p style="margin: 8px 0;"><b>ตัวคูณความเสี่ยง:</b> {risk_multiplier}x</p>
                    <p style="margin: 8px 0; font-size: 1.2rem;"><b>คะแนนรวม:</b> {final_score}</p>
                    <p style="margin: 8px 0; font-size: 1.2rem;"><b>ระดับความเสี่ยง:</b> {risk_level}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f'<h4 style="color: #0083b0; margin-top: 30px;">อาการที่คุณเลือก ({len(selected_symptoms)} อาการ)</h4>')
            for symptom in selected_symptoms:
                st.markdown(f"• {symptom}")
            
            if notes:
                st.markdown(f'<h4 style="color: #0083b0; margin-top: 20px;">หมายเหตุ</h4>')
                st.markdown(f"{notes}")
            
            record = {
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "name": name, "age": age, "gender": gender,
                "chronic": ", ".join(chronic) if chronic else "ไม่มี",
                "medications": medications if medications else "ไม่มี",
                "bp": bp if bp else "-",
                "bs": bs,
                "score": final_score, "risk": risk_level,
                "symptoms": ", ".join(selected_symptoms),
                "notes": notes if notes else "-"
            }
            save_to_csv(record)
            
            st.success(f"✅ บันทึกผลการประเมินเรียบร้อยแล้ว! (รวม {get_data_count()} รายการ)")
            st.info("💾 ข้อมูลของคุณถูกบันทึกในไฟล์ `assessment_data.csv` แล้ว")

# ==================== หน้าที่ 3: ประวัติการประเมินของฉัน ====================
elif menu == "📋 ประวัติ":
    st.markdown('<div class="page-header"><h1>📋 ประวัติการประเมินของคุณ</h1></div>', unsafe_allow_html=True)
    
    df = load_data()
    
    if df.empty:
        st.markdown("""
        <div class="info-box" style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 4rem; margin-bottom: 20px;">📭</div>
            <h3 style="color: #0083b0; margin: 0;">ยังไม่มีข้อมูล</h3>
            <p style="margin: 15px 0 0 0; font-size: 1.1rem; color: #6c757d;">กรุณาไปที่หน้า 'ประเมินอาการ' เพื่อเริ่มประเมิน</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success(f"✅ พบข้อมูลการประเมิน **{len(df)} รายการ** ของคุณ")
        
        tab1, tab2, tab3 = st.tabs(["👁️ ดูข้อมูล", "✏️ แก้ไข/ลบ", "📥 ดาวน์โหลด"])
        
        with tab1:
            st.markdown("### 📄 ตารางข้อมูลการประเมินทั้งหมด")
            st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True, height=400)
            
            if len(df) > 0:
                selected_index = st.selectbox(
                    "เลือกรายการเพื่อดูรายละเอียด",
                    range(len(df)),
                    format_func=lambda x: f"{df.iloc[x]['date']} - {df.iloc[x]['name']} (ความเสี่ยง: {df.iloc[x]['risk']})"
                )
                
                if selected_index is not None:
                    record = df.iloc[selected_index]
                    st.markdown("### 📝 รายละเอียด")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        <div class="info-box">
                            <p style="margin: 8px 0;"><b>วันที่:</b> {record['date']}</p>
                            <p style="margin: 8px 0;"><b>ชื่อ:</b> {record['name']}</p>
                            <p style="margin: 8px 0;"><b>อายุ:</b> {record['age']} ปี</p>
                            <p style="margin: 8px 0;"><b>เพศ:</b> {record['gender']}</p>
                            <p style="margin: 8px 0;"><b>โรคประจำตัว:</b> {record['chronic']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="info-box">
                            <p style="margin: 8px 0;"><b>คะแนน:</b> {record['score']}</p>
                            <p style="margin: 8px 0;"><b>ความเสี่ยง:</b> {record['risk']}</p>
                            <p style="margin: 8px 0;"><b>อาการ:</b> {record['symptoms']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    if record['notes'] != '-':
                        st.markdown(f'<div class="info-box"><b>หมายเหตุ:</b> {record["notes"]}</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown("### ✏️ แก้ไขหรือลบข้อมูล")
            if len(df) > 0:
                edit_index = st.selectbox("เลือกรายการที่ต้องการแก้ไข/ลบ", range(len(df)), format_func=lambda x: f"{df.iloc[x]['date']} - {df.iloc[x]['name']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ ลบรายการนี้", type="secondary"):
                        if delete_record(edit_index):
                            st.success("✅ ลบข้อมูลเรียบร้อยแล้ว!")
                            st.rerun()
                
                with col2:
                    new_risk = st.selectbox("แก้ไขระดับความเสี่ยง", ["ต่ำ", "กลาง", "สูง"], index=["ต่ำ", "กลาง", "สูง"].index(df.iloc[edit_index]['risk']))
                    if st.button("💾 บันทึกการแก้ไข"):
                        update_record(edit_index, {'risk': new_risk})
                        st.success("✅ อัปเดตข้อมูลเรียบร้อยแล้ว!")
                        st.rerun()
        
        with tab3:
            st.markdown("### 📥 ดาวน์โหลดข้อมูลของคุณ")
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ CSV",
                data=csv,
                file_name=f'my_health_data_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv',
                use_container_width=True
            )
            
            st.info("💡 **วิธีเปิดไฟล์ CSV:** คลิกปุ่มดาวน์โหลดด้านบน แล้วเปิดไฟล์ด้วย Microsoft Excel หรือ Google Sheets")
        
        st.markdown("---")
        if st.button("⚠️ ล้างข้อมูลทั้งหมด (ระวัง!)", type="secondary"):
            st.warning("⚠️ การดำเนินการนี้จะลบข้อมูลทั้งหมดของคุณถาวร!")
            if st.checkbox("ฉันเข้าใจและยืนยันที่จะลบข้อมูลทั้งหมด"):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                    st.success("✅ ลบข้อมูลทั้งหมดเรียบร้อยแล้ว!")
                    st.rerun()

# ==================== หน้าที่ 4: สถิติส่วนตัว ====================
elif menu == "📊 สถิติ":
    st.markdown('<div class="page-header"><h1>📊 สถิติการประเมินของคุณ</h1></div>', unsafe_allow_html=True)

    df = load_data()
    
    if df.empty:
        st.info("💡 ยังไม่มีข้อมูล กรุณาประเมินอาการอย่างน้อย 1 ครั้งเพื่อดูสถิติของคุณ")
    else:
        st.success(f"📊 แสดงสถิติจากข้อมูลของคุณ **{len(df)} รายการ**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2.5rem;">📋</div>
                <h3>{len(df)}</h3>
                <p>การประเมินทั้งหมด</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            high_count = len(df[df['risk'] == 'สูง'])
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2.5rem;">🚨</div>
                <h3>{high_count}</h3>
                <p>ความเสี่ยงสูง</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            avg_score = df['score'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2.5rem;">📈</div>
                <h3>{avg_score:.1f}</h3>
                <p>คะแนนเฉลี่ย</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        st.markdown('<h3 class="section-title">📊 สัดส่วนระดับความเสี่ยงของคุณ</h3>', unsafe_allow_html=True)
        risk_counts = df['risk'].value_counts().reset_index()
        risk_counts.columns = ['ระดับความเสี่ยง', 'จำนวน']
        fig_pie = px.pie(risk_counts, values='จำนวน', names='ระดับความเสี่ยง', 
                        color='ระดับความเสี่ยง', color_discrete_map={'ต่ำ': '#38ef7d', 'กลาง': '#ffd200', 'สูง': '#ff4b2b'}, hole=0.4)
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#333', family='Prompt'))
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.markdown('<h3 class="section-title">📊 คะแนนความเสี่ยงในแต่ละครั้ง</h3>', unsafe_allow_html=True)
        fig_bar = px.bar(df.sort_values('date'), x='date', y='score', color='risk',
                        color_discrete_map={'ต่ำ': '#38ef7d', 'กลาง': '#ffd200', 'สูง': '#ff4b2b'}, text='score', hover_data=['name', 'symptoms'])
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#333', family='Prompt'))
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.markdown('<h3 class="section-title">📈 ความสัมพันธ์ อายุ vs คะแนน</h3>', unsafe_allow_html=True)
        fig_scatter = px.scatter(df, x='age', y='score', color='risk',
                                color_discrete_map={'ต่ำ': '#38ef7d', 'กลาง': '#ffd200', 'สูง': '#ff4b2b'},
                                hover_data=['name', 'date', 'symptoms'], size='score')
        fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#333', family='Prompt'))
        st.plotly_chart(fig_scatter, use_container_width=True)

# ==================== หน้าที่ 5: เกี่ยวกับ ====================
elif menu == "ℹ️ เกี่ยวกับ":
    st.markdown('<div class="page-header"><h1>ℹ️ เกี่ยวกับระบบ</h1></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box" style="padding: 2rem;">
        <h3 style="color: #0083b0; margin-top: 0;">🎓 โปรเจกต์ปี 4 (Senior Project)</h3>
        <h4 style="color: #0083b0;">ระบบประเมินการตัดสินใจไปพบแพทย์สำหรับวัยกลางคนและผู้สูงอายุ (40+ ปี)</h4>
        <p style="line-height: 1.8; font-size: 1.05rem; color: #495057;">
            ระบบนี้ถูกพัฒนาขึ้นเพื่อให้คุณสามารถประเมินอาการสุขภาพด้วยตัวเอง 
            โดยเน้นการคัดกรองโรคไม่ติดต่อเรื้อรัง (NCDs) เช่น เบาหวาน ความดันโลหิตสูง โรคหัวใจและหลอดเลือด
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h3 class="section-title">💾 การจัดเก็บข้อมูลของคุณ</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box" style="padding: 2rem;">
        <p style="margin: 10px 0; color: #495057;"><b>📁 ไฟล์ข้อมูล:</b> <code>assessment_data.csv</code></p>
        <p style="margin: 10px 0; color: #495057;"><b>📍 ตำแหน่ง:</b> โฟลเดอร์เดียวกับแอปนี้</p>
        <p style="margin: 10px 0; color: #495057;"><b>🔒 ความเป็นส่วนตัว:</b> ข้อมูลถูกเก็บในเครื่องของคุณเท่านั้น</p>
        <p style="margin: 10px 0; color: #495057;"><b>📥 การสำรองข้อมูล:</b> สามารถดาวน์โหลดไฟล์ CSV ได้จากหน้า "ประวัติ"</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box" style="margin-top: 40px; padding: 2rem; border-left-color: #ff4b2b; background: linear-gradient(to right, #fff5f5, #ffffff);">
        <h4 style="color: #ff4b2b; margin-top: 0;">⚠️ ข้อจำกัดสำคัญ</h4>
        <p style="line-height: 1.8; font-size: 1.05rem; color: #495057;">
            ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น 
            <b>ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้</b> หากมีอาการรุนแรงหรือกังวลใจ 
            ควรปรึกษาแพทย์หรือบุคลากรทางการแพทย์โดยตรง
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==================== Footer ====================
st.markdown("---")
st.markdown("""
<div class="footer">
    <p style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #0083b0;">🏥 ระบบประเมินสุขภาพส่วนตัว (40+ ปี) | โปรเจกต์ปี 4</p>
    <p style="margin: 10px 0 0 0; font-size: 0.9rem; color: #6c757d;">พัฒนาด้วย Streamlit • Python • Data Visualization</p>
</div>
""", unsafe_allow_html=True)