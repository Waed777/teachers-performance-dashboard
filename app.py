import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

st.set_page_config(page_title="لوحة متابعة المعلمات", layout="wide")

st.title("📊 لوحة متابعة الأداء الأسبوعي")

uploaded_file = st.file_uploader("ارفعي ملف المتابعة Excel", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    # تنظيف الفراغات
    df.columns = df.columns.str.strip()

    st.subheader("📌 البيانات")

    st.dataframe(df)

    # المؤشرات الرئيسية
    total_teachers = df["اسم المعلمة"].nunique()
    total_missing = df["عدد النواقص"].sum()

    completed = df[df["عدد النواقص"] == 0].shape[0]
    need_support = df[df["عدد النواقص"] >= 3].shape[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("عدد المعلمات", total_teachers)
    col2.metric("عدد النواقص الكلي", total_missing)
    col3.metric("مكتملات", completed)
    col4.metric("يحتاج متابعة", need_support)

    # رسم بياني
    st.subheader("📈 توزيع النواقص")

    fig, ax = plt.subplots()
    ax.bar(df["اسم المعلمة"], df["عدد النواقص"])
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # توليد تقرير PDF لكل معلمة
    st.subheader("📄 توليد تقرير فردي")

    teacher_list = df["اسم المعلمة"].unique()
    selected_teacher = st.selectbox("اختاري المعلمة", teacher_list)

    if st.button("إنشاء تقرير PDF"):

        teacher_data = df[df["اسم المعلمة"] == selected_teacher].iloc[0]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt=f"تقرير الأداء - {selected_teacher}", ln=True)

        pdf.cell(200, 10, txt=f"عدد النواقص: {teacher_data['عدد النواقص']}", ln=True)
        pdf.cell(200, 10, txt=f"التقييم العام: {teacher_data['التقييم العام']}", ln=True)

        file_name = f"{selected_teacher}_report.pdf"
        pdf.output(file_name)

        with open(file_name, "rb") as file:
            st.download_button(
                label="تحميل التقرير",
                data=file,
                file_name=file_name,
                mime="application/pdf"
            )
