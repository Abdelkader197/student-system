import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# منع تكرار الاتصال بالقاعدة
if not firebase_admin._apps:
    try:
        # قراءة البيانات من Secrets
        fb_dict = dict(st.secrets["firebase_secrets"])
        # السطر ده هو اللي بيحل مشكلة InvalidPadding اللي ظهرتلك
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        
        cred = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"خطأ في الاتصال: {e}")

db = firestore.client()

# --- واجهة التطبيق ---
st.set_page_config(page_title="منظومة الطالب الذكية", layout="centered")
st.title("🎓 منظومة الاستعلام عن النتائج")

uid = st.text_input("أدخل الرقم القومي للطالب")

if st.button("عرض النتيجة"):
    if uid:
        try:
            # البحث في مجموعة students
            doc = db.collection('students').document(uid).get()
            if doc.exists:
                res = doc.to_dict()
                st.success(f"تم العثور على البيانات: {res.get('name')}")
                # عرض البيانات في جدول شيك
                st.table({
                    "المادة": ["اللغة العربية", "الرياضيات", "اللغة الإنجليزية"],
                    "الدرجة": [res.get('arabic', 0), res.get('math', 0), res.get('english', 0)]
                })
            else:
                st.error("عذراً، هذا الرقم القومي غير مسجل لدينا.")
        except Exception as e:
            st.error(f"حدث خطأ فني: {e}")
    else:
        st.warning("من فضلك أدخل الرقم القومي أولاً.")
