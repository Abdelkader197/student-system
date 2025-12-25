# --- [ منطقة الطالب - Student ] ---
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
            
            # --- هذا هو السطر الذي أعدت فيه الرقم القومي للظهور في الأعلى ---
            st.markdown(f"<div class='id-header'>الرقم القومي: {sid}</div>", unsafe_allow_html=True)

            if page == "بيانات الطالب":
                # يمكنك إظهار اسم الطالب أيضاً تحت الرقم القومي
                st.subheader(f"مرحباً بك: {data.get('أسم الطالب', '')}")
                
                def render_smart_field(label, key):
                    val = data.get(key)
                    is_empty = not val or str(val).lower() in ["nan", "none", "", "null"]
                    if not is_empty:
                        st.markdown(f"<div class='data-card'><div class='field-key'>{label}</div><div class='field-val'>{val}</div></div>", unsafe_allow_html=True)
                    else:
                        st.warning(f"⚠️ بيان ناقص: {label}")
                        new_input = st.text_input(f"يرجى إدخال {label}", key=f"in_{key}")
                        if st.button(f"حفظ {label}", key=f"btn_{key}"):
                            if new_input:
                                doc_ref.update({key: new_input})
                                st.success(f"✅ تم حفظ {label}")
                                st.rerun()

                st.markdown("<div class='section-header'>👤 البيانات الشخصية</div>", unsafe_allow_html=True)
                render_smart_field("أسم الطالب", "أسم الطالب")
                render_smart_field("تاريخ الميلاد", "تاريخ الميلاد")
                render_smart_field("رقم التليفون", "رقم التليفون")
                render_smart_field("العنوان", "العنوان")

                st.markdown("<div class='section-header'>🎓 البيانات الأكاديمية</div>", unsafe_allow_html=True)
                render_smart_field("أسم البرنامج", "أسم البرنامج")
                render_smart_field("الطبيعة", "الطبيعة")
                render_smart_field("المستوى", "المستوى")
                render_smart_field("الاميل الجامعى", "الاميل الجامعى")
            
            # بقية الصفحات (المصروفات والشكاوى) تظل كما هي في الكود السابق...
