# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# ------------------------
# واجهة التطبيق
st.set_page_config(page_title="🎓 لوحة متابعة أداء المعلمات", layout="wide", page_icon="📊")
st.title("🎓 لوحة متابعة أداء المعلمات – الإدارة التعليمية")

# رفع شعار المدرسة
st.image("شعار.png", width=120)

# رفع ملف Excel
uploaded_file = st.file_uploader("📂 ارفعي ملف Excel (البيانات القادمة من Google Form)", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # ===============================
    # تنظيف وتحضير البيانات
    df.fillna("", inplace=True)
    actions = ["هل تم رفع التحضير؟", "هل تم رفع محاضرات الفيديو؟",
               "هل تم رفع الواجبات؟", "هل تم رفع الاختبارات؟",
               "هل تم رفع المقاطع الإثرائية؟", "هل تم رفع تسجيل الحصص"]

    # حالة كل خانة (مكتمل/ناقص)
    for col in actions:
        status_col = f"حالة {col.split(' ')[-1]}"
        df[status_col] = df[col].apply(lambda x: "✅ مكتمل" if x.strip().lower() == "نعم" else "❌ ناقص")

    # عدد النواقص
    df["عدد النواقص"] = df[[f"حالة {col.split(' ')[-1]}" for col in actions]].apply(lambda row: sum(1 if val=="❌ ناقص" else 0 for val in row), axis=1)

    # التقييم العام
    def evaluate(row):
        if row["عدد النواقص"] == 0:
            return "🌟 ممتاز"
        elif row["عدد النواقص"] <= 2:
            return "🙂 جيد"
        else:
            return "⚠️ يحتاج متابعة"
    df["التقييم العام"] = df.apply(evaluate, axis=1)

    # ===============================
    # المؤشرات العامة
    st.subheader("📊 المؤشرات العامة")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👩‍🏫 عدد المعلمات", df.shape[0])
    col2.metric("❌ عدد النواقص الكلي", df["عدد النواقص"].sum())
    col3.metric("🌟 المكتملات", (df["التقييم العام"]=="🌟 ممتاز").sum())
    col4.metric("⚠️ يحتاج متابعة", (df["التقييم العام"]=="⚠️ يحتاج متابعة").sum())

    # ===============================
    # جدول المتابعة التفصيلي
    st.subheader("📋 جدول المتابعة التفصيلي")
    st.dataframe(df)

    # ===============================
    # رسم توزيع النواقص لكل معلمة
    st.subheader("📈 توزيع النواقص لكل معلمة")
    fig = px.bar(df, x="اسم المعلمة", y="عدد النواقص", text="عدد النواقص", color="عدد النواقص",
                 color_continuous_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)

    # ===============================
    # رسم نسبة التقييم العام
    st.subheader("🥧 نسبة التقييم العام")
    fig2 = px.pie(df, names="التقييم العام", title="نسبة التقييم العام للمعلمات", color="التقييم العام",
                  color_discrete_map={"🌟 ممتاز":"blue", "🙂 جيد":"lightblue", "⚠️ يحتاج متابعة":"red"})
    st.plotly_chart(fig2, use_container_width=True)

    # ===============================
    # إرسال التقييمات بالبريد الإلكتروني
    st.subheader("📧 إرسال التقييمات بالبريد الإلكتروني")
    st.info("ملاحظة: ضع بيانات بريدك وApp Password الخاصة بـ Gmail قبل الإرسال")
    sender_email = st.text_input("📧 بريدك الإلكتروني (Gmail)")
    app_password = st.text_input("🔑 App Password", type="password")

    if st.button("إرسال التقييمات"):
        if sender_email and app_password:
            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, app_password)

                for idx, row in df.iterrows():
                    msg = MIMEMultipart()
                    msg["From"] = sender_email
                    msg["To"] = row["البريد الإلكتروني للمعلمة"]
                    msg["Subject"] = "تقييم أداءك الأسبوعي"

                    # نص الرسالة
                    body = f"""
                    مرحبًا {row['اسم المعلمة']}،

                    هذا تقييمك للأسبوع {row['"الأسبوع\nالأسبوع السادس"']}:

                    عدد النواقص: {row['عدد النواقص']}
                    التقييم العام: {row['التقييم العام']}
                    """

                    msg.attach(MIMEText(body, "plain"))

                    # إضافة شعار كصورة في البريد
                    with open("شعار.png", "rb") as img_file:
                        img = MIMEImage(img_file.read())
                        img.add_header("Content-ID", "<logo>")
                        img.add_header("Content-Disposition", "inline", filename="شعار.png")
                        msg.attach(img)

                    server.send_message(msg)

                server.quit()
                st.success("✅ تم إرسال جميع التقييمات بنجاح!")

            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء الإرسال: {e}")
        else:
            st.warning("⚠️ الرجاء إدخال بريدك وApp Password قبل الإرسال.")
