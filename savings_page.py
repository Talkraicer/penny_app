import pandas as pd
import streamlit as st
import json
import user
import numpy as np
import ast
import requests
import time
API_URL = "https://api-inference.huggingface.co/models/intfloat/e5-base"
headers = {"Authorization": "Bearer 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"}

MONTHS = list(range(1, 13))
INCOME_CATEGORIES = ["Salary/Wages", "Bonuses", "Investment income", "Rental income", "Side hustle income",
                     "Government benefits", "Other"]
EXPENSES_CATEGORIES = ["Housing", "Utilities", "Transportation", "Groceries", "Dining out", "Health",
                       "Entertainment", "Clothing", "Personal care", "Education", "Travel", "Other"]
#nonsense

def cosine_similarity_texts(input_text,comapred_text):
    json_data = {"source_sentence": input_text, "sentences":[comapred_text]}
    status = 0
    while status != 200:
        response = requests.post(API_URL, headers=headers, json=json_data)
        status = response.status_code
        time.sleep(1)
    return eval(response.text)[0]

def load_data(username):
    with open("data/user_data.json", "r") as f:
        user_data = json.load(f)
        df_income = json.loads(user_data[username]["income"])
        df_expenses = json.loads(user_data[username]["expenses"])
    return df_income, df_expenses


def load_data_for_embedding(username):
    with open("data/user_data.json", "r") as f:
        user_data = json.load(f)
        df_income = json.loads(user_data[username]["income"])
        df_expenses = json.loads(user_data[username]["expenses"])
        months = 0
        amount = 0
        text = ""
        weights = []

        # if text and weights dont exist in the data/user_data.json file, just return empty strings
        try:
            months = int(json.dumps(user_data[username]["savings"]["months"]))
            amount = int(json.dumps(user_data[username]["savings"]["amount"]))
            text = json.dumps(user_data[username]["savings"]["text"])
            weights = json.dumps(user_data[username]["savings"]["weights"])
            weights = ast.literal_eval(weights)
        except:
            pass
    return df_income, df_expenses, months, amount, text, weights


def update_user_plan(username, amount, months):
    with open("data/user_data.json", "r") as f:
        user_data = json.load(f)
    user_data[username]["savings"] = {}
    user_data[username]["savings"]["amount"] = amount
    user_data[username]["savings"]["months"] = months
    with open("data/user_data.json", "w") as f:
        json.dump(user_data, f)


def layout():
    st.title("Savings Plan")
    amount = st.number_input("Enter the amount you want to save", min_value=1)
    months = st.number_input("How many months do you want to save for?", min_value=1)
    username = st.session_state.current_user
    if st.session_state.built_plan or st.button("Build Plan"):
        st.session_state.built_plan = True
        st.write(
            f"Your plan is to save **{amount}\$** over **{months} months**. You need to save **{amount / months}\$** per month.")
        st.session_state.plan = [amount, months, amount / months]
        update_user_plan(username, amount, months)

        st.subheader("System recommended this plan for you:")
        recomend_plan(username, amount, months)

        df_income, df_expenses = load_data(username)
        categories = pd.json_normalize(df_expenses)["Category"]
        categories = categories.tolist()
        categories = list(set(categories))
        category_percentage = []
        count = 100

        st.title("make your own plan")
        for i, category in enumerate(categories):
            st.write(f"{category} ")
            category_percentage.append(
                st.slider(f"Percentage of {category} to save", min_value=0, max_value=count, value=0))
            count -= category_percentage[-1]
        if st.button("Save"):
            st.write("Saved")
            st.session_state.category_percentage = category_percentage
            st.session_state.categories = categories
            show_plan()
            save_plan(username, amount, months, categories, category_percentage)


def show_plan():
    amount = st.session_state.plan[0]
    category_percentage = st.session_state.category_percentage
    table = {"Category": [], "Percentage": [], "Amount to save": []}
    table["Category"] = st.session_state.categories
    for i in range(len(category_percentage)):
        table["Amount to save"].append(amount * category_percentage[i] / 100)
        table["Percentage"].append(category_percentage[i])
    st.table(pd.DataFrame(table))


def save_plan(username, amount, months, categories, category_percentage):
    with open("data/user_data.json", "r") as f:
        user_data = json.load(f)
    user_data[username]["savings"] = {"amount": amount, "months": months, "categories": categories,
                                      "category_percentage": category_percentage, "text": "", "weights": []}
    with open("data/user_data.json", "w") as f:
        json.dump(user_data, f)


def save_text_weight(username, text, weights):
    with open("data/user_data.json", "r") as f:
        user_data = json.load(f)
    user_data[username]["savings"]["text"] = text
    user_data[username]["savings"]["weights"] = weights
    with open("data/user_data.json", "w") as f:
        json.dump(user_data, f)


def recomend_plan(username, amount, months):
    # find the average spending by category
    income, expenses = load_data(username)
    df_income = pd.DataFrame(income)
    df_expenses = pd.DataFrame(expenses)
    categories = df_expenses["Category"].values
    categories = categories.tolist()
    categories = list(set(categories))
    category_percentage = []

    category_percentage = recommend_by_avg(categories, df_expenses)
    st.write("(we used the average spending by category to recommend this plan)")
    st.session_state.category_percentage = category_percentage
    save_plan(username, amount, months, categories, category_percentage)
    st.session_state.categories = categories
    show_plan()
    st.subheader("or:")
    text = st.text_input("tell us about your goals and we will recommend a better plan for you", "I want to save...")
    st.write(
        "the system will take in account your income, expenses and more features. you can adjust their weights as you like")
    # add tht weights sum to 100
    w1 = st.number_input("income weight", min_value=0, max_value=100, value=25)
    w2 = st.number_input("expenses weight", min_value=0, max_value=100, value=25)
    w3 = st.number_input("saving amount to month ratio weight", min_value=0, max_value=100, value=25)
    w4 = st.number_input("text weight", min_value=0, max_value=100, value=25)
    if st.button("Recommend"):
        st.session_state.text = text
        st.session_state.weights = [w1, w2, w3, w4]
        save_text_weight(username, text, [w1, w2, w3, w4])
        category_percentage, sim_user = recommend_by_sim()
        st.session_state.category_percentage = category_percentage
        save_plan(username, amount, months, categories, category_percentage)
        show_plan()
        st.write(f"we also found a user with similar goals to you, his plan is {sim_user}'s plan")


def recommend_by_avg(categories, df_expenses):
    # find the average spending by category
    category_percentage = []
    expenses_sun = 0
    for category in categories:
        category_percentage.append(df_expenses.loc[df_expenses["Category"] == category, "Amount"].sum())
        expenses_sun += category_percentage[-1]
    category_percentage = [int(100 * category / expenses_sun) for category in category_percentage]
    return category_percentage


def fill_categories_and_months(df, type):
    df_list = []
    if type == "income":
        for category in INCOME_CATEGORIES:
            if category not in df["Category"].values:
                df_list.append({"Category": category, "Amount": 0, "Month": 1})
        for i, row in df.iterrows():
            if row["Category"] not in INCOME_CATEGORIES:
                row["Category"] = "Other"
    if type == "expenses":
        for category in EXPENSES_CATEGORIES:
            if category not in df["Category"].values:
                df_list.append({"Category": category, "Amount": 0, "Month": 1})
        for i, row in df.iterrows():
            if row["Category"] not in EXPENSES_CATEGORIES:
                tempRow = row
                tempRow["Category"] = "Other"
                df.iloc[i] = tempRow
    df_list = pd.DataFrame(df_list)
    df = pd.concat([df, df_list], ignore_index=True)
    df_list = []
    for month in MONTHS:
        for category in df["Category"].unique():
            if category not in df.loc[df["Month"] == month, "Category"].values:
                df_list.append({"Category": category, "Amount": 0, "Month": month})
    df_list = pd.DataFrame(df_list)
    df = pd.concat([df, df_list], ignore_index=True)
    return df


def create_matrix(df, type):
    df = pd.json_normalize(df)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.month
    df.drop(columns=["Date"], inplace=True)
    df = fill_categories_and_months(df, type)
    df = df.sort_values(by=['Category', 'Month'])
    df_pivot = df.pivot_table(index='Category', columns='Month', values='Amount', fill_value=0)
    vector = df_pivot.values.flatten()
    # create index list for the vector
    index = []
    for i, row in df.iterrows():
        index.append((row["Category"], str(row["Month"])))
    return vector, index


def data_to_embedding(user1):
    df_income, df_expenses, months, amount, text, weights = load_data_for_embedding(user1)
    income_vec, income_index = create_matrix(df_income, type="income")
    expenses_vec, expenses_index = create_matrix(df_expenses, type="expenses")
    amount_month_vec = [amount, months]

    return income_vec, expenses_vec, amount_month_vec, text

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def recommend_by_sim():
    users_list = user.load_users().keys()
    users_list = list(users_list)
    users_list.remove(st.session_state.current_user)
    users_income = []
    users_expenses = []
    users_amount_month = []
    users_text = []
    c_user_income, c_user_expenses, c_user_amount_month, c_user_text = data_to_embedding(st.session_state.current_user,
                                                                                         )
    for user1 in users_list:
        user_income, user_expenses, user_amount_month, user_text = data_to_embedding(user1)
        users_income.append(user_income)
        users_expenses.append(user_expenses)
        users_amount_month.append(user_amount_month)
        users_text.append(user_text)
    # find the most similar user
    income_sim = []
    expenses_sim = []
    amount_month_sim = []
    text_sim = []
    for i, user1 in enumerate(users_list):
        income_sim.append(cosine_similarity(c_user_income, users_income[i]))
        expenses_sim.append(cosine_similarity(c_user_expenses, users_expenses[i]))
        amount_month_sim.append(cosine_similarity(c_user_amount_month, users_amount_month[i]))
        text_sim.append(cosine_similarity_texts(c_user_text, users_text[i]))
    # multiply by the weights
    income_sim = [income_sim[i] * st.session_state.weights[0] for i in range(len(income_sim))]
    expenses_sim = [expenses_sim[i] * st.session_state.weights[1] for i in range(len(expenses_sim))]
    amount_month_sim = [amount_month_sim[i] * st.session_state.weights[2] for i in range(len(amount_month_sim))]
    text_sim = [text_sim[i] * st.session_state.weights[3] for i in range(len(text_sim))]
    sum_sims = [income_sim[i] + expenses_sim[i] + amount_month_sim[i] + text_sim[i] for i in range(len(income_sim))]
    most_sim_user = users_list[sum_sims.index(max(sum_sims))]
    # recommend by his plan
    with open("data/user_data.json", "r") as f:
        user_data = json.load(f)
    category_percentage = user_data[most_sim_user]["savings"]["category_percentage"]
    return category_percentage, most_sim_user

if __name__ == '__main__':
    cosine_similarity_texts("Hello world","hey bye")