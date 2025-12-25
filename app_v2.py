import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import datetime

# --- 1. الاتصال بـ Firebase (من خلال Secrets) ---
if not firebase_admin._apps:
    try:
        firebase_dict = dict(st.secrets["firebase_secrets"])
        if "private_key" in firebase_dict:
            firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(firebase_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"حدث خطأ في الاتصال بقاعدة البيانات: {e}")

db = firestore.client()

# --- 2. التنسيق الجمالي ---
st.set_page_config(page_title="منظومة الطالب الذكية", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #f8fafc; }
    .id-header { background: #1E3A8A; color: white; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 25px; font-weight: bold; font-size: 1.2em; }
    .section-header { background: linear-gradient(90deg, #3B82F6, #1E3A8A); color: white; padding: 12px 20px; border-radius: 10px; margin: 20px 0 10px 0; font-size: 1.1em; font-weight: bold; }
    .data-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 8px; border-right: 6px solid #3B82F6; }
    .field-key { color: #64748b; font-size: 0.85em; margin-bottom: 2px; }
    .field-val { color: #1e293b; font-size: 1.1em; font-weight: bold; }
    .stButton>button { background-color: #16a34a !important; color: white !important; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- 3. بوابة الدخول ---
if not st.session_state.logged_in:
    st.markdown("<div class='id-header'>🔒 بوابة تسجيل الدخول الموحدة</div>", unsafe_allow_html=True)
    uid = st.text_input("أدخل الرقم القومي الخاص بك").strip()
    if st.button("دخول للنظام"):
        if uid == "000": 
            st.session_state.logged_in = True
            st.session_state.student_id = "admin"
            st.rerun()
        elif uid:
            doc = db.collection('students').document(uid).get()
            if doc.exists:
                st.session_state.logged_in = True
                st.session_state.student_id = uid
                st.rerun()
            else:
                st.error("⚠️ الرقم القومي غير مسجل")

# --- 4. لوحة التحكم ---
else:
    sid = st.session_state.student_id
    doc_ref = db.collection('students').document(sid)
    
    if sid == "admin":
        with st.sidebar:
            st.title("🛠️ إدارة النظام")
            admin_page = st.radio("القائمة:", ["عرض الشكاوى", "تحديث بيانات الطلاب"])
            if st.button("تسجيل الخروج"):
                st.session_state.logged_in = False
                st.rerun()
        
        if admin_page == "عرض الشكاوى":
            st.markdown("<div class='id-header'>صندوق الشكاوى الواردة</div>", unsafe_allow_html=True)
            complaints = db.collection('complaints').order_by('date', direction=firestore.Query.DESCENDING).get()
            if complaints:
                for comp in complaints:
                    c_data = comp.to_dict()
                    with st.expander(f"✉️ {c_data.get('student_name', 'طالب')} - {c_data.get('subject', 'بدون موضوع')}"):
                        st.write(f"**التفاصيل:** {c_data.get('details')}")
                        st.write(f"**التاريخ:** {c_data.get('date')}")
                        if st.button("حذف الشكوى", key=comp.id):
                            db.collection('complaints').document(comp.id).delete()
                            st.rerun()
            else: st.info("لا توجد شكاوى حالياً.")
        
        elif admin_page == "تحديث بيانات الطلاب":
            st.markdown("<div class='id-header'>رفع وتحديث بيانات الطلاب</div>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("اختر ملف الإكسيل", type=['xlsx'])
            if uploaded_file:
                df = pd.read_excel(uploaded_file)
                if st.button("🚀 رفع البيانات"):
                    for _, row in df.iterrows():
                        s_data = {str(k).strip(): v for k, v in row.to_dict().items() if pd.notnull(v)}
                        n_id = str(s_data.get('الرقم القومي')).strip()
                        if n_id: db.collection('students').document(n_id).set(s_data, merge=True)
                    st.success("✅ تم الرفع بنجاح")

    else:
        with st.sidebar:
            st.title("📌 القائمة")
            page = st.radio("اختر الصفحة:", ["بيانات الطالب", "مصروفات البرنامج", "ارسال شكوى"])
            if st.button("خروج"):
                st.session_state.logged_in = False
                st.rerun()

        data_doc = doc_ref.get()
        if data_doc.exists:
            data = data_doc.to_dict()
            st.markdown(f"<div class='id-header'>الرقم القومي: {sid}</div>", unsafe_allow_html=True)

            if page == "بيانات الطالب":
                st.subheader(f"مرحباً بك: {data.get('أسم الطالب', '')}")
                
                def render_field(label, key):
                    val = data.get(key)
                    if val and str(val).lower() not in ["nan", "none", "", "null"]:
                        st.markdown(f"<div class='data-card'><div class='field-key'>{label}</div><div class='field-val'>{val}</div></div>", unsafe_allow_html=True)
                    else:
                        st.warning(f"⚠️ بيان ناقص: {label}")
                        new_in = st.text_input(f"أدخل {label}", key=f"i_{key}")
                        if st.button(f"حفظ {label}", key=f"b_{key}"):
                            if new_in:
                                doc_ref.update({key: new_in})
                                st.rerun()

                st.markdown("<div class='section-header'>👤 البيانات الشخصية</div>", unsafe_allow_html=True)
                render_field("أسم الطالب", "أسم الطالب")
                render_field("رقم التليفون", "رقم التليفون")
                render_field("العنوان", "العنوان")

                st.markdown("<div class='section-header'>🎓 البيانات الأكاديمية</div>", unsafe_allow_html=True)
                render_field("أسم البرنامج", "أسم البرنامج")
                render_field("المستوى", "المستوى")

            elif page == "مصروفات البرنامج":
                st.markdown("<div class='section-header'>💰 الموقف المالي</div>", unsafe_allow_html=True)
                must_pay = data.get('المصروفات المستحقة', '0')
                st.warning(f"### المبلغ المطلوب سداده: {must_pay} ج.م")
                
                payments = data.get('payments', [])
                if payments: st.table(pd.DataFrame(payments))
                else: st.info("لا توجد سجلات سداد.")

            elif page == "ارسال شكوى":
                st.markdown("<div class='section-header'>📧 قسم الشكاوى</div>", unsafe_allow_html=True)
                with st.form("c_f"):
                    sub = st.text_input("الموضوع")
                    det = st.text_area("التفاصيل")
                    if st.form_submit_button("إرسال"):
                        if sub and det:
                            db.collection('complaints').add({
                                'student_id': sid, 'student_name': data.get('أسم الطالب'),
                                'subject': sub, 'details': det, 'date': datetime.datetime.now()
                            })
                            st.success("✅ تم الإرسال")
