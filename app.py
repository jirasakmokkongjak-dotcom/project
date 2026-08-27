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
    """บันทึกข้อมูลใหม่ลง CSV"""
    df_new = pd.DataFrame([data_dict])
    if os.path.exists(DATA_FILE):
        df_new.to_csv(DATA_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(DATA_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')

def load_data():
    """โหลดข้อมูลจาก CSV"""
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

def get_data_count():
    """นับจำนวนข้อมูล"""
    if os.path.exists(DATA_FILE):
        return len(pd.read_csv(DATA_FILE))
    return 0

def update_record(index, updated_data):
    """อัปเดตข้อมูลตาม index"""
    df = load_data()
    if 0 <= index < len(df):
        for key, value in updated_data.items():
            df.loc[index, key] = value
        df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
        return True
    return False

def delete_record(index):
    """ลบข้อมูลตาม index"""
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
    .stApp {
        background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 50%, #80deea 100%);
        background-attachment: fixed;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* ===== Hero Section ===== */
    .hero-section {
        background: linear-gradient(135deg, #00bcd4 0%, #0097a7 100%);
        padding: 50px 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 15px 50px rgba(0,188,212,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 30s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .hero-section h1 {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 15px;
        position: relative;
        z-index: 1;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
        letter-spacing: 1px;
    }
    
    .hero-section h3 {
        font-size: 1.4rem;
        font-weight: 400;
        opacity: 0.95;
        position: relative;
        z-index: 1;
        margin-top: 10px;
    }
    
    .hero-section p {
        font-size: 1.1rem;
        margin-top: 20px;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    /* ===== Page Header ===== */
    .page-header {
        background: linear-gradient(135deg, #00bcd4 0%, #0097a7 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,188,212,0.3);
    }
    
    .page-header h1 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.5px;
    }
    
    /* ===== Metric Cards ===== */
    .metric-card {
        background: rgba(255,255,255,0.95);
        padding: 30px 25px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,188,212,0.15);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 2px solid transparent;
        backdrop-filter: blur(10px);
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 50px rgba(0,188,212,0.3);
        border-color: #00bcd4;
    }
    
    .metric-card h3 {
        color: #0097a7;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 15px 0 10px 0;
    }
    
    .metric-card p {
        color: #555;
        font-size: 1rem;
        margin: 0;
        font-weight: 500;
    }
    
    /* ===== Risk Cards ===== */
    .risk-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(238,90,111,0.4);
        animation: pulse 2s infinite;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #ffa726 0%, #fb8c00 100%);
        color: white;
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(251,140,0,0.4);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #66bb6a 0%, #43a047 100%);
        color: white;
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(67,160,71,0.4);
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); box-shadow: 0 15px 40px rgba(238,90,111,0.4); }
        50% { transform: scale(1.03); box-shadow: 0 20px 50px rgba(238,90,111,0.6); }
    }
    
    /* ===== Info Box ===== */
    .info-box {
        background: rgba(255,255,255,0.95);
        padding: 25px;
        border-radius: 15px;
        border-left: 6px solid #00bcd4;
        box-shadow: 0 5px 20px rgba(0,188,212,0.15);
        margin: 20px 0;
        backdrop-filter: blur(10px);
    }
    
    .info-box b {
        color: #0097a7;
        font-size: 1.1rem;
    }
    
    /* ===== Section Title ===== */
    .section-title {
        color: #0097a7;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 35px 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 4px solid #00bcd4;
        display: inline-block;
        letter-spacing: 0.5px;
    }
    
    /* ===== Buttons ===== */
    .stButton>button {
        background: linear-gradient(135deg, #00bcd4 0%, #0097a7 100%);
        color: white;
        border: none;
        padding: 14px 35px;
        border-radius: 30px;
        font-size: 1.05rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 20px rgba(0,188,212,0.4);
        letter-spacing: 0.5px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0,188,212,0.6);
    }
    
    .stButton>button:active {
        transform: translateY(-1px);
    }
    
    /* ===== Form Elements ===== */
    .stTextInput>div>div>input, 
    .stNumberInput>div>div>input, 
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 12px 15px;
        transition: all 0.3s ease;
        background: rgba(255,255,255,0.9);
    }
    
    .stTextInput>div>div>input:focus, 
    .stNumberInput>div>div>input:focus, 
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #00bcd4;
        box-shadow: 0 0 0 4px rgba(0,188,212,0.2);
        outline: none;
    }
    
    /* ===== Checkbox ===== */
    .stCheckbox>label {
        font-size: 1.05rem;
        font-weight: 500;
    }
    
    /* ===== Expander ===== */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.9);
        border-radius: 12px;
        padding: 15px;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* ===== Footer ===== */
    .footer {
        text-align: center;
        color: white;
        padding: 35px;
        margin-top: 60px;
        background: rgba(0,151,167,0.2);
        border-radius: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 5px 20px rgba(0,151,167,0.2);
    }
    
    /* ===== Sidebar Enhancement ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0097a7 0%, #00838f 100%);
    }
    
    /* ===== Tabs ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.7);
        border-radius: 12px 12px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: white;
        box-shadow: 0 -5px 15px rgba(0,0,0,0.1);
    }
    
    /* ===== Alert Boxes ===== */
    .stAlert {
        border-radius: 12px;
        padding: 20px;
        font-size: 1.05rem;
    }
    
    /* ===== Dataframe ===== */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    /* ===== Scrollbar ===== */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0,188,212,0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #00bcd4;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #0097a7;
    }
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
    <div style="text-align: center; padding: 30px 20px; color: white;">
        <div style="font-size: 4rem; margin-bottom: 15px;">🏥</div>
        <h2 style="font-size: 1.8rem; margin: 15px 0; font-weight: 700; letter-spacing: 1px;">Health Check</h2>
        <p style="font-size: 1rem; opacity: 0.9; font-weight: 400;">ระบบประเมินสุขภาพส่วนตัว</p>
        <p style="font-size: 0.9rem; opacity: 0.7; margin-top: 10px;">สำหรับวัย 40+ ปี</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    elderly_mode = st.checkbox("👓 โหมดตัวหนังสือใหญ่", help="เพิ่มขนาดตัวอักษรสำหรับผู้สูงอายุ")
    if elderly_mode:
        st.markdown("<style> html { font-size: 125% !important; } </style>", unsafe_allow_html=True)
    
    menu = st.radio(
        "📋 เมนูหลัก",
        ["🏠 หน้าหลัก", " ประเมินอาการ", "📋 ประวัติ", "📊 สถิติ", "ℹ️ เกี่ยวกับ"],
        index=1
    )
    
    st.markdown("---")
    
    data_count = get_data_count()
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; text-align: center; color: white; backdrop-filter: blur(10px);">
        <p style="margin: 0; font-size: 0.95rem; font-weight: 500;"> ข้อมูลของคุณ</p>
        <h3 style="margin: 15px 0; font-size: 2.5rem; font-weight: 800;">{data_count}</h3>
        <p style="margin: 0; font-size: 0.85rem; opacity: 0.9;">รายการประเมิน</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ==================== หน้าที่ 1: หน้าหลัก ====================
if menu == "🏠 หน้าหลัก":
    st.markdown("""
    <div class="hero-section">
        <h1>🏥 ระบบประเมินสุขภาพส่วนตัว</h1>
        <h3>สำหรับวัยกลางคนและผู้สูงอายุ (40+ ปี)</h3>
        <p>ประเมินอาการด้วยตัวเอง • บันทึกข้อมูลส่วนตัว • ติดตามผลสุขภาพ</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 3rem; margin-bottom: 10px;"></div>
            <h3>{get_data_count()}</h3>
            <p>การประเมินของคุณ</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 3rem; margin-bottom: 10px;">👤</div>
            <h3>ส่วนตัว</h3>
            <p>ข้อมูลเป็นของคุณ</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 3rem; margin-bottom: 10px;">🔒</div>
            <h3>ปลอดภัย</h3>
            <p>เก็บในเครื่องคุณ</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-title">📝 วิธีใช้งาน</h2>', unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""
        <div class="info-box">
            <h4 style="color: #0097a7; margin-top: 0;">1️⃣ ประเมินอาการ</h4>
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li>กรอกข้อมูลส่วนตัว</li>
                <li>เลือกอาการที่เป็น</li>
                <li>ระบบคำนวณความเสี่ยง</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="info-box">
            <h4 style="color: #0097a7; margin-top: 0;">2️⃣ บันทึกข้อมูล</h4>
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li>ข้อมูลจะถูกบันทึกอัตโนมัติ</li>
                <li>เก็บเป็นไฟล์ CSV</li>
                <li>เปิดดูใน Excel ได้</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown("""
        <div class="info-box">
            <h4 style="color: #0097a7; margin-top: 0;">3️⃣ ดูประวัติ</h4>
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li>ดูผลการประเมินย้อนหลัง</li>
                <li>เปรียบเทียบผลลัพธ์</li>
                <li>ดาวน์โหลดข้อมูล</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box" style="margin-top: 40px; padding: 30px;">
        <b>💾 ข้อมูลของคุณ:</b> ระบบจะบันทึกข้อมูลการประเมินทั้งหมดลงในไฟล์ <code>assessment_data.csv</code> 
        ในโฟลเดอร์เดียวกับแอปนี้ คุณสามารถเปิดดู แก้ไข หรือสำรองข้อมูลได้ตลอดเวลา<br><br>
        <b>⚠️ หมายเหตุสำคัญ:</b> ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น 
        <b>ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้</b>
    </div>
    """, unsafe_allow_html=True)

# ==================== หน้าที่ 2: ประเมินอาการใหม่ ====================
elif menu == "🩺 ประเมินอาการ":
    st.markdown('<div class="page-header"><h1>🩺 แบบประเมินอาการ</h1></div>', unsafe_allow_html=True)

    with st.form("assessment_form", clear_on_submit=False):
        st.markdown('<h3 class="section-title">👤 ข้อมูลส่วนตัวของคุณ</h3>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: 
            name = st.text_input("ชื่อ-นามสกุล *", placeholder="กรอกชื่อของคุณ", help="ระบุชื่อ-นามสกุลของคุณ")
        with col2: 
            age = st.number_input("อายุ (ปี) *", min_value=40, max_value=120, value=45, help="ระบุอายุของคุณ")
        with col3: 
            gender = st.selectbox("เพศ *", ["ชาย", "หญิง", "ไม่ระบุ"], help="เลือกเพศของคุณ")

        st.markdown('<h3 class="section-title"> ข้อมูลสุขภาพ</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            chronic = st.multiselect("โรคประจำตัว", CHRONIC_DISEASES, help="เลือกโรคประจำตัวที่คุณมี")
        with col2:
            medications = st.text_input("ยาที่รับประทานประจำ (ถ้ามี)", placeholder="เช่น ยาลดความดัน, ยาเบาหวาน")
        
        col1, col2 = st.columns(2)
        with col1:
            bp = st.text_input("ความดันโลหิตล่าสุด", placeholder="เช่น 120/80", help="ความดันโลหิตตัวบน/ตัวล่าง")
        with col2:
            bs = st.number_input("ระดับน้ำตาลในเลือด (mg/dL)", min_value=0, max_value=600, value=100, help="ระดับน้ำตาลในเลือด")
        
        st.markdown('<h3 class="section-title"> อาการที่คุณกำลังประสบอยู่</h3>', unsafe_allow_html=True)
        st.info("💡 **คำแนะนำ:** เลือกอาการที่คุณกำลังเป็นอยู่ในขณะนี้ สามารถเลือกได้มากกว่า 1 อาการ")
        
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
            help="กรอกรายละเอียดเพิ่มเติมเกี่ยวกับอาการของคุณ",
            height=100
        )

        submitted = st.form_submit_button("🔍 ประเมินผลตอนนี้", type="primary", use_container_width=True)

    if submitted:
        if not name:
            st.error("⚠️ กรุณากรอกชื่อ-นามสกุล")
        elif not selected_symptoms:
            st.warning("⚠️ กรุณาเลือกอาการอย่างน้อย 1 รายการ")
        else:
            # คำนวณคะแนน
            risk_multiplier = 1.0
            
            # ปรับตามอายุ
            if age >= 70: 
                risk_multiplier += 0.3
            elif age >= 60: 
                risk_multiplier += 0.2
            elif age >= 50: 
                risk_multiplier += 0.1
            
            # ปรับตามโรคประจำตัว
            if "โรคหัวใจและหลอดเลือด" in chronic: 
                risk_multiplier += 0.3
            if "โรคไตเรื้อรัง" in chronic:
                risk_multiplier += 0.2
            if "เบาหวาน" in chronic:
                risk_multiplier += 0.1
            
            final_score = int(total_score * risk_multiplier)
            
            # ตัดสินผล
            if final_score >= 50 or len(emergency_symptoms) > 0:
                risk_level, risk_class = "สูง", "risk-high"
                st.markdown(f'<div class="{risk_class}"><h2 style="font-size: 2.5rem; margin: 0; font-weight: 800;">🚨 ความเสี่ยงสูง!</h2><p style="font-size: 1.4rem; margin: 15px 0 0 0; font-weight: 500;">กรุณาไปพบแพทย์ทันที</p></div>', unsafe_allow_html=True)
                
                # ส่ง Line Notify
                line_msg = f"🚨 แจ้งเตือนฉุกเฉิน!\nชื่อ: {name}\nอายุ: {age} ปี\nคะแนน: {final_score}\nอาการ: {', '.join(selected_symptoms)}"
                send_line_notify(line_msg)
                
            elif final_score >= 20:
                risk_level, risk_class = "กลาง", "risk-medium"
                st.markdown(f'<div class="{risk_class}"><h2 style="font-size: 2.5rem; margin: 0; font-weight: 800;">⚠️ ความเสี่ยงกลาง</h2><p style="font-size: 1.4rem; margin: 15px 0 0 0; font-weight: 500;">ควรพบแพทย์ภายใน 24 ชั่วโมง</p></div>', unsafe_allow_html=True)
            else:
                risk_level, risk_class = "ต่ำ", "risk-low"
                st.markdown(f'<div class="{risk_class}"><h2 style="font-size: 2.5rem; margin: 0; font-weight: 800;">✅ ความเสี่ยงต่ำ</h2><p style="font-size: 1.4rem; margin: 15px 0 0 0; font-weight: 500;">ดูแลตัวเองได้</p></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown('<h3 class="section-title">📊 สรุปผลการประเมินของคุณ</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="info-box">
                    <h4 style="color: #0097a7; margin-top: 0;">👤 ข้อมูลผู้ประเมิน</h4>
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
                    <h4 style="color: #0097a7; margin-top: 0;">📊 ผลการประเมิน</h4>
                    <p style="margin: 8px 0;"><b>คะแนนดิบ:</b> {total_score}</p>
                    <p style="margin: 8px 0;"><b>ตัวคูณความเสี่ยง:</b> {risk_multiplier}x</p>
                    <p style="margin: 8px 0; font-size: 1.2rem;"><b>คะแนนรวม:</b> {final_score}</p>
                    <p style="margin: 8px 0; font-size: 1.2rem;"><b>ระดับความเสี่ยง:</b> {risk_level}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f'<h4 style="color: #0097a7; margin-top: 30px;">อาการที่คุณเลือก ({len(selected_symptoms)} อาการ)</h4>')
            for symptom in selected_symptoms:
                st.markdown(f"• {symptom}")
            
            if notes:
                st.markdown(f'<h4 style="color: #0097a7; margin-top: 20px;">หมายเหตุ</h4>')
                st.markdown(f"{notes}")
            
            # บันทึกข้อมูล
            record = {
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "name": name, 
                "age": age, 
                "gender": gender,
                "chronic": ", ".join(chronic) if chronic else "ไม่มี",
                "medications": medications if medications else "ไม่มี",
                "bp": bp if bp else "-",
                "bs": bs,
                "score": final_score, 
                "risk": risk_level,
                "symptoms": ", ".join(selected_symptoms),
                "notes": notes if notes else "-"
            }
            save_to_csv(record)
            
            st.success(f"✅ บันทึกผลการประเมินเรียบร้อยแล้ว! (รวม {get_data_count()} รายการ)")
            st.info("💾 ข้อมูลของคุณถูกบันทึกในไฟล์ assessment_data.csv แล้ว")

# ==================== หน้าที่ 3: ประวัติการประเมินของฉัน ====================
elif menu == "📋 ประวัติ":
    st.markdown('<div class="page-header"><h1>📋 ประวัติการประเมินของคุณ</h1></div>', unsafe_allow_html=True)
    
    df = load_data()
    
    if df.empty:
        st.markdown("""
        <div class="info-box" style="text-align: center; padding: 50px;">
            <div style="font-size: 4rem; margin-bottom: 20px;">📭</div>
            <h3 style="color: #0097a7; margin: 0;">ยังไม่มีข้อมูล</h3>
            <p style="margin: 15px 0 0 0; font-size: 1.1rem;">กรุณาไปที่หน้า 'ประเมินอาการ' เพื่อเริ่มประเมิน</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success(f"✅ พบข้อมูลการประเมิน **{len(df)} รายการ** ของคุณ")
        
        # แสดงตัวเลือกการจัดการ
        tab1, tab2, tab3 = st.tabs(["👁️ ดูข้อมูล", "✏️ แก้ไข/ลบ", "📥 ดาวน์โหลด"])
        
        with tab1:
            st.markdown("### 📄 ตารางข้อมูลการประเมินทั้งหมด")
            st.dataframe(
                df.sort_values(by='date', ascending=False),
                use_container_width=True,
                height=400
            )
            
            # แสดงรายละเอียดเมื่อคลิก
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
                edit_index = st.selectbox(
                    "เลือกรายการที่ต้องการแก้ไข/ลบ",
                    range(len(df)),
                    format_func=lambda x: f"{df.iloc[x]['date']} - {df.iloc[x]['name']}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ ลบรายการนี้", type="secondary"):
                        if delete_record(edit_index):
                            st.success("✅ ลบข้อมูลเรียบร้อยแล้ว!")
                            st.rerun()
                        else:
                            st.error("❌ เกิดข้อผิดพลาดในการลบ")
                
                with col2:
                    new_risk = st.selectbox(
                        "แก้ไขระดับความเสี่ยง (ถ้าต้องการ)",
                        ["ต่ำ", "กลาง", "สูง"],
                        index=["ต่ำ", "กลาง", "สูง"].index(df.iloc[edit_index]['risk'])
                    )
                    if st.button("💾 บันทึกการแก้ไข"):
                        update_record(edit_index, {'risk': new_risk})
                        st.success("✅ อัปเดตข้อมูลเรียบร้อยแล้ว!")
                        st.rerun()
            else:
                st.info("ไม่มีข้อมูลให้แก้ไข")
        
        with tab3:
            st.markdown("### 📥 ดาวน์โหลดข้อมูลของคุณ")
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ CSV",
                data=csv,
                file_name=f'my_health_data_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv',
                help="คลิกเพื่อดาวน์โหลดข้อมูลการประเมินทั้งหมดของคุณ"
            )
            
            st.info("""
            **💡 วิธีเปิดไฟล์ CSV:**
            - คลิกปุ่มดาวน์โหลดด้านบน
            - เปิดไฟล์ด้วย Microsoft Excel, Google Sheets หรือโปรแกรมตารางคำนวณ
            - ข้อมูลจะแสดงเป็นตารางพร้อมใช้งาน
            """)
        
        # ปุ่มล้างข้อมูลทั้งหมด
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
                <div style="font-size: 3rem; margin-bottom: 10px;"></div>
                <h3>{len(df)}</h3>
                <p>การประเมินทั้งหมด</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            high_count = len(df[df['risk'] == 'สูง'])
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 3rem; margin-bottom: 10px;">🚨</div>
                <h3>{high_count}</h3>
                <p>ความเสี่ยงสูง</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            avg_score = df['score'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 3rem; margin-bottom: 10px;">📈</div>
                <h3>{avg_score:.1f}</h3>
                <p>คะแนนเฉลี่ย</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        st.markdown('<h3 class="section-title">📊 สัดส่วนระดับความเสี่ยงของคุณ</h3>', unsafe_allow_html=True)
        risk_counts = df['risk'].value_counts().reset_index()
        risk_counts.columns = ['ระดับความเสี่ยง', 'จำนวน']
        fig_pie = px.pie(
            risk_counts, 
            values='จำนวน', 
            names='ระดับความเสี่ยง', 
            color='ระดับความเสี่ยง',
            color_discrete_map={'ต่ำ': '#66bb6a', 'กลาง': '#ffa726', 'สูง': '#ff6b6b'}, 
            hole=0.4
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333', size=14)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.markdown('<h3 class="section-title">📊 คะแนนความเสี่ยงในแต่ละครั้ง</h3>', unsafe_allow_html=True)
        fig_bar = px.bar(
            df.sort_values('date'), 
            x='date', 
            y='score', 
            color='risk',
            color_discrete_map={'ต่ำ': '#66bb6a', 'กลาง': '#ffa726', 'สูง': '#ff6b6b'},
            text='score',
            hover_data=['name', 'symptoms']
        )
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333', size=14)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.markdown('<h3 class="section-title"> ความสัมพันธ์ อายุ vs คะแนน</h3>', unsafe_allow_html=True)
        fig_scatter = px.scatter(
            df, 
            x='age', 
            y='score', 
            color='risk',
            color_discrete_map={'ต่ำ': '#66bb6a', 'กลาง': '#ffa726', 'สูง': '#ff6b6b'},
            hover_data=['name', 'date', 'symptoms'], 
            size='score'
        )
        fig_scatter.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333', size=14)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# ==================== หน้าที่ 5: เกี่ยวกับ ====================
elif menu == "ℹ️ เกี่ยวกับ":
    st.markdown('<div class="page-header"><h1>️ เกี่ยวกับระบบ</h1></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box" style="padding: 30px;">
        <h3 style="color: #0097a7; margin-top: 0;">🎓 โปรเจกต์ปี 4 (Senior Project)</h3>
        <h4 style="color: #0097a7;">ระบบประเมินการตัดสินใจไปพบแพทย์สำหรับวัยกลางคนและผู้สูงอายุ (40+ ปี)</h4>
        <p style="line-height: 1.8; font-size: 1.05rem;">
            ระบบนี้ถูกพัฒนาขึ้นเพื่อให้คุณสามารถประเมินอาการสุขภาพด้วยตัวเอง 
            โดยเน้นการคัดกรองโรคไม่ติดต่อเรื้อรัง (NCDs) เช่น เบาหวาน ความดันโลหิตสูง โรคหัวใจและหลอดเลือด
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h3 class="section-title"> การจัดเก็บข้อมูลของคุณ</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box" style="padding: 30px;">
        <p style="margin: 10px 0;"><b>📁 ไฟล์ข้อมูล:</b> <code>assessment_data.csv</code></p>
        <p style="margin: 10px 0;"><b> ตำแหน่ง:</b> โฟลเดอร์เดียวกับแอปนี้</p>
        <p style="margin: 10px 0;"><b> ความเป็นส่วนตัว:</b> ข้อมูลถูกเก็บในเครื่องของคุณเท่านั้น</p>
        <p style="margin: 10px 0;"><b>📥 การสำรองข้อมูล:</b> สามารถดาวน์โหลดไฟล์ CSV ได้จากหน้า "ประวัติ"</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box" style="margin-top: 40px; padding: 30px; border-left-color: #ff6b6b;">
        <h4 style="color: #ff6b6b; margin-top: 0;">⚠️ ข้อจำกัดสำคัญ</h4>
        <p style="line-height: 1.8; font-size: 1.05rem;">
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
    <p style="margin: 0; font-size: 1.2rem; font-weight: 600;">🏥 ระบบประเมินสุขภาพส่วนตัว (40+ ปี) | โปรเจกต์ปี 4</p>
    <p style="margin: 15px 0 0 0; font-size: 1rem; opacity: 0.9;">พัฒนาด้วย Streamlit • Python • Data Visualization</p>
</div>
""", unsafe_allow_html=True)