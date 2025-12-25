import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase_secrets"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"خطأ اتصال: {e}")

db = firestore.client()

st.title("🔍 كاشف بيانات الطالب")
uid = st.text_input("أدخل الرقم القومي لرؤية البيانات المخزنة")

if uid:
    doc = db.collection('students').document(uid).get()
    if doc.exists:
        res = doc.to_dict()
        st.success("✅ تم الاتصال والوصول للبيانات!")
        
        st.subheader("البيانات الخام من Firebase:")
        # هذا السطر سيظهر لك كل الأسماء الحقيقية للخانات عندك
        st.write(res) 
        
        st.divider()
        st.info("انظر للأعلى، ستجد الأسماء الحقيقية للحقول. أخبرني بها لأقوم بضبط الكود عليها فوراً.")
    else:
        st.error("الرقم القومي هذا غير موجود في Firebase")
