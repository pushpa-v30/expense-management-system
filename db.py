import mysql.connector
import pandas as pd

# ---------- DATABASE CONNECTION ----------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",        # change if different
        password="root",        # enter MySQL password if set
        database="expense_manager"
    )

# ---------- AUTH FUNCTIONS ----------
def check_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

# ---------- TRANSACTION FUNCTIONS ----------
def add_expense(user_email, title, date, amount, category, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (user_email, title, date, amount, category, description)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_email, title, date, amount, category, description))
    conn.commit()
    conn.close()

def add_income(user_email, title, date, amount, source, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO income (user_email, title, date, amount, source, description)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_email, title, date, amount, source, description))
    conn.commit()
    conn.close()

def get_expenses(user_email):
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM expenses WHERE user_email=%s", conn, params=(user_email,))
    conn.close()
    return df

def get_incomes(user_email):
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM income WHERE user_email=%s", conn, params=(user_email,))
    conn.close()
    return df

# ---------- REPORT FUNCTIONS ----------
def get_income_expense_summary(user_email):
    """Fetch total income, total expenses, and balance for the user."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT IFNULL(SUM(amount), 0) FROM income WHERE user_email=%s", (user_email,))
    total_income = cursor.fetchone()[0]

    cursor.execute("SELECT IFNULL(SUM(amount), 0) FROM expenses WHERE user_email=%s", (user_email,))
    total_expense = cursor.fetchone()[0]

    balance = total_income - total_expense
    conn.close()
    return total_income, total_expense, balance

def get_expense_data(user_email):
    """Fetch all expense records for reports page."""
    conn = get_connection()
    query = "SELECT category, amount, date FROM expenses WHERE user_email=%s"
    df = pd.read_sql(query, conn, params=(user_email,))
    conn.close()
    return df
def delete_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
    conn.commit()
    conn.close()

def delete_income(income_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM income WHERE id = %s", (income_id,))
    conn.commit()
    conn.close()
def get_monthly_summary(user_email, month, year):
    db = get_connection()
    cursor = db.cursor()

    # Income
    cursor.execute("""
        SELECT IFNULL(SUM(amount), 0) 
        FROM income
        WHERE user_email=%s AND MONTH(date)=%s AND YEAR(date)=%s
    """, (user_email, month, year))
    income = cursor.fetchone()[0]

    # Expense
    cursor.execute("""
        SELECT IFNULL(SUM(amount), 0) 
        FROM expenses
        WHERE user_email=%s AND MONTH(date)=%s AND YEAR(date)=%s
    """, (user_email, month, year))
    expense = cursor.fetchone()[0]

    db.close()
    return income, expense, income - expense


def get_yearly_summary(user_email, year):
    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        SELECT IFNULL(SUM(amount), 0)
        FROM income
        WHERE user_email=%s AND YEAR(date)=%s
    """, (user_email, year))
    income = cursor.fetchone()[0]

    cursor.execute("""
        SELECT IFNULL(SUM(amount), 0)
        FROM expenses
        WHERE user_email=%s AND YEAR(date)=%s
    """, (user_email, year))
    expense = cursor.fetchone()[0]

    db.close()
    return income, expense, income - expense

def get_monthly_expense_data(user_email, month, year):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(amount) 
        FROM expenses
        WHERE user_email=%s AND MONTH(date)=%s AND YEAR(date)=%s
        GROUP BY category
    """, (user_email, month, year))

    result = cursor.fetchall()
    conn.close()
    return result


def get_yearly_expense_data(user_email, year):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(amount) 
        FROM expenses
        WHERE user_email=%s AND YEAR(date)=%s
        GROUP BY category
    """, (user_email, year))

    result = cursor.fetchall()
    conn.close()
    return result

