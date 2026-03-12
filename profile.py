import streamlit as st
from db import get_connection

def profile_page(user_email):
    st.title("👤 My Profile")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, email, phone, age FROM users WHERE email=%s", (user_email,))
    user = cursor.fetchone()

    st.subheader("🔎 Profile Information")
    st.write(f"**Name:** {user[0]}")
    st.write(f"**Email:** {user[1]}")
    st.write(f"**Phone:** {user[2]}")
    st.write(f"**Age:** {user[3]}")

    st.divider()

    st.subheader("🔐 Change Password")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Update Password"):
        if new_pass.strip() != "":
            cursor.execute("UPDATE users SET password=%s WHERE email=%s", (new_pass, user_email))
            conn.commit()
            st.success("✅ Password updated successfully!")
        else:
            st.warning("Password cannot be empty.")

    conn.close()
