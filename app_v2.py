import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# 1. الاتصال بقاعدة البيانات
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase_secrets"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"خطأ في الاتصال: {e}")

db = firestore.client()

# إعداد واجهة الصفحة
st.set_page_config(page_title="منظومة إدارة الطالب", layout="wide")
st.title("🎓 ملف الطالب المتكامل")

uid = st.text_input("برجاء إدخال الرقم القومي للاستعلام")

if st.button("عرض الملف الكامل"):
    if uid:
        try:
            doc = db.collection('students').document(uid).get()
            if doc.exists:
                res = doc.to_dict()
                st.success(f"✅ تم تحميل بيانات الطالب: {res.get('الاسم', '')}")

                # --- الجزء الأول: البيانات الشخصية والأكاديمية ---
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 👤 البيانات الشخصية")
                    st.write(f"**الاسم:** {res.get('الاسم', '---')}")
                    st.write(f"**العنوان:** {res.get('العنوان', '---')}")
                    st.write(f"**رقم الهاتف:** {res.get('الهاتف', '---')}")

                with col2:
                    st.markdown("### 📚 البيانات الأكاديمية")
                    st.write(f"**المرحلة:** {res.get('المرحلة', '---')}")
                    st.write(f"**الصف:** {res.get('الصف', '---')}")
                    st.write(f"**حالة القيد:** {res.get('الحالة', '---')}")

                st.divider()

                # --- الجزء الثاني: المصروفات الدراسية ---
                st.markdown("### 💰 الشؤون المالية")
                st.info(f"**المصروفات المستحقة للعام الحالي:** {res.get('المصروفات_المستحقة', 0)} جنيه")

                # جدول سجل السداد السابقة
                st.markdown("#### 📑 سجل عمليات السداد")
                payments = res.get('سجل_السداد', []) 
                if payments:
                    st.table(payments) # سيعرض الجدول بشكل تلقائي إذا كانت البيانات قائمة
                else:
                    st.warning("لا توجد عمليات سداد مسجلة حالياً.")

                st.divider()

                # --- الجزء الثالث: الشكاوى ---
                st.markdown("### 📝 قسم الشكاوى")
                st.write(f"**آخر شكوى:** {res.get('الشكاوى', 'لا يوجد')}")
                st.write(f"**رد الإدارة:** {res.get('الرد', '---')}")

            else:
                st.error("❌ الرقم القومي غير مسجل.")
        except Exception as e:
            st.error(f"حدث خطأ أثناء جلب البيانات: {e}")
