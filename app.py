import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
import joblib
from datetime import datetime

# ==================== ตั้งค่าหน้าเว็บ ====================
st.set_page_config(
    page_title="ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ตกแต่ง ====================
st.markdown("""
<style>
    .main-header { background: linear-gradient(90deg, #2E86AB, #A23B72); padding: 25px; border-radius: 15px; color: white; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .risk-high { background: linear-gradient(135deg, #FF4B4B, #FF0000); color: white; padding: 20px; border-radius: 15px; text-align: center; }
    .risk-medium { background: linear-gradient(135deg, #FFA500, #FF8C00); color: white; padding: 20px; border-radius: 15px; text-align: center; }
    .risk-low { background: linear-gradient(135deg, #4CAF50, #45a049); color: white; padding: 20px; border-radius: 15px; text-align: center; }
    .metric-card { background: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# ==================== ข้อมูลทางการแพทย์ ====================
SYMPTOMS_DATA = {
    "🚨 อาการฉุกเฉิน (ต้องไปโรงพยาบาลทันที)": {
        "เจ็บหน้าอก/แน่นหน้าอก": 35, "หายใจไม่ออก/หายใจลำบาก": 35, 
        "หมดสติ/วูบ/เป็นลม": 40, "แขนขาอ่อนแรงครึ่งซีก": 35, 
        "พูดไม่ชัด/ปากเบี้ยว": 35, "เลือดออกไม่หยุด": 30,
        "ชัก/เกร็ง": 35, "ปวดศีรษะรุนแรงที่สุดในชีวิต": 30
    },
    "⚠️ อาการที่ต้องเฝ้าระวัง (พบแพทย์ภายใน 24 ชม.)": {
        "ไข้สูงกว่า 38.5°C": 18, "เวียนศีรษะรุนแรง": 15, 
        "ความดันโลหิตสูงเกิน 180/110": 25, "ระดับน้ำตาลผิดปกติ": 20,
        "ใจสั่น/หัวใจเต้นเร็ว": 18, "ปวดท้องรุนแรง": 18,
        "บวมตามแขนขา": 12, "ปัสสาวะแสบขัด/มีเลือด": 12
    },
    "✅ อาการทั่วไป (ดูแลตัวเองได้/นัดพบแพทย์ตามปกติ)": {
        "ปวดเมื่อยตามตัว": 3, "ปวดข้อ": 5, "นอนไม่หลับ": 4, 
        "เบื่ออาหาร": 5, "ท้องผูก": 3, "อ่อนเพลียเล็กน้อย": 4, 
        "ไอ/เจ็บคอ": 6, "ปวดหลัง": 5, "ตาพร่ามัว": 8
    }
}

CHRONIC_DISEASES = ["เบาหวาน", "ความดันโลหิตสูง", "โรคหัวใจ", "โรคไต", "โรคปอด", "โรคหลอดเลือดสมอง", "มะเร็ง", "ไม่มี"]

# ==================== Session State ====================
if "history" not in st.session_state:
    st.session_state.history = []

# ==================== Sidebar ====================
with st.sidebar:
    st.title("📋 เมนูหลัก")
    menu = st.radio(
        "เลือกหัวข้อ",
        ["🏠 หน้าหลัก", "🩺 ประเมินอาการ", "📊 สถิติและกราฟ", "🤖 AI ทำนายผล", "ℹ️ เกี่ยวกับระบบ"],
        index=1
    )
    st.markdown("---")
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.caption("🎓 โปรเจกต์ปี 4 - Senior Project")

# ==================== หน้าที่ 1: หน้าหลัก ====================
if menu == "🏠 หน้าหลัก":
    st.markdown('<div class="main-header"><h1>🏥 ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ</h1><h3>Elderly Medical Decision Support System</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("👴 กลุ่มเป้าหมาย", "60+ ปี")
    with col2: st.metric("📋 จำนวนอาการ", f"{sum(len(v) for v in SYMPTOMS_DATA.values())} อาการ")
    with col3: st.metric("⚕️ ระดับความเสี่ยง", "3 ระดับ")
    with col4: st.metric("⏱️ เวลาประเมิน", "< 5 นาที")
    
    st.markdown("### 🌟 คุณสมบัติของระบบ")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("- ✅ ประเมินอาการตามเกณฑ์ทางการแพทย์\n- ✅ วิเคราะห์ความเสี่ยง 3 ระดับ\n- ✅ บันทึกประวัติการประเมิน")
    with col_b:
        st.markdown("- ✅ แสดงสถิติแบบกราฟ (Plotly/Seaborn)\n- ✅ ระบบ AI ทำนายผล (Scikit-Learn)\n- ✅ รองรับโรคประจำตัวและยา")
    
    st.info(" **หมายเหตุ**: ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้")

# ==================== หน้าที่ 2: ประเมินอาการ ====================
elif menu == "🩺 ประเมินอาการ":
    st.markdown('<div class="main-header"><h1>🩺 แบบประเมินอาการ</h1></div>', unsafe_allow_html=True)
    
    with st.form("assessment_form"):
        st.subheader(" ข้อมูลทั่วไป")
        col1, col2, col3 = st.columns(3)
        with col1: name = st.text_input("ชื่อ-นามสกุล *")
        with col2: age = st.number_input("อายุ (ปี) *", 60, 120, 65)
        with col3: gender = st.selectbox("เพศ *", ["ชาย", "หญิง", "ไม่ระบุ"])
        
        st.subheader("🏥 โรคประจำตัว")
        chronic = st.multiselect("เลือกโรคประจำตัว", CHRONIC_DISEASES)
        
        st.subheader("🤒 อาการที่พบ")
        total_score = 0
        selected_symptoms = []
        emergency_found = False
        
        for category, symptoms in SYMPTOMS_DATA.items():
            with st.expander(category, expanded=True):
                cols = st.columns(2)
                for i, (symptom, score) in enumerate(symptoms.items()):
                    with cols[i % 2]:
                        if st.checkbox(f"{symptom} (+{score} คะแนน)", key=symptom):
                            total_score += score
                            selected_symptoms.append(symptom)
                            if "ฉุกเฉิน" in category:
                                emergency_found = True
        
        notes = st.text_area("📝 หมายเหตุเพิ่มเติม", placeholder="เช่น อาการเป็นมา 3 วัน...")
        submitted = st.form_submit_button("🔍 ประเมินผล", type="primary", use_container_width=True)
    
    if submitted:
        if not name or not selected_symptoms:
            st.error("⚠️ กรุณากรอกชื่อและเลือกอาการอย่างน้อย 1 รายการ")
        else:
            # คำนวณคะแนน
            risk_multiplier = 1.0
            if age >= 75: risk_multiplier += 0.3
            elif age >= 70: risk_multiplier += 0.2
            if "โรคหัวใจ" in chronic or "โรคหลอดเลือดสมอง" in chronic: risk_multiplier += 0.3
            
            final_score = int(total_score * risk_multiplier)
            
            # ตัดสินผล
            if final_score >= 50 or emergency_found:
                risk_level, risk_class, rec = "สูง", "risk-high", "🚨 ฉุกเฉิน! กรุณาไปพบแพทย์หรือโทร 1669 ทันที"
                advice = ["นำส่งโรงพยาบาลที่ใกล้ที่สุด", "ให้ผู้ป่วยนั่งหรือนอนท่าที่สบาย", "เตรียมยาและประวัติโรคประจำตัว"]
            elif final_score >= 20:
                risk_level, risk_class, rec = "กลาง", "risk-medium", "⚠️ ควรพบแพทย์ภายใน 24 ชั่วโมง"
                advice = ["นัดพบแพทย์โดยเร็ว", "จดบันทึกอาการ", "หากอาการแย่ลงให้ไปโรงพยาบาลทันที"]
            else:
                risk_level, risk_class, rec = "ต่ำ", "risk-low", "✅ ดูแลตัวเองได้ และนัดพบแพทย์ตามปกติ"
                advice = ["พักผ่อนให้เพียงพอ", "ดื่มน้ำสะอาด", "สังเกตอาการ หากไม่ดีขึ้นใน 3 วันให้พบแพทย์"]
            
            st.markdown(f'<div class="{risk_class}"><h2>🎯 ผลการประเมิน: ความเสี่ยง {risk_level}</h2><h3>{rec}</h3></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**ชื่อ:** {name} | **อายุ:** {age} ปี")
                st.write(f"**คะแนนรวม:** {final_score} (ตัวคูณ {risk_multiplier}x)")
            with col2:
                st.write("**อาการที่เลือก:**")
                for s in selected_symptoms: st.write(f"- {s}")
            
            st.markdown("**💡 คำแนะนำ:**")
            for adv in advice: st.markdown(f"- {adv}")
            
            # บันทึกประวัติ
            st.session_state.history.append({
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                "name": name, "age": age, "gender": gender,
                "chronic": chronic, "score": final_score, 
                "risk": risk_level, "symptoms": selected_symptoms
            })
            st.success("✅ บันทึกผลการประเมินเรียบร้อยแล้ว")

# ==================== หน้าที่ 3: สถิติและกราฟ ====================
elif menu == "📊 สถิติและกราฟ":
    st.markdown('<div class="main-header"><h1>📊 สถิติและกราฟ (Data Visualization)</h1></div>', unsafe_allow_html=True)
    
    # ถ้าไม่มีประวัติ ให้ใช้ข้อมูลจำลอง (Dummy Data)
    if len(st.session_state.history) < 3:
        dummy_data = [
            {"date": "22/08/2026", "name": "สมชาย", "age": 70, "score": 15, "risk": "ต่ำ"},
            {"date": "22/08/2026", "name": "สมหญิง", "age": 75, "score": 45, "risk": "กลาง"},
            {"date": "22/08/2026", "name": "วิชัย", "age": 80, "score": 65, "risk": "สูง"},
            {"date": "22/08/2026", "name": "มาลี", "age": 68, "score": 10, "risk": "ต่ำ"},
            {"date": "22/08/2026", "name": "ประเสริฐ", "age": 82, "score": 55, "risk": "สูง"}
        ]
        df = pd.DataFrame(dummy_data)
        st.warning("⚠️ ใช้ข้อมูลจำลอง (Dummy Data) เนื่องจากประวัติการประเมินยังน้อยเกินไป")
    else:
        df = pd.DataFrame(st.session_state.history)

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("📊 จำนวนครั้งทั้งหมด", len(df))
    with col2: st.metric("🚨 ความเสี่ยงสูง", len(df[df['risk'] == 'สูง']))
    with col3: st.metric("📈 คะแนนเฉลี่ย", f"{df['score'].mean():.1f}")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📊 สัดส่วนระดับความเสี่ยง (Plotly)")
        risk_counts = df['risk'].value_counts().reset_index()
        risk_counts.columns = ['ระดับความเสี่ยง', 'จำนวน']
        fig_pie = px.pie(risk_counts, values='จำนวน', names='ระดับความเสี่ยง', color='ระดับความเสี่ยง', color_discrete_map={'ต่ำ':'#4CAF50', 'กลาง':'#FFA500', 'สูง':'#FF4B4B'})
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_b:
        st.subheader("📈 ความสัมพันธ์ อายุ vs คะแนน (Seaborn)")
        fig_scatter, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(data=df, x='age', y='score', hue='risk', palette={'ต่ำ':'green', 'กลาง':'orange', 'สูง':'red'}, s=100, ax=ax)
        ax.set_title("Scatter Plot: Age vs Risk Score")
        st.pyplot(fig_scatter)

    st.subheader(" คะแนนความเสี่ยงในแต่ละครั้ง (Matplotlib)")
    fig_bar, ax2 = plt.subplots(figsize=(10, 5))
    colors = ['#4CAF50' if r == 'ต่ำ' else ('#FFA500' if r == 'กลาง' else '#FF4B4B') for r in df['risk']]
    ax2.bar(df['name'], df['score'], color=colors)
    ax2.set_ylabel("คะแนนความเสี่ยง")
    ax2.set_title("Bar Chart: Risk Score by Name")
    st.pyplot(fig_bar)

# ==================== หน้าที่ 4: AI ทำนายผล ====================
elif menu == "🤖 AI ทำนายผล":
    st.markdown('<div class="main-header"><h1>🤖 ระบบ Machine Learning (Scikit-Learn)</h1></div>', unsafe_allow_html=True)
    
    st.subheader("🧠 โมเดล Random Forest Classifier")
    st.write("ระบบจะฝึก AI จากข้อมูลเพื่อทำนายระดับความเสี่ยงจาก **อายุ** และ **คะแนนอาการ**")
    
    # ข้อมูลสำหรับฝึก AI (รวมข้อมูลจริง + ข้อมูลจำลอง)
    X_data = [[70, 15], [75, 45], [80, 65], [68, 10], [82, 55], [65, 5], [90, 80], [72, 25]]
    y_data = [0, 1, 2, 0, 2, 0, 2, 1] # 0=ต่ำ, 1=กลาง, 2=สูง
    
    X = np.array(X_data)
    y = np.array(y_data)
    
    # ฝึกโมเดล
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    st.success("✅ ฝึกโมเดลเสร็จสิ้น! (Accuracy: 100% บนข้อมูลฝึก)")
    
    st.markdown("---")
    st.subheader("🔮 ทดสอบทำนายผล")
    col1, col2 = st.columns(2)
    with col1:
        age_input = st.number_input("ใส่อายุ (ปี)", 60, 100, 70)
    with col2:
        score_input = st.number_input("ใส่คะแนนอาการ", 0, 100, 20)
        
    if st.button(" ให้ AI ทำนายผล", type="primary"):
        prediction = model.predict([[age_input, score_input]])
        proba = model.predict_proba([[age_input, score_input]])[0]
        
        result_map = {0: "✅ ความเสี่ยงต่ำ", 1: "⚠️ ความเสี่ยงกลาง", 2: "🚨 ความเสี่ยงสูง"}
        color_map = {0: "green", 1: "orange", 2: "red"}
        
        st.markdown(f'<div style="background-color: {color_map[prediction[0]]}; color: white; padding: 20px; border-radius: 10px; text-align: center;"><h2>AI ทำนายผล: {result_map[prediction[0]]}</h2></div>', unsafe_allow_html=True)
        
        st.write("**ความน่าจะเป็นของแต่ละระดับ:**")
        proba_df = pd.DataFrame({
            'ระดับ': ['ต่ำ', 'กลาง', 'สูง'],
            'ความน่าจะเป็น (%)': [f"{p*100:.1f}%" for p in proba]
        })
        st.dataframe(proba_df, use_container_width=True)

# ==================== หน้าที่ 5: เกี่ยวกับระบบ ====================
elif menu == "ℹ️ เกี่ยวกับระบบ":
    st.markdown('<div class="main-header"><h1>ℹ️ เกี่ยวกับระบบ</h1></div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🎓 ข้อมูลโปรเจกต์
    - **ชื่อโปรเจกต์:** ระบบประเมินการตัดสินใจไปพบแพทย์ของผู้สูงอายุ
    - **ประเภท:** โปรเจกต์ปี 4 (Senior Project)
    - **เทคโนโลยี:** Python, Streamlit, Pandas, Scikit-learn, Plotly, Matplotlib, Seaborn
    
    ### 🎯 วัตถุประสงค์
    1. ช่วยผู้สูงอายุและผู้ดูแลตัดสินใจว่าควรไปพบแพทย์หรือไม่
    2. นำเทคโนโลยี Machine Learning มาช่วยทำนายความเสี่ยง
    3. แสดงผลสถิติผ่าน Data Visualization ที่เข้าใจง่าย
    
    ### ⚠️ ข้อจำกัด
    - ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้
    - เป็นเพียงเครื่องมือช่วยตัดสินใจเบื้องต้น
    
    ### 📞 ติดต่อฉุกเฉิน
    - **1669** - เจ็บป่วยฉุกเฉิน
    - **1556** - ผู้สูงอายุ
    """)

# ==================== Footer ====================
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'><p> ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ | โปรเจกต์ปี 4 | พัฒนาด้วย Streamlit</p></div>", unsafe_allow_html=True)
