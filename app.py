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

warnings.filterwarnings('ignore')

# ==================== ตั้งค่าไฟล์เก็บข้อมูล ====================
DATA_FILE = "assessment_data.csv"

def save_to_csv(data_dict):
    """บันทึกข้อมูลลงไฟล์ CSV"""
    df_new = pd.DataFrame([data_dict])
    if os.path.exists(DATA_FILE):
        df_new.to_csv(DATA_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(DATA_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')

def load_data():
    """โหลดข้อมูลจากไฟล์ CSV"""
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

def get_data_count():
    """นับจำนวนข้อมูลที่มี"""
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        return len(df)
    return 0

# ==================== ตั้งค่าหน้าเว็บ ====================
st.set_page_config(
    page_title="ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ตกแต่ง ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .risk-high { background: linear-gradient(135deg, #FF4B4B, #FF0000); color: white; padding: 20px; border-radius: 15px; text-align: center; }
    .risk-medium { background: linear-gradient(135deg, #FFA500, #FF8C00); color: white; padding: 20px; border-radius: 15px; text-align: center; }
    .risk-low { background: linear-gradient(135deg, #4CAF50, #45a049); color: white; padding: 20px; border-radius: 15px; text-align: center; }
    .info-box { background-color: #E8F4FD; padding: 15px; border-radius: 10px; border-left: 5px solid #2E86AB; }
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

CHRONIC_DISEASES = ["เบาหวาน", "ความดันโลหิตสูง", "โรคหัวใจ", "โรคไต", "โรคปอด", "โรคหลอดเลือดสมอง", "ไม่มี"]

# ==================== Sidebar ====================
with st.sidebar:
    st.title("📋 เมนูหลัก")
    menu = st.radio("เลือกหัวข้อ", ["🏠 หน้าหลัก", "🩺 ประเมินอาการ", " ประวัติการประเมิน", "📈 สถิติและกราฟ", "ℹ️ เกี่ยวกับระบบ"], index=1)
    
    # แสดงจำนวนข้อมูลที่เก็บไว้
    data_count = get_data_count()
    st.markdown("---")
    st.info(f"📊 **จำนวนข้อมูลที่เก็บ:** {data_count} รายการ")
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ==================== หน้าที่ 1: หน้าหลัก ====================
if menu == "🏠 หน้าหลัก":
    st.markdown('<div class="main-header"><h1>🏥 ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ</h1></div>', unsafe_allow_html=True)
    
    data_count = get_data_count()
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("📋 จำนวนการประเมิน", data_count)
    with col2: st.metric("👴 กลุ่มเป้าหมาย", "60+ ปี")
    with col3: st.metric("⚕️ ระดับความเสี่ยง", "3 ระดับ")
    
    st.markdown("### 📂 ไฟล์ข้อมูลที่เก็บ")
    st.markdown(f"""
    <div class="info-box">
        <b>📁 ตำแหน่งไฟล์:</b> <code>assessment_data.csv</code> (ในโฟลเดอร์โปรเจกต์)<br>
        <b>💾 จำนวนบันทึก:</b> {data_count} รายการ<br>
        <b> อัปเดตล่าสุด:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </div>
    """, unsafe_allow_html=True)
    
    st.info(" ระบบจะบันทึกข้อมูลการประเมินทุกครั้งลงไฟล์ CSV โดยอัตโนมัติ")

# ==================== หน้าที่ 2: ประเมินอาการ ====================
elif menu == "🩺 ประเมินอาการ":
    st.markdown('<div class="main-header"><h1>🩺 แบบประเมินอาการ</h1></div>', unsafe_allow_html=True)

    with st.form("assessment_form"):
        col1, col2, col3 = st.columns(3)
        with col1: name = st.text_input("ชื่อ-นามสกุล *", placeholder="กรอกชื่อ")
        with col2: age = st.number_input("อายุ (ปี) *", 60, 120, 65)
        with col3: gender = st.selectbox("เพศ *", ["ชาย", "หญิง", "ไม่ระบุ"])

        chronic = st.multiselect("🏥 โรคประจำตัว", CHRONIC_DISEASES)
        
        st.subheader("🤒 อาการที่พบ")
        total_score = 0
        selected_symptoms = []
        emergency_symptoms = []

        for category, symptoms in SYMPTOMS_DATA.items():
            with st.expander(category, expanded=True):
                cols = st.columns(2)
                for i, (symptom, score) in enumerate(symptoms.items()):
                    with cols[i % 2]:
                        if st.checkbox(f"{symptom} (+{score})", key=symptom):
                            total_score += score
                            selected_symptoms.append(symptom)
                            if "ฉุกเฉิน" in category: emergency_symptoms.append(symptom)

        submitted = st.form_submit_button("🔍 ประเมินผล", type="primary", use_container_width=True)

    if submitted:
        if not name or not selected_symptoms:
            st.error("⚠️ กรุณากรอกชื่อและเลือกอาการ")
        else:
            # คำนวณคะแนน
            risk_multiplier = 1.0
            if age >= 75: risk_multiplier += 0.3
            elif age >= 70: risk_multiplier += 0.2
            if "โรคหัวใจ" in chronic or "โรคหลอดเลือดสมอง" in chronic: risk_multiplier += 0.3
            
            final_score = int(total_score * risk_multiplier)
            
            # ตัดสินผล
            if final_score >= 50 or len(emergency_symptoms) > 0:
                risk_level, risk_class = "สูง", "risk-high"
                st.markdown(f'<div class="{risk_class}"><h2> ความเสี่ยงสูง! ไปพบแพทย์ทันที</h2></div>', unsafe_allow_html=True)
            elif final_score >= 20:
                risk_level, risk_class = "กลาง", "risk-medium"
                st.markdown(f'<div class="{risk_class}"><h2>⚠️ ความเสี่ยงกลาง พบแพทย์ใน 24 ชม.</h2></div>', unsafe_allow_html=True)
            else:
                risk_level, risk_class = "ต่ำ", "risk-low"
                st.markdown(f'<div class="{risk_class}"><h2>✅ ความเสี่ยงต่ำ ดูแลตัวเองได้</h2></div>', unsafe_allow_html=True)
            
            st.write(f"**คะแนน:** {final_score} | **อาการ:** {', '.join(selected_symptoms)}")
            
            # บันทึกข้อมูลลง CSV
            record = {
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "name": name, "age": age, "gender": gender,
                "chronic": ", ".join(chronic) if chronic else "ไม่มี",
                "score": final_score, "risk": risk_level,
                "symptoms": ", ".join(selected_symptoms)
            }
            save_to_csv(record)
            st.success(f"✅ บันทึกผลการประเมินเรียบร้อยแล้ว! (รวม {get_data_count()} รายการ)")

# ==================== หน้าที่ 3: ประวัติการประเมิน ====================
elif menu == " ประวัติการประเมิน":
    st.markdown('<div class="main-header"><h1> ประวัติการประเมิน</h1></div>', unsafe_allow_html=True)
    
    df = load_data()
    
    if df.empty:
        st.info(" ยังไม่มีข้อมูลการประเมิน กรุณาไปที่หน้า 'ประเมินอาการ' เพื่อเริ่มประเมิน")
    else:
        st.success(f"✅ พบข้อมูลการประเมิน **{len(df)} รายการ** ที่เก็บไว้ในระบบ")
        
        # แสดงตารางข้อมูล
        st.subheader(" ตารางข้อมูลทั้งหมด")
        st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True)
        
        # ดาวน์โหลดไฟล์ CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์ CSV",
            data=csv,
            file_name='assessment_data.csv',
            mime='text/csv',
        )
        
        if st.button("🗑️ ล้างข้อมูลทั้งหมด", type="secondary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
                st.success("ลบข้อมูลเรียบร้อยแล้ว!")
                st.rerun()

# ==================== หน้าที่ 4: สถิติและกราฟ ====================
elif menu == "📈 สถิติและกราฟ":
    st.markdown('<div class="main-header"><h1>📊 สถิติและกราฟ</h1></div>', unsafe_allow_html=True)

    df = load_data()
    
    if df.empty:
        st.warning("⚠️ ยังไม่มีข้อมูลจริงในระบบ กรุณาประเมินอาการอย่างน้อย 1 ครั้งเพื่อดูกราฟ")
        st.info("💡 หลังจากประเมินอาการ ข้อมูลจะถูกบันทึกและแสดงในกราฟโดยอัตโนมัติ")
    else:
        st.success(f"📊 แสดงกราฟจากข้อมูลจริง **{len(df)} รายการ**")
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("จำนวนการประเมิน", len(df))
        with col2: st.metric("ความเสี่ยงสูง", len(df[df['risk'] == 'สูง']))
        with col3: st.metric("คะแนนเฉลี่ย", f"{df['score'].mean():.1f}")

        st.markdown("---")
        
        # กราฟที่ 1: Pie Chart
        st.subheader("📊 สัดส่วนระดับความเสี่ยง")
        risk_counts = df['risk'].value_counts().reset_index()
        risk_counts.columns = ['ระดับความเสี่ยง', 'จำนวน']
        fig_pie = px.pie(risk_counts, values='จำนวน', names='ระดับความเสี่ยง', 
                        color='ระดับความเสี่ยง',
                        color_discrete_map={'ต่ำ': '#4CAF50', 'กลาง': '#FFA500', 'สูง': '#FF4B4B'})
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        
        # กราฟที่ 2: Bar Chart
        st.subheader(" คะแนนความเสี่ยงตามชื่อ")
        fig_bar = px.bar(df, x='name', y='score', color='risk',
                        color_discrete_map={'ต่ำ': '#4CAF50', 'กลาง': '#FFA500', 'สูง': '#FF4B4B'},
                        text='score', hover_data=['age', 'date'])
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        
        # กราฟที่ 3: Scatter
        st.subheader("📊 ความสัมพันธ์ อายุ vs คะแนน")
        fig_scatter = px.scatter(df, x='age', y='score', color='risk',
                                color_discrete_map={'ต่ำ': '#4CAF50', 'กลาง': '#FFA500', 'สูง': '#FF4B4B'},
                                hover_data=['name', 'symptoms'])
        st.plotly_chart(fig_scatter, use_container_width=True)

# ==================== หน้าที่ 5: เกี่ยวกับระบบ ====================
elif menu == "ℹ️ เกี่ยวกับระบบ":
    st.markdown('<div class="main-header"><h1>ℹ️ เกี่ยวกับระบบ</h1></div>', unsafe_allow_html=True)
    st.markdown("""
    ### 🎓 โปรเจกต์ปี 4
    **ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ**
    
    ### 💾 การจัดเก็บข้อมูล
    - ระบบบันทึกข้อมูลการประเมินทุกครั้งลงไฟล์ **CSV**
    - ไฟล์จะถูกสร้างอัตโนมัติในโฟลเดอร์โปรเจกต์
    - สามารถเปิดดูด้วย Excel หรือโปรแกรม Spreadsheet ทั่วไป
    
    ### 📂 ไฟล์ที่สำคัญ
    - `app.py` - โค้ดหลักของระบบ
    - `assessment_data.csv` - ฐานข้อมูลการประเมิน
    - `requirements.txt` - ไลบรารีที่ต้องการ
    
    ### ⚠️ ข้อจำกัด
    ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้
    """)

# ==================== Footer ====================
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'><p> ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ | โปรเจกต์ปี 4</p></div>", unsafe_allow_html=True)