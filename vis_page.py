import streamlit as st
import streamlit as st
import pandas as pd
import plotly.express as px
from savings_page import load_data_for_embedding
def layout():
    st.session_state.current_tab = "VIS"

    df_income, df_expenses, months, amount, text, weights= load_data_for_embedding(st.session_state.current_user)
    df_income = pd.json_normalize(df_income)
    df_income["Date"] = pd.to_datetime(df_income["Date"])
    df_income["Month"] = df_income["Date"].dt.month

    df_expenses = pd.json_normalize(df_expenses)
    df_expenses["Date"] = pd.to_datetime(df_expenses["Date"])
    df_expenses["Month"] = df_expenses["Date"].dt.month

    df_income_by_categories= df_income[["Amount", "Category"]].groupby("Category").sum()
    df_income_by_categories["Category"]= df_income_by_categories.index
    df_expenses_by_categories= df_expenses[["Amount", "Category"]].groupby("Category").sum()
    df_expenses_by_categories["Category"]= df_expenses_by_categories.index

    avg_monthly_income_l =[df_income[df_income["Month"]==i]["Amount"].sum() for i in range(1, 13)]
    avg_monthly_income= round(sum(avg_monthly_income_l)/len(avg_monthly_income_l), 2)
    avg_monthly_expenses_l =[df_expenses[df_expenses["Month"]==i]["Amount"].sum() for i in range(1, 13)]
    avg_monthly_expenses= round(sum(avg_monthly_expenses_l)/len(avg_monthly_expenses_l), 2)

    st.sidebar.header('visualization parameters:')


    st.sidebar.subheader('Income chart parameters')
    categories_income = st.sidebar.multiselect('Select Categories', df_income_by_categories.index)

    st.sidebar.subheader('Expenses chart parameters')
    categories_expenses = st.sidebar.multiselect('Select Categories', df_expenses_by_categories.index)



    st.markdown('### Metrics')
    col1, col2 = st.columns(2)
    col1.metric("Avg Monthly Income", f"{avg_monthly_income}$")
    col2.metric("Avg Monthly Expenses", f"{avg_monthly_expenses}$")



    st.markdown('### income by category')
    fig = px.pie(df_income_by_categories, values='Amount', names='Category', hole=0.4)
    st.plotly_chart(fig)
    st.markdown('### expenses by category')
    fig = px.pie(df_expenses_by_categories, values='Amount', names='Category', hole=0.4)
    st.plotly_chart(fig)


    st.markdown('### Income chart')
    st.bar_chart(df_income[df_income["Category"].isin(categories_income)], x='Date', y='Amount',
                 color= "#00FF00")

    st.markdown('### Expenses chart')
    st.bar_chart(df_expenses[df_expenses["Category"].isin(categories_expenses)], x='Date', y='Amount',
                 color="#FF0000")
