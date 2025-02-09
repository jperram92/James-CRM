import streamlit as st
import sqlite3
from datetime import datetime

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to create a new budget for a contact
def create_budget(contact_id, budget_name, total_budget, start_date, end_date, currency):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO budgets (contact_id, budget_name, total_budget, start_date, end_date, currency)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (contact_id, budget_name, total_budget, start_date, end_date, currency))
    conn.commit()
    conn.close()
    st.success("Budget created successfully!")

# Function to update an existing budget
def update_budget(budget_id, budget_name=None, total_budget=None, start_date=None, end_date=None, currency=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    values = []

    if budget_name:
        updates.append("budget_name = ?")
        values.append(budget_name)
    if total_budget:
        updates.append("total_budget = ?")
        values.append(total_budget)
    if start_date:
        updates.append("start_date = ?")
        values.append(start_date)
    if end_date:
        updates.append("end_date = ?")
        values.append(end_date)
    if currency:
        updates.append("currency = ?")
        values.append(currency)

    updates_str = ", ".join(updates)
    values.append(budget_id)

    cursor.execute(f'''
        UPDATE budgets SET {updates_str} WHERE id = ?
    ''', tuple(values))
    conn.commit()
    conn.close()
    st.success("Budget updated successfully!")

# Function to delete a budget
def delete_budget(budget_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM budgets WHERE id = ?', (budget_id,))
    conn.commit()
    conn.close()
    st.success("Budget deleted successfully!")

# Function to get all budgets for a contact
def get_budgets_for_contact(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM budgets WHERE contact_id = ?
    ''', (contact_id,))
    budgets = cursor.fetchall()
    conn.close()
    return budgets

# Function to add an expense for a budget
def add_expense(budget_id, expense_amount):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the current_spent value
    cursor.execute('''
        UPDATE budgets
        SET current_spent = current_spent + ?
        WHERE id = ?
    ''', (expense_amount, budget_id))

    # Get the new remaining budget
    cursor.execute('''
        SELECT total_budget - current_spent AS remaining_budget
        FROM budgets WHERE id = ?
    ''', (budget_id,))
    remaining_budget = cursor.fetchone()['remaining_budget']

    conn.commit()
    conn.close()
    
    st.success(f"Expense added successfully! Remaining budget: {remaining_budget}")
    return remaining_budget

# Function to check the remaining budget for a specific budget
def check_remaining_budget(budget_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT remaining_budget FROM budgets WHERE id = ?
    ''', (budget_id,))
    remaining_budget = cursor.fetchone()
    conn.close()
    return remaining_budget["remaining_budget"] if remaining_budget else None

# Streamlit UI for budget management
st.title("Budget Management for Contacts")

# Get the contact ID (for demo purposes, manually input contact ID)
contact_id = st.number_input("Enter Contact ID", min_value=1, step=1)

# Display existing budgets for the contact
if contact_id:
    budgets = get_budgets_for_contact(contact_id)
    if budgets:
        st.subheader(f"Existing Budgets for Contact {contact_id}")
        for budget in budgets:
            st.write(f"Budget Name: {budget['budget_name']}")
            st.write(f"Total Budget: {budget['total_budget']}")
            st.write(f"Start Date: {budget['start_date']}")
            st.write(f"End Date: {budget['end_date']}")
            st.write(f"Currency: {budget['currency']}")
            st.write(f"Status: {budget['status']}")
            st.write(f"Remaining Budget: {budget['remaining_budget']}")
            st.write("---")
    else:
        st.write("No budgets found for this contact.")

# Form to create a new budget
st.subheader("Create a New Budget")
with st.form(key="create_budget_form"):
    budget_name = st.text_input("Budget Name")
    total_budget = st.number_input("Total Budget", min_value=0.0, step=0.01)
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    currency = st.selectbox("Currency", ["USD", "AUD", "EUR", "GBP"])

    submit_button = st.form_submit_button("Create Budget")

    if submit_button:
        create_budget(contact_id, budget_name, total_budget, start_date, end_date, currency)

# Form to update an existing budget
st.subheader("Update an Existing Budget")
budget_id_to_update = st.number_input("Enter Budget ID to Update", min_value=1, step=1)
budget_name_to_update = st.text_input("New Budget Name")
total_budget_to_update = st.number_input("New Total Budget", min_value=0.0, step=0.01)
start_date_to_update = st.date_input("New Start Date")
end_date_to_update = st.date_input("New End Date")
currency_to_update = st.selectbox("New Currency", ["USD", "AUD", "EUR", "GBP"])

update_button = st.button("Update Budget")

if update_button:
    update_budget(budget_id_to_update, budget_name_to_update, total_budget_to_update, start_date_to_update, end_date_to_update, currency_to_update)

# Form to delete an existing budget
st.subheader("Delete an Existing Budget")
budget_id_to_delete = st.number_input("Enter Budget ID to Delete", min_value=1, step=1)
delete_button = st.button("Delete Budget")

if delete_button:
    delete_budget(budget_id_to_delete)

# Form to add an expense to a budget
st.subheader("Add an Expense to a Budget")
budget_id_to_add_expense = st.number_input("Enter Budget ID to Add Expense", min_value=1, step=1)
expense_amount = st.number_input("Expense Amount", min_value=0.0, step=0.01)

add_expense_button = st.button("Add Expense")

if add_expense_button:
    add_expense(budget_id_to_add_expense, expense_amount)

# Form to check the remaining budget for a budget
st.subheader("Check Remaining Budget")
budget_id_to_check = st.number_input("Enter Budget ID to Check Remaining Budget", min_value=1, step=1)
check_remaining_button = st.button("Check Remaining Budget")

if check_remaining_button:
    remaining_budget = check_remaining_budget(budget_id_to_check)
    if remaining_budget is not None:
        st.write(f"Remaining Budget: {remaining_budget}")
    else:
        st.write("Budget not found.")
