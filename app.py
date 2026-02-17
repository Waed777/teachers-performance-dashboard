import streamlit as st
import pandas as pd

st.set_page_config(page_title="لوحة متابعة المعلمات", layout="wide")

st.title("🎓 لوحة متابعة أداء المعلمات – الإدارة التعليمية")

uploaded_file = st.file_uploader(
    "📂 ارفعي ملف Excel (البيانات القادمة من Google Form)",
    type=["xlsx"]
)

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)

        st.success("✅ تم تحميل الملف بنجاح")

        # ===============================
        # تنظيف أسماء الأعمدة (مهم جدا)
        # ===============================
        df.columns = df.columns.str.strip()

        st.subheader("📋 معاينة البيانات")
        st.dataframe(df, use_container_width=True)

        # ===============================
        # تحديد أعمدة نعم / لا تلقائياً
        # ===============================
        yes_no_cols = []
        for col in df.columns:
            sample_values = df[col].astype(str).unique()
            if any(v.strip() in ["نعم", "لا"] for v in sample_values):
                yes_no_cols.append(col)

        st.info(f"🔍 تم اكتشاف {len(yes_no_cols)} أعمدة نعم/لا")

        # ===============================
        # حساب عدد النواقص
        # ===============================
        def count_missing(row):
            return sum(
                1 for c in yes_no_cols
                if str(row[c]).strip() == "لا"
            )

        df["عدد النواقص"] = df.apply(count_missing, axis=1)

        # ===============================
        # التقييم العام
        # ===============================
        def evaluate(n):
            if n == 0:
                return "🌟 ممتاز"
            elif n <= 2:
                return "🙂 جيد"
            else:
                return "⚠️ يحتاج متابعة"

        df["التقييم العام"] = df["عدد النواقص"].apply(evaluate)

        # ===============================
        # المؤشرات
        # ===============================
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("👩‍🏫 عدد المعلمات", len(df))
        col2.metric("❌ عدد النواقص الكلي", int(df["عدد النواقص"].sum()))
        col3.metric("🌟 المكتملات", int((df["التقييم العام"] == "🌟 ممتاز").sum()))
        col4.metric("⚠️ يحتاج متابعة", int((df["التقييم العام"] == "⚠️ يحتاج متابعة").sum()))

        st.subheader("📊 جدول المتابعة النهائي")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error("❌ حصل خطأ")
        st.exception(e)
else:
    st.info("⬆️ في انتظار رفع الملف")
