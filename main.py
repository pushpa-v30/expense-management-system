import streamlit as st
from auth import login_user,register
from transactions import transaction_page
from reports import reports_page
from db import get_income_expense_summary
from chatbot import ai_chatbot_page
from profile import profile_page



# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Expense & Budget Manager",
    page_icon="💰",
    layout="wide"
)

# -------------------- SESSION STATE --------------------
if 'user' not in st.session_state:
    st.session_state['user'] = None

# -------------------- LOGIN / REGISTER PAGE --------------------
if st.session_state['user'] is None:
    st.title("💰 Expense & Budget Management System")

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])


    # ---------- LOGIN ----------
    with tab1:
        st.subheader("Welcome back! Please log in.")

        login_email = st.text_input("📧 Email", key="login_email_field").strip()
        login_password = st.text_input("🔒 Password", type="password", key="login_pass_field").strip()

        if st.button("Login", key="login_btn"):
            user = login_user(login_email, login_password)

            if user:
                st.session_state['user'] = login_email
                st.success(f"✅ Welcome back, {login_email.split('@')[0].capitalize()}!")
                st.rerun()
            else:
                st.error("❌ Invalid email or password. Please try again.")


    # ---------- REGISTER ----------
    with tab2:
        st.subheader("Create a New Account")

        reg_name = st.text_input("👤 Full Name", key="reg_name_new").strip()
        reg_phone = st.text_input("📱 Phone Number", key="reg_phone_new").strip()
        reg_email = st.text_input("📧 Email", key="reg_email_new").strip()
        reg_password = st.text_input("🔒 Password", type="password", key="reg_pass_new").strip()
        reg_age = st.number_input("🎂 Age", min_value=1, max_value=120, step=1, key="reg_age_new")

        st.write("DEBUG:", reg_name, reg_phone, reg_email, reg_password, reg_age)

        if st.button("Register", key="register_btn"):
            if reg_name and reg_phone and reg_email and reg_password:
                success = register(reg_email, reg_password, reg_name, reg_phone, reg_age)

                if success:
                    st.success("✅ Account created successfully! You can now log in.")
                else:
                    st.error("❌ User already exists.")
            else:
                st.warning("⚠️ Please fill all fields.")



# -------------------- MAIN APP INTERFACE --------------------
else:
    st.sidebar.title("Dashboard")

    # Fetch current balance
    total_income, total_expense, balance = get_income_expense_summary(st.session_state['user'])
    st.sidebar.markdown(f"### 💰 Current Balance: ₹{balance:.2f}")

    page = st.sidebar.radio("Go to:", ["Profile","Transactions", "Reports","AI Chatbot"])
    st.sidebar.write("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state['user'] = None
        st.rerun()

    if page == "Transactions":
        transaction_page()
    elif page == "Reports":
        reports_page()
    elif page == "AI Chatbot":
        ai_chatbot_page()
    elif page == "Profile":
        profile_page(st.session_state['user'])

