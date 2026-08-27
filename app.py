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

# ==================== CSS แก้สีตัวอักษรให้อ่านง่าย ====================
st.markdown("""
<style>
    /* พื้นหลังสีอ่อนสบายตา */
    .stApp {
        background-color: #f0f4f8;
    }
    
    /* หัวข้อใหญ่ - ตัวหนังสือขาวชัดเจน */
    .hero-section, .page-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .hero-section h1, .page-header h1 {
        font-size: 2.2rem;
        font-weight: bold;
        margin: 0;
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-section h3, .hero-section p {
        color: white !important;
        font-size: 1.2rem;
    }
    
    /* การ์ดข้อมูล - พื้นขาว ตัวหนังสือเข้ม */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 2px solid #e0e0e0;
    }
    
    .metric-card h3 {
        color: #667eea !important;
        font-size: 2rem;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .metric-card p {
        color: #333 !important;
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
    }
    
    /* การ์ดความเสี่ยง - ตัวหนังสือขาวชัดเจน */
    .risk-high {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(255,75,43,0.4);
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(247,151,30,0.4);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(17,153,142,0.4);
    }
    
    .risk-high h2, .risk-medium h2, .risk-low h2 {
        color: white !important;
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    
    .risk-high p, .risk-medium p, .risk-low p {
        color: white !important;
        font-size: 1.2rem;
        margin: 10px 0 0 0;
    }
    
    /* กล่องข้อมูล - พื้นขาว ตัวหนังสือเข้ม */
    .info-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    
    .info-box b {
        color: #667eea !important;
        font-size: 1.1rem;
    }
    
    .info-box p, .info-box span {
        color: #333 !important;
        line-height: 1.8;
    }
    
    /* หัวข้อส่วน - สีเข้มชัดเจน */
    .section-title {
        color: #667eea !important;
        font-size: 1.6rem;
        font-weight: bold;
        margin: 2rem 0 1rem 0;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
        display: inline-block;
    }
    
    /* ปุ่ม */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        font-size: 1rem;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Footer - ตัวหนังสือขาวชัดเจน */
    .footer {
        text-align: center;
        color: white !important;
        padding: 2rem;
        margin-top: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .footer p {
        color: white !important;
        margin: 5px 0;
    }
    
    /* Sidebar - ปรับให้อ่านง่าย */
    section[data-testid="stSidebar"] {
        background-color: #2d3748;
    }
    
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== ข้อมูลทางการแพทย์ ====================
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
    st.title("🏥 Health Check")
    st.markdown("### ระบบประเมินสุขภาพส่วนตัว")
    st.markdown("**สำหรับวัย 40+ ปี**")
    st.markdown("---")
    
    elderly_mode = st.checkbox("👓 โหมดตัวหนังสือใหญ่")
    if elderly_mode:
        st.markdown("<style> html { font-size: 125% !important; } </style>", unsafe_allow_html=True)
    
    menu = st.radio(
        "เมนูหลัก",
        [" หน้าหลัก", "🩺 ประเมินอาการ", "📋 ประวัติ", "📊 สถิติ", "ℹ️ เกี่ยวกับ"],
        index=1
    )
    
    st.markdown("---")
    
    data_count = get_data_count()
    st.info(f"📊 ข้อมูลของคุณ: **{data_count} รายการ**")
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ==================== หน้าที่ 1: หน้าหลัก ====================
if menu == "🏠 หน้าหลัก":
    st.markdown("""
    <div class="hero-section">
        <h1> ระบบประเมินสุขภาพส่วนตัว</h1>
        <h3>สำหรับวัยกลางคนและผู้สูงอายุ (40+ ปี)</h3>
        <p>ประเมินอาการด้วยตัวเอง • บันทึกข้อมูลส่วนตัว • ติดตามผลสุขภาพ</p>
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
            <h3> ส่วนตัว</h3>
            <p>ข้อมูลเป็นของคุณ</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3> ปลอดภัย</h3>
            <p>เก็บในเครื่องคุณ</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">📝 วิธีใช้งาน</div>', unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.info("**1. ประเมินอาการ**\n- กรอกข้อมูลส่วนตัว\n- เลือกอาการที่เป็น\n- ระบบคำนวณความเสี่ยง")
    with col_b:
        st.info("**2. บันทึกข้อมูล**\n- ข้อมูลจะถูกบันทึกอัตโนมัติ\n- เก็บเป็นไฟล์ CSV\n- เปิดดูใน Excel ได้")
    with col_c:
        st.info("**3. ดูประวัติ**\n- ดูผลการประเมินย้อนหลัง\n- เปรียบเทียบผลลัพธ์\n- ดาวน์โหลดข้อมูล")
    
    st.warning("⚠️ **หมายเหตุ:** ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้")

# ==================== หน้าที่ 2: ประเมินอาการ ====================
elif menu == "🩺 ประเมินอาการ":
    st.markdown('<div class="page-header"><h1>🩺 แบบประเมินอาการ</h1></div>', unsafe_allow_html=True)

    with st.form("assessment_form", clear_on_submit=False):
        st.markdown("### 👤 ข้อมูลส่วนตัวของคุณ")
        col1, col2, col3 = st.columns(3)
        with col1: 
            name = st.text_input("ชื่อ-นามสกุล *", placeholder="กรอกชื่อของคุณ")
        with col2: 
            age = st.number_input("อายุ (ปี) *", min_value=40, max_value=120, value=45)
        with col3: 
            gender = st.selectbox("เพศ *", ["ชาย", "หญิง", "ไม่ระบุ"])

        st.markdown("### 🏥 ข้อมูลสุขภาพ")
        col1, col2 = st.columns(2)
        with col1:
            chronic = st.multiselect("โรคประจำตัว", CHRONIC_DISEASES)
        with col2:
            medications = st.text_input("ยาที่รับประทานประจำ (ถ้ามี)", placeholder="เช่น ยาลดความดัน")
        
        col1, col2 = st.columns(2)
        with col1:
            bp = st.text_input("ความดันโลหิตล่าสุด", placeholder="เช่น 120/80")
        with col2:
            bs = st.number_input("ระดับน้ำตาลในเลือด (mg/dL)", min_value=0, max_value=600, value=100)
        
        st.markdown("### 🤒 อาการที่คุณกำลังประสบอยู่")
        st.info("💡 เลือกอาการที่คุณกำลังเป็นอยู่ (เลือกได้มากกว่า 1)")
        
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

        notes = st.text_area(" หมายเหตุเพิ่มเติม (ถ้ามี)", placeholder="เช่น อาการเป็นมา 3 วัน", height=100)

        submitted = st.form_submit_button(" ประเมินผลตอนนี้", type="primary", use_container_width=True)

    if submitted:
        if not name:
            st.error("️ กรุณากรอกชื่อ-นามสกุล")
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
                risk_level = "สูง"
                st.markdown('<div class="risk-high"><h2>🚨 ความเสี่ยงสูง!</h2><p>กรุณาไปพบแพทย์ทันที</p></div>', unsafe_allow_html=True)
                line_msg = f" แจ้งเตือนฉุกเฉิน!\nชื่อ: {name}\nอายุ: {age} ปี\nคะแนน: {final_score}\nอาการ: {', '.join(selected_symptoms)}"
                send_line_notify(line_msg)
            elif final_score >= 20:
                risk_level = "กลาง"
                st.markdown('<div class="risk-medium"><h2>⚠️ ความเสี่ยงกลาง</h2><p>ควรพบแพทย์ภายใน 24 ชั่วโมง</p></div>', unsafe_allow_html=True)
            else:
                risk_level = "ต่ำ"
                st.markdown('<div class="risk-low"><h2>✅ ความเสี่ยงต่ำ</h2><p>ดูแลตัวเองได้</p></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("###  สรุปผลการประเมิน")
            
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
                    <b>📊 ผลการประเมิน:</b><br>
                    • คะแนนดิบ: {total_score}<br>
                    • ตัวคูณความเสี่ยง: {risk_multiplier}x<br>
                    • <b>คะแนนรวม: {final_score}</b><br>
                    • ระดับความเสี่ยง: {risk_level}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"**อาการที่คุณเลือก ({len(selected_symptoms)} อาการ):**")
            for symptom in selected_symptoms:
                st.write(f"• {symptom}")
            
            if notes:
                st.markdown(f"**หมายเหตุ:** {notes}")
            
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

# ==================== หน้าที่ 3: ประวัติ ====================
elif menu == "📋 ประวัติ":
    st.markdown('<div class="page-header"><h1>📋 ประวัติการประเมินของคุณ</h1></div>', unsafe_allow_html=True)
    
    df = load_data()
    
    if df.empty:
        st.info(" ยังไม่มีข้อมูล กรุณาไปที่หน้า 'ประเมินอาการ' เพื่อเริ่มประเมิน")
    else:
        st.success(f"✅ พบข้อมูลการประเมิน **{len(df)} รายการ**")
        
        tab1, tab2, tab3 = st.tabs(["️ ดูข้อมูล", "✏️ แก้ไข/ลบ", "📥 ดาวน์โหลด"])
        
        with tab1:
            st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True)
            
            if len(df) > 0:
                selected_index = st.selectbox("เลือกรายการเพื่อดูรายละเอียด", range(len(df)),
                    format_func=lambda x: f"{df.iloc[x]['date']} - {df.iloc[x]['name']} (ความเสี่ยง: {df.iloc[x]['risk']})")
                
                record = df.iloc[selected_index]
                st.write(f"**วันที่:** {record['date']}")
                st.write(f"**ชื่อ:** {record['name']}")
                st.write(f"**อายุ:** {record['age']} ปี")
                st.write(f"**คะแนน:** {record['score']}")
                st.write(f"**ความเสี่ยง:** {record['risk']}")
                st.write(f"**อาการ:** {record['symptoms']}")
        
        with tab2:
            if len(df) > 0:
                edit_index = st.selectbox("เลือกรายการที่ต้องการลบ", range(len(df)),
                    format_func=lambda x: f"{df.iloc[x]['date']} - {df.iloc[x]['name']}")
                if st.button("️ ลบรายการนี้"):
                    if delete_record(edit_index):
                        st.success("✅ ลบข้อมูลเรียบร้อยแล้ว!")
                        st.rerun()
        
        with tab3:
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label="📥 ดาวน์โหลดไฟล์ CSV", data=csv,
                file_name=f'my_health_data_{datetime.now().strftime("%Y%m%d")}.csv', mime='text/csv')

# ==================== หน้าที่ 4: สถิติ ====================
elif menu == "📊 สถิติ":
    st.markdown('<div class="page-header"><h1>📊 สถิติการประเมินของคุณ</h1></div>', unsafe_allow_html=True)

    df = load_data()
    
    if df.empty:
        st.info("💡 ยังไม่มีข้อมูล กรุณาประเมินอาการอย่างน้อย 1 ครั้ง")
    else:
        st.success(f"📊 แสดงสถิติจากข้อมูลของคุณ **{len(df)} รายการ**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><h3>📋 {len(df)}</h3><p>การประเมินทั้งหมด</p></div>', unsafe_allow_html=True)
        with col2:
            high_count = len(df[df['risk'] == 'สูง'])
            st.markdown(f'<div class="metric-card"><h3>🚨 {high_count}</h3><p>ความเสี่ยงสูง</p></div>', unsafe_allow_html=True)
        with col3:
            avg_score = df['score'].mean()
            st.markdown(f'<div class="metric-card"><h3>📈 {avg_score:.1f}</h3><p>คะแนนเฉลี่ย</p></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📊 สัดส่วนระดับความเสี่ยง")
        risk_counts = df['risk'].value_counts().reset_index()
        risk_counts.columns = ['ระดับความเสี่ยง', 'จำนวน']
        fig_pie = px.pie(risk_counts, values='จำนวน', names='ระดับความเสี่ยง', 
                        color='ระดับความเสี่ยง', color_discrete_map={'ต่ำ': '#2ed573', 'กลาง': '#ffa502', 'สูง': '#ff6b6b'})
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.markdown("### 📊 คะแนนความเสี่ยงในแต่ละครั้ง")
        fig_bar = px.bar(df.sort_values('date'), x='date', y='score', color='risk',
                        color_discrete_map={'ต่ำ': '#2ed573', 'กลาง': '#ffa502', 'สูง': '#ff6b6b'})
        st.plotly_chart(fig_bar, use_container_width=True)

# ==================== หน้าที่ 5: เกี่ยวกับ ====================
elif menu == "ℹ️ เกี่ยวกับ":
    st.markdown('<div class="page-header"><h1>ℹ️ เกี่ยวกับระบบ</h1></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <b>🎓 โปรเจกต์ปี 4 (Senior Project)</b><br>
        <b>ระบบประเมินการตัดสินใจไปพบแพทย์สำหรับวัยกลางคนและผู้สูงอายุ (40+ ปี)</b><br><br>
        ระบบนี้ถูกพัฒนาขึ้นเพื่อให้คุณสามารถประเมินอาการสุขภาพด้วยตัวเอง 
        โดยเน้นการคัดกรองโรคไม่ติดต่อเรื้อรัง (NCDs)
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("️ **ข้อจำกัด:** ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้")

# ==================== Footer ====================
st.markdown("---")
st.markdown('<div class="footer"><p>🏥 ระบบประเมินสุขภาพส่วนตัว (40+ ปี) | โปรเจกต์ปี 4</p><p>พัฒนาด้วย Streamlit • Python</p></div>', unsafe_allow_html=True)