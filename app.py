@"
import streamlit as st
import json
import datetime
import pandas as pd
from datetime import datetime

# ==================== Config ====================
st.set_page_config(
    page_title=""ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ"",
    page_icon=""🏥"",
    layout=""wide"",
    initial_sidebar_state=""expanded""
)

# ==================== Custom CSS ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .risk-high { 
        background: linear-gradient(135deg, #FF4B4B, #FF0000); 
        color: white; 
        padding: 25px; 
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        animation: pulse 2s;
    }
    .risk-medium { 
        background: linear-gradient(135deg, #FFA500, #FF8C00); 
        color: white; 
        padding: 25px; 
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .risk-low { 
        background: linear-gradient(135deg, #4CAF50, #45a049); 
        color: white; 
        padding: 25px; 
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .info-box { 
        background-color: #E8F4FD; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #2E86AB;
        margin: 10px 0;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# ==================== ข้อมูลทางการแพทย์ ====================
SYMPTOMS_DATA = {
    ""อาการฉุกเฉิน (ต้องไปโรงพยาบาลทันที)"": {
        ""เจ็บหน้าอก/แน่นหน้าอก"": {""score"": 35, ""urgency"": ""ฉุกเฉิน""},
        ""หายใจไม่ออก/หายใจลำบาก"": {""score"": 35, ""urgency"": ""ฉุกเฉิน""},
        ""หมดสติ/วูบ/เป็นลม"": {""score"": 40, ""urgency"": ""ฉุกเฉิน""},
        ""แขนขาอ่อนแรงครึ่งซีก"": {""score"": 35, ""urgency"": ""ฉุกเฉิน""},
        ""พูดไม่ชัด/ปากเบี้ยว/หน้าเบี้ยว"": {""score"": 35, ""urgency"": ""ฉุกเฉิน""},
        ""เลือดออกไม่หยุด"": {""score"": 30, ""urgency"": ""ฉุกเฉิน""},
        ""ชัก/เกร็ง"": {""score"": 35, ""urgency"": ""ฉุกเฉิน""},
        ""ปวดศีรษะรุนแรงที่สุดในชีวิต"": {""score"": 30, ""urgency"": ""ฉุกเฉิน""},
        ""อาเจียนเป็นเลือด"": {""score"": 35, ""urgency"": ""ฉุกเฉิน""},
        ""ถ่ายอุจจาระเป็นเลือด"": {""score"": 30, ""urgency"": ""ฉุกเฉิน""},
    },
    ""อาการที่ต้องเฝ้าระวัง (พบแพทย์ภายใน 24 ชม.)"": {
        ""ไข้สูงกว่า 38.5°C"": {""score"": 18, ""urgency"": ""เฝ้าระวัง""},
        ""เวียนศีรษะรุนแรง"": {""score"": 15, ""urgency"": ""เฝ้าระวัง""},
        ""คลื่นไส้/อาเจียนต่อเนื่อง"": {""score"": 15, ""urgency"": ""เฝ้าระวัง""},
        ""ปวดศีรษะรุนแรง"": {""score"": 15, ""urgency"": ""เฝ้าระวัง""},
        ""ความดันโลหิตสูงเกิน 180/110"": {""score"": 25, ""urgency"": ""เฝ้าระวัง""},
        ""ระดับน้ำตาลต่ำกว่า 70 mg/dL"": {""score"": 20, ""urgency"": ""เฝ้าระวัง""},
        ""ระดับน้ำตาลสูงกว่า 300 mg/dL"": {""score"": 22, ""urgency"": ""เฝ้าระวัง""},
        ""บวมตามแขนขา"": {""score"": 12, ""urgency"": ""เฝ้าระวัง""},
        ""ใจสั่น/หัวใจเต้นเร็ว"": {""score"": 18, ""urgency"": ""เฝ้าระวัง""},
        ""ปวดท้องรุนแรง"": {""score"": 18, ""urgency"": ""เฝ้าระวัง""},
        ""หายใจมีเสียงวี้ด"": {""score"": 20, ""urgency"": ""เฝ้าระวัง""},
        ""ปัสสาวะแสบขัด/มีเลือด"": {""score"": 12, ""urgency"": ""เฝ้าระวัง""},
    },
    ""อาการทั่วไป (ดูแลตัวเองได้/นัดพบแพทย์ตามปกติ)"": {
        ""ปวดเมื่อยตามตัว"": {""score"": 3, ""urgency"": ""ทั่วไป""},
        ""ปวดข้อ"": {""score"": 5, ""urgency"": ""ทั่วไป""},
        ""นอนไม่หลับ"": {""score"": 4, ""urgency"": ""ทั่วไป""},
        ""เบื่ออาหาร"": {""score"": 5, ""urgency"": ""ทั่วไป""},
        ""ท้องผูก"": {""score"": 3, ""urgency"": ""ทั่วไป""},
        ""อ่อนเพลียเล็กน้อย"": {""score"": 4, ""urgency"": ""ทั่วไป""},
        ""ไอ/เจ็บคอ"": {""score"": 6, ""urgency"": ""ทั่วไป""},
        ""น้ำมูกไหล"": {""score"": 3, ""urgency"": ""ทั่วไป""},
        ""ปวดหลัง"": {""score"": 5, ""urgency"": ""ทั่วไป""},
        ""ตาพร่ามัว"": {""score"": 8, ""urgency"": ""ทั่วไป""},
    }
}

CHRONIC_DISEASES = [
    ""เบาหวาน"", ""ความดันโลหิตสูง"", ""โรคหัวใจ"", ""โรคไต"", 
    ""โรคปอด"", ""โรคหลอดเลือดสมอง"", ""มะเร็ง"", ""โรคไทรอยด์"",
    ""โรคเกาต์"", ""โรคกระดูกพรุน"", ""โรคพาร์กินสัน"", ""ไม่มี""
]

MEDICATIONS = [
    ""ยาเบาหวาน"", ""ยาความดัน"", ""ยาหัวใจ"", ""ยาละลายลิ่มเลือด"",
    ""ยาขยายหลอดลม"", ""ยาขับปัสสาวะ"", ""ยาแก้ปวด"", ""อื่นๆ""
]

# ==================== Session State ====================
if ""history"" not in st.session_state:
    st.session_state.history = []

# ==================== Sidebar ====================
with st.sidebar:
    st.image(""https://cdn-icons-png.flaticon.com/512/3043/3043898.png"", width=100)
    st.title(""📋 เมนูหลัก"")
    
    menu = st.radio(
        ""เลือกหัวข้อ"",
        [""🏠 หน้าหลัก"", ""🩺 ประเมินอาการ"", ""📊 ประวัติการประเมิน"", ""📈 สถิติ"", ""️ เกี่ยวกับระบบ""],
        index=1
    )
    
    st.markdown(""---"")
    st.caption(f""📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}"")
    st.caption(""🎓 โปรเจกต์ปี 4 - ระบบประเมินผู้สูงอายุ"")

# ==================== Pages ====================

if menu == ""🏠 หน้าหลัก"":
    st.markdown('<div class=""main-header""><h1>🏥 ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ</h1><h3>Elderly Medical Decision Support System</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(""👴 กลุ่มเป้าหมาย"", ""ผู้สูงอายุ 60+ ปี"")
    with col2:
        st.metric(""📋 จำนวนอาการ"", f""{sum(len(v) for v in SYMPTOMS_DATA.values())} อาการ"")
    with col3:
        st.metric("" ระดับความเสี่ยง"", ""3 ระดับ"")
    with col4:
        st.metric(""️ เวลาประเมิน"", ""< 5 นาที"")
    
    st.markdown(""### 🌟 คุณสมบัติของระบบ"")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        - ✅ **ประเมินอาการ** จากแบบสอบถามที่ออกแบบตามเกณฑ์ทางการแพทย์
        - ✅ **วิเคราะห์ความเสี่ยง** 3 ระดับ (สูง/กลาง/ต่ำ)
        - ✅ **แนะนำการปฏิบัติตัว** ที่เหมาะสมกับแต่ละระดับ
        - ✅ **บันทึกประวัติ** การประเมินย้อนหลัง
        """)
    with col_b:
        st.markdown("""
        - ✅ **รองรับโรคประจำตัว** และปัจจัยเสี่ยงเพิ่มเติม
        - ✅ **คำนวณคะแนน** โดยปรับตามอายุและโรคประจำตัว
        - ✅ **แสดงสถิติ** การประเมินแบบกราฟ
        - ✅ **ใช้งานง่าย** เหมาะกับผู้สูงอายุ
        """)
    
    st.info(""💡 **หมายเหตุ**: ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้"")

elif menu == ""🩺 ประเมินอาการ"":
    st.markdown('<div class=""main-header""><h1>🩺 แบบประเมินอาการ</h1></div>', unsafe_allow_html=True)
    
    with st.form(""assessment_form"", clear_on_submit=False):
        st.subheader(""👤 ข้อมูลทั่วไป"")
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(""ชื่อ-นามสกุล *"", placeholder=""กรอกชื่อ-นามสกุล"")
        with col2:
            age = st.number_input(""อายุ (ปี) *"", min_value=60, max_value=120, value=65)
        with col3:
            gender = st.selectbox(""เพศ *"", [""ชาย"", ""หญิง"", ""ไม่ระบุ""])
        
        st.subheader(""🏥 โรคประจำตัว"")
        chronic = st.multiselect(""เลือกโรคประจำตัว (เลือกได้มากกว่า 1)"", CHRONIC_DISEASES)
        
        st.subheader(""💊 ยาที่รับประทานเป็นประจำ"")
        medications = st.multiselect(""เลือกยา (ถ้ามี)"", MEDICATIONS)
        
        col1, col2 = st.columns(2)
        with col1:
            bp = st.text_input(""ความดันโลหิตล่าสุด (เช่น 120/80)"", placeholder=""120/80"")
        with col2:
            bs = st.number_input(""ระดับน้ำตาลในเลือด (mg/dL)"", min_value=0, max_value=600, value=100)
        
        st.subheader("" อาการที่พบ (เลือกทั้งหมดที่เป็น)"")
        st.markdown(""**เลือกอาการที่คุณกำลังประสบอยู่ในขณะนี้**"")
        
        total_score = 0
        selected_symptoms = []
        emergency_symptoms = []
        
        for category, symptoms in SYMPTOMS_DATA.items():
            with st.expander(category, expanded=True):
                cols = st.columns(2)
                for i, (symptom, data) in enumerate(symptoms.items()):
                    with cols[i % 2]:
                        if st.checkbox(f""{symptom} (+{data['score']} คะแนน)"", key=symptom):
                            total_score += data['score']
                            selected_symptoms.append((symptom, data['score'], data['urgency']))
                            if data['urgency'] == ""ฉุกเฉิน"":
                                emergency_symptoms.append(symptom)
        
        st.subheader(""📝 หมายเหตุเพิ่มเติม"")
        notes = st.text_area(""อธิบายอาการเพิ่มเติม (ถ้ามี)"", placeholder=""เช่น อาการเป็นมา 3 วัน, มีไข้ร่วมด้วย, ฯลฯ"")
        
        submitted = st.form_submit_button(""🔍 ประเมินผล"", type=""primary"", use_container_width=True)
    
    if submitted:
        if not name:
            st.error(""⚠️ กรุณากรอกชื่อ-นามสกุล"")
        elif not selected_symptoms:
            st.warning(""⚠️ กรุณาเลือกอาการอย่างน้อย 1 รายการ"")
        else:
            # ===== Risk Calculation =====
            risk_multiplier = 1.0
            
            # ปรับตามอายุ
            if age >= 75:
                risk_multiplier += 0.3
            elif age >= 70:
                risk_multiplier += 0.2
            elif age >= 65:
                risk_multiplier += 0.1
            
            # ปรับตามโรคประจำตัว
            if ""โรคหัวใจ"" in chronic or ""โรคหลอดเลือดสมอง"" in chronic:
                risk_multiplier += 0.3
            if ""เบาหวาน"" in chronic and (bs < 70 or bs > 250):
                risk_multiplier += 0.2
            if ""ความดันโลหิตสูง"" in chronic:
                risk_multiplier += 0.1
            
            # ปรับตามยา
            if ""ยาละลายลิ่มเลือด"" in medications:
                risk_multiplier += 0.2
            
            final_score = int(total_score * risk_multiplier)
            
            # ===== Determine Risk Level =====
            has_emergency = len(emergency_symptoms) > 0
            
            if final_score >= 50 or has_emergency:
                risk_level = ""สูง""
                risk_class = ""risk-high""
                recommendation = ""🚨 **ฉุกเฉิน!** กรุณาไปพบแพทย์หรือโทร 1669 ทันที""
                advice = [
                    ""อย่ารอช้า นำส่งโรงพยาบาลที่ใกล้ที่สุด"",
                    ""ให้ผู้ป่วยนั่งหรือนอนในท่าที่สบาย"",
                    ""หากหมดสติ ให้จัดท่า recovery position"",
                    ""เตรียมรายการยาและประวัติโรคประจำตัว"",
                    ""โทรแจ้งญาติหรือผู้ดูแลทันที"",
                    ""อย่าให้ผู้ป่วยกินอาหารหรือน้ำ""
                ]
            elif final_score >= 20:
                risk_level = ""กลาง""
                risk_class = ""risk-medium""
                recommendation = ""⚠️ **ควรพบแพทย์ภายใน 24 ชั่วโมง**""
                advice = [
                    ""นัดพบแพทย์โดยเร็ว (ภายใน 1 วัน)"",
                    ""จดบันทึกอาการและเวลาที่เกิด"",
                    ""งดอาหารหนักก่อนพบแพทย์"",
                    ""ดื่มน้ำเพียงพอ พักผ่อนให้มาก"",
                    ""หากอาการแย่ลง ให้ไปโรงพยาบาลทันที"",
                    ""ทานยาตามแพทย์สั่งอย่างเคร่งครัด""
                ]
            else:
                risk_level = ""ต่ำ""
                risk_class = ""risk-low""
                recommendation = ""✅ **ดูแลตัวเองได้ และนัดพบแพทย์ตามปกติ**""
                advice = [
                    ""พักผ่อนให้เพียงพอ"",
                    ""ดื่มน้ำสะอาด 8-10 แก้วต่อวัน"",
                    ""ทานอาหารที่มีประโยชน์ ครบ 5 หมู่"",
                    ""สังเกตอาการ หากไม่ดีขึ้นใน 3 วัน ให้พบแพทย์"",
                    ""ออกกำลังกายเบาๆ เช่น เดิน ยืดเหยียด"",
                    ""วัดความดัน/น้ำตาลเป็นประจำ""
                ]
            
            # ===== Display Results =====
            st.markdown(""---"")
            st.markdown(f'<div class=""{risk_class}""><h2>🎯 ผลการประเมิน: ระดับความเสี่ยง <u>{risk_level}</u></h2><h3>{recommendation}</h3></div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(""### 📊 ข้อมูลการประเมิน"")
                st.write(f""**ชื่อ:** {name}"")
                st.write(f""**อายุ:** {age} ปี"")
                st.write(f""**เพศ:** {gender}"")
                st.write(f""**โรคประจำตัว:** {', '.join(chronic) if chronic else 'ไม่มี'}"")
            
            with col2:
                st.markdown(""### 📈 คะแนนความเสี่ยง"")
                st.metric(""คะแนนดิบ"", total_score)
                st.metric(""ตัวคูณความเสี่ยง"", f""{risk_multiplier}x"")
                st.metric(""คะแนนรวม"", final_score)
                st.progress(min(final_score / 100, 1.0))
            
            with col3:
                st.markdown(""### 💊 ยาที่รับประทาน"")
                if medications:
                    for med in medications:
                        st.write(f""- {med}"")
                else:
                    st.write(""ไม่มี"")
            
            st.markdown(""### 💡 คำแนะนำในการปฏิบัติตัว"")
            for i, adv in enumerate(advice, 1):
                st.markdown(f""{i}. {adv}"")
            
            if selected_symptoms:
                st.markdown(""### 📋 อาการที่เลือก"")
                for symptom, score, urgency in selected_symptoms:
                    emoji = ""🚨"" if urgency == ""ฉุกเฉิน"" else (""️"" if urgency == ""เฝ้าระวัง"" else ""✅"")
                    st.markdown(f""{emoji} {symptom} (+{score} คะแนน) - {urgency}"")
            
            # Save to history
            assessment_record = {
                ""date"": datetime.now().strftime(""%d/%m/%Y %H:%M""),
                ""name"": name,
                ""age"": age,
                ""gender"": gender,
                ""chronic"": chronic,
                ""medications"": medications,
                ""bp"": bp,
                ""bs"": bs,
                ""score"": final_score,
                ""risk"": risk_level,
                ""symptoms"": [s[0] for s in selected_symptoms],
                ""notes"": notes
            }
            st.session_state.history.append(assessment_record)
            
            st.success(""✅ บันทึกผลการประเมินเรียบร้อยแล้ว"")
            
            # Emergency button
            if risk_level == ""สูง"":
                if st.button(""📞 โทรฉุกเฉิน 1669"", type=""primary""):
                    st.balloons()
                    st.info("" กรุณาโทร 1669 ทันที"")

elif menu == "" ประวัติการประเมิน"":
    st.markdown('<div class=""main-header""><h1> ประวัติการประเมิน</h1></div>', unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info(""📭 ยังไม่มีประวัติการประเมิน"")
    else:
        # Filter options
        filter_name = st.text_input(""🔍 ค้นหาตามชื่อ"")
        
        filtered_history = st.session_state.history
        if filter_name:
            filtered_history = [r for r in filtered_history if filter_name.lower() in r['name'].lower()]
        
        st.write(f""**จำนวนรายการ:** {len(filtered_history)} รายการ"")
        
        for i, record in enumerate(reversed(filtered_history), 1):
            risk_emoji = ""🚨"" if record['risk'] == ""สูง"" else (""⚠️"" if record['risk'] == ""กลาง"" else ""✅"")
            with st.expander(f""#{i} - {record['name']} ({record['date']}) - {risk_emoji} ความเสี่ยง{record['risk']}"", expanded=(i==1)):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f""**อายุ:** {record['age']} ปี"")
                    st.write(f""**เพศ:** {record['gender']}"")
                    st.write(f""**คะแนน:** {record['score']}"")
                    st.write(f""**โรคประจำตัว:** {', '.join(record['chronic']) if record['chronic'] else 'ไม่มี'}"")
                
                with col2:
                    st.write(f""**อาการ:** {', '.join(record['symptoms'])}"")
                    if record['notes']:
                        st.write(f""**หมายเหตุ:** {record['notes']}"")
        
        if st.button(""🗑️ ล้างประวัติทั้งหมด"", type=""secondary""):
            st.session_state.history = []
            st.rerun()

elif menu == ""📈 สถิติ"":
    st.markdown('<div class=""main-header""><h1>📈 สถิติการประเมิน</h1></div>', unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info(""📭 ยังไม่มีข้อมูลสำหรับแสดงสถิติ"")
    else:
        # Convert to DataFrame
        df = pd.DataFrame(st.session_state.history)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            total = len(df)
            st.metric(""📊 จำนวนครั้งทั้งหมด"", total)
        with col2:
            high_risk = len(df[df['risk'] == 'สูง'])
            st.metric(""🚨 ความเสี่ยงสูง"", high_risk)
        with col3:
            avg_score = df['score'].mean()
            st.metric(""📈 คะแนนเฉลี่ย"", f""{avg_score:.1f}"")
        
        st.markdown(""---"")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader(""📊 สัดส่วนระดับความเสี่ยง"")
            risk_counts = df['risk'].value_counts()
            st.bar_chart(risk_counts)
        
        with col_b:
            st.subheader(""📈 คะแนนความเสี่ยงในแต่ละครั้ง"")
            score_df = df[['date', 'score']].set_index('date')
            st.line_chart(score_df)
        
        st.markdown(""---"")
        st.subheader(""🏥 โรคประจำตัวที่พบบ่อย"")
        all_diseases = []
        for diseases in df['chronic']:
            all_diseases.extend(diseases)
        disease_counts = pd.Series(all_diseases).value_counts()
        st.bar_chart(disease_counts.head(10))

elif menu == ""ℹ️ เกี่ยวกับระบบ"":
    st.markdown('<div class=""main-header""><h1>️ เกี่ยวกับระบบ</h1></div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🎓 ข้อมูลโปรเจกต์
    - **ชื่อโปรเจกต์:** ระบบประเมินการตัดสินใจไปพบแพทย์ของผู้สูงอายุ
    - **ประเภท:** โปรเจกต์ปี 4 (Senior Project)
    - **เทคโนโลยี:** Python, Streamlit, Pandas
    - **กลุ่มเป้าหมาย:** ผู้สูงอายุ 60 ปีขึ้นไป และผู้ดูแล
    
    ### 🎯 วัตถุประสงค์
    1. ช่วยผู้สูงอายุและผู้ดูแลตัดสินใจว่าควรไปพบแพทย์หรือไม่
    2. ลดความกังวลจากการประเมินอาการผิดพลาด
    3. ป้องกันการไปพบแพทย์โดยไม่จำเป็น และป้องกันกรณีฉุกเฉินที่ถูกละเลย
    4. บันทึกประวัติการประเมินเพื่อติดตามอาการ
    
    ###  เกณฑ์การประเมิน
    ระบบใช้เกณฑ์คะแนนถ่วงน้ำหนัก (Weighted Scoring) โดยแบ่งอาการเป็น 3 ระดับ:
    
    **อาการฉุกเฉิน** (25-40 คะแนน)
    - เจ็บหน้าอก, หายใจไม่ออก, หมดสติ
    - แขนขาอ่อนแรง, พูดไม่ชัด
    - เลือดออกไม่หยุด, ชัก
    
    **อาการที่ต้องเฝ้าระวัง** (10-25 คะแนน)
    - ไข้สูง, เวียนศีรษะรุนแรง
    - ความดันสูง, น้ำตาลผิดปกติ
    - ใจสั่น, ปวดท้องรุนแรง
    
    **อาการทั่วไป** (3-8 คะแนน)
    - ปวดเมื่อย, นอนไม่หลับ
    - ไอ, เจ็บคอ, ปวดหลัง
    
    ###  การคำนวณคะแนน
    ```
    คะแนนรวม = (คะแนนอาการรวม) × (ตัวคูณความเสี่ยง)
    ```
    
    **ตัวคูณความเสี่ยง:**
    - อายุ 65-69 ปี: +0.1
    - อายุ 70-74 ปี: +0.2
    - อายุ 75 ปีขึ้นไป: +0.3
    - มีโรคหัวใจ/หลอดเลือดสมอง: +0.3
    - เบาหวาน + น้ำตาลผิดปกติ: +0.2
    
    ###  เกณฑ์การตัดสิน
    - **ความเสี่ยงสูง** (>= 50 คะแนน หรือมีอาการฉุกเฉิน): ไปโรงพยาบาลทันที
    - **ความเสี่ยงกลาง** (20-49 คะแนน): พบแพทย์ภายใน 24 ชั่วโมง
    - **ความเสี่ยงต่ำ** (< 20 คะแนน): ดูแลตัวเองได้, นัดพบแพทย์ตามปกติ
    
    ### 👨‍💻 ผู้พัฒนา
    พัฒนาเป็นโปรเจกต์ปี 4 เพื่อการศึกษา
    
    ### ⚠️ ข้อจำกัด
    - ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้
    - เป็นเพียงเครื่องมือช่วยตัดสินใจเบื้องต้น
    - ควรปรึกษาแพทย์หรือบุคลากรทางการแพทย์เสมอ
    - ข้อมูลทางการแพทย์อ้างอิงจากแนวทางปฏิบัติทั่วไป
    
    ### 📞 ติดต่อฉุกเฉิน
    - **1669** - เจ็บป่วยฉุกเฉิน
    - **1556** - ผู้สูงอายุ
    - **1663** - สุขภาพจิต
    """)

# ==================== Footer ====================
st.markdown(""---"")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>🏥 ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ | โปรเจกต์ปี 4</p>
    <p>พัฒนาด้วย Streamlit | ข้อมูลทางการแพทย์อ้างอิงจากแนวทางปฏิบัติทั่วไป</p>
    <p>⚠️ ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้</p>
</div>
""", unsafe_allow_html=True)
"@ | Out-File -FilePath "app.py" -Encoding utf8