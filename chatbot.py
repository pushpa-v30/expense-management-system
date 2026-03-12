# ai_chatbot.py
import streamlit as st
import difflib
import re
from db import get_income_expense_summary

# -------------------------------
# Local Finance Knowledge Base
# -------------------------------
KNOWLEDGE_BASE = {
    "budget": "A budget is a plan for managing your income and expenses so you can save and control overspending.",
    "savings": "Savings represent the portion of income left after all expenses. It’s ideal to save at least 20% of your income.",
    "expense limit": "Your expense limit is the maximum amount you can spend without affecting savings. Usually, not more than 80% of income.",
    "income": "Income is the total money you earn — from salary, freelance, gifts, or other sources.",
    "expense": "Expenses are the money you spend. Keeping them below 80% of income is a good rule.",
    "investment": "Investment means putting your savings into assets like stocks, gold, or mutual funds to grow wealth.",
    "balance": "Balance is the difference between your total income and expenses.",
    "margin": "A margin or limit ensures your expenses don’t exceed a certain percentage of your income."
}

FINANCE_KEYWORDS = [
    "budget", "income", "expense", "savings", "saving", "salary", "limit",
    "margin", "spend", "spending", "balance", "money", "financial", "investment",
    "debt", "loan", "bank", "interest", "fund", "cash"
]

# -------------------------------
# Helper Functions
# -------------------------------
def is_finance_related(query):
    """Check if a query is finance related"""
    query_lower = query.lower()
    for word in FINANCE_KEYWORDS:
        if word in query_lower:
            return True
    return False

def get_best_answer_from_kb(query):
    """Try to find a close match in the local KB"""
    query_lower = query.lower()
    matches = difflib.get_close_matches(query_lower, KNOWLEDGE_BASE.keys(), n=1, cutoff=0.4)
    if matches:
        return KNOWLEDGE_BASE[matches[0]]
    return None

def generate_dynamic_answer(query, user_email):
    """Use the user's data to give personalized responses"""
    total_income, total_expense, balance = get_income_expense_summary(user_email)
    total_income = float(total_income or 0)
    total_expense = float(total_expense or 0)
    balance = float(balance or 0)
    limit = 0.8 * total_income if total_income > 0 else 0

    q = query.lower()

    # Dynamic personalized responses
    if "income" in q and "total" in q:
        return f"Your total income is ₹{total_income:.2f}."
    elif "expense" in q and "total" in q:
        return f"Your total expenses are ₹{total_expense:.2f}."
    elif "balance" in q or "remaining" in q:
        return f"Your current balance (income - expenses) is ₹{balance:.2f}."
    elif "80" in q or "limit" in q or "margin" in q:
        if total_income == 0:
            return "You haven't added any income yet, so the 80% limit can't be calculated."
        elif total_expense >= limit:
            return (f"⚠️ Your expenses ₹{total_expense:.2f} have **exceeded** your margin limit of ₹{limit:.2f}. "
                    f"Consider reducing spending.")
        else:
            remaining = limit - total_expense
            percentage = (total_expense / total_income * 100) if total_income > 0 else 0
            return (f"You're currently at {percentage:.1f}% of your income in expenses. "
                    f"You can still spend ₹{remaining:.2f} before reaching your 80% margin limit.")
    elif "save" in q or "savings" in q:
        savings = total_income - total_expense
        if total_income == 0:
            return "You haven’t added income yet, so your savings can’t be calculated."
        rate = (savings / total_income) * 100 if total_income > 0 else 0
        return f"Your current savings are ₹{savings:.2f}, which is {rate:.1f}% of your income."
    else:
        return None

# -------------------------------
# Streamlit Chatbot Interface
# -------------------------------
def ai_chatbot_page():
    st.header("🤖 Smart Finance Assistant")
    st.write("Ask me anything related to your finances (income, expenses, budget, savings, etc.)")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # User input
    user_query = st.text_input("💬 Your question:")

    if st.button("Ask"):
        if not user_query.strip():
            st.warning("Please enter a question.")
        else:
            # Store user message
            st.session_state['chat_history'].append(("🧑 You", user_query))

            # Check if question is finance related
            if not is_finance_related(user_query):
                answer = "❌ I can’t answer these types of questions. Please ask finance-related ones."
            else:
                # First check dynamic data-based answer
                user_email = st.session_state.get('user')
                dynamic_answer = generate_dynamic_answer(user_query, user_email)
                if dynamic_answer:
                    answer = dynamic_answer
                else:
                    # If not dynamic, check knowledge base
                    kb_answer = get_best_answer_from_kb(user_query)
                    if kb_answer:
                        answer = kb_answer
                    else:
                        answer = "Hmm, I’m not sure about that. Try asking something like 'What’s my current balance?' or 'What is my expense limit?'"

            st.session_state['chat_history'].append(("🤖 AI", answer))
            st.rerun()

    # Display chat history
    for role, msg in st.session_state['chat_history']:
        st.markdown(f"**{role}:** {msg}")
