# app.py
# Streamlit OPD Fever AI Triage (Thai)
# Deploy on Streamlit Cloud
# requirements.txt:
# streamlit
# openai

import streamlit as st
from openai import OpenAI
import os

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(
    page_title="AI คัดกรองไข้ OPD",
    page_icon="🌡️",
    layout="centered"
)

st.title("🌡️ AI คัดกรองไข้ OPD จากอุณหภูมิหน้าผาก")
st.caption("ใช้ข้อมูลพื้นฐาน + GPT เพื่อช่วยประเมินเบื้องต้น (ไม่ใช่การวินิจฉัยโรค)")

# ---------------------------
# OPENAI KEY
# ---------------------------
api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

if not api_key:
    st.error("กรุณาใส่ OPENAI_API_KEY ใน Streamlit Secrets")
    st.stop()

client = OpenAI(api_key=api_key)

# ---------------------------
# INPUT FORM
# ---------------------------
with st.form("fever_form"):

    st.subheader("กรอกข้อมูลผู้ป่วย")

    temp_now = st.number_input(
        "Forehead T ตอนนี้ (°C)",
        min_value=30.0,
        max_value=45.0,
        value=36.5,
        step=0.1
    )

    temp_repeat = st.number_input(
        "Forehead T ซ้ำหลัง 3 นาที (°C)",
        min_value=30.0,
        max_value=45.0,
        value=36.6,
        step=0.1
    )

    hr = st.number_input(
        "ชีพจร HR (ครั้ง/นาที)",
        min_value=30,
        max_value=220,
        value=80,
        step=1
    )

    age = st.number_input(
        "อายุ (ปี)",
        min_value=0,
        max_value=120,
        value=35,
        step=1
    )

    symptoms = st.multiselect(
        "อาการ",
        [
            "ไม่มีอาการ",
            "หนาวสั่น",
            "ไอ",
            "เจ็บคอ",
            "น้ำมูก",
            "ปวดเมื่อย",
            "หอบเหนื่อย",
            "อ่อนเพลีย",
            "ปวดศีรษะ",
            "ถ่ายเหลว",
            "ปัสสาวะแสบขัด"
        ]
    )

    submitted = st.form_submit_button("วิเคราะห์")

# ---------------------------
# ANALYSIS
# ---------------------------
if submitted:

    delta = round(temp_repeat - temp_now, 2)

    symptom_text = ", ".join(symptoms) if symptoms else "ไม่มีอาการ"

    prompt = f"""
คุณคือ AI ผู้ช่วยคัดกรอง OPD ภาษาไทย

ข้อมูลผู้ป่วย:
- Forehead T ตอนนี้: {temp_now} °C
- Forehead T ซ้ำหลัง 3 นาที: {temp_repeat} °C
- ΔT = {delta} °C
- HR = {hr} bpm
- อายุ = {age} ปี
- อาการ = {symptom_text}

จงประเมินเป็นภาษาไทยแบบสั้น กระชับ สำหรับพยาบาล OPD

ให้เลือกผลลัพธ์หลักเพียง 1 ข้อ:
1. likely afebrile = น่าจะไม่มีไข้
2. probable fever = น่าจะมีไข้
3. hidden fever possible = อาจมีไข้แฝง

และแนะนำว่า:
- use tympanic/oral confirmation = ควรวัดยืนยันทางหูหรือทางปาก
หรือ
- เฝ้าระวัง/ประเมินซ้ำ

ตอบในรูปแบบนี้เท่านั้น:

ผลประเมิน: ...
เหตุผล: ...
คำแนะนำ: ...
"""

    with st.spinner("กำลังวิเคราะห์..."):

        try:
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "คุณเป็นผู้ช่วยคัดกรองผู้ป่วย OPD ภาษาไทย"},
                    {"role": "user", "content": prompt}
                ]
            )

            result = response.choices[0].message.content

            st.success("ผลวิเคราะห์")
            st.write(result)

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

# ---------------------------
# FOOTER
# ---------------------------
st.divider()
st.caption(
    "คำเตือน: เครื่องมือนี้ใช้ช่วยคัดกรองเบื้องต้น ไม่แทนการตรวจรักษาโดยแพทย์ "
    "หากมีอาการรุนแรงให้พบแพทย์ทันที"
)
