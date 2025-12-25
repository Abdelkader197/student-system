import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# الاتصال بقاعدة البيانات
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase_secrets"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"خطأ في الاتصال: {e}")

db = firestore.client()

st.set_page_config(page_title="منظومة إدارة الطالب", layout="centered")
st.title("📂 نظام بيانات الطالب والمصروفات")

uid = st.text_input("أدخل الرقم القومي للطالب")

if st.button("استعلام"):
    if uid:
        try:
            doc = db.collection('students').document(uid).get()
            if doc.exists:
                res = doc.to_dict()
                st.success("✅ تم العثور على سجل الطالب")
                
                # قسم البيانات الشخصية
                st.subheader("👤 البيانات الشخصية")
                st.write(f"**الاسم:** {res.get('الاسم', 'غير مسجل')}")
                st.write(f"**العنوان:** {res.get('العنوان', 'غير مسجل')}")
                st.write(f"**المرحلة الدراسية:** {res.get('المرحلة', 'غير مسجل')}")
                
                st.divider()
                
                # قسم المصروفات والشكاوى
                col1, col2 = st.columns(2)
                with col1:
                    st.info("💰 المصروفات الدراسية")
                    st.write(f"**إجمالي المطلوب:** {res.get('المصروفات_الكلية', 0)}")
                    st.write(f"**المبلغ المسدد:** {res.get('المسدد', 0)}")
                    st.write(f"**المتبقي:** {res.get('المتبقي', 0)}")
                
                with col2:
                    st.warning("📝 حالة الشكاوى")
                    st.write(f"**آخر شكوى:** {res.get('الشكاوى', 'لا يوجد شكاوى حالية')}")
                    st.write(f"**حالة الرد:** {res.get('الرد_على_الشكوى', 'قيد الانتظار')}")
                    
            else:
                st.error("❌ الرقم القومي غير مسجل في المنظومة")
        except Exception as e:
            st.error(f"حدث خطأ في جلب البيانات: {e}")
