import streamlit as st
import json
import datetime

# ==================== Config ====================
st.set_page_config(
    page_title="ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== Custom CSS ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .risk-high { background-color: #FF4B4B; color: white; padding: 15px; border-radius: 10px; }
    .risk-medium { background-color: #FFA500; color: white; padding: 15px; border-radius: 10px; }
    .risk-low { background-color: #4CAF50; color: white; padding: 15px; border-radius: 10px; }
    .info-box { background-color: #E8F4FD; padding: 15px; border-radius: 10px; border-left: 5px solid #2E86AB; }
</style>
""", unsafe_allow_html=True)

# ==================== Data ====================
SYMPTOMS_DATA = {
    "อาการฉุกเฉิน (คะแนนสูง)": {
        "เจ็บหน้าอก": 30,
        "หายใจไม่ออก/หายใจลำบาก": 30,
        "หมดสติหรือวูบ": 35,
        "แขนขาอ่อนแรงครึ่งซีก": 30,
        "พูดไม่ชัด/ปากเบี้ยว": 30,
        "เลือดออกไม่หยุด": 25,
    },
    "อาการที่ต้องเฝ้าระวัง (คะแนนกลาง)": {
        "ไข้สูงกว่า 38.5°C": 15,
        "เวียนศีรษะรุนแรง": 12,
        "คลื่นไส้/อาเจียนต่อเนื่อง": 12,
        "ปวดศีรษะรุนแรง": 12,
        "ความดันโลหิตสูงเกิน 180/110": 20,
        "ระดับน้ำตาลต่ำกว่า 70 หรือสูงกว่า 300": 18,
        "บวมตามแขนขา": 10,
    },
    "อาการทั่วไป (คะแนนต่ำ)": {
        "ปวดเมื่อยตามตัว": 3,
        "ปวดข้อ": 5,
        "นอนไม่หลับ": 3,
        "เบื่ออาหาร": 4,
        "ท้องผูก": 3,
        "อ่อนเพลียเล็กน้อย": 3,
    }
}

CHRONIC_DISEASES = ["เบาหวาน", "ความดันโลหิตสูง", "โรคหัวใจ", "โรคไต", "โรคปอด", "โรคหลอดเลือดสมอง", "มะเร็ง", "ไม่มี"]

# ==================== Sidebar ====================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3043/3043898.png", width=100)
    st.title("📋 เมนูหลัก")
    menu = st.radio(
        "เลือกหัวข้อ",
        ["🏠 หน้าหลัก", "🩺 ประเมินอาการ", "📊 ประวัติการประเมิน", "ℹ️ เกี่ยวกับระบบ"],
        index=1
    )
    st.markdown("---")
    st.caption(f"📅 {datetime.date.today().strftime('%d/%m/%Y')}")
    st.caption("🎓 โปรเจกต์ปี 4")

# ==================== Session State ====================
if "history" not in st.session_state:
    st.session_state.history = []

# ==================== Pages ====================
if menu == "🏠 หน้าหลัก":
    st.markdown('<div class="main-header"><h1>🩺 ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ</h1><h3>Elderly Medical Decision Support System</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👴 กลุ่มเป้าหมาย", "ผู้สูงอายุ 60+ ปี")
    with col2:
        st.metric("📋 จำนวนอาการ", f"{sum(len(v) for v in SYMPTOMS_DATA.values())} อาการ")
    with col3:
        st.metric("🎯 ความแม่นยำ", "ตามเกณฑ์แพทย์")
    
    st.markdown("### 🌟 คุณสมบัติของระบบ")
    st.markdown("""
    - ✅ **ประเมินอาการ** จากแบบสอบถามที่ออกแบบตามเกณฑ์ทางการแพทย์
    - ✅ **วิเคราะห์ความเสี่ยง** 3 ระดับ (สูง/กลาง/ต่ำ)
    - ✅ **แนะนำการปฏิบัติตัว** ที่เหมาะสมกับแต่ละระดับ
    - ✅ **บันทึกประวัติ** การประเมินย้อนหลัง
    - ✅ **รองรับโรคประจำตัว** และปัจจัยเสี่ยงเพิ่มเติม
    """)
    
    st.info("💡 **หมายเหตุ**: ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้")

elif menu == "🩺 ประเมินอาการ":
    st.markdown('<div class="main-header"><h1>🩺 แบบประเมินอาการ</h1></div>', unsafe_allow_html=True)
    
    with st.form("assessment_form"):
        st.subheader("👤 ข้อมูลทั่วไป")
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("ชื่อ-นามสกุล")
        with col2:
            age = st.number_input("อายุ (ปี)", min_value=60, max_value=120, value=65)
        with col3:
            gender = st.selectbox("เพศ", ["ชาย", "หญิง", "ไม่ระบุ"])
        
        st.subheader("🏥 โรคประจำตัว")
        chronic = st.multiselect("เลือกโรคประจำตัว (เลือกได้มากกว่า 1)", CHRONIC_DISEASES)
        
        col1, col2 = st.columns(2)
        with col1:
            bp = st.text_input("ความดันโลหิตล่าสุด (เช่น 120/80)", placeholder="120/80")
        with col2:
            bs = st.number_input("ระดับน้ำตาลในเลือด (mg/dL)", min_value=0, max_value=600, value=100)
        
        st.subheader("🤒 อาการที่พบ (เลือกทั้งหมดที่เป็น)")
        total_score = 0
        selected_symptoms = []
        
        for category, symptoms in SYMPTOMS_DATA.items():
            st.markdown(f"**{category}**")
            cols = st.columns(2)
            for i, (symptom, score) in enumerate(symptoms.items()):
                with cols[i % 2]:
                    if st.checkbox(f"{symptom} (+{score} คะแนน)", key=symptom):
                        total_score += score
                        selected_symptoms.append((symptom, score))
        
        st.subheader("📝 หมายเหตุเพิ่มเติม")
        notes = st.text_area("อธิบายอาการเพิ่มเติม (ถ้ามี)")
        
        submitted = st.form_submit_button("🔍 ประเมินผล", type="primary", use_container_width=True)
    
    if submitted:
        if not name:
            st.error("⚠️ กรุณากรอกชื่อ-นามสกุล")
        elif not selected_symptoms:
            st.warning("⚠️ กรุณาเลือกอาการอย่างน้อย 1 รายการ")
        else:
            # ===== Risk Calculation =====
            # ปรับคะแนนตามโรคประจำตัว
            risk_multiplier = 1.0
            if "โรคหัวใจ" in chronic or "โรคหลอดเลือดสมอง" in chronic:
                risk_multiplier += 0.3
            if "เบาหวาน" in chronic and bs > 250:
                risk_multiplier += 0.2
            if age >= 75:
                risk_multiplier += 0.2
            
            final_score = int(total_score * risk_multiplier)
            
            # ===== Determine Risk Level =====
            if final_score >= 50 or any(s[0] in ["เจ็บหน้าอก", "หายใจไม่ออก/หายใจลำบาก", "หมดสติหรือวูบ", "แขนขาอ่อนแรงครึ่งซีก", "พูดไม่ชัด/ปากเบี้ยว"] for s in selected_symptoms):
                risk_level = "สูง"
                risk_class = "risk-high"
                recommendation = "🚨 **ฉุกเฉิน!** กรุณาไปพบแพทย์หรือโทร 1669 ทันที"
                advice = [
                    "อย่ารอช้า นำส่งโรงพยาบาลที่ใกล้ที่สุด",
                    "ให้ผู้ป่วยนั่งหรือนอนในท่าที่สบาย",
                    "หากหมดสติ ให้จัดท่า recovery position",
                    "เตรียมรายการยาและประวัติโรคประจำตัว",
                    "โทรแจ้งญาติหรือผู้ดูแลทันที"
                ]
            elif final_score >= 20:
                risk_level = "กลาง"
                risk_class = "risk-medium"
                recommendation = "⚠️ **ควรพบแพทย์ภายใน 24 ชั่วโมง**"
                advice = [
                    "นัดพบแพทย์โดยเร็ว (ภายใน 1 วัน)",
                    "จดบันทึกอาการและเวลาที่เกิด",
                    "งดอาหารหนักก่อนพบแพทย์",
                    "ดื่มน้ำเพียงพอ พักผ่อนให้มาก",
                    "หากอาการแย่ลง ให้ไปโรงพยาบาลทันที"
                ]
            else:
                risk_level = "ต่ำ"
                risk_class = "risk-low"
                recommendation = "✅ **ดูแลตัวเองได้ และนัดพบแพทย์ตามปกติ**"
                advice = [
                    "พักผ่อนให้เพียงพอ",
                    "ดื่มน้ำสะอาด 8-10 แก้วต่อวัน",
                    "ทานอาหารที่มีประโยชน์ ครบ 5 หมู่",
                    "สังเกตอาการ หากไม่ดีขึ้นใน 3 วัน ให้พบแพทย์",
                    "ออกกำลังกายเบาๆ เช่น เดิน ยืดเหยียด"
                ]
            
            # ===== Display Results =====
            st.markdown("---")
            st.markdown(f'<div class="{risk_class}"><h2>🎯 ผลการประเมิน: ระดับความเสี่ยง <u>{risk_level}</u></h2><h3>{recommendation}</h3></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📊 ข้อมูลการประเมิน")
                st.write(f"**ชื่อ:** {name}")
                st.write(f"**อายุ:** {age} ปี")
                st.write(f"**เพศ:** {gender}")
                st.write(f"**โรคประจำตัว:** {', '.join(chronic) if chronic else 'ไม่มี'}")
                st.write(f"**คะแนนความเสี่ยง:** {final_score} คะแนน")
            
            with col2:
                st.markdown("### 📈 คะแนนรวม")
                st.progress(min(final_score / 100, 1.0))
                st.write(f"คะแนนดิบ: {total_score} × ตัวคูณ {risk_multiplier} = **{final_score}**")
            
            st.markdown("### 💡 คำแนะนำในการปฏิบัติตัว")
            for adv in advice:
                st.markdown(f"- {adv}")
            
            if selected_symptoms:
                st.markdown("### 📋 อาการที่เลือก")
                for symptom, score in selected_symptoms:
                    st.markdown(f"- {symptom} (+{score} คะแนน)")
            
            # Save to history
            st.session_state.history.append({
                "date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                "name": name,
                "age": age,
                "score": final_score,
                "risk": risk_level,
                "symptoms": [s[0] for s in selected_symptoms]
            })
            
            st.success("✅ บันทึกผลการประเมินเรียบร้อยแล้ว")

elif menu == "📊 ประวัติการประเมิน":
    st.markdown('<div class="main-header"><h1>📊 ประวัติการประเมิน</h1></div>', unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info("📭 ยังไม่มีประวัติการประเมิน")
    else:
        for i, record in enumerate(reversed(st.session_state.history), 1):
            with st.expander(f"#{i} - {record['name']} ({record['date']}) - ความเสี่ยง: {record['risk']}"):
                st.write(f"**อายุ:** {record['age']} ปี")
                st.write(f"**คะแนน:** {record['score']}")
                st.write(f"**อาการ:** {', '.join(record['symptoms'])}")
        
        if st.button("🗑️ ล้างประวัติทั้งหมด"):
            st.session_state.history = []
            st.rerun()

elif menu == "ℹ️ เกี่ยวกับระบบ":
    st.markdown('<div class="main-header"><h1>ℹ️ เกี่ยวกับระบบ</h1></div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🎓 ข้อมูลโปรเจกต์
    - **ชื่อโปรเจกต์:** ระบบประเมินการตัดสินใจไปพบแพทย์ของผู้สูงอายุ
    - **ประเภท:** โปรเจกต์ปี 4 (Senior Project)
    - **เทคโนโลยี:** Python, Streamlit
    - **กลุ่มเป้าหมาย:** ผู้สูงอายุ 60 ปีขึ้นไป และผู้ดูแล
    
    ### 🎯 วัตถุประสงค์
    1. ช่วยผู้สูงอายุและผู้ดูแลตัดสินใจว่าควรไปพบแพทย์หรือไม่
    2. ลดความกังวลจากการประเมินอาการผิดพลาด
    3. ป้องกันการไปพบแพทย์โดยไม่จำเป็น และป้องกันกรณีฉุกเฉินที่ถูกละเลย
    
    ### 🔬 เกณฑ์การประเมิน
    ระบบใช้เกณฑ์คะแนนถ่วงน้ำหนัก (Weighted Scoring) โดยแบ่งอาการเป็น 3 ระดับ:
    - **อาการฉุกเฉิน** (25-35 คะแนน)
    - **อาการที่ต้องเฝ้าระวัง** (10-20 คะแนน)
    - **อาการทั่วไป** (3-5 คะแนน)
    
    พร้อมปรับคะแนนตาม **โรคประจำตัว** และ **อายุ**
    
    ### 👨‍💻 ผู้พัฒนา
    พัฒนาเป็นโปรเจกต์ปี 4 เพื่อการศึกษา
    
    ### ⚠️ ข้อจำกัด
    - ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้
    - เป็นเพียงเครื่องมือช่วยตัดสินใจเบื้องต้น
    - ควรปรึกษาแพทย์หรือบุคลากรทางการแพทย์เสมอ
    """)