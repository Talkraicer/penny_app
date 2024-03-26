import streamlit as st
import json
import os

def load_users(filename="data/users.json"):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Function to save user information to a JSON file
def save_users(users,username,  filename="data/users.json"):
    with open(filename, "w") as file:
        json.dump(users, file)
    with open("data/user_data.json", "r") as f:
        user_data = json.load(f)
    user_data[username] = {}
    user_data[username]["income"] = {}
    user_data[username]["expenses"] = {}
    with open("data/user_data.json", "w") as f:
        json.dump(user_data, f)

# Add a sidebar section for user authentication and registration
def authenticate(users):
    st.sidebar.title("Login / Register")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username in users and users[username] == password:
            st.sidebar.success("Logged in as {}".format(username))
            if "username" not in st.session_state.keys():
                st.session_state["username"]= username
            st.session_state.built_plan = False
            return True
        else:
            st.sidebar.error("Invalid username or password")
            return False

    elif st.sidebar.button("Register"):
        if username in users:
            st.sidebar.error("Username already exists")
        else:
            users[username] = password
            save_users(users, username)
            st.sidebar.success("Registration successful. You can now login.")
        return False

def getCurrentUsername():
    return st.session_state["username"]


if __name__ == '__main__':
    users = load_users()
    incomes_folder = r"/Users/emilyramim/Desktop/projects /semester 7/נבונות/generating_usres/incomes"
    user_names = [file.split(".")[0].replace("_income","") for file in os.listdir(incomes_folder)]
    for user_name in user_names:
        users[user_name] = user_name
        save_users(users, user_name)
