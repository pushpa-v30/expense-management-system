import streamlit as st
import mysql.connector
from db import get_connection

# -------------------- BUDGET TRACKER PAGE --------------------
def budget_page(user_email):
    st.title("🎯 Budget Tracker & Expense Alert")

    db = get_connection()
    cursor = db.cursor()

    # -------------------- Fetch income & expenses --------------------
    cursor.execute("SELECT SUM(amount) FROM income WHERE email=%s", (user_email,))
    income = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT SUM(amount) FROM expenses WHERE email=%s", (user_email,))
    expenses = cursor.fetchone()[0] or 0.0

    # -------------------- Fetch margin limit from users table --------------------
    cursor.execute("SELECT margin_limit FROM users WHERE email=%s", (user_email,))
    result = cursor.fetchone()
    current_limit = result[0] if result else 0.0

    # -------------------- Display summary --------------------
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💵 Total Income", f"₹{income:,.2f}")
    with col2:
        st.metric("💸 Total Expenses", f"₹{expenses:,.2f}")
    with col3:
        st.metric("🎯 Current Limit", f"₹{current_limit:,.2f}")

    st.divider()

    # -------------------- Set or update margin limit --------------------
    st.subheader("Set or Update Your Expense Limit")
    new_limit = st.number_input("Enter your monthly expense limit (₹):", min_value=0.0, step=500.0, value=current_limit)

    if st.button("💾 Save Limit"):
        cursor.execute("UPDATE users SET margin_limit=%s WHERE email=%s", (new_limit, user_email))
        db.commit()
        st.success(f"✅ Limit set to ₹{new_limit:,.2f}")
        current_limit = new_limit

    st.divider()

    # -------------------- Show Alerts --------------------
    st.subheader("📊 Budget Status")

    if current_limit == 0:
        st.info("ℹ️ Please set a limit to start tracking.")
    elif expenses > current_limit:
        st.error("🚨 You’ve exceeded your expense limit!")
    elif expenses > 0.4 * current_limit:
        st.warning("⚠️ You’re close to your limit. Control spending!")
    else:
        st.success("✅ You’re within your budget. Keep saving!")

    # -------------------- Remaining budget --------------------
    remaining = current_limit - expenses
    if remaining >= 0:
        st.write(f"💡 Remaining budget: ₹{remaining:,.2f}")
    else:
        st.write(f"🔴 Overspent by ₹{abs(remaining):,.2f}")

    db.close()
