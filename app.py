import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from datetime import datetime
import warnings
import os
import requests

warnings.filterwarnings('ignore')

# ==================== ตั้งค่า Line Notify ====================
# ไปสร้าง Token ที่: https://notify-bot.line.me/th/
LINE_NOTIFY_TOKEN = "ใส่_TOKEN_ของคุณที่นี่" # ตัวอย่าง: "AbCdEfGhIjKlMnOpQrStUvWxYz123456"

def send_line_notify(message):
    """ส่งข้อความแจ้งเตือนทาง LINE"""
    if LINE_NOTIFY_TOKEN == "ใส่_TOKEN_ของคุณที่นี่":
        return # ข้ามถ้ายังไม่ได้ใส่ Token
    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    data = {"message": message}
    try:
        requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)
    except Exception as e:
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
    .risk-high { background: linear-gradient(135deg, #FF4B4B, #FF0000); color: white; padding: 20px; border-radius: 15px; text-align: center; animation: pulse 2s; }
    .risk-medium { background: linear-gradient(135deg, #FFA500, #FF8C00); color: white; padding: 20px; border-radius: 15px; text-align: center; }
    .risk-low { background: linear-gradient(135deg, #4CAF50, #45a049); color: white; padding: 20px; border-radius: 15px; text-align: center; }
    .info-box { background-color: #E8F4FD; padding: 15px; border-radius: 10px; border-left: 5px solid #2E86AB; }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }
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
    
    # ฟีเจอร์ปีที่ 4: โหมดผู้สูงอายุ
    elderly_mode = st.checkbox("👓 โหมดตัวหนังสือใหญ่ (สำหรับผู้สูงอายุ)")
    if elderly_mode:
        st.markdown("<style> html { font-size: 125% !important; } .stTextInput > div > div > input, .stSelectbox > div > div > select { font-size: 1.2rem !important; } </style>", unsafe_allow_html=True)
    
    menu = st.radio("เลือกหัวข้อ", ["🏠 หน้าหลัก", "🩺 ประเมินอาการ", "📊 ประวัติการประเมิน", "📈 สถิติและกราฟ", "🤖 AI ทำนายผล", "ℹ️ เกี่ยวกับระบบ"], index=1)
    
    st.markdown("---")
    st.info(f"📊 **ข้อมูลในระบบ:** {get_data_count()} รายการ")
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ==================== หน้าที่ 1: หน้าหลัก ====================
if menu == "🏠 หน้าหลัก":
    st.markdown('<div class="main-header"><h1>🏥 ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ</h1><h3>Elderly Medical Decision Support System</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("📋 จำนวนการประเมิน", get_data_count())
    with col2: st.metric("👴 กลุ่มเป้าหมาย", "60+ ปี")
    with col3: st.metric("⚕️ ระดับความเสี่ยง", "3 ระดับ")
    
    st.markdown("### 💾 การจัดเก็บข้อมูล")
    st.markdown(f"""
    <div class="info-box">
        <b>📁 ตำแหน่งไฟล์:</b> <code>assessment_data.csv</code><br>
        <b>💾 จำนวนบันทึก:</b> {get_data_count()} รายการ<br>
        <b>⚠️ หมายเหตุ:</b> หากใช้งานบน Streamlit Cloud กรุณาดาวน์โหลดไฟล์ CSV เป็นระยะเพื่อสำรองข้อมูล
    </div>
    """, unsafe_allow_html=True)

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
            # คำนวณคะแนน (Weighted Scoring)
            risk_multiplier = 1.0
            if age >= 75: risk_multiplier += 0.3
            elif age >= 70: risk_multiplier += 0.2
            if "โรคหัวใจ" in chronic or "โรคหลอดเลือดสมอง" in chronic: risk_multiplier += 0.3
            
            final_score = int(total_score * risk_multiplier)
            
            # ตัดสินผล
            if final_score >= 50 or len(emergency_symptoms) > 0:
                risk_level, risk_class = "สูง", "risk-high"
                st.markdown(f'<div class="{risk_class}"><h2>🚨 ความเสี่ยงสูง! ไปพบแพทย์ทันที</h2></div>', unsafe_allow_html=True)
                
                # ส่ง Line Notify
                line_msg = f"🚨 แจ้งเตือนฉุกเฉิน!\nชื่อ: {name}\nอายุ: {age} ปี\nคะแนนความเสี่ยง: {final_score}\nอาการ: {', '.join(selected_symptoms)}\nกรุณาตรวจสอบทันที!"
                send_line_notify(line_msg)
                
            elif final_score >= 20:
                risk_level, risk_class = "กลาง", "risk-medium"
                st.markdown(f'<div class="{risk_class}"><h2>⚠️ ความเสี่ยงกลาง พบแพทย์ใน 24 ชม.</h2></div>', unsafe_allow_html=True)
            else:
                risk_level, risk_class = "ต่ำ", "risk-low"
                st.markdown(f'<div class="{risk_class}"><h2>✅ ความเสี่ยงต่ำ ดูแลตัวเองได้</h2></div>', unsafe_allow_html=True)
            
            st.write(f"**คะแนนรวม:** {final_score} (ตัวคูณ {risk_multiplier}x) | **อาการ:** {', '.join(selected_symptoms)}")
            
            # บันทึกข้อมูล
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
elif menu == "📊 ประวัติการประเมิน":
    st.markdown('<div class="main-header"><h1>📊 ประวัติการประเมิน</h1></div>', unsafe_allow_html=True)
    
    df = load_data()
    if df.empty:
        st.info("📭 ยังไม่มีข้อมูลการประเมิน กรุณาไปที่หน้า 'ประเมินอาการ'")
    else:
        st.success(f"✅ พบข้อมูลการประเมิน **{len(df)} รายการ**")
        st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True)
        
        # ปุ่มดาวน์โหลด (สำคัญมากสำหรับ Streamlit Cloud)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์ CSV (สำรองข้อมูล)",
            data=csv,
            file_name=f'assessment_data_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )
        
        if st.button("🗑️ ล้างข้อมูลทั้งหมด", type="secondary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
                st.success("ลบข้อมูลเรียบร้อยแล้ว!")
                st.rerun()

# ==================== หน้าที่ 4: สถิติและกราฟ ====================
elif menu == "📈 สถิติและกราฟ":
    st.markdown('<div class="main-header"><h1>📊 สถิติและกราฟ (Data Visualization)</h1></div>', unsafe_allow_html=True)

    df = load_data()
    
    # ถ้าไม่มีข้อมูลจริง ให้สร้าง Dummy Data ที่สมจริงตาม Logic ระบบ
    if df.empty:
        st.info("💡 สร้างข้อมูลจำลองเพื่อแสดงตัวอย่างกราฟ (กรุณาประเมินอาการจริงเพื่อดูข้อมูลของคุณ)")
        dummy_data = [
            {"date": "22/08/2026 10:00", "name": "สมชาย ใจดี", "age": 70, "gender": "ชาย", "chronic": "ความดันโลหิตสูง", "score": 15, "risk": "ต่ำ", "symptoms": "ปวดเมื่อยตามตัว"},
            {"date": "22/08/2026 11:30", "name": "สมหญิง รักเรียน", "age": 75, "gender": "หญิง", "chronic": "เบาหวาน, ความดันโลหิตสูง", "score": 45, "risk": "กลาง", "symptoms": "เวียนศีรษะรุนแรง, ระดับน้ำตาลผิดปกติ"},
            {"date": "22/08/2026 13:00", "name": "วิชัย ชาญชัย", "age": 80, "gender": "ชาย", "chronic": "โรคหัวใจ", "score": 65, "risk": "สูง", "symptoms": "เจ็บหน้าอก/แน่นหน้าอก, หายใจไม่ออก/หายใจลำบาก"},
            {"date": "22/08/2026 14:15", "name": "มาลี มีสุข", "age": 68, "gender": "หญิง", "chronic": "ไม่มี", "score": 10, "risk": "ต่ำ", "symptoms": "ไอ/เจ็บคอ"},
            {"date": "22/08/2026 15:30", "name": "ประเสริฐ สุขใจ", "age": 82, "gender": "ชาย", "chronic": "โรคหลอดเลือดสมอง", "score": 55, "risk": "สูง", "symptoms": "พูดไม่ชัด/ปากเบี้ยว"}
        ]
        df = pd.DataFrame(dummy_data)

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("จำนวนการประเมิน", len(df))
    with col2: st.metric("ความเสี่ยงสูง", len(df[df['risk'] == 'สูง']))
    with col3: st.metric("คะแนนเฉลี่ย", f"{df['score'].mean():.1f}")

    st.markdown("---")
    
    st.subheader("📊 สัดส่วนระดับความเสี่ยง")
    risk_counts = df['risk'].value_counts().reset_index()
    risk_counts.columns = ['ระดับความเสี่ยง', 'จำนวน']
    fig_pie = px.pie(risk_counts, values='จำนวน', names='ระดับความเสี่ยง', 
                    color='ระดับความเสี่ยง', color_discrete_map={'ต่ำ': '#4CAF50', 'กลาง': '#FFA500', 'สูง': '#FF4B4B'}, hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 คะแนนความเสี่ยงตามชื่อ")
    fig_bar = px.bar(df, x='name', y='score', color='risk',
                    color_discrete_map={'ต่ำ': '#4CAF50', 'กลาง': '#FFA500', 'สูง': '#FF4B4B'},
                    text='score', hover_data=['age', 'chronic'])
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("📈 ความสัมพันธ์ อายุ vs คะแนน")
    fig_scatter = px.scatter(df, x='age', y='score', color='risk',
                            color_discrete_map={'ต่ำ': '#4CAF50', 'กลาง': '#FFA500', 'สูง': '#FF4B4B'},
                            hover_data=['name', 'symptoms'], size='score')
    st.plotly_chart(fig_scatter, use_container_width=True)

# ==================== หน้าที่ 5: AI ทำนายผล ====================
elif menu == "🤖 AI ทำนายผล":
    st.markdown('<div class="main-header"><h1>🤖 ระบบ Machine Learning (Scikit-Learn)</h1></div>', unsafe_allow_html=True)
    st.subheader("🧠 โมเดล Random Forest Classifier")
    st.info("💡 **หมายเหตุทางวิชาการ:** โมเดลนี้ถูกฝึกด้วย Synthetic Dataset (ข้อมูลจำลอง 500 รายการ) ที่สร้างขึ้นจาก Logic การให้คะแนนทางการแพทย์ของระบบนี้โดยตรง เพื่อให้การทำนายของ AI สอดคล้องกับเกณฑ์การประเมินจริง")

    # สร้างข้อมูลจำลอง 500 รายการที่สอดคล้องกับ Logic ของเรา (Academic Sound)
    np.random.seed(42)
    ages_sim = np.random.randint(60, 100, 500)
    scores_sim = np.random.randint(5, 80, 500) + (ages_sim - 60) * 0.5 
    X_sim = np.column_stack((ages_sim, scores_sim))

    y_sim = []
    for age, score in X_sim:
        multiplier = 1.0 + (0.3 if age >= 75 else (0.2 if age >= 70 else 0.1))
        # สมมติว่ามีโรคหัวใจ 30% ของข้อมูลเพื่อเพิ่มความสมจริง
        has_heart_disease = np.random.choice([True, False], p=[0.3, 0.7])
        if has_heart_disease: multiplier += 0.3
        
        final_score = int(score * multiplier)
        if final_score >= 50:
            y_sim.append(2) # สูง
        elif final_score >= 20:
            y_sim.append(1) # กลาง
        else:
            y_sim.append(0) # ต่ำ
    y_sim = np.array(y_sim)

    # ฝึกโมเดล
    X_train, X_test, y_train, y_test = train_test_split(X_sim, y_sim, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    accuracy = accuracy_score(y_test, model.predict(X_test))
    st.success(f"✅ ฝึกโมเดลเสร็จสิ้น! (Accuracy บน Test Set: {accuracy*100:.1f}%)")

    st.markdown("---")
    st.subheader("🔮 ทดสอบทำนายผล")
    col1, col2 = st.columns(2)
    with col1: age_input = st.number_input("ใส่อายุ (ปี)", 60, 100, 70)
    with col2: score_input = st.number_input("ใส่คะแนนอาการดิบ", 0, 100, 20)

    if st.button("🤖 ให้ AI ทำนายผล", type="primary"):
        # คำนวณคะแนนขั้นสุดท้ายก่อนส่งเข้าโมเดล (เพื่อให้สอดคล้องกับระบบ)
        multiplier = 1.0 + (0.3 if age_input >= 75 else (0.2 if age_input >= 70 else 0.1))
        final_score_input = int(score_input * multiplier)
        
        prediction = model.predict([[age_input, final_score_input]])
        proba = model.predict_proba([[age_input, final_score_input]])[0]
        
        result_map = {0: "✅ ความเสี่ยงต่ำ", 1: "⚠️ ความเสี่ยงกลาง", 2: "🚨 ความเสี่ยงสูง"}
        color_map = {0: "#4CAF50", 1: "#FFA500", 2: "#FF4B4B"}

        st.markdown(f'<div style="background-color: {color_map[prediction[0]]}; color: white; padding: 20px; border-radius: 10px; text-align: center;"><h2>AI ทำนายผล: {result_map[prediction[0]]}</h2><p>คะแนนหลังปรับตัวคูณ: {final_score_input}</p></div>', unsafe_allow_html=True)
        
        fig_proba = go.Figure(data=[
            go.Bar(x=['ต่ำ', 'กลาง', 'สูง'], y=proba * 100, marker_color=['#4CAF50', '#FFA500', '#FF4B4B'], text=[f"{p*100:.1f}%" for p in proba], textposition='auto')
        ])
        fig_proba.update_layout(title="ความน่าจะเป็นของแต่ละระดับความเสี่ยง (%)", xaxis_title="ระดับ", yaxis_title="ความน่าจะเป็น")
        st.plotly_chart(fig_proba, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 ความสำคัญของฟีเจอร์ (Feature Importance)")
    st.info("กราฟนี้แสดงว่าปัจจัยใดมีผลต่อการตัดสินใจของ AI มากที่สุด")
    feature_names = ['อายุ', 'คะแนนอาการ']
    importances = model.feature_importances_
    fig_imp = go.Figure(data=[go.Bar(x=feature_names, y=importances, marker_color=['#2E86AB', '#A23B72'], text=[f"{i*100:.1f}%" for i in importances], textposition='auto')])
    fig_imp.update_layout(title="Feature Importance", xaxis_title="ฟีเจอร์", yaxis_title="Importance Score")
    st.plotly_chart(fig_imp, use_container_width=True)

# ==================== หน้าที่ 6: เกี่ยวกับระบบ ====================
elif menu == "ℹ️ เกี่ยวกับระบบ":
    st.markdown('<div class="main-header"><h1>ℹ️ เกี่ยวกับระบบ</h1></div>', unsafe_allow_html=True)
    st.markdown("""
    ### 🎓 โปรเจกต์ปี 4 (Senior Project)
    **ระบบประเมินการตัดสินใจไปพบแพทย์ของผู้สูงอายุ**
    
    ### 🛠️ เทคโนโลยีที่ใช้
    - **Frontend:** Streamlit (Python)
    - **Data Processing:** Pandas, NumPy
    - **Data Visualization:** Plotly (รองรับภาษาไทย)
    - **Machine Learning:** Scikit-Learn (Random Forest Classifier)
    - **Integration:** Line Notify API
    
    ### 🎯 วัตถุประสงค์
    1. ช่วยผู้สูงอายุและผู้ดูแลตัดสินใจว่าควรไปพบแพทย์หรือไม่
    2. นำเทคโนโลยี Machine Learning มาช่วยทำนายความเสี่ยง
    3. ออกแบบ UI/UX ที่เหมาะสมกับผู้สูงอายุ (Accessibility)
    
    ### ⚠️ ข้อจำกัด
    ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น **ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้**
    """)

# ==================== Footer ====================
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; padding: 20px;'><p>🏥 ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ | โปรเจกต์ปี 4 | พัฒนาด้วย Streamlit</p></div>", unsafe_allow_html=True)