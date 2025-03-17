import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Database connection details
host = "localhost"
port = "5432"
database = "sport"
username = "postgres"
password = "ajayguvi29"

# PostgreSQL connection string
engine_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(engine_string)

# Fetch categories from PostgreSQL
@st.cache_data
def load_categories():
    query = "SELECT * FROM categories"
    return pd.read_sql(query, engine)

# Fetch competitions from PostgreSQL
@st.cache_data
def load_competitions():
    query = "SELECT * FROM competitions"
    return pd.read_sql(query, engine)

# Load data
df_categories = load_categories()
df_competitions = load_competitions()

# Sidebar: Category filter
category_filter = st.sidebar.selectbox("🔍 Select Category:", ["All"] + df_categories["category_name"].tolist())

# Sidebar: Dark mode toggle
dark_mode = st.sidebar.checkbox("🌙 Dark Mode")

# Apply category filter
if category_filter != "All":
    category_id = df_categories[df_categories["category_name"] == category_filter]["category_id"].values[0]
    df_competitions = df_competitions[df_competitions["category_id"] == category_id]

# Search competitions
search_query = st.sidebar.text_input("🔎 Search Competition:")
if search_query:
    df_competitions = df_competitions[df_competitions["competition_name"].str.contains(search_query, case=False, na=False)]

# Streamlit Page Styling
if dark_mode:
    st.markdown("""
        <style>
            body { background-color: #222; color: white; }
            .css-1aumxhk { color: white !important; }
        </style>
    """, unsafe_allow_html=True)

# Header
st.title("🎾 Tennis Competitions Table")

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("📂 Total Categories", len(df_categories))
col2.metric("🏆 Total Competitions", len(df_competitions))
if "type" in df_competitions.columns:
    col3.metric("🎭 Most Common Type", df_competitions["type"].mode()[0])

# Toggle View
view_option = st.radio("View Data As:", ["📊 Charts", "📜 Tables"])

if view_option == "📊 Charts":
    # Bar Chart: Number of competitions per category
    st.subheader("📊 Competitions Count by Category")
    category_counts = df_competitions["category_id"].value_counts().reset_index()
    category_counts.columns = ["category_id", "count"]
    category_counts = category_counts.merge(df_categories, on="category_id")
    fig_bar = px.bar(category_counts, x="category_name", y="count", title="Number of Competitions per Category")
    st.plotly_chart(fig_bar)

    # Pie Chart: Competition type distribution
    st.subheader("🥧 Competition Type Distribution")
    if "type" in df_competitions.columns:
        fig_pie = px.pie(df_competitions, names="type", title="Competition Type Proportion")
        st.plotly_chart(fig_pie)
    else:
        st.warning("No 'type' column found in competitions data.")
else:
    # Display Categories
    st.subheader("📂 Categories Table")
    st.dataframe(df_categories)

    # Display Competitions
    st.subheader("🏆 Competitions Table")
    st.dataframe(df_competitions)

# Download Button
st.download_button(
    label="⬇️ Download Competitions Data",
    data=df_competitions.to_csv(index=False),
    file_name="competitions.csv",
    mime="text/csv"
)

# Competition Details Popup
selected_competition = st.selectbox("🔍 View Competition Details:", df_competitions["competition_name"].tolist())
if selected_competition:
    comp_details = df_competitions[df_competitions["competition_name"] == selected_competition].iloc[0]
    st.write(f"**🏆 Competition Name:** {comp_details['competition_name']}")
    st.write(f"**📂 Category ID:** {comp_details['category_id']}")
    if 'type' in comp_details:
        st.write(f"**🎭 Type:** {comp_details['type']}")
    st.write(f"**🔗 Competition ID:** {comp_details['competition_id']}")

st.success("✅ Data successfully visualized with interactive features!")










import requests
import pandas as pd
import streamlit as st
import plotly.express as px

# API Endpoint and Key
url = "https://api.sportradar.com/tennis/trial/v3/en/complexes.json"
api_key = "VgHSqORWydVoXCS64SKXiEIAUpEpAMjIWHzfNiQP"  # Replace with your actual key

# Streamlit App Title
st.title("🎾 Tennis Complexes Table")

# API Request
params = {"api_key": api_key}
headers = {"accept": "application/json"}

response = requests.get(url, headers=headers, params=params)

# Check Response
if response.status_code == 200:
    data = response.json()  # Convert response to JSON
    
    # Extract complex IDs and names
    if "complexes" in data:
        complexes = []
        
        for complex_ in data["complexes"]:
            complex_id = complex_.get("id", "N/A")
            complex_name = complex_.get("name", "Unknown")
            latitude = complex_.get("latitude", None)
            longitude = complex_.get("longitude", None)
            
            complexes.append({"Complex ID": complex_id, "Name": complex_name, 
                              "Latitude": latitude, "Longitude": longitude})

        # Convert to DataFrame
        df = pd.DataFrame(complexes)

        # Search bar for filtering complexes
        search_term = st.text_input("🔍 Search Complex Name", "")
        if search_term:
            df = df[df["Name"].str.contains(search_term, case=False, na=False)]

        # Display Table
        st.subheader("📊 Complexes Table")
        st.dataframe(df)  

        # Bar Chart - Complex Name Frequency
        if not df.empty:
            st.subheader("📈 Complex Count Visualization")
            fig_bar = px.bar(df["Name"].value_counts(), title="Complex Name Distribution")
            st.plotly_chart(fig_bar)

            # Pie Chart
            st.subheader("🟠 Complex Distribution")
            fig_pie = px.pie(df, names="Name", title="Complex Name Proportions")
            st.plotly_chart(fig_pie)

            

    else:
        st.warning("No complexes data found.")
else:
    st.error(f"Error {response.status_code}: {response.text}")















import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# API URL
url = "https://api.sportradar.com/tennis/trial/v3/en/complexes.json?api_key=VgHSqORWydVoXCS64SKXiEIAUpEpAMjIWHzfNiQP"

# Headers
headers = {"accept": "application/json"}

# Fetch response
response = requests.get(url, headers=headers)

# Streamlit UI
st.title("🎾Tennis Venue Table")

if response.status_code == 200:
    data = response.json()

    # Extract required fields
    venue_list = []
    for complex_data in data.get("complexes", []):
        complex_id = complex_data.get("id")
        for venue in complex_data.get("venues", []):
            venue_list.append([
                venue.get("id"),
                venue.get("name"),
                venue.get("city_name"),
                venue.get("country_name"),
                venue.get("country_code"),
                venue.get("timezone"),
                complex_id
            ])

    # Create DataFrame
    df = pd.DataFrame(venue_list, columns=["venue_id", "venue_name", "city", "country", "country_code", "timezone", "complex_id"])

    # Display DataFrame
    st.subheader("📊 Venue Data")
    st.dataframe(df)

    # Bar chart - Venue count by country
    country_counts = df["country"].value_counts().reset_index()
    country_counts.columns = ["Country", "Venue Count"]
    fig_bar = px.bar(country_counts, x="Country", y="Venue Count", title="Venue Count by Country", color="Venue Count")
    st.plotly_chart(fig_bar)

    # Pie chart - Distribution of venues by country
    fig_pie = px.pie(country_counts, names="Country", values="Venue Count", title="Venue Distribution by Country")
    st.plotly_chart(fig_pie)

    # Search and filter
    st.subheader("🔍 Search & Filter")
    country_filter = st.selectbox("Select a country", ["All"] + list(df["country"].unique()))
    search_query = st.text_input("Search for a venue")

    filtered_df = df.copy()
    if country_filter != "All":
        filtered_df = filtered_df[filtered_df["country"] == country_filter]
    if search_query:
        filtered_df = filtered_df[filtered_df["venue_name"].str.contains(search_query, case=False, na=False)]

    st.dataframe(filtered_df)

else:
    st.error(f"Error: {response.status_code}, {response.text}")












import requests
import streamlit as st
import pandas as pd
import altair as alt
import random

# API URL
url = "https://api.sportradar.com/tennis/trial/v3/en/double_competitors_rankings.json?api_key=VgHSqORWydVoXCS64SKXiEIAUpEpAMjIWHzfNiQP"

# Headers
headers = {"accept": "application/json"}

# Make API request
response = requests.get(url, headers=headers)

# Streamlit App Title
st.title("🎾tennis Competitions Ranking")

# Check if request was successful
if response.status_code == 200:
    data = response.json()

    # Extract competitors' details
    competitors_data = []
    rankings = data.get("rankings", [])
    for ranking in rankings:
        competitors = ranking.get("competitor_rankings", [])
        for competitor in competitors:
            competitor_id = competitor.get("competitor", {}).get("id", "N/A")
            name = competitor.get("competitor", {}).get("name", "N/A")
            country = competitor.get("competitor", {}).get("country", "N/A")
            country_code = competitor.get("competitor", {}).get("country_code", "N/A")
            abbreviation = competitor.get("competitor", {}).get("abbreviation", "N/A")

            competitors_data.append({
                "ID": competitor_id,
                "Name": name,
                "Country": country,
                "Country Code": country_code,
                "Abbreviation": abbreviation
            })

    # Convert to DataFrame
    df = pd.DataFrame(competitors_data)

    # Search Box
    search_query = st.text_input("🔍 Search Competitors", "")
    if search_query:
        df = df[df["Name"].str.contains(search_query, case=False, na=False)]

    # Display Data in Streamlit
    st.dataframe(df)
    st.subheader("📊 Competitions Table")

    # Competitors by Country
    country_counts = df["Country"].value_counts().reset_index()
    country_counts.columns = ["Country", "Count"]

    # Bar Chart
    st.subheader("📌 Top Countries with Most Competitors")
    st.bar_chart(country_counts.set_index("Country").head(10))  # Top 10 countries

    # Simulated Competitor Count Over Time (For Trend Visualization)
    st.subheader("📈 Competitor Count Over Time (Simulated Data)")
    dates = pd.date_range(start="2024-01-01", periods=10, freq="M")
    competitor_trend = pd.DataFrame({
        "Date": dates,
        "Competitor Count": [random.randint(50, 150) for _ in range(10)]
    }).set_index("Date")
    st.line_chart(competitor_trend)

    # Pie Chart (Altair) for Country Distribution
    st.subheader("🌍 Distribution of Competitors by Country")
    pie_chart = alt.Chart(country_counts.head(10)).mark_arc().encode(
        theta="Count",
        color="Country",
        tooltip=["Country", "Count"]
    ).properties(width=500, height=400)
    st.altair_chart(pie_chart, use_container_width=True)

    # Area Chart - Competitor Count
    st.subheader("📊 Competitor Count Growth (Simulated)")
    st.area_chart(competitor_trend)

else:
    st.error(f"Failed to retrieve data: {response.status_code}")












import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Fetch data from API
def fetch_data():
    url = "https://api.sportradar.com/tennis/trial/v3/en/double_competitors_rankings.json?api_key=VgHSqORWydVoXCS64SKXiEIAUpEpAMjIWHzfNiQP"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error {response.status_code}: {response.text}")
        return None

# Process data into a DataFrame
def process_data(data):
    rankings = []
    for ranking in data.get("rankings", []):
        for competitor in ranking.get("competitor_rankings", []):
            rankings.append({
                "Rank": competitor.get("rank"),
                "Movement": competitor.get("movement"),
                "Points": competitor.get("points"),
                "Competitions Played": competitor.get("competitions_played"),
                "Competitor Name": competitor.get("competitor", {}).get("name"),
                "Competitor Country": competitor.get("competitor", {}).get("country_code")
            })
    return pd.DataFrame(rankings)

# Streamlit App
st.title("Tennis Competitors Rankings")
st.write("### Interactive Tennis Rankings Dashboard")

# Fetch and process data
data = fetch_data()
if data:
    df = process_data(data)
    
    if not df.empty:
        # Add filters
        country_filter = st.selectbox("Select a Country", ["All"] + sorted(df["Competitor Country"].dropna().unique().tolist()))
        rank_threshold = st.slider("Select Rank Threshold", int(df["Rank"].min()), int(df["Rank"].max()), int(df["Rank"].median()))
        
        # Apply filters
        if country_filter != "All":
            df = df[df["Competitor Country"] == country_filter]
        df = df[df["Rank"] <= rank_threshold]
        
        st.write("### Filtered Rankings Data")
        st.dataframe(df)
        
        # Bar chart for top competitors by points
        st.write("### Top Competitors by Points")
        top_competitors = df.nlargest(10, "Points")
        fig_points = px.bar(top_competitors, x="Competitor Name", y="Points", color="Points", title="Top 10 Competitors by Points")
        st.plotly_chart(fig_points)
        
        # Pie chart for country representation
        st.write("### Country Representation in Rankings")
        country_counts = df["Competitor Country"].value_counts().reset_index()
        country_counts.columns = ["Country", "Count"]
        fig_pie = px.pie(country_counts, names="Country", values="Count", title="Distribution of Competitors by Country")
        st.plotly_chart(fig_pie)
        
        # Scatter plot for Rank vs. Competitions Played
        st.write("### Rank vs. Competitions Played")
        fig_scatter = px.scatter(df, x="Rank", y="Competitions Played", color="Points", hover_data=["Competitor Name"], title="Rank vs. Competitions Played")
        st.plotly_chart(fig_scatter)
    else:
        st.warning("No ranking data available.")
else:
    st.warning("Failed to retrieve data.")