import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
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

# ==================== ตั้งค่าหน้าเว็บ ====================
st.set_page_config(
    page_title="ระบบประเมินสุขภาพ (วัยกลางคนและผู้สูงอายุ 40+)",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ตกแต่งแบบ Modern ====================
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 60px 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
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
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .hero-section h1 {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 15px;
        position: relative;
        z-index: 1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-section h3 {
        font-size: 1.5rem;
        font-weight: 400;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    /* Page Header */
    .page-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .page-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        border-color: #667eea;
    }
    
    .metric-card h3 {
        color: #667eea;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .metric-card p {
        color: #666;
        font-size: 1rem;
        margin: 0;
    }
    
    /* Risk Cards */
    .risk-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(238,90,111,0.4);
        animation: pulse 2s infinite;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #ffa502 0%, #ff7f50 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(255,165,2,0.4);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #2ed573 0%, #7bed9f 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(46,213,115,0.4);
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 25px;
        border-radius: 15px;
        border-left: 6px solid #667eea;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    .info-box b {
        color: #667eea;
        font-size: 1.1rem;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    .feature-card h4 {
        color: #667eea;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    .feature-card ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .feature-card li {
        padding: 8px 0;
        color: #555;
        font-size: 1rem;
    }
    
    .feature-card li:before {
        content: "✨ ";
        margin-right: 8px;
    }
    
    /* Emergency Contact Cards */
    .emergency-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-top: 4px solid #ff6b6b;
    }
    
    .emergency-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    .emergency-card h3 {
        color: #ff6b6b;
        font-size: 2rem;
        font-weight: 800;
        margin: 10px 0;
    }
    
    .emergency-card p {
        color: #666;
        font-size: 1rem;
        margin: 0;
    }
    
    /* Section Headers */
    .section-title {
        color: #667eea;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102,126,234,0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102,126,234,0.6);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: white;
        padding: 30px;
        margin-top: 50px;
        background: rgba(0,0,0,0.2);
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar Enhancement */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Form Enhancement */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 12px;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ==================== ข้อมูลทางการแพทย์ ====================
SYMPTOMS_DATA = {
    "🚨 อาการฉุกเฉิน (ต้องไปโรงพยาบาลทันที)": {
        "เจ็บหน้าอก/แน่นหน้าอก": 35, "หายใจไม่ออก/หายใจลำบาก": 35, "หมดสติ/วูบ/เป็นลม": 40,
        "แขนขาอ่อนแรงครึ่งซีก": 35, "พูดไม่ชัด/ปากเบี้ยว": 35, "เลือดออกไม่หยุด": 30,
        "ชัก/เกร็ง": 35, "ปวดศีรษะรุนแรงที่สุดในชีวิต": 30
    },
    "⚠️ อาการที่ต้องเฝ้าระวัง (พบแพทย์ภายใน 24 ชม.)": {
        "ไข้สูงกว่า 38.5°C": 18, "เวียนศีรษะรุนแรง": 15, "ความดันโลหิตสูงเกิน 180/110": 25,
        "ระดับน้ำตาลผิดปกติ": 20, "ใจสั่น/หัวใจเต้นเร็ว": 18, "ปวดท้องรุนแรง": 18
    },
    "✅ อาการทั่วไป (ดูแลตัวเองได้)": {
        "ปวดเมื่อยตามตัว": 3, "ปวดข้อ": 5, "นอนไม่หลับ": 4, "เบื่ออาหาร": 5,
        "ท้องผูก": 3, "อ่อนเพลียเล็กน้อย": 4, "ไอ/เจ็บคอ": 6, "ปวดหลัง": 5
    }
}

CHRONIC_DISEASES = ["เบาหวาน", "ความดันโลหิตสูง", "โรคหัวใจ", "โรคไต", "โรคปอด", "โรคหลอดเลือดสมอง", "ไขมันในเลือดสูง", "ไม่มี"]

# ==================== Sidebar ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: white;">
        <h2 style="font-size: 2rem; margin: 0;"></h2>
        <h3 style="font-size: 1.3rem; margin: 10px 0;">Health Check</h3>
        <p style="font-size: 0.9rem; opacity: 0.9;">40+ Years</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    elderly_mode = st.checkbox("👓 โหมดตัวหนังสือใหญ่", help="เพิ่มขนาดตัวอักษรสำหรับผู้สูงอายุ")
    if elderly_mode:
        st.markdown("<style> html { font-size: 125% !important; } </style>", unsafe_allow_html=True)
    
    menu = st.radio(
        "เมนูหลัก",
        ["🏠 หน้าหลัก", "🩺 ประเมินอาการ", "📊 ประวัติ", "📈 สถิติ", " AI", "ℹ️ เกี่ยวกับ"],
        index=1
    )
    
    st.markdown("---")
    
    data_count = get_data_count()
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; text-align: center; color: white;">
        <p style="margin: 0; font-size: 0.9rem;">📊 ข้อมูลในระบบ</p>
        <h3 style="margin: 10px 0; font-size: 2rem;">{data_count}</h3>
        <p style="margin: 0; font-size: 0.8rem;">รายการ</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ==================== หน้าที่ 1: หน้าหลัก ====================
if menu == "🏠 หน้าหลัก":
    st.markdown("""
    <div class="hero-section">
        <h1>🏥 ระบบประเมินการไปพบแพทย์</h1>
        <h3>สำหรับวัยกลางคนและผู้สูงอายุ (40+ ปี)</h3>
        <p style="font-size: 1.1rem; margin-top: 20px; opacity: 0.9;">
            ตรวจสอบสุขภาพเบื้องต้นด้วย AI • แม่นยำ • รวดเร็ว • ใช้งานง่าย
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📋 {get_data_count()}</h3>
            <p>การประเมินทั้งหมด</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>👥 40+</h3>
            <p>กลุ่มเป้าหมาย (ปี)</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>⚕️ 3</h3>
            <p>ระดับความเสี่ยง</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-title">✨ คุณสมบัติของระบบ</h2>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="feature-card">
            <h4>🎯 การประเมินอัจฉริยะ</h4>
            <ul>
                <li>วิเคราะห์อาการตามเกณฑ์ทางการแพทย์</li>
                <li>คำนวณความเสี่ยง 3 ระดับ (สูง/กลาง/ต่ำ)</li>
                <li>ปรับคะแนนตามอายุและโรคประจำตัว</li>
                <li>ให้คำแนะนำเฉพาะบุคคล</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 เทคโนโลยีล้ำสมัย</h4>
            <ul>
                <li>AI Machine Learning (Random Forest)</li>
                <li>กราฟสถิติแบบ Interactive</li>
                <li>แจ้งเตือนฉุกเฉินผ่าน LINE</li>
                <li>บันทึกข้อมูลอัตโนมัติ</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-title"> เบอร์โทรฉุกเฉิน</h2>', unsafe_allow_html=True)
    
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        st.markdown("""
        <div class="emergency-card">
            <h3>🚑 1669</h3>
            <p>เจ็บป่วยฉุกเฉิน</p>
        </div>
        """, unsafe_allow_html=True)
    with col_e2:
        st.markdown("""
        <div class="emergency-card">
            <h3>👴 1330</h3>
            <p>สายด่วนสุขภาพ</p>
        </div>
        """, unsafe_allow_html=True)
    with col_e3:
        st.markdown("""
        <div class="emergency-card">
            <h3>🧠 1323</h3>
            <p>สุขภาพจิต</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box" style="margin-top: 30px;">
        <b>💾 การจัดเก็บข้อมูล:</b> ระบบบันทึกข้อมูลการประเมินทุกครั้งลงไฟล์ CSV โดยอัตโนมัติ<br>
        <b>⚠️ หมายเหตุสำคัญ:</b> ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น <b>ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้</b>
    </div>
    """, unsafe_allow_html=True)

# ==================== หน้าที่ 2: ประเมินอาการ ====================
elif menu == " ประเมินอาการ":
    st.markdown('<div class="page-header"><h1>🩺 แบบประเมินอาการ</h1></div>', unsafe_allow_html=True)

    with st.form("assessment_form"):
        st.markdown('<h3 class="section-title">👤 ข้อมูลส่วนตัว</h3>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: name = st.text_input("ชื่อ-นามสกุล *", placeholder="กรอกชื่อ-นามสกุล")
        with col2: age = st.number_input("อายุ (ปี) *", min_value=40, max_value=120, value=45)
        with col3: gender = st.selectbox("เพศ *", ["ชาย", "หญิง", "ไม่ระบุ"])

        st.markdown('<h3 class="section-title">🏥 ประวัติสุขภาพ</h3>', unsafe_allow_html=True)
        chronic = st.multiselect("โรคประจำตัว", CHRONIC_DISEASES)
        
        st.markdown('<h3 class="section-title">🤒 อาการที่พบ</h3>', unsafe_allow_html=True)
        st.info("💡 เลือกอาการที่คุณกำลังประสบอยู่ในขณะนี้ (สามารถเลือกได้มากกว่า 1 อาการ)")
        
        total_score = 0
        selected_symptoms = []
        emergency_symptoms = []

        for category, symptoms in SYMPTOMS_DATA.items():
            with st.expander(category, expanded=True):
                cols = st.columns(2)
                for i, (symptom, score) in enumerate(symptoms.items()):
                    with cols[i % 2]:
                        if st.checkbox(f"{symptom} (+{score} คะแนน)", key=symptom):
                            total_score += score
                            selected_symptoms.append(symptom)
                            if "ฉุกเฉิน" in category: emergency_symptoms.append(symptom)

        submitted = st.form_submit_button("🔍 ประเมินผลตอนนี้", type="primary", use_container_width=True)

    if submitted:
        if not name or not selected_symptoms:
            st.error("⚠️ กรุณากรอกชื่อและเลือกอาการอย่างน้อย 1 รายการ")
        else:
            risk_multiplier = 1.0
            if age >= 70: risk_multiplier += 0.3
            elif age >= 60: risk_multiplier += 0.2
            elif age >= 50: risk_multiplier += 0.1
            
            if "โรคหัวใจ" in chronic or "โรคหลอดเลือดสมอง" in chronic: 
                risk_multiplier += 0.3
            
            final_score = int(total_score * risk_multiplier)
            
            if final_score >= 50 or len(emergency_symptoms) > 0:
                risk_level, risk_class = "สูง", "risk-high"
                st.markdown(f'<div class="{risk_class}"><h2 style="font-size: 2rem; margin: 0;">🚨 ความเสี่ยงสูง!</h2><p style="font-size: 1.3rem; margin: 10px 0 0 0;">กรุณาไปพบแพทย์ทันที</p></div>', unsafe_allow_html=True)
                
                line_msg = f"🚨 แจ้งเตือนฉุกเฉิน!\nชื่อ: {name}\nอายุ: {age} ปี\nคะแนน: {final_score}\nอาการ: {', '.join(selected_symptoms)}"
                send_line_notify(line_msg)
                
            elif final_score >= 20:
                risk_level, risk_class = "กลาง", "risk-medium"
                st.markdown(f'<div class="{risk_class}"><h2 style="font-size: 2rem; margin: 0;">⚠️ ความเสี่ยงกลาง</h2><p style="font-size: 1.3rem; margin: 10px 0 0 0;">ควรพบแพทย์ภายใน 24 ชั่วโมง</p></div>', unsafe_allow_html=True)
            else:
                risk_level, risk_class = "ต่ำ", "risk-low"
                st.markdown(f'<div class="{risk_class}"><h2 style="font-size: 2rem; margin: 0;">✅ ความเสี่ยงต่ำ</h2><p style="font-size: 1.3rem; margin: 10px 0 0 0;">ดูแลตัวเองได้</p></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="info-box">
                    <b> ข้อมูลผู้ประเมิน:</b><br>
                    • ชื่อ: {name}<br>
                    • อายุ: {age} ปี<br>
                    • เพศ: {gender}<br>
                    • โรคประจำตัว: {', '.join(chronic) if chronic else 'ไม่มี'}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="info-box">
                    <b> ผลการประเมิน:</b><br>
                    • คะแนนดิบ: {total_score}<br>
                    • ตัวคูณความเสี่ยง: {risk_multiplier}x<br>
                    • <b>คะแนนรวม: {final_score}</b><br>
                    • ระดับ: {risk_level}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f'<h3 class="section-title"> อาการที่เลือก ({len(selected_symptoms)} อาการ)</h3>', unsafe_allow_html=True)
            for symptom in selected_symptoms:
                st.markdown(f"• {symptom}")
            
            record = {
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "name": name, "age": age, "gender": gender,
                "chronic": ", ".join(chronic) if chronic else "ไม่มี",
                "score": final_score, "risk": risk_level,
                "symptoms": ", ".join(selected_symptoms)
            }
            save_to_csv(record)
            st.success(f"✅ บันทึกผลการประเมินเรียบร้อยแล้ว! (รวม {get_data_count()} รายการ)")

# ==================== หน้าที่ 3: ประวัติ ====================
elif menu == "📊 ประวัติ":
    st.markdown('<div class="page-header"><h1>📊 ประวัติการประเมิน</h1></div>', unsafe_allow_html=True)
    
    df = load_data()
    if df.empty:
        st.markdown("""
        <div class="info-box" style="text-align: center; padding: 40px;">
            <h3 style="color: #667eea; margin: 0;">📭 ยังไม่มีข้อมูล</h3>
            <p style="margin: 10px 0 0 0;">กรุณาไปที่หน้า 'ประเมินอาการ' เพื่อเริ่มประเมิน</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success(f"✅ พบข้อมูลการประเมิน **{len(df)} รายการ**")
        st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์ CSV",
            data=csv,
            file_name=f'health_data_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )
        
        if st.button("🗑️ ล้างข้อมูลทั้งหมด", type="secondary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
                st.success("ลบข้อมูลเรียบร้อยแล้ว!")
                st.rerun()

# ==================== หน้าที่ 4: สถิติ ====================
elif menu == "📈 สถิติ":
    st.markdown('<div class="page-header"><h1>📊 สถิติและกราฟ</h1></div>', unsafe_allow_html=True)

    df = load_data()
    
    if df.empty:
        st.info("💡 ยังไม่มีข้อมูลจริง กรุณาประเมินอาการเพื่อดูกราฟของคุณ")
        dummy_data = [
            {"date": "22/08/2026 10:00", "name": "สมชาย", "age": 45, "score": 15, "risk": "ต่ำ"},
            {"date": "22/08/2026 11:30", "name": "สมหญิง", "age": 55, "score": 35, "risk": "กลาง"},
            {"date": "22/08/2026 13:00", "name": "วิชัย", "age": 68, "score": 65, "risk": "สูง"},
            {"date": "22/08/2026 14:15", "name": "มาลี", "age": 42, "score": 10, "risk": "ต่ำ"},
            {"date": "22/08/2026 15:30", "name": "ประเสริฐ", "age": 75, "score": 55, "risk": "สูง"}
        ]
        df = pd.DataFrame(dummy_data)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📋 {len(df)}</h3>
            <p>การประเมินทั้งหมด</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        high_count = len(df[df['risk'] == 'สูง'])
        st.markdown(f"""
        <div class="metric-card">
            <h3>🚨 {high_count}</h3>
            <p>ความเสี่ยงสูง</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        avg_score = df['score'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 {avg_score:.1f}</h3>
            <p>คะแนนเฉลี่ย</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    st.markdown('<h3 class="section-title">📊 สัดส่วนระดับความเสี่ยง</h3>', unsafe_allow_html=True)
    risk_counts = df['risk'].value_counts().reset_index()
    risk_counts.columns = ['ระดับความเสี่ยง', 'จำนวน']
    fig_pie = px.pie(risk_counts, values='จำนวน', names='ระดับความเสี่ยง', 
                    color='ระดับความเสี่ยง', color_discrete_map={'ต่ำ': '#2ed573', 'กลาง': '#ffa502', 'สูง': '#ff6b6b'}, hole=0.4)
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.markdown('<h3 class="section-title"> คะแนนความเสี่ยงตามชื่อ</h3>', unsafe_allow_html=True)
    fig_bar = px.bar(df, x='name', y='score', color='risk',
                    color_discrete_map={'ต่ำ': '#2ed573', 'กลาง': '#ffa502', 'สูง': '#ff6b6b'},
                    text='score', hover_data=['age'])
    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.markdown('<h3 class="section-title">📈 ความสัมพันธ์ อายุ vs คะแนน</h3>', unsafe_allow_html=True)
    fig_scatter = px.scatter(df, x='age', y='score', color='risk',
                            color_discrete_map={'ต่ำ': '#2ed573', 'กลาง': '#ffa502', 'สูง': '#ff6b6b'},
                            hover_data=['name'], size='score')
    fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
    st.plotly_chart(fig_scatter, use_container_width=True)

# ==================== หน้าที่ 5: AI ====================
elif menu == " AI":
    st.markdown('<div class="page-header"><h1>🤖 ระบบ AI ทำนายผล</h1></div>', unsafe_allow_html=True)
    st.subheader("🧠 โมเดล Random Forest Classifier")
    st.info("💡 โมเดลนี้ถูกฝึกด้วย Synthetic Dataset 500 รายการ ที่สร้างจาก Logic การให้คะแนนทางการแพทย์ของระบบ")

    np.random.seed(42)
    ages_sim = np.random.randint(40, 90, 500)
    scores_sim = np.random.randint(5, 80, 500) + (ages_sim - 40) * 0.3 
    X_sim = np.column_stack((ages_sim, scores_sim))

    y_sim = []
    for age, score in X_sim:
        multiplier = 1.0
        if age >= 70: multiplier += 0.3
        elif age >= 60: multiplier += 0.2
        elif age >= 50: multiplier += 0.1
        has_heart_disease = np.random.choice([True, False], p=[0.3, 0.7])
        if has_heart_disease: multiplier += 0.3
        final_score = int(score * multiplier)
        if final_score >= 50: y_sim.append(2)
        elif final_score >= 20: y_sim.append(1)
        else: y_sim.append(0)
    y_sim = np.array(y_sim)

    X_train, X_test, y_train, y_test = train_test_split(X_sim, y_sim, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test))
    st.success(f"✅ ฝึกโมเดลเสร็จสิ้น! (Accuracy: {accuracy*100:.1f}%)")

    st.markdown("---")
    st.markdown('<h3 class="section-title">🔮 ทดสอบทำนายผล</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: age_input = st.number_input("อายุ (ปี)", 40, 100, 45)
    with col2: score_input = st.number_input("คะแนนอาการดิบ", 0, 100, 20)

    if st.button("🤖 ให้ AI ทำนายผล", type="primary"):
        multiplier = 1.0
        if age_input >= 70: multiplier += 0.3
        elif age_input >= 60: multiplier += 0.2
        elif age_input >= 50: multiplier += 0.1
        final_score_input = int(score_input * multiplier)
        
        prediction = model.predict([[age_input, final_score_input]])
        proba = model.predict_proba([[age_input, final_score_input]])[0]
        
        result_map = {0: "✅ ความเสี่ยงต่ำ", 1: "⚠️ ความเสี่ยงกลาง", 2: "🚨 ความเสี่ยงสูง"}
        color_map = {0: "#2ed573", 1: "#ffa502", 2: "#ff6b6b"}

        st.markdown(f'<div style="background: linear-gradient(135deg, {color_map[prediction[0]]} 0%, {color_map[prediction[0]]}cc 100%); color: white; padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 15px 40px rgba(0,0,0,0.3);"><h2 style="font-size: 2rem; margin: 0;">{result_map[prediction[0]]}</h2><p style="font-size: 1.2rem; margin: 10px 0 0 0;">คะแนนหลังปรับตัวคูณ: {final_score_input}</p></div>', unsafe_allow_html=True)
        
        fig_proba = go.Figure(data=[
            go.Bar(x=['ต่ำ', 'กลาง', 'สูง'], y=proba * 100, marker_color=['#2ed573', '#ffa502', '#ff6b6b'], 
                   text=[f"{p*100:.1f}%" for p in proba], textposition='auto')
        ])
        fig_proba.update_layout(title="ความน่าจะเป็นของแต่ละระดับ (%)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig_proba, use_container_width=True)

    st.markdown("---")
    st.markdown('<h3 class="section-title">📊 Feature Importance</h3>', unsafe_allow_html=True)
    feature_names = ['อายุ', 'คะแนนอาการ']
    importances = model.feature_importances_
    fig_imp = go.Figure(data=[go.Bar(x=feature_names, y=importances, marker_color=['#667eea', '#764ba2'], 
                                     text=[f"{i*100:.1f}%" for i in importances], textposition='auto')])
    fig_imp.update_layout(title="ความสำคัญของฟีเจอร์", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
    st.plotly_chart(fig_imp, use_container_width=True)

# ==================== หน้าที่ 6: เกี่ยวกับ ====================
elif menu == "ℹ️ เกี่ยวกับ":
    st.markdown('<div class="page-header"><h1>ℹ️ เกี่ยวกับระบบ</h1></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card" style="margin-bottom: 20px;">
        <h4>🎓 โปรเจกต์ปี 4 (Senior Project)</h4>
        <p style="color: #555; line-height: 1.6;">
            <b>ระบบประเมินการตัดสินใจไปพบแพทย์สำหรับวัยกลางคนและผู้สูงอายุ (40+ ปี)</b><br><br>
            ระบบนี้ถูกพัฒนาขึ้นเพื่อช่วยกลุ่มวัยกลางคนและผู้สูงอายุในการประเมินอาการเบื้องต้น 
            และตัดสินใจว่าควรไปพบแพทย์หรือไม่ โดยนำเทคโนโลยี Machine Learning และ Data Visualization 
            มาประยุกต์ใช้เพื่อให้ได้ผลลัพธ์ที่แม่นยำและเข้าใจง่าย
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h3 class="section-title">🛠️ เทคโนโลยีที่ใช้</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>💻 Frontend & Backend</h4>
            <ul>
                <li>Streamlit (Python Web Framework)</li>
                <li>Pandas & NumPy (Data Processing)</li>
                <li>Plotly (Interactive Visualization)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 AI & Integration</h4>
            <ul>
                <li>Scikit-Learn (Machine Learning)</li>
                <li>Random Forest Classifier</li>
                <li>Line Notify API (Real-time Alert)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h3 class="section-title">🎯 วัตถุประสงค์</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="feature-card">
        <ul>
            <li>ช่วยกลุ่มวัยกลางคน (40+) และผู้สูงอายุ ตัดสินใจว่าควรไปพบแพทย์หรือไม่</li>
            <li>เน้นการป้องกันและเฝ้าระวังโรคไม่ติดต่อเรื้อรัง (NCDs) ตั้งแต่เนิ่นๆ</li>
            <li>นำเทคโนโลยี AI มาช่วยวิเคราะห์และทำนายความเสี่ยง</li>
            <li>ออกแบบ UI/UX ที่เหมาะสมและใช้งานง่าย (Accessibility)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box" style="margin-top: 30px;">
        <b>️ ข้อจำกัดสำคัญ:</b> ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น <b>ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้</b> 
        หากมีอาการรุนแรงหรือกังวลใจ ควรปรึกษาแพทย์หรือบุคลากรทางการแพทย์โดยตรง
    </div>
    """, unsafe_allow_html=True)

# ==================== Footer ====================
st.markdown("---")
st.markdown("""
<div class="footer">
    <p style="margin: 0; font-size: 1.1rem;">🏥 ระบบประเมินสุขภาพ (40+ ปี) | โปรเจกต์ปี 4</p>
    <p style="margin: 10px 0 0 0; font-size: 0.9rem; opacity: 0.8;">พัฒนาด้วย Streamlit • Python • Machine Learning</p>
</div>
""", unsafe_allow_html=True)