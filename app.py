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
warnings.filterwarnings('ignore')

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
    .risk-high {
        background: linear-gradient(135deg, #FF4B4B, #FF0000);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }
    .risk-medium {
        background: linear-gradient(135deg, #FFA500, #FF8C00);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }
    .risk-low {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ==================== ข้อมูลทางการแพทย์ ====================
SYMPTOMS_DATA = {
    " อาการฉุกเฉิน (ต้องไปโรงพยาบาลทันที)": {
        "เจ็บหน้าอก/แน่นหน้าอก": 35,
        "หายใจไม่ออก/หายใจลำบาก": 35,
        "หมดสติ/วูบ/เป็นลม": 40,
        "แขนขาอ่อนแรงครึ่งซีก": 35,
        "พูดไม่ชัด/ปากเบี้ยว": 35,
        "เลือดออกไม่หยุด": 30,
        "ชัก/เกร็ง": 35,
        "ปวดศีรษะรุนแรงที่สุดในชีวิต": 30,
        "อาเจียนเป็นเลือด": 35,
        "ถ่ายอุจจาระเป็นเลือด": 30
    },
    "⚠️ อาการที่ต้องเฝ้าระวัง (พบแพทย์ภายใน 24 ชม.)": {
        "ไข้สูงกว่า 38.5°C": 18,
        "เวียนศีรษะรุนแรง": 15,
        "คลื่นไส้/อาเจียนต่อเนื่อง": 15,
        "ปวดศีรษะรุนแรง": 15,
        "ความดันโลหิตสูงเกิน 180/110": 25,
        "ระดับน้ำตาลต่ำกว่า 70 mg/dL": 20,
        "ระดับน้ำตาลสูงกว่า 300 mg/dL": 22,
        "บวมตามแขนขา": 12,
        "ใจสั่น/หัวใจเต้นเร็ว": 18,
        "ปวดท้องรุนแรง": 18,
        "หายใจมีเสียงวี้ด": 20,
        "ปัสสาวะแสบขัด/มีเลือด": 12
    },
    "✅ อาการทั่วไป (ดูแลตัวเองได้/นัดพบแพทย์ตามปกติ)": {
        "ปวดเมื่อยตามตัว": 3,
        "ปวดข้อ": 5,
        "นอนไม่หลับ": 4,
        "เบื่ออาหาร": 5,
        "ท้องผูก": 3,
        "อ่อนเพลียเล็กน้อย": 4,
        "ไอ/เจ็บคอ": 6,
        "น้ำมูกไหล": 3,
        "ปวดหลัง": 5,
        "ตาพร่ามัว": 8
    }
}

CHRONIC_DISEASES = [
    "เบาหวาน", "ความดันโลหิตสูง", "โรคหัวใจ", "โรคไต",
    "โรคปอด", "โรคหลอดเลือดสมอง", "มะเร็ง", "โรคไทรอยด์",
    "โรคเกาต์", "โรคกระดูกพรุน", "โรคพาร์กินสัน", "ไม่มี"
]

MEDICATIONS = [
    "ยาเบาหวาน", "ยาความดัน", "ยาหัวใจ", "ยาละลายลิ่มเลือด",
    "ยาขยายหลอดลม", "ยาขับปัสสาวะ", "ยาแก้ปวด", "อื่นๆ"
]

# ==================== Session State ====================
if "history" not in st.session_state:
    st.session_state.history = []

# ==================== Sidebar ====================
with st.sidebar:
    st.title("📋 เมนูหลัก")
    menu = st.radio(
        "เลือกหัวข้อ",
        ["🏠 หน้าหลัก", " ประเมินอาการ", "📊 ประวัติการประเมิน", "📈 สถิติและกราฟ", " AI ทำนายผล", "ℹ️ เกี่ยวกับระบบ"],
        index=1
    )
    st.markdown("---")
    st.caption(f" {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.caption(" โปรเจกต์ปี 4 - Senior Project")

# ==================== หน้าที่ 1: หน้าหลัก ====================
if menu == "🏠 หน้าหลัก":
    st.markdown('<div class="main-header"><h1>🏥 ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ</h1><h3>Elderly Medical Decision Support System</h3></div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👴 กลุ่มเป้าหมาย", "60+ ปี")
    with col2:
        total_symptoms = sum(len(v) for v in SYMPTOMS_DATA.values())
        st.metric("📋 จำนวนอาการ", f"{total_symptoms} อาการ")
    with col3:
        st.metric("⚕️ ระดับความเสี่ยง", "3 ระดับ")
    with col4:
        st.metric("⏱️ เวลาประเมิน", "< 5 นาที")

    st.markdown("###  คุณสมบัติของระบบ")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        - ✅ ประเมินอาการตามเกณฑ์ทางการแพทย์
        - ✅ วิเคราะห์ความเสี่ยง 3 ระดับ (สูง/กลาง/ต่ำ)
        - ✅ บันทึกประวัติการประเมิน
        - ✅ รองรับโรคประจำตัวและยา
        """)
    with col_b:
        st.markdown("""
        - ✅ แสดงสถิติแบบกราฟ (Plotly)
        - ✅ ระบบ AI ทำนายผล (Scikit-Learn)
        - ✅ คำแนะนำเฉพาะบุคคล
        - ✅ UI ใช้งานง่าย เหมาะกับผู้สูงอายุ
        """)

    st.info("💡 **หมายเหตุ**: ระบบนี้เป็นเครื่องมือช่วยตัดสินใจเบื้องต้น ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้")

    st.markdown("### 📞 เบอร์โทรศัพท์ฉุกเฉิน")
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        st.markdown("<div class='metric-card'><h3>🚑 1669</h3><p>เจ็บป่วยฉุกเฉิน</p></div>", unsafe_allow_html=True)
    with col_e2:
        st.markdown("<div class='metric-card'><h3>👴 1556</h3><p>สายด่วนผู้สูงอายุ</p></div>", unsafe_allow_html=True)
    with col_e3:
        st.markdown("<div class='metric-card'><h3>🧠 1323</h3><p>สุขภาพจิต</p></div>", unsafe_allow_html=True)

# ==================== หน้าที่ 2: ประเมินอาการ ====================
elif menu == "🩺 ประเมินอาการ":
    st.markdown('<div class="main-header"><h1>🩺 แบบประเมินอาการ</h1></div>', unsafe_allow_html=True)

    with st.form("assessment_form"):
        st.subheader(" ข้อมูลทั่วไป")
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("ชื่อ-นามสกุล *", placeholder="กรอกชื่อ-นามสกุล")
        with col2:
            age = st.number_input("อายุ (ปี) *", min_value=60, max_value=120, value=65)
        with col3:
            gender = st.selectbox("เพศ *", ["ชาย", "หญิง", "ไม่ระบุ"])

        st.subheader("🏥 โรคประจำตัว")
        chronic = st.multiselect("เลือกโรคประจำตัว (เลือกได้มากกว่า 1)", CHRONIC_DISEASES)

        st.subheader("💊 ยาที่รับประทานเป็นประจำ")
        medications = st.multiselect("เลือกยา (ถ้ามี)", MEDICATIONS)

        col1, col2 = st.columns(2)
        with col1:
            bp = st.text_input("ความดันโลหิตล่าสุด (เช่น 120/80)", placeholder="120/80")
        with col2:
            bs = st.number_input("ระดับน้ำตาลในเลือด (mg/dL)", min_value=0, max_value=600, value=100)

        st.subheader("🤒 อาการที่พบ (เลือกทั้งหมดที่เป็น)")
        st.markdown("**เลือกอาการที่คุณกำลังประสบอยู่ในขณะนี้**")

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
                            selected_symptoms.append((symptom, score, category))
                            if "ฉุกเฉิน" in category:
                                emergency_symptoms.append(symptom)

        st.subheader("📝 หมายเหตุเพิ่มเติม")
        notes = st.text_area("อธิบายอาการเพิ่มเติม (ถ้ามี)", placeholder="เช่น อาการเป็นมา 3 วัน, มีไข้ร่วมด้วย, ฯลฯ")

        submitted = st.form_submit_button("🔍 ประเมินผล", type="primary", use_container_width=True)

    if submitted:
        if not name:
            st.error("⚠️ กรุณากรอกชื่อ-นามสกุล")
        elif not selected_symptoms:
            st.warning("️ กรุณาเลือกอาการอย่างน้อย 1 รายการ")
        else:
            # คำนวณคะแนน
            risk_multiplier = 1.0

            if age >= 75:
                risk_multiplier += 0.3
            elif age >= 70:
                risk_multiplier += 0.2
            elif age >= 65:
                risk_multiplier += 0.1

            if "โรคหัวใจ" in chronic or "โรคหลอดเลือดสมอง" in chronic:
                risk_multiplier += 0.3
            if "เบาหวาน" in chronic and (bs < 70 or bs > 250):
                risk_multiplier += 0.2
            if "ความดันโลหิตสูง" in chronic:
                risk_multiplier += 0.1

            if "ยาละลายลิ่มเลือด" in medications:
                risk_multiplier += 0.2

            final_score = int(total_score * risk_multiplier)

            has_emergency = len(emergency_symptoms) > 0

            if final_score >= 50 or has_emergency:
                risk_level = "สูง"
                risk_class = "risk-high"
                recommendation = "🚨 ฉุกเฉิน! กรุณาไปพบแพทย์หรือโทร 1669 ทันที"
                advice = [
                    "อย่ารอช้า นำส่งโรงพยาบาลที่ใกล้ที่สุด",
                    "ให้ผู้ป่วยนั่งหรือนอนในท่าที่สบาย",
                    "หากหมดสติ ให้จัดท่า recovery position",
                    "เตรียมรายการยาและประวัติโรคประจำตัว",
                    "โทรแจ้งญาติหรือผู้ดูแลทันที",
                    "อย่าให้ผู้ป่วยกินอาหารหรือน้ำ"
                ]
            elif final_score >= 20:
                risk_level = "กลาง"
                risk_class = "risk-medium"
                recommendation = "⚠️ ควรพบแพทย์ภายใน 24 ชั่วโมง"
                advice = [
                    "นัดพบแพทย์โดยเร็ว (ภายใน 1 วัน)",
                    "จดบันทึกอาการและเวลาที่เกิด",
                    "งดอาหารหนักก่อนพบแพทย์",
                    "ดื่มน้ำเพียงพอ พักผ่อนให้มาก",
                    "หากอาการแย่ลง ให้ไปโรงพยาบาลทันที",
                    "ทานยาตามแพทย์สั่งอย่างเคร่งครัด"
                ]
            else:
                risk_level = "ต่ำ"
                risk_class = "risk-low"
                recommendation = "✅ ดูแลตัวเองได้ และนัดพบแพทย์ตามปกติ"
                advice = [
                    "พักผ่อนให้เพียงพอ",
                    "ดื่มน้ำสะอาด 8-10 แก้วต่อวัน",
                    "ทานอาหารที่มีประโยชน์ ครบ 5 หมู่",
                    "สังเกตอาการ หากไม่ดีขึ้นใน 3 วัน ให้พบแพทย์",
                    "ออกกำลังกายเบาๆ เช่น เดิน ยืดเหยียด",
                    "วัดความดัน/น้ำตาลเป็นประจำ"
                ]

            st.markdown("---")
            st.markdown(f'<div class="{risk_class}"><h2>🎯 ผลการประเมิน: ระดับความเสี่ยง {risk_level}</h2><h3>{recommendation}</h3></div>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("### 📊 ข้อมูลการประเมิน")
                st.write(f"**ชื่อ:** {name}")
                st.write(f"**อายุ:** {age} ปี")
                st.write(f"**เพศ:** {gender}")
                st.write(f"**โรคประจำตัว:** {', '.join(chronic) if chronic else 'ไม่มี'}")

            with col2:
                st.markdown("### 📈 คะแนนความเสี่ยง")
                st.metric("คะแนนดิบ", total_score)
                st.metric("ตัวคูณความเสี่ยง", f"{risk_multiplier}x")
                st.metric("คะแนนรวม", final_score)
                st.progress(min(final_score / 100, 1.0))

            with col3:
                st.markdown("### 💊 ยาที่รับประทาน")
                if medications:
                    for med in medications:
                        st.write(f"- {med}")
                else:
                    st.write("ไม่มี")

            st.markdown("### 💡 คำแนะนำในการปฏิบัติตัว")
            for i, adv in enumerate(advice, 1):
                st.markdown(f"{i}. {adv}")

            if selected_symptoms:
                st.markdown("### 📋 อาการที่เลือก")
                for symptom, score, category in selected_symptoms:
                    if "ฉุกเฉิน" in category:
                        emoji = "🚨"
                    elif "เฝ้าระวัง" in category:
                        emoji = "⚠️"
                    else:
                        emoji = "✅"
                    st.markdown(f"{emoji} {symptom} (+{score} คะแนน)")

            st.session_state.history.append({
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "name": name,
                "age": age,
                "gender": gender,
                "chronic": chronic,
                "medications": medications,
                "bp": bp,
                "bs": bs,
                "score": final_score,
                "risk": risk_level,
                "symptoms": [s[0] for s in selected_symptoms],
                "notes": notes
            })

            st.success("✅ บันทึกผลการประเมินเรียบร้อยแล้ว")

            if risk_level == "สูง":
                st.markdown("---")
                st.error("📞 **กรุณาโทร 1669 ทันที** หากมีอาการฉุกเฉิน")

# ==================== หน้าที่ 3: ประวัติการประเมิน ====================
elif menu == " ประวัติการประเมิน":
    st.markdown('<div class="main-header"><h1>📊 ประวัติการประเมิน</h1></div>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.info("📭 ยังไม่มีประวัติการประเมิน")
    else:
        filter_name = st.text_input("🔍 ค้นหาตามชื่อ")

        filtered_history = st.session_state.history
        if filter_name:
            filtered_history = [r for r in filtered_history if filter_name.lower() in r['name'].lower()]

        st.write(f"**จำนวนรายการ:** {len(filtered_history)} รายการ")

        for i, record in enumerate(reversed(filtered_history), 1):
            if record['risk'] == "สูง":
                risk_emoji = "🚨"
            elif record['risk'] == "กลาง":
                risk_emoji = "⚠️"
            else:
                risk_emoji = "✅"

            with st.expander(f"#{i} - {record['name']} ({record['date']}) - {risk_emoji} ความเสี่ยง{record['risk']}", expanded=(i == 1)):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**อายุ:** {record['age']} ปี")
                    st.write(f"**เพศ:** {record['gender']}")
                    st.write(f"**คะแนน:** {record['score']}")
                    st.write(f"**โรคประจำตัว:** {', '.join(record['chronic']) if record['chronic'] else 'ไม่มี'}")

                with col2:
                    st.write(f"**อาการ:** {', '.join(record['symptoms'])}")
                    if record.get('notes'):
                        st.write(f"**หมายเหตุ:** {record['notes']}")

        if st.button("🗑️ ล้างประวัติทั้งหมด", type="secondary"):
            st.session_state.history = []
            st.rerun()

# ==================== หน้าที่ 4: สถิติและกราฟ (ใช้ Plotly ทั้งหมด) ====================
elif menu == "📈 สถิติและกราฟ":
    st.markdown('<div class="main-header"><h1>📊 สถิติและกราฟ (Data Visualization)</h1></div>', unsafe_allow_html=True)

    if len(st.session_state.history) < 3:
        dummy_data = [
            {"date": "22/08/2026", "name": "สมชาย", "age": 70, "score": 15, "risk": "ต่ำ"},
            {"date": "22/08/2026", "name": "สมหญิง", "age": 75, "score": 45, "risk": "กลาง"},
            {"date": "22/08/2026", "name": "วิชัย", "age": 80, "score": 65, "risk": "สูง"},
            {"date": "22/08/2026", "name": "มาลี", "age": 68, "score": 10, "risk": "ต่ำ"},
            {"date": "22/08/2026", "name": "ประเสริฐ", "age": 82, "score": 55, "risk": "สูง"},
            {"date": "22/08/2026", "name": "สุดา", "age": 72, "score": 25, "risk": "กลาง"},
            {"date": "22/08/2026", "name": "วิภา", "age": 65, "score": 8, "risk": "ต่ำ"},
            {"date": "22/08/2026", "name": "สมศักดิ์", "age": 88, "score": 70, "risk": "สูง"}
        ]
        df = pd.DataFrame(dummy_data)
        st.warning("️ ใช้ข้อมูลจำลอง (Dummy Data) เนื่องจากประวัติการประเมินยังน้อยเกินไป")
    else:
        df = pd.DataFrame(st.session_state.history)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 จำนวนครั้งทั้งหมด", len(df))
    with col2:
        high_risk = len(df[df['risk'] == 'สูง'])
        st.metric("🚨 ความเสี่ยงสูง", high_risk)
    with col3:
        avg_score = df['score'].mean()
        st.metric(" คะแนนเฉลี่ย", f"{avg_score:.1f}")

    st.markdown("---")

    st.subheader("📊 สัดส่วนระดับความเสี่ยง (Pie Chart)")
    risk_counts = df['risk'].value_counts().reset_index()
    risk_counts.columns = ['ระดับความเสี่ยง', 'จำนวน']
    fig_pie = px.pie(
        risk_counts,
        values='จำนวน',
        names='ระดับความเสี่ยง',
        color='ระดับความเสี่ยง',
        color_discrete_map={'ต่ำ': '#4CAF50', 'กลาง': '#FFA500', 'สูง': '#FF4B4B'},
        hole=0.4
    )
    fig_pie.update_layout(title_text="สัดส่วนระดับความเสี่ยง")
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    st.subheader("📈 ความสัมพันธ์ อายุ vs คะแนน (Scatter Plot)")
    fig_scatter = px.scatter(
        df,
        x='age',
        y='score',
        color='risk',
        color_discrete_map={'ต่ำ': '#4CAF50', 'กลาง': '#FFA500', 'สูง': '#FF4B4B'},
        size='score',
        hover_data=['name', 'date'],
        title="Scatter Plot: อายุ vs คะแนนความเสี่ยง",
        labels={'age': 'อายุ (ปี)', 'score': 'คะแนนความเสี่ยง', 'risk': 'ระดับความเสี่ยง'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    st.subheader("📊 คะแนนความเสี่ยงในแต่ละครั้ง (Bar Chart)")
    fig_bar = px.bar(
        df,
        x='name',
        y='score',
        color='risk',
        color_discrete_map={'ต่ำ': '#4CAF50', 'กลาง': '#FFA500', 'สูง': '#FF4B4B'},
        title="Bar Chart: คะแนนความเสี่ยงตามชื่อ",
        labels={'name': 'ชื่อผู้ประเมิน', 'score': 'คะแนนความเสี่ยง', 'risk': 'ระดับความเสี่ยง'},
        text='score'
    )
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    st.subheader("📊 การกระจายตัวของคะแนน (Histogram)")
    fig_hist = px.histogram(
        df,
        x='score',
        color='risk',
        color_discrete_map={'ต่ำ': '#4CAF50', 'กลาง': '#FFA500', 'สูง': '#FF4B4B'},
        nbins=10,
        title="การกระจายตัวของคะแนนความเสี่ยง",
        labels={'score': 'คะแนนความเสี่ยง', 'risk': 'ระดับความเสี่ยง'}
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")

    st.subheader("📦 การกระจายตัวของคะแนนตามระดับความเสี่ยง (Box Plot)")
    fig_box = px.box(
        df,
        x='risk',
        y='score',
        color='risk',
        color_discrete_map={'ต่ำ': '#4CAF50', 'กลาง': '#FFA500', 'สูง': '#FF4B4B'},
        title="Box Plot: การกระจายตัวของคะแนน",
        labels={'risk': 'ระดับความเสี่ยง', 'score': 'คะแนนความเสี่ยง'}
    )
    st.plotly_chart(fig_box, use_container_width=True)

# ==================== หน้าที่ 5: AI ทำนายผล ====================
elif menu == "🤖 AI ทำนายผล":
    st.markdown('<div class="main-header"><h1>🤖 ระบบ Machine Learning (Scikit-Learn)</h1></div>', unsafe_allow_html=True)

    st.subheader(" โมเดล Random Forest Classifier")
    st.write("ระบบจะฝึก AI จากข้อมูลเพื่อทำนายระดับความเสี่ยงจาก **อายุ** และ **คะแนนอาการ**")

    X_data = [
        [65, 10], [70, 15], [68, 12], [72, 18], [66, 8],
        [75, 45], [78, 50], [73, 40], [76, 48], [74, 42],
        [80, 65], [82, 70], [85, 75], [79, 60], [88, 80],
        [67, 14], [71, 20], [69, 16], [77, 52], [81, 62]
    ]
    y_data = [
        0, 0, 0, 0, 0,
        1, 1, 1, 1, 1,
        2, 2, 2, 2, 2,
        0, 1, 0, 1, 2
    ]

    X = np.array(X_data)
    y = np.array(y_data)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    st.success(f"✅ ฝึกโมเดลเสร็จสิ้น! (Accuracy: {accuracy*100:.1f}%)")

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

        result_map = {0: "✅ ความเสี่ยงต่ำ", 1: "️ ความเสี่ยงกลาง", 2: " ความเสี่ยงสูง"}
        color_map = {0: "green", 1: "orange", 2: "red"}

        st.markdown(f'<div style="background-color: {color_map[prediction[0]]}; color: white; padding: 20px; border-radius: 10px; text-align: center;"><h2>AI ทำนายผล: {result_map[prediction[0]]}</h2></div>', unsafe_allow_html=True)

        st.write("**ความน่าจะเป็นของแต่ละระดับ:**")
        proba_df = pd.DataFrame({
            'ระดับ': ['ต่ำ', 'กลาง', 'สูง'],
            'ความน่าจะเป็น (%)': [f"{p*100:.1f}%" for p in proba]
        })
        st.dataframe(proba_df, use_container_width=True)

        fig_proba = go.Figure(data=[
            go.Bar(
                x=['ต่ำ', 'กลาง', 'สูง'],
                y=proba * 100,
                marker_color=['green', 'orange', 'red']
            )
        ])
        fig_proba.update_layout(
            title="ความน่าจะเป็นของแต่ละระดับความเสี่ยง",
            xaxis_title="ระดับความเสี่ยง",
            yaxis_title="ความน่าจะเป็น (%)"
        )
        st.plotly_chart(fig_proba, use_container_width=True)

    st.markdown("---")
    st.subheader(" Feature Importance")
    feature_names = ['อายุ', 'คะแนนอาการ']
    importances = model.feature_importances_

    fig_imp = go.Figure(data=[
        go.Bar(
            x=feature_names,
            y=importances,
            marker_color=['#2E86AB', '#A23B72']
        )
    ])
    fig_imp.update_layout(
        title="ความสำคัญของฟีเจอร์ (Feature Importance)",
        xaxis_title="ฟีเจอร์",
        yaxis_title="Importance Score"
    )
    st.plotly_chart(fig_imp, use_container_width=True)

# ==================== หน้าที่ 6: เกี่ยวกับระบบ ====================
elif menu == "️ เกี่ยวกับระบบ":
    st.markdown('<div class="main-header"><h1>ℹ️ เกี่ยวกับระบบ</h1></div>', unsafe_allow_html=True)

    st.markdown("""
    ### 🎓 ข้อมูลโปรเจกต์
    - **ชื่อโปรเจกต์:** ระบบประเมินการตัดสินใจไปพบแพทย์ของผู้สูงอายุ
    - **ประเภท:** โปรเจกต์ปี 4 (Senior Project)
    - **เทคโนโลยี:** Python, Streamlit, Pandas, Scikit-learn, Plotly
    - **กลุ่มเป้าหมาย:** ผู้สูงอายุ 60 ปีขึ้นไป และผู้ดูแล

    ### 🎯 วัตถุประสงค์
    1. ช่วยผู้สูงอายุและผู้ดูแลตัดสินใจว่าควรไปพบแพทย์หรือไม่
    2. นำเทคโนโลยี Machine Learning มาช่วยทำนายความเสี่ยง
    3. แสดงผลสถิติผ่าน Data Visualization ที่เข้าใจง่าย
    4. บันทึกประวัติการประเมินเพื่อติดตามอาการ

    ### 🔬 เกณฑ์การประเมิน
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

    ### 🤖 ระบบ AI
    - ใช้ **Random Forest Classifier** จาก Scikit-Learn
    - ฝึกด้วยข้อมูลอายุและคะแนนอาการ
    - ทำนายระดับความเสี่ยง 3 ระดับ

    ### ⚠️ ข้อจำกัด
    - ไม่สามารถทดแทนการวินิจฉัยของแพทย์ได้
    - เป็นเพียงเครื่องมือช่วยตัดสินใจเบื้องต้น
    - ควรปรึกษาแพทย์หรือบุคลากรทางการแพทย์เสมอ

    ### 📞 ติดต่อฉุกเฉิน
    - **1669** - เจ็บป่วยฉุกเฉิน
    - **1556** - ผู้สูงอายุ
    - **1323** - สุขภาพจิต
    """)

# ==================== Footer ====================
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; padding: 20px;'><p>🏥 ระบบประเมินการไปพบแพทย์ของผู้สูงอายุ | โปรเจกต์ปี 4 | พัฒนาด้วย Streamlit</p></div>", unsafe_allow_html=True)