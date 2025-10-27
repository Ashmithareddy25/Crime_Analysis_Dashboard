import streamlit as st
import pandas as pd
import altair as alt
import folium
from streamlit_folium import folium_static
import requests

# Set page config
st.set_page_config(page_title="Crime Analysis Dashboard", layout="wide")

# --- Background Styling ---

st.markdown(
    """
    <style>
        .stApp {
            background-image: url('https://www.shutterstock.com/shutterstock/photos/2238349149/display_1500/stock-photo-magnifier-fingerprint-blood-drops-microscope-map-and-police-form-vintage-background-on-the-2238349149.jpg');
            background-size: cover;
            background-position: center;
        }
        .stApp::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(255, 255, 255, 0.6);  /* Lighter overlay */
            z-index: -1;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            text-align: center;
        }
        .stTable thead th {
            background-color: rgba(44, 62, 80, 0.8);  /* Darker background for table headers */
            color: white;
        }
        .stTable tbody td {
            background-color: rgba(255, 255, 255, 0.7);  /* Slightly opaque background for table rows */
            color: #2c3e50;
        }
    </style>
    """,
    unsafe_allow_html=True
)



# --- Tabs Navigation ---
tab1, tab2, tab3, tab4 = st.tabs(["\U0001F3E0 Introduction", "\U0001F4CA Visualizations", "\U0001F693 Real-Time Dashboard", "\U0001F6E1️ Safety Checker"])

# --- Tab 1: Introduction ---
with tab1:
    st.markdown("""
        <h1 style='text-align: center; color: #1e3799;'>Comprehensive Interactive Crime Analysis Dashboard</h1>
    """, unsafe_allow_html=True)

    st.subheader("\U0001F465 Team 11: Ashmitha Reddy, Adbuth Kumar Kasturi, Akshara Guvvala")
    st.markdown("""
        ### \U0001F3AF Objective:
        Analyze crime data, trends, weapon types, gender-based crime distribution, and create a real-time safety checking tool for different US cities.

        ### \U0001F4CA Deliverables:
        - Crime trends across states and years.
        - Top dangerous and safest states.
        - Weapon and bias crime analysis.
        - Real-time city-wise crime data.
        - Crime safety checker tool.
    """)

# --- Load datasets common for Tab2 ---
crime_data_usa = pd.read_csv(r'Data\crime_data.csv')
crime_data_ml = pd.read_csv(r'Data\crime__data.csv')
weapon_data = pd.read_csv(r'Data\cleaned_weapon_data.csv')
hate_crimes = pd.read_csv(r'Data\Hate_Crimes.csv')

weapon_data.rename(columns={"Unnamed: 0": "Weapon Type"}, inplace=True)


# --- Tab 2: Visualizations ---
with tab2:
    # Custom styles for background and text
    

    # Title with custom styling
    st.markdown("""
        <h1 style='text-align: center; color: #1e3799;'>Comprehensive Interactive Crime Analysis Dashboard</h1>
    """, unsafe_allow_html=True)

    # Sidebar Styling
    st.sidebar.markdown("""
        <h2 style='color: #2980b9;'>Filters</h2>
    """, unsafe_allow_html=True)

    # Sidebar Filters
    year_filter = st.sidebar.slider("Select Year", int(crime_data_usa["Year"].min()), int(crime_data_usa["Year"].max()), int(crime_data_usa["Year"].max()))
    crime_type_filter = st.sidebar.multiselect("Select Crime Types", crime_data_usa["Crime Type"].unique(), default=crime_data_usa["Crime Type"].unique())
    states_filter = st.sidebar.multiselect("Select States", crime_data_usa["City"].unique(), default=crime_data_usa["City"].unique())
    weapon_filter = st.sidebar.multiselect(
        "Select Weapon Types",
        weapon_data["Weapon Type"].dropna().unique(),
        default=weapon_data["Weapon Type"].dropna().unique()
    )
    # Sidebar filter for Hate Crimes
    bias_filter = st.sidebar.multiselect(
        "Select Bias Motivation",
        hate_crimes["Bias"].dropna().unique(),
        default=hate_crimes["Bias"].dropna().unique()
    )

    # Filtered Hate Crimes data
    hate_crimes_filtered = hate_crimes[hate_crimes["Bias"].isin(bias_filter)]

    # Correct filtering
    weapon_filtered = weapon_data[weapon_data["Weapon Type"].isin(weapon_filter)]


    # Map city names to predefined coordinates
    city_coordinates = {
        "New York": (40.7128, -74.0060),
        "Los Angeles": (34.0522, -118.2437),
        "Chicago": (41.8781, -87.6298),
        "Houston": (29.7604, -95.3698),
        "Philadelphia": (39.9526, -75.1652),
        "Phoenix": (33.4484, -112.0740),
        "San Antonio": (29.4241, -98.4936),
        "San Diego": (32.7157, -117.1611),
        "Dallas": (32.7767, -96.7970),
        "San Jose": (37.3382, -121.8863)
    }

    # Add Latitude and Longitude to crime_data_usa
    crime_data_usa["Latitude"] = crime_data_usa["City"].apply(lambda x: city_coordinates.get(x, (None, None))[0])
    crime_data_usa["Longitude"] = crime_data_usa["City"].apply(lambda x: city_coordinates.get(x, (None, None))[1])

    # Filtered Data
    data_filtered = crime_data_usa[(crime_data_usa["Year"] == year_filter) & (crime_data_usa["Crime Type"].isin(crime_type_filter)) & (crime_data_usa["City"].isin(states_filter))]

    # Ensure Latitude and Longitude exist in filtered data
    data_filtered = data_filtered.dropna(subset=["Latitude", "Longitude"], how='any')


    # Crime Trends Over the Years Based on Selected States
    st.subheader("Crime Trends Over the Years")
    crime_trend_filtered = crime_data_usa[crime_data_usa["City"].isin(states_filter)]
    crime_trend = alt.Chart(crime_trend_filtered).mark_line().encode(
        x="Year:O",
        y="sum(Total Crimes):Q",
        color="City:N",
        tooltip=["Year", "sum(Total Crimes)", "City"]
    ).interactive()
    st.altair_chart(crime_trend, use_container_width=True)

    # Crime Distribution by City
    st.subheader("Crime Distribution by City")
    city_crime = alt.Chart(data_filtered).mark_bar().encode(
        x=alt.X("City:N", sort="-y"),
        y="sum(Total Crimes):Q",
        color="Crime Type:N",
        tooltip=["City", "sum(Total Crimes)"]
    ).interactive()
    st.altair_chart(city_crime, use_container_width=True)

    # Top 5 Safest and Most Dangerous States Based on Selected Year
    st.subheader("Top 5 Safest and Most Dangerous States")
    state_crime_totals = data_filtered.groupby("City")["Total Crimes"].sum().reset_index()
    top_5_dangerous = state_crime_totals.nlargest(5, "Total Crimes")
    top_5_safest = state_crime_totals.nsmallest(5, "Total Crimes")

    col1, col2 = st.columns(2)
    col1.subheader("Top 5 Most Dangerous States")
    col1.dataframe(top_5_dangerous)
    col2.subheader("Top 5 Safest States")
    col2.dataframe(top_5_safest)

    # US Heat Map for Crime Density with Bigger Circles and State Names on Hover
    st.subheader("Crime Heat Map of the USA")
    st.markdown("""
        - 🔴 **Red**: Top 5 most dangerous areas (highest crime rates)
        - 🟢 **Green**: Top 5 safest areas (lowest crime rates)
        - 🔵 **Blue**: Other locations
    """)

    us_map = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
    for index, row in data_filtered.iterrows():
        color = 'red' if row["City"] in top_5_dangerous["City"].values else 'green' if row["City"] in top_5_safest["City"].values else 'blue'
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=max(row["Total Crimes"] / 500, 10),  # Increased circle size for better visibility
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            tooltip=f"{row['City']}: {row['Total Crimes']} crimes"
        ).add_to(us_map)
    folium_static(us_map)


    # Crime Comparisons Between States
    st.subheader("Crime Comparison Between Selected States")
    state_comparison = alt.Chart(data_filtered).mark_bar().encode(
        x="City:N",
        y="sum(Total Crimes):Q",
        color="Crime Type:N",
        tooltip=["City", "sum(Total Crimes)"]
    ).interactive()
    st.altair_chart(state_comparison, use_container_width=True)

    st.subheader("Crimes by Weapon Type")

    weapon_chart = alt.Chart(weapon_filtered).mark_bar().encode(
        x=alt.X("Weapon Type:N", sort="-y"),  # <<< Correct field name
        y=alt.Y("Robbery:Q"),                 # or you can change to "Assault Offenses" if you want
        color="Weapon Type:N",
        tooltip=["Weapon Type", "Robbery"]
    ).interactive()

    st.altair_chart(weapon_chart, use_container_width=True)

    st.subheader("Weapon Type Distribution (Top 5)")

    top5_weapons = weapon_filtered.groupby("Weapon Type")["Robbery"].sum().nlargest(5).reset_index()

    pie_chart = alt.Chart(top5_weapons).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Robbery", type="quantitative"),
        color=alt.Color(field="Weapon Type", type="nominal"),
        tooltip=["Weapon Type", "Robbery"]
    )

    st.altair_chart(pie_chart, use_container_width=True)

    st.subheader("Top Bias Motivations in Hate Crimes")

    bias_counts = hate_crimes_filtered["Bias"].value_counts().reset_index()
    bias_counts.columns = ["Bias", "Count"]

    bias_chart = alt.Chart(bias_counts).mark_bar().encode(
        x=alt.X("Bias:N", sort="-y"),
        y="Count:Q",
        color="Bias:N",
        tooltip=["Bias", "Count"]
    ).interactive()

    st.altair_chart(bias_chart, use_container_width=True)

    # Offender and Victim Demographics
    st.subheader("Offender and Victim Demographics")
    offender_gender = crime_data_ml["Offender_Gender"].value_counts().reset_index()
    offender_gender.columns = ["Gender", "Count"]  # Rename columns for clarity
    offender_chart = alt.Chart(offender_gender).mark_bar().encode(
        x="Gender:N",
        y="Count:Q",
        color="Gender:N",
        tooltip=["Gender", "Count"]
    )
    st.altair_chart(offender_chart, use_container_width=True)

    # Gender-Based Crime Distribution
    st.subheader("Gender-Based Crime Distribution")
    victim_gender_counts = crime_data_ml["Victim_Gender"].value_counts().reset_index()
    victim_gender_counts.columns = ["Gender", "Count"]  # Rename columns for clarity
    victim_pie_chart = alt.Chart(victim_gender_counts).mark_arc().encode(
        theta="Count:Q",
        color="Gender:N",
        tooltip=["Gender", "Count"]
    )
    st.altair_chart(victim_pie_chart, use_container_width=True)


# Tab3 and Tab4 are continued below...
# --- Tab 3: Real-Time Dashboard ---
with tab3:
    st.header("🚓 Real-Time Crime Data - Multi-City API Integration")

    city_option = st.selectbox(
        "Select a city to view real-time crime data:",
        ("Chicago", "New York City", "Los Angeles")
    )

    if city_option == "Chicago":
        url = "https://data.cityofchicago.org/resource/ijzp-q8t2.json?$limit=500"
        response = requests.get(url)
        data = pd.DataFrame(response.json())

    elif city_option == "New York City":
        url = "https://data.cityofnewyork.us/resource/qgea-i56i.json?$limit=500"
        response = requests.get(url)
        data = pd.DataFrame(response.json())

    elif city_option == "Los Angeles":
        data = pd.DataFrame({
            "date": ["2025-04-25", "2025-04-26"],
            "crime_type": ["Robbery", "Assault"],
            "location": ["Downtown LA", "Hollywood Blvd"],
            "latitude": [34.0522, 34.0928],
            "longitude": [-118.2437, -118.3287]
        })

    if not data.empty:
        st.subheader(f"Recent Crimes in {city_option}")
        st.dataframe(data.head())

        # Dynamic column mapping
        crime_type_col = None
        if city_option == "Chicago":
            crime_type_col = "primary_type"
        elif city_option == "New York City":
            crime_type_col = "ofns_desc"
        elif city_option == "Los Angeles":
            crime_type_col = "crime_type"

        if crime_type_col and crime_type_col in data.columns:
            top_crimes = data[crime_type_col].value_counts().head(10).reset_index()
            top_crimes.columns = ['Crime Type', 'Count']
            st.bar_chart(top_crimes.set_index('Crime Type'))
        else:
            st.warning(f"Crime type column not found for {city_option}")

        # Map Section
        st.subheader(f"Crime Locations in {city_option}")
        if city_option != "Los Angeles":
            m = folium.Map(location=[41.8781, -87.6298], zoom_start=10)
            for _, row in data.iterrows():
                try:
                    lat = float(row.get("latitude"))
                    lon = float(row.get("longitude"))
                    crime_label = row.get(crime_type_col, "Crime")
                    folium.Marker(
                        location=[lat, lon],
                        popup=crime_label,
                        icon=folium.Icon(color="red")
                    ).add_to(m)
                except:
                    continue
            folium_static(m)
        else:
            m = folium.Map(location=[34.0522, -118.2437], zoom_start=10)
            for _, row in data.iterrows():
                folium.Marker(
                    location=[row["latitude"], row["longitude"]],
                    popup=row["crime_type"],
                    icon=folium.Icon(color="red")
                ).add_to(m)
            folium_static(m)
    else:
        st.warning("No live data available right now.")

# --- Tab 4: Safety Checker Tool ---
with tab4:
    st.header("🛡️ Crime Safety Checker Tool")

    city_selected = st.selectbox(
        "Select a city to check safety:",
        ("Chicago", "New York City", "Los Angeles")
    )

    area_input = st.text_input(
        "Enter area/neighborhood (Optional)", 
        placeholder="Example: Englewood / Brooklyn / Downtown LA"
    )

    if st.button("Check Safety"):
        with st.spinner('Fetching latest crime data...'):
            if city_selected == "Chicago":
                url = "https://data.cityofchicago.org/resource/ijzp-q8t2.json?$limit=1000"
                response = requests.get(url)
                data = pd.DataFrame(response.json())

            elif city_selected == "New York City":
                url = "https://data.cityofnewyork.us/resource/qgea-i56i.json?$limit=1000"
                response = requests.get(url)
                data = pd.DataFrame(response.json())

            elif city_selected == "Los Angeles":
                data = pd.DataFrame({
                    "date": ["2025-04-25", "2025-04-26", "2025-04-27"],
                    "crime_type": ["Robbery", "Assault", "Theft"],
                    "location": ["Downtown LA", "Hollywood Blvd", "Santa Monica"],
                    "latitude": [34.0522, 34.0928, 34.0195],
                    "longitude": [-118.2437, -118.3287, -118.4912]
                })

        if not data.empty:
            # Area filtering
            if area_input:
                if city_selected == "Chicago" and "location_description" in data.columns:
                    data_area = data[data["location_description"].str.contains(area_input, case=False, na=False)]
                elif city_selected == "New York City" and "boro_nm" in data.columns:
                    data_area = data[data["boro_nm"].str.contains(area_input, case=False, na=False)]
                elif city_selected == "Los Angeles" and "location" in data.columns:
                    data_area = data[data["location"].str.contains(area_input, case=False, na=False)]
                else:
                    data_area = pd.DataFrame()
            else:
                data_area = data

            # Crime Count
            crime_count = len(data_area)

            # Safety Evaluation
            st.subheader("Safety Evaluation 🚔")
            if crime_count == 0:
                st.success("✅ No recent crimes reported. Safe to visit!")
            elif crime_count <= 20:
                st.success(f"✅ Only {crime_count} crimes reported recently. Generally Safe!")
            elif crime_count <= 50:
                st.warning(f"⚠️ {crime_count} crimes reported. Moderate Risk. Please be cautious.")
            else:
                st.error(f"❌ {crime_count} crimes reported! High Risk Area. Avoid if possible.")

            # Display Recent Incidents
            if not data_area.empty:
                st.subheader("Recent Incidents 📰")
                if city_selected == "Chicago" and "primary_type" in data_area.columns:
                    st.dataframe(data_area[["date", "primary_type", "location_description"]].head(10))
                elif city_selected == "New York City" and "ofns_desc" in data_area.columns:
                    st.dataframe(data_area[["cmplnt_fr_dt", "ofns_desc", "boro_nm"]].head(10))
                elif city_selected == "Los Angeles" and "crime_type" in data_area.columns:
                    st.dataframe(data_area[["date", "crime_type", "location"]].head(10))

            # Top Dangerous Areas
            st.subheader("⚠️ Most Dangerous Areas Recently:")
            if city_selected == "Chicago" and "location_description" in data.columns:
                top_areas = data["location_description"].value_counts().head(5).reset_index()
                top_areas.columns = ["Area", "Crime Count"]
                st.table(top_areas)
            elif city_selected == "New York City" and "boro_nm" in data.columns:
                top_areas = data["boro_nm"].value_counts().head(5).reset_index()
                top_areas.columns = ["Borough", "Crime Count"]
                st.table(top_areas)
            elif city_selected == "Los Angeles" and "location" in data.columns:
                top_areas = data["location"].value_counts().head(5).reset_index()
                top_areas.columns = ["Area", "Crime Count"]
                st.table(top_areas)

        else:
            st.error("Failed to fetch crime data. Please try again later.")

# Footer
st.markdown("""
    <hr>
    <p style='text-align: center; color: #2c3e50; font-size: 22px;'>
        Created by Ashmitha Reddy, Adbuth Kumar Kasturi, and Akshara guvvala
    </p>
""", unsafe_allow_html=True)
