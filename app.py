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
    .metric-card h3 { color: #667eea; font-size: 1.8rem; font-weight: 700; margin: 10px 0; }
    .risk-high { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); color: white; padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 15px 40px rgba(238,90,111,0.4); animation: pulse 2s infinite; }
    .risk-medium { background: linear-gradient(135deg, #ffa502 0%, #ff7f50 100%); color: white; padding: 30px; border-radius: 20px; text-align: center; }
    .risk-low { background: linear-gradient(135deg, #2ed573 0%, #7bed9f 100%); color: white; padding: 30px; border-radius: 20px; text-align: center; }
    @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.02); } }
    .info-box { background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 25px; border-radius: 15px; border-left: 6px solid #667eea; box-shadow: 0 5px 20px rgba(0,0,0,0.1); margin: 20px 0; }
    .section-title { color: #667eea; font-size: 1.8rem; font-weight: 700; margin: 30px 0 20px 0; padding-bottom: 10px; border-bottom: 3px solid #667eea; display: inline-block; }
    .footer { text-align: center; color: white; padding: 30px; margin-top: 50px; background: rgba(0,0,0,0.2); border-radius: 15px; }
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
    <div style="text-align: center; padding: 20px; color: white;">
        <h2 style="font-size: 2rem; margin: 0;">🏥</h2>
        <h3 style="font-size: 1.3rem; margin: 10px 0;">Health Check</h3>
        <p style="font-size: 0.9rem; opacity: 0.9;">ระบบประเมินสุขภาพส่วนตัว</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    elderly_mode = st.checkbox("👓 โหมดตัวหนังสือใหญ่")
    if elderly_mode:
        st.markdown("<style> html { font-size: 125% !important; } </style>", unsafe_allow_html=True)
    
    menu = st.radio(
        "เมนูหลัก",
        ["🏠 หน้าหลัก", "🩺 ประเมินอาการใหม่", "📋 ประวัติการประเมินของฉัน", "📊 สถิติส่วนตัว", "ℹ️ เกี่ยวกับ"],
        index=1
    )
    
    st.markdown("---")
    
    data_count = get_data_count()
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; text-align: center; color: white;">
        <p style="margin: 0; font-size: 0.9rem;">📊 ข้อมูลของคุณ</p>
        <h3 style="margin: 10px 0; font-size: 2rem;">{data_count}</h3>
        <p style="margin: 0; font-size: 0.8rem;">รายการประเมิน</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ==================== หน้าที่ 1: หน้าหลัก ====================
if menu == "🏠 หน้าหลัก":
    st.markdown("""
    <div class="hero-section">
        <h1>🏥 ระบบประเมินสุขภาพส่วนตัว</h1>
        <h3>สำหรับวัยกลางคนและผู้สูงอายุ (40+ ปี)</h3>
        <p style="font-size: 1.1rem; margin-top: 20px; opacity: 0.9;">
            ประเมินอาการด้วยตัวเอง • บันทึกข้อมูลส่วนตัว • ติดตามผลสุขภาพ
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📋 {get_data_count()}</h3>
            <p>การประเมินของคุณ</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>👤 ส่วนตัว</h3>
            <p>ข้อมูลเป็นของคุณ</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🔒 ปลอดภัย</h3>
            <p>เก็บในเครื่องคุณ</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-title">📝 วิธีใช้งาน</h2>', unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.info("""
        **1. ประเมินอาการ**
        - กรอกข้อมูลส่วนตัว
        - เลือกอาการที่เป็น
        - ระบบคำนวณความเสี่ยง
        """)
    with col_b:
        st.info("""
        **2. บันทึกข้อมูล**
        - ข้อมูลจะถูกบันทึกอัตโนมัติ
        - เก็บเป็นไฟล์ CSV
        - เปิดดูใน Excel ได้
        """)
    with col_c:
        st.info("""
        **3. ดูประวัติ**
        - ดูผลการประเมินย้อนหลัง
        - เปรียบเทียบผลลัพธ์
        - ดาวน์โหลดข้อมูล
        """)
    
    st.markdown("""
    <div class="info-box" style="margin-top: 30px;">
        <b>💾 ข้อมูลของคุณ:</b> ระบบจะบันทึกข้อมูลการประเมินทั้งหมดลงในไฟล์ <code>assessment_data.csv</code> 
        ในโฟลเดอร์เดียวกับแอปนี้ คุณสามารถเปิดดู แก้ไข หรือสำรองข้อมูลได้ตลอดเวลา<br>
        <b>⚠️ หมายเหตุ:</b> ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น <b>ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้</b>
    </div>
    """, unsafe_allow_html=True)

# ==================== หน้าที่ 2: ประเมินอาการใหม่ ====================
elif menu == "🩺 ประเมินอาการใหม่":
    st.markdown('<div class="page-header"><h1>🩺 แบบประเมินอาการ (กรอกเอง)</h1></div>', unsafe_allow_html=True)

    with st.form("assessment_form", clear_on_submit=False):
        st.markdown('<h3 class="section-title">👤 ข้อมูลส่วนตัวของคุณ</h3>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: 
            name = st.text_input("ชื่อ-นามสกุล *", placeholder="กรอกชื่อของคุณ", help="ระบุชื่อ-นามสกุลของคุณ")
        with col2: 
            age = st.number_input("อายุ (ปี) *", min_value=40, max_value=120, value=45, help="ระบุอายุของคุณ")
        with col3: 
            gender = st.selectbox("เพศ *", ["ชาย", "หญิง", "ไม่ระบุ"], help="เลือกเพศของคุณ")

        st.markdown('<h3 class="section-title">🏥 ข้อมูลสุขภาพ</h3>', unsafe_allow_html=True)
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
        
        st.markdown('<h3 class="section-title">🤒 อาการที่คุณกำลังประสบอยู่ (เลือกเอง)</h3>', unsafe_allow_html=True)
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
            help="กรอกรายละเอียดเพิ่มเติมเกี่ยวกับอาการของคุณ"
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
                st.markdown(f'<div class="{risk_class}"><h2 style="font-size: 2rem; margin: 0;">🚨 ความเสี่ยงสูง!</h2><p style="font-size: 1.3rem; margin: 10px 0 0 0;">กรุณาไปพบแพทย์ทันที</p></div>', unsafe_allow_html=True)
                
                # ส่ง Line Notify
                line_msg = f"🚨 แจ้งเตือนฉุกเฉิน!\nชื่อ: {name}\nอายุ: {age} ปี\nคะแนน: {final_score}\nอาการ: {', '.join(selected_symptoms)}"
                send_line_notify(line_msg)
                
            elif final_score >= 20:
                risk_level, risk_class = "กลาง", "risk-medium"
                st.markdown(f'<div class="{risk_class}"><h2 style="font-size: 2rem; margin: 0;">⚠️ ความเสี่ยงกลาง</h2><p style="font-size: 1.3rem; margin: 10px 0 0 0;">ควรพบแพทย์ภายใน 24 ชั่วโมง</p></div>', unsafe_allow_html=True)
            else:
                risk_level, risk_class = "ต่ำ", "risk-low"
                st.markdown(f'<div class="{risk_class}"><h2 style="font-size: 2rem; margin: 0;">✅ ความเสี่ยงต่ำ</h2><p style="font-size: 1.3rem; margin: 10px 0 0 0;">ดูแลตัวเองได้</p></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown('<h3 class="section-title">📊 สรุปผลการประเมินของคุณ</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="info-box">
                    <b>👤 ข้อมูลผู้ประเมิน:</b><br>
                    • ชื่อ: {name}<br>
                    • อายุ: {age} ปี<br>
                    • เพศ: {gender}<br>
                    • โรคประจำตัว: {', '.join(chronic) if chronic else 'ไม่มี'}<br>
                    • ยาที่รับประทาน: {medications if medications else 'ไม่มี'}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="info-box">
                    <b>📊 ผลการประเมิน:</b><br>
                    • คะแนนดิบ: {total_score}<br>
                    • ตัวคูณความเสี่ยง: {risk_multiplier}x<br>
                    • <b>คะแนนรวม: {final_score}</b><br>
                    • ระดับความเสี่ยง: {risk_level}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f'<h4>อาการที่คุณเลือก ({len(selected_symptoms)} อาการ)</h4>')
            for symptom in selected_symptoms:
                st.markdown(f"• {symptom}")
            
            if notes:
                st.markdown(f"**หมายเหตุ:** {notes}")
            
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
elif menu == "📋 ประวัติการประเมินของฉัน":
    st.markdown('<div class="page-header"><h1>📋 ประวัติการประเมินของคุณ</h1></div>', unsafe_allow_html=True)
    
    df = load_data()
    
    if df.empty:
        st.markdown("""
        <div class="info-box" style="text-align: center; padding: 40px;">
            <h3 style="color: #667eea; margin: 0;">📭 ยังไม่มีข้อมูล</h3>
            <p style="margin: 10px 0 0 0;">กรุณาไปที่หน้า 'ประเมินอาการใหม่' เพื่อเริ่มประเมิน</p>
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
                        st.write(f"**วันที่:** {record['date']}")
                        st.write(f"**ชื่อ:** {record['name']}")
                        st.write(f"**อายุ:** {record['age']} ปี")
                        st.write(f"**เพศ:** {record['gender']}")
                        st.write(f"**โรคประจำตัว:** {record['chronic']}")
                    with col2:
                        st.write(f"**คะแนน:** {record['score']}")
                        st.write(f"**ความเสี่ยง:** {record['risk']}")
                        st.write(f"**อาการ:** {record['symptoms']}")
                        if record['notes'] != '-':
                            st.write(f"**หมายเหตุ:** {record['notes']}")
        
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
elif menu == "📊 สถิติส่วนตัว":
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
        
        st.markdown('<h3 class="section-title">📊 สัดส่วนระดับความเสี่ยงของคุณ</h3>', unsafe_allow_html=True)
        risk_counts = df['risk'].value_counts().reset_index()
        risk_counts.columns = ['ระดับความเสี่ยง', 'จำนวน']
        fig_pie = px.pie(
            risk_counts, 
            values='จำนวน', 
            names='ระดับความเสี่ยง', 
            color='ระดับความเสี่ยง',
            color_discrete_map={'ต่ำ': '#2ed573', 'กลาง': '#ffa502', 'สูง': '#ff6b6b'}, 
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.markdown('<h3 class="section-title">📊 คะแนนความเสี่ยงในแต่ละครั้ง</h3>', unsafe_allow_html=True)
        fig_bar = px.bar(
            df.sort_values('date'), 
            x='date', 
            y='score', 
            color='risk',
            color_discrete_map={'ต่ำ': '#2ed573', 'กลาง': '#ffa502', 'สูง': '#ff6b6b'},
            text='score',
            hover_data=['name', 'symptoms']
        )
        fig_bar.update_traces(textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.markdown('<h3 class="section-title">📈 ความสัมพันธ์ อายุ vs คะแนน</h3>', unsafe_allow_html=True)
        fig_scatter = px.scatter(
            df, 
            x='age', 
            y='score', 
            color='risk',
            color_discrete_map={'ต่ำ': '#2ed573', 'กลาง': '#ffa502', 'สูง': '#ff6b6b'},
            hover_data=['name', 'date', 'symptoms'], 
            size='score'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# ==================== หน้าที่ 5: เกี่ยวกับ ====================
elif menu == "ℹ️ เกี่ยวกับ":
    st.markdown('<div class="page-header"><h1>ℹ️ เกี่ยวกับระบบ</h1></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <b>🎓 โปรเจกต์ปี 4 (Senior Project)</b><br>
        <b>ระบบประเมินการตัดสินใจไปพบแพทย์สำหรับวัยกลางคนและผู้สูงอายุ (40+ ปี)</b><br><br>
        ระบบนี้ถูกพัฒนาขึ้นเพื่อให้คุณสามารถประเมินอาการสุขภาพด้วยตัวเอง 
        โดยเน้นการคัดกรองโรคไม่ติดต่อเรื้อรัง (NCDs) เช่น เบาหวาน ความดันโลหิตสูง โรคหัวใจและหลอดเลือด
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h3 class="section-title">💾 การจัดเก็บข้อมูลของคุณ</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        <b>📁 ไฟล์ข้อมูล:</b> <code>assessment_data.csv</code><br>
        <b>📍 ตำแหน่ง:</b> โฟลเดอร์เดียวกับแอปนี้<br>
        <b>🔒 ความเป็นส่วนตัว:</b> ข้อมูลถูกเก็บในเครื่องของคุณเท่านั้น<br>
        <b>📥 การสำรองข้อมูล:</b> สามารถดาวน์โหลดไฟล์ CSV ได้จากหน้า "ประวัติการประเมิน"
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box" style="margin-top: 30px;">
        <b>⚠️ ข้อจำกัดสำคัญ:</b> ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น 
        <b>ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้</b> หากมีอาการรุนแรงหรือกังวลใจ 
        ควรปรึกษาแพทย์หรือบุคลากรทางการแพทย์โดยตรง
    </div>
    """, unsafe_allow_html=True)

# ==================== Footer ====================
st.markdown("---")
st.markdown("""
<div class="footer">
    <p style="margin: 0; font-size: 1.1rem;">🏥 ระบบประเมินสุขภาพส่วนตัว (40+ ปี) | โปรเจกต์ปี 4</p>
    <p style="margin: 10px 0 0 0; font-size: 0.9rem; opacity: 0.8;">พัฒนาด้วย Streamlit • Python • Data Visualization</p>
</div>
""", unsafe_allow_html=True)