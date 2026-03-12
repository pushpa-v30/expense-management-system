import streamlit as st
from db import get_connection

# ---------- REGISTER NEW USER ----------
def register(email, password, name, phone, age):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        return False  # User already exists

    cursor.execute("""
        INSERT INTO users (email, password, name, phone, age)
        VALUES (%s, %s, %s, %s, %s)
    """, (email, password, name, phone, age))
    conn.commit()
    conn.close()
    return True

# ---------- LOGIN USER ----------
def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user
