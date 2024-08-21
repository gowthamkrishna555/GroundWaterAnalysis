import streamlit as st
import pandas as pd
import plotly.express as px
import json
import random

# Load data
with open('karnataka.json', 'r') as f:
    geojson = json.load(f)


df = pd.read_csv('water_data5.csv')

# Define color options for the dropdown
color_options = ['cl', 'k', 'ph_gen', 'Level (m)']
st.set_page_config(layout="wide", page_title="Groundwater Analysis", page_icon=":chart_with_upwards_trend:")

# Add background image using Streamlit markdown
if not st.session_state.get('started', False):
    bg_img = '''
    <style>
            [data-testid="stAppViewContainer"] {
            background-image: url('https://img.freepik.com/free-photo/tranquil-pond-reflects-beauty-nature-generated-by-ai_188544-28048.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            }
    </style>
    '''
    st.markdown(bg_img, unsafe_allow_html=True)
    st.title("Welcome to Groundwater Analysis")
    if st.button('Get Started'):
        st.session_state.started = True
else:
    st.title("Groundwater Analysis")

    # Hide the "Get Started" button on the next page
    st.session_state.started = True

    selected_color = st.selectbox("Select Color:", color_options, index=0)

    year_slider = st.slider("Select Year:", min_value=2018, max_value=2020, value=2018, step=1)

    # Filter data based on selected year
    filtered_df = df[df['Date Collection'] == year_slider].copy()  # Create a copy to avoid the SettingWithCopyWarning
    filtered_df['ca'].fillna(0, inplace=True)  # You can replace NaN with 0 or any other value

    # Update choropleth map
    fig_choropleth = px.choropleth_mapbox(filtered_df,
                                          geojson=geojson,
                                          locations='District',
                                          color=selected_color,
                                          featureidkey="properties.district",
                                          center={"lat": filtered_df['Latitude'].mean(), "lon": filtered_df['Longitude'].mean()},
                                          mapbox_style="carto-positron",
                                          zoom=5,
                                          hover_data=['Station Name', 'Agency Name', 'District', selected_color])
    fig_choropleth.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # Update scatter plot to show Karnataka map
    fig_scatter = px.scatter_geo(df,
                                 lat=df['Latitude'],
                                 lon=df['Longitude'],
                                 scope='asia',
                                 template='plotly',
                                 color=selected_color,
                                 hover_data=['Station Name', 'Agency Name', 'District', selected_color])
    fig_scatter.update_geos(fitbounds="locations", visible=False)

    # Display choropleth map
    st.plotly_chart(fig_choropleth)

    # Display scatter plot
    scatter_chart = st.plotly_chart(fig_scatter)

    # Additional Plots
    for additional_color in color_options:
        if additional_color == selected_color:
            # Line Plot with more data
            fig_line = px.line(filtered_df, x='Date Collection', y=[selected_color, 'ca', 'mg', 'k'],
                              color='District', labels={'variable': 'Parameter', 'value': 'Value'},
                              title=f"{selected_color.capitalize()} and Other Parameters Over Time")
            st.plotly_chart(fig_line)

            # Bar Chart
            fig_bar = px.bar(filtered_df, x='District', y=selected_color)
            st.plotly_chart(fig_bar)

            # Histogram
            fig_hist = px.histogram(filtered_df, x=selected_color, y='District', nbins=30)
            st.plotly_chart(fig_hist)

            # Bubble Plot
            fig_bubble = px.scatter(filtered_df, x='Longitude', y='Latitude', size='ca', color='District')
            st.plotly_chart(fig_bubble)

            # 3D Scatter Plot
            fig_3d = px.scatter_3d(filtered_df, x='k', y='ph_gen', z=selected_color, color='District')
            st.plotly_chart(fig_3d)

            # Select a district
            selected_district = st.selectbox("Select District:", filtered_df['District'].unique())
            st.write(f"Selected District: {selected_district}")

            # Suggested Crops based on Conditions
            def suggest_crops(cl, k, ph_gen, level_m):
                # Define conditions based on the features
                conditions = [
                    (5.5 <= ph_gen <= 7.5 and 100 <= k <= 300 and 20 <= cl <= 60 and level_m >= 1.5, "Rice"),
                    (6.0 <= ph_gen <= 7.5 and 150 <= k <= 250 and 30 <= cl <= 50 and level_m >= 1.0, "Wheat"),
                    (5.5 <= ph_gen <= 7.5 and 80 <= k <= 200 and 25 <= cl <= 55 and level_m >= 1.2, "Barley"),
                    (6.5 <= ph_gen <= 8.0 or 120 <= k <= 280 or 15 <= cl <= 70 or level_m >= 1.3, "Maize"),
                    (5.0 <= ph_gen <= 7.0 or 80 <= k <= 220 or 20 <= cl <= 50 or level_m >= 1.0, "Oats"),
                    (6.0 <= ph_gen <= 7.5 or 100 <= k <= 250 or 30 <= cl <= 60 or level_m >= 1.4, "Soybeans"),
                    (5.8 <= ph_gen <= 7.2 or 130 <= k <= 260 or 25 <= cl <= 55 or level_m >= 1.1, "Peas"),
                    (6.2 <= ph_gen <= 8.0 or 120 <= k <= 240 or 20 <= cl <= 65 or level_m >= 1.2, "Lentils"),
                    (6.0 <= ph_gen <= 7.5 or 90 <= k <= 200 or 25 <= cl <= 60 or level_m >= 1.3, "Sunflower"),
                    (5.5 <= ph_gen <= 7.0 or 150 <= k <= 300 or 15 <= cl <= 50 or level_m >= 1.0, "Cotton"),
                    # Add more conditions and crops as needed
                ]

                # Shuffle conditions to randomize suggestions
                random.shuffle(conditions)

                # Collect all crops that meet at least one condition
                eligible_crops = [crop for condition, crop in conditions if condition]

                # Return a random crop from the list of eligible crops, guaranteed to be non-empty
                return random.choice(eligible_crops)

            # Predict crop name for the selected region
            suggested_crop = suggest_crops(*filtered_df[['cl', 'k', 'ph_gen', 'Level (m)']].mean())

            # Display the suggested crop for the selected district
            st.write(f"Suggested Crop for {selected_district}:")
            st.write(suggested_crop)
