# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===============================
# إعداد الصفحة
st.set_page_config(
    page_title="لوحة متابعة أداء المعلمات",
    layout="wide"
)

st.title("🎓 لوحة متابعة أداء المعلمات – الإدارة التعليمية")

# ===============================
# رفع الملف
uploaded_file = st.file_uploader(
    "📂 ارفعي ملف Excel (البيانات القادمة من Google Form)",
    type=["xlsx"]
)

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.fillna("", inplace=True)

    # ===============================
    # حساب عدد النواقص
    yes_no_cols = [
        "هل تم رفع التحضير؟",
        "هل تم رفع الواجبات؟",
        "هل تم رفع محاضرات الفيديوم",
        "هل تم رفع تسجيل الحصص",
        "هل تم رفع المقاطع الاثرائية"
    ]

    def count_missing(row):
        return sum(1 for c in yes_no_cols if str(row[c]).strip() != "نعم")

    df["عدد النواقص"] = df.apply(count_missing, axis=1)

    # ===============================
    # التقييم العام
    def evaluate(m):
        if m == 0:
            return "🌟 ممتاز"
        elif m <= 2:
            return "🙂 جيد"
        else:
            return "⚠️ يحتاج متابعة"

    df["التقييم العام"] = df["عدد النواقص"].apply(evaluate)

    # ===============================
    # مؤشرات عامة
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👩‍🏫 عدد المعلمات", len(df))
    c2.metric("❌ عدد النواقص الكلي", int(df["عدد النواقص"].sum()))
    c3.metric("🌟 المكتملات", int((df["التقييم العام"] == "🌟 ممتاز").sum()))
    c4.metric("⚠️ يحتاج متابعة", int((df["التقييم العام"] == "⚠️ يحتاج متابعة").sum()))

    # ===============================
    # جدول
    st.subheader("📋 جدول المتابعة التفصيلي")
    st.dataframe(df, use_container_width=True)

    # ===============================
    # رسم توزيع النواقص
    st.subheader("📈 توزيع النواقص لكل معلمة")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(df["اسم المعلمة"].astype(str), df["عدد النواقص"])
    ax.set_ylabel("عدد النواقص")
    ax.set_xlabel("اسم المعلمة")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

    # ===============================
    # رسم التقييم العام
    st.subheader("🥧 نسبة التقييم العام")
    eval_counts = df["التقييم العام"].value_counts()
    fig2, ax2 = plt.subplots()
    ax2.pie(
        eval_counts.values,
        labels=eval_counts.index,
        autopct="%1.0f%%",
        startangle=90
    )
    ax2.axis("equal")
    st.pyplot(fig2)

    # ===============================
    # إرسال الإيميلات (اختياري)
    st.subheader("📧 إرسال التقييمات بالبريد الإلكتروني")

    sender = st.text_input("📧 بريد الإرسال (Gmail)")
    password = st.text_input("🔑 App Password", type="password")

    if st.button("إرسال التقييمات"):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender, password)

            for _, row in df.iterrows():
                msg = MIMEMultipart()
                msg["From"] = sender
                msg["To"] = row["البريد الإلكتروني للمعلمة"]
                msg["Subject"] = "تقييم الأداء التعليمي"

                body = f"""
مرحبًا {row['اسم المعلمة']}

عدد النواقص: {row['عدد النواقص']}
التقييم العام: {row['التقييم العام']}

مع خالص التقدير 🌷
"""
                msg.attach(MIMEText(body, "plain"))
                server.send_message(msg)

            server.quit()
            st.success("✅ تم إرسال جميع التقييمات بنجاح")

        except Exception as e:
            st.error("❌ فشل إرسال البريد – تأكدي من App Password")

