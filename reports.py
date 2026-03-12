import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from db import (
    get_income_expense_summary,
    get_expense_data,
    get_monthly_summary,
    get_yearly_summary
)

def reports_page():
    st.header("📈 Financial Reports")
    
    user = st.session_state['user']

    # ----------- OVERALL SUMMARY -----------
    total_income, total_expense, balance = get_income_expense_summary(user)
    st.write(f"### 💰 Current Balance: ₹{balance:.2f}")
    st.write(f"#### 📥 Total Income: ₹{total_income:.2f}")
    st.write(f"#### 📤 Total Expenses: ₹{total_expense:.2f}")

    st.write("---")
    
    # Load all expenses
    df = get_expense_data(user)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])

    # ----------- MONTHLY REPORT -----------
    st.subheader("📅 Monthly Expense Report")
    colM1, colM2 = st.columns(2)

    month = colM1.selectbox(
        "Select Month", 
        list(range(1, 13)), 
        format_func=lambda x: datetime(2000, x, 1).strftime("%B")
    )

    year_m = colM2.number_input(
        "Select Year", 
        min_value=2000, 
        max_value=2100, 
        value=datetime.now().year
    )

    if not df.empty:
        df_month = df[(df['date'].dt.month == month) & (df['date'].dt.year == year_m)]

        if not df_month.empty:
            st.write("### 🧾 Expense Records for Selected Month")
            # Show only columns that exist in dataframe
            columns_to_show = [col for col in ["date", "category", "amount", "description"] if col in df_month.columns]
            st.dataframe(df_month[columns_to_show])


            m_income, m_expense, m_balance = get_monthly_summary(user, month, year_m)
            st.write(f"**• Income:** ₹{m_income:.2f}")
            st.write(f"**• Expense:** ₹{m_expense:.2f}")
            st.write(f"**• Balance:** ₹{m_balance:.2f}")

            # Pie Chart
            st.write("### 📊 Monthly Expense Category Breakdown")
            category_month = df_month.groupby("category")["amount"].sum()
            fig_m, ax_m = plt.subplots(figsize=(3,3))
            ax_m.pie(category_month, labels=category_month.index, autopct="%1.1f%%", startangle=90)
            ax_m.axis("equal")
            st.pyplot(fig_m)
        else:
            st.info("⚠️ No expenses found for the selected month.")

    st.write("---")

    # ----------- YEARLY REPORT -----------
    st.subheader("📆 Yearly Expense Report")
    year_y = st.number_input("Choose Year", min_value=2000, max_value=2100, value=datetime.now().year)

    if not df.empty:
        df_year = df[df['date'].dt.year == year_y]

        if not df_year.empty:
            st.write("### 🧾 Expense Records for Selected Year")
            columns_to_show = [col for col in ["date", "category", "amount", "description"] if col in df_year.columns]
            st.dataframe(df_year[columns_to_show])


            y_income, y_expense, y_balance = get_yearly_summary(user, year_y)
            st.write(f"**• Total Income:** ₹{y_income:.2f}")
            st.write(f"**• Total Expenses:** ₹{y_expense:.2f}")
            st.write(f"**• Yearly Balance:** ₹{y_balance:.2f}")

            # Pie Chart
            st.write("### 📊 Yearly Expense Category Breakdown")
            category_year = df_year.groupby("category")["amount"].sum()
            fig_y, ax_y = plt.subplots(figsize=(3,3))
            ax_y.pie(category_year, labels=category_year.index, autopct="%1.1f%%", startangle=90)
            ax_y.axis("equal")
            st.pyplot(fig_y)
        else:
            st.info("⚠️ No expenses found for the selected year.")

    st.write("---")

    # ----------- OVERALL CHARTS -----------
    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💸 Overall Expense Distribution")
            category_summary = df.groupby("category")["amount"].sum()
            fig1, ax1 = plt.subplots(figsize=(3,3))
            ax1.pie(category_summary, labels=category_summary.index, autopct="%1.1f%%", startangle=90)
            ax1.axis("equal")
            st.pyplot(fig1)

        with col2:
            st.subheader("📊 Income vs Expense Overview")
            data = {"Type": ["Income", "Expense"], "Amount": [total_income, total_expense]}
            df_bar = pd.DataFrame(data)
            fig2, ax2 = plt.subplots(figsize=(3,3))
            ax2.bar(df_bar["Type"], df_bar["Amount"])
            ax2.set_ylabel("Amount (₹)")
            st.pyplot(fig2)
