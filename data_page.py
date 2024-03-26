import streamlit as st
import json
import os
import pandas as pd
import warnings

warnings.filterwarnings("ignore")


def read_user_data_f(username, file, type):
    with open("data/user_data.json", "r") as f:
        user_data = json.load(f)
        if username not in user_data:
            user_data[username] = {}
            user_data[username]["income"] = {}
            user_data[username]["expenses"] = {}
        if username in user_data:
            # data= pd.read_json(user_data[username][type])
            data_file = pd.read_json(file)
            if len(user_data[username][type]) == 0:
                stored_data = pd.DataFrame()
            else:
                stored_data = pd.read_json(user_data[username][type], orient="records", convert_dates=["Date"])
            stored_data = pd.concat([stored_data, data_file], ignore_index=True).drop_duplicates()
            user_data[username][type] = stored_data.to_json(orient="records", date_format="iso")
            with open("data/user_data.json", "w") as f:
                json.dump(user_data, f)


def create_upload_drag_drop(username):
    st.title("Income and Expenses Tracker")
    # Upload files
    st.title("Upload Files")
    income_file = st.file_uploader("Upload Income File", type=["csv"])
    expenses_file = st.file_uploader("Upload Expenses File", type=["csv"])
    income_expenses(username, income_file, expenses_file)


def income_expenses(username, income_file, expenses_file):
    st.session_state.user_loaded_income = False
    st.session_state.user_loaded_expenses = False
    # Process uploaded files
    if income_file is not None:
        st.write("Income file uploaded:", income_file.name)
        income_df = pd.read_csv(income_file)
        read_user_data_f(username, income_df.to_json(), "income")
        st.session_state.user_loaded_income = True

    if expenses_file is not None:
        st.write("Expenses file uploaded:", expenses_file.name)
        expenses_df = pd.read_csv(expenses_file)
        read_user_data_f(username, expenses_df.to_json(), "expenses")
        st.session_state.user_loaded_expenses = True

    # Display the user data
    if st.session_state.user_loaded_income or st.session_state.user_loaded_expenses:
        with open("data/user_data.json", "r") as f:
            user_data = json.load(f)
            df_income = json.loads(user_data[username]["income"])
            df_expenses = json.loads(user_data[username]["expenses"])

        st.table(df_income)
        st.table(df_expenses)


def income_expenses_pir(user_name, income_file, expenses_file):
    # Process uploaded files
    if income_file is not None:
        income_df = pd.read_csv(income_file)
        read_user_data_f(user_name, income_df.to_json(), "income")

    if expenses_file is not None:
        expenses_df = pd.read_csv(expenses_file)
        read_user_data_f(user_name, expenses_df.to_json(), "expenses")


if __name__ == "__main__":
    expenses_folder = r"/Users/emilyramim/Desktop/projects /semester 7/נבונות/generating_usres/expenses"
    incomes_folder = r"/Users/emilyramim/Desktop/projects /semester 7/נבונות/generating_usres/incomes"
    income_files = [os.path.join(incomes_folder, file) for file in sorted(os.listdir(incomes_folder))]
    expenses_files = [os.path.join(expenses_folder, file) for file in sorted(os.listdir(expenses_folder))]
    user_names = [file.split(".")[0].replace("_income","") for file in sorted(os.listdir(incomes_folder))]
    for user_name, income_file, expenses_file in zip(user_names, income_files, expenses_files):
        income_expenses_pir(user_name, income_file, expenses_file)
