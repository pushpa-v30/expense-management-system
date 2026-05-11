import streamlit as st
import pandas as pd
from db import (
    add_expense, add_income, get_expenses, get_incomes,
    delete_expense, delete_income, get_income_expense_summary
)

def transaction_page():
    st.header("💵 Manage Your Transactions")

     # Fetch user income/expense summary
    total_income, total_expense, balance = get_income_expense_summary(st.session_state['user'])
    total_income = float(total_income or 0)
    total_expense = float(total_expense or 0)
    balance = float(balance or 0)

    # Define margin limit (80% of income)
    margin_limit = 0.4 * total_income if total_income > 0 else 0

    # ---------------- MARGIN ALERT ----------------
    if total_income == 0:
        st.info("ℹ️ Add an income first to set your expense margin limit (40% of income).")
    elif total_expense >= margin_limit:
        st.error(f"⚠️ Alert: Your expenses ₹{total_expense:.2f} have **exceeded the 80% margin limit** of ₹{margin_limit:.2f}!")
    elif total_expense >= 0.4 * total_income:
        st.warning(f"⚠️ Caution: You've spent around {((total_expense / total_income) * 100):.1f}% of your income. "
                   f"You're nearing the 80% limit (₹{margin_limit:.2f}).")
    else:
        st.success(f"✅ You're within your spending limit. Current expenses: ₹{total_expense:.2f} / ₹{margin_limit:.2f}.")

    st.write("---")



    tab1, tab2 = st.tabs(["➕ Add Expense", "➕ Add Income"])

    # ---------- ADD EXPENSE ----------
    with tab1:
        st.subheader("Add New Expense")
        title = st.text_input("Title")
        amount = st.number_input("Amount", min_value=0.0)
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Other"])
        description = st.text_area("Description")

        # Show current financial summary
        st.info(f"💰 Total Income: ₹{total_income:.2f}")
        st.info(f"📤 Current Expenses: ₹{total_expense:.2f}")
        st.info(f"🚨 Expense Limit (40% of Income): ₹{margin_limit:.2f}")

        if st.button("Add Expense"):
            if title and amount:
                new_total = total_expense + amount
                if new_total > margin_limit:
                    st.error(
                        f"⚠️ Cannot add this expense! "
                        f"Your total expenses (₹{new_total:.2f}) exceed 40% of your income (₹{margin_limit:.2f})."
                    )
                else:
                    add_expense(st.session_state['user'], title, date, amount, category, description)
                    st.success("Expense added successfully!")
                    st.rerun()
            else:
                st.error("Please fill all required fields.")

    # ---------- ADD INCOME ----------
    with tab2:
        st.subheader("Add New Income")
        title = st.text_input("Source Title", key="income_title")
        amount = st.number_input("Amount", min_value=0.0, key="income_amount")
        date = st.date_input("Date", key="income_date")
        source = st.selectbox("Source", ["Salary", "Freelance", "Gift", "Other"], key="income_source")
        description = st.text_area("Description", key="income_desc")

        if st.button("Add Income"):
            if title and amount:
                add_income(st.session_state['user'], title, date, amount, source, description)
                st.success("Income added successfully!")
                st.rerun()
            else:
                st.error("Please fill all required fields.")

    st.write("---")
    st.subheader("📋 Transaction History")

    col1, col2 = st.columns(2)

    # ---------- EXPENSE TABLE ----------
    with col1:
        st.write("### 💸 Expenses")
        expenses_df = get_expenses(st.session_state['user'])

        if not expenses_df.empty:
            expenses_df["Delete"] = False
            edited_expenses = st.data_editor(
                expenses_df[["id", "title", "amount", "category", "date", "description", "Delete"]],
                hide_index=True,
                use_container_width=True,
                key="expense_editor"
            )

            delete_rows = edited_expenses[edited_expenses["Delete"] == True]
            if not delete_rows.empty:
                for _, row in delete_rows.iterrows():
                    delete_expense(int(row["id"]))
                st.success(f"Deleted {len(delete_rows)} expense(s) successfully!")
                st.rerun()
        else:
            st.info("No expenses found.")

    # ---------- INCOME TABLE ----------
    with col2:
        st.write("### 💰 Income")
        incomes_df = get_incomes(st.session_state['user'])

        if not incomes_df.empty:
            incomes_df["Delete"] = False
            edited_incomes = st.data_editor(
                incomes_df[["id", "title", "amount", "source", "date", "description", "Delete"]],
                hide_index=True,
                use_container_width=True,
                key="income_editor"
            )

            delete_rows = edited_incomes[edited_incomes["Delete"] == True]
            if not delete_rows.empty:
                for _, row in delete_rows.iterrows():
                    delete_income(int(row["id"]))
                st.success(f"Deleted {len(delete_rows)} income record(s) successfully!")
                st.rerun()
        else:
            st.info("No income records found.")
