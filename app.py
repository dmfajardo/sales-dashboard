import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load Data
@st.cache_data
def load_data():
    file_path = "finalDataSet.csv"  # Make sure the file is in the same directory
    df = pd.read_csv(file_path, encoding="ISO-8859-1")
    df.columns = df.columns.str.strip()  # Ensure column names have no leading/trailing spaces
    if 'Total' in df.columns:
        df['Total'] = pd.to_numeric(df['Total'].replace({'\$': '', ',': ''}, regex=True), errors='coerce').fillna(0)  # Ensure 'Total' column is numeric and replace NaN with 0
    if 'Total Number of Accounts' in df.columns:
        df['Total Number of Accounts'] = pd.to_numeric(df['Total Number of Accounts'], errors='coerce').fillna(0).astype(int)
    return df

df = load_data()

# Function to format large numbers in abbreviated format
def format_currency(value):
    if pd.isna(value) or value == 0:
        return "N/A"
    if value >= 1e9:
        return f"${value / 1e9:.2f}B"
    elif value >= 1e6:
        return f"${value / 1e6:.2f}MM"
    elif value >= 1e3:
        return f"${value / 1e3:.2f}K"
    return f"${value:,.2f}"

# Function to categorize AUM into ranges
def categorize_aum(value):
    if value > 800e6:
        return ">$800MM"
    for i in range(100, 900, 100):
        if value <= i * 1e6:
            return f"${i-100}MM - ${i}MM"
    return "N/A"

# Apply AUM categorization
df['AUM Range'] = df['Total'].apply(categorize_aum)

# Title
st.title("Sales Opportunities Dashboard")

# Filters
st.sidebar.header("Filters")
if not df.empty:
    selected_state = st.sidebar.selectbox("Select State", ['All'] + sorted(list(df['State'].dropna().unique())))
    selected_account_type = st.sidebar.selectbox("Select Account Type", ['All', 'Individuals', 'Corporations', 'Pensions'])
    selected_aum_ranges = st.sidebar.multiselect("Select AUM Ranges", sorted(df['AUM Range'].unique()), default=sorted(df['AUM Range'].unique()))

    # Apply Filters
    if selected_state != 'All':
        df = df[df['State'] == selected_state]
    if selected_account_type != 'All':
        df = df[df[f'Accts-{selected_account_type}'].notna()]
    if selected_aum_ranges:
        df = df[df['AUM Range'].isin(selected_aum_ranges)]

    # Key Metrics
    st.subheader("Key Sales Insights")
    st.metric("Total Businesses", len(df))
    if 'Total Number of Accounts' in df.columns:
        st.metric("Total Accounts", f"{df['Total Number of Accounts'].sum():,}")
    if 'Total' in df.columns:
        st.metric("Total AUM", format_currency(df['Total'].sum()))

    # Pie Chart: Account Distribution
    st.subheader("Account Type Distribution")
    account_types = ['Accts-Individuals', 'Accts-Corps', 'Accts-Pensions']
    account_data = df[account_types].sum()
    if account_data.sum() > 0:
        fig, ax = plt.subplots()
        ax.pie(account_data, labels=account_types, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
        st.pyplot(fig)
    else:
        st.write("No data available for the selected filters.")

    # Table of Opportunities
    st.subheader("Sales Opportunities")
    df = df.rename(columns={
        'Primary Business Name': 'RIA',
        'Total Number of Accounts': 'Accounts'
    })
    if 'Total' in df.columns:
        df['AUM'] = df['Total'].apply(format_currency)
    df['Accounts'] = df['Accounts'].apply(lambda x: f"{x:,}")  # Format accounts as '0,000'
    columns_to_show = ['CRD', 'RIA', 'City', 'State', 'Accounts', 'AUM', 'AUM Range']
    st.dataframe(df[columns_to_show])

    st.write("Use the filters on the left to refine insights!")