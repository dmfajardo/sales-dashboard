import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load Data
@st.cache_data
def load_data():
    file_path = "finalDataSet.csv"  # Make sure the file is in the same directory
    df = pd.read_csv(file_path, encoding="ISO-8859-1")
    return df

df = load_data()

# Title
st.title("Sales Opportunities Dashboard")

# Filters
st.sidebar.header("Filters")
selected_state = st.sidebar.selectbox("Select State", ['All'] + list(df['State'].dropna().unique()))
selected_account_type = st.sidebar.selectbox("Select Account Type", ['All', 'Individuals', 'Corporations', 'Pensions'])

# Filter Data
if selected_state != 'All':
    df = df[df['State'] == selected_state]
if selected_account_type != 'All':
    df = df[df[f'Accts-{selected_account_type}'].notna()]

# Key Metrics
st.subheader("Key Sales Insights")
st.metric("Total Businesses", len(df))
st.metric("Total Accounts", df['Total Number of Accounts'].sum())
st.metric("Total AUM", f"${df['Total'].sum():,.2f}")

# Pie Chart: Account Distribution
st.subheader("Account Type Distribution")
account_types = ['Accts-Individuals', 'Accts-Corps', 'Accts-Pensions']
account_data = df[account_types].sum()
fig, ax = plt.subplots()
ax.pie(account_data, labels=account_types, autopct='%1.1f%%', startangle=90)
ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
st.pyplot(fig)

# Table of Opportunities
st.subheader("Top Sales Opportunities")
columns_to_show = ['Primary Business Name', 'State', 'Total', 'Total Number of Accounts']
st.dataframe(df[columns_to_show].sort_values(by='Total', ascending=False).head(10))

st.write("Use the filters on the left to refine insights!")
