import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Directory pathing
curr_dir = os.path.dirname(__file__)
csv_path = os.path.relpath('../synthetic-data/Dummy_Data - Available_Property.csv', start=curr_dir)

# Data filtering
df = pd.read_csv(csv_path)

def filter_data(budget_range, rent_or_buy, min_rooms, max_rooms, districts, lease_length, property_type):
    '''
    This function filters the data according to the user's choices
    returns a filtered pandas dataframe
    '''
    if rent_or_buy == 'Rent':
        filtered_data = df[(df['Rent'] >= budget_range[0]) & (df['Rent'] <= budget_range[1])]
    else:
        filtered_data = df[(df['Cost'] >= budget_range[0]) & (df['Cost'] <= budget_range[1])] # Change the slider range dynamically if it's cost
    
    filtered_data = filtered_data[
        (filtered_data['Number of rooms'] >= min_rooms) & 
        (filtered_data['Number of rooms'] <= max_rooms) & 
        (filtered_data['District/Arrondissement'].isin(districts)) &
        (filtered_data['Lease Duration (Months)'] >= lease_length) &
        (filtered_data['Property_Type'].isin(property_type))
    ]

    if co_living:
        filtered_data = filtered_data[filtered_data['Co-Living'] == 1]    
    if pet_friendly:
        filtered_data = filtered_data[filtered_data['Pets allowed'] == 1]
    
    return filtered_data

# Streamlit UI
st.title('Paris Property Listings')

# Sidebar for user inputs, the right portion would be dedicated for user-preview
st.sidebar.header('Please Provide your preferences')

# Initial choice of rent/purchase
# Docs:- https://docs.streamlit.io/develop/api-reference/widgets/st.radio
rent_or_buy = st.sidebar.radio('Do you want to rent or buy a property?', ('Rent', 'Buy'))

# Budget range slider
# Docs:- https://docs.streamlit.io/develop/api-reference/widgets/st.slider

if rent_or_buy == 'Rent':
    budget_range = st.sidebar.slider(
    'Select your budget range (in euros):', 
    min_value=0, 
    max_value=10000, 
    value=(500, 2000), # Default Range
    step=100 # Increase by 100 Euros
)

if rent_or_buy == 'Buy':
    budget_range = st.sidebar.slider(
    'Select your budget range (in euros):', 
    min_value=100000, 
    max_value=500000, 
    value=(100000, 200000), # Default Range
    step=10000 # Increase by 10000 Euros
)

# Number of rooms slider
min_rooms = st.sidebar.slider('Minimum Number of Rooms:', 0, 10, 1)
max_rooms = st.sidebar.slider('Maximum Number of Rooms:', 1, 10, 5)

# District preference
# Docs:- https://docs.streamlit.io/develop/api-reference/widgets/st.multiselect
districts = st.sidebar.multiselect(
    'Preferred Arrondissement/District:', 
    options=df['District/Arrondissement'].unique(), 
    default=df['District/Arrondissement'].unique() # Select all by default
)

# Property Type Preference
property_type = st.sidebar.multiselect(
    'Choose your Property Preference:',
    options=df['Property_Type'].unique(), 
    default=df['Property_Type'].unique()  # Select all by default
)

# Lease length
# Docs:- https://docs.streamlit.io/develop/api-reference/widgets/st.number_input
lease_length = st.sidebar.number_input(
    'Minimum Lease Length (months):', 
    min_value=0, 
    step=1, 
    value=6  # Default lease length
)

# Checkbox docs :- https://docs.streamlit.io/develop/api-reference/widgets/st.checkbox
co_living = st.sidebar.checkbox('Do you Prefer Co-living?', value=False)
pet_friendly = st.sidebar.checkbox('Do you Require Property to be Pet-Friendly?', value=False)

# Call the function to Filter data, All options to filter data should be made available before this step
filtered_df = filter_data(budget_range, rent_or_buy, min_rooms, max_rooms, districts, lease_length, property_type)

# Render KPI Card
# Function to render a KPI card with CSS
def render_kpi_card(title, value, footer_icon, footer_text, gradient_start, gradient_end):
    st.markdown(
        f"""
        <style>
        .kpi-card {{
            background: linear-gradient(135deg, {gradient_start}, {gradient_end});
            border-radius: 15px;
            padding: 20px;
            color: black;
            text-align: center;
            font-weight: bold;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
        }}
        .kpi-value {{
            font-size: 36px;
        }}
        .kpi-label {{
            font-size: 18px;
            color: black;
        }}
        .kpi-footer {{
            color: black;
            font-size: 14px;
            margin-top: 5px;
        }}
        </style>
        """, unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-footer">{footer_icon} {footer_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Display the title
st.title("Property Listings KPI Dashboard")

# Create three columns for the KPI cards
col1, col2, col3 = st.columns(3)

# Render each KPI card in its respective column with different gradient colors
with col1:
    render_kpi_card(
        title="Total Properties Found",
        value=len(filtered_df),
        footer_icon="🔍",
        footer_text="Market Overview",
        gradient_start="#ff7eb3",  # Light Pink
        gradient_end="#ff758c"     # Pink
    )

with col2:
    render_kpi_card(
        title=f"Average {rent_or_buy}",
        value=round(filtered_df[rent_or_buy].mean()),
        footer_icon="💲",
        footer_text="Rental Market",
        gradient_start="#FFFFFF",  # Light Green
        gradient_end="#000000"     # Green
    )

with col3:
    render_kpi_card(
        title="Average Size",
        value=round(filtered_df['Size'].mean()),
        footer_icon="💰",
        footer_text="Buying Market",
        gradient_start="#1CB5E0",  # Light Blue
        gradient_end="#000851"     # Blue
    )
    
# If no properties found
if filtered_df.empty:
    st.warning('No properties found matching your criteria. Please adjust your filters.')

# Plotting the map using Plotly
# Docs:- https://plotly.com/python/scattermapbox/

# Custom colors for property types
# Color pallete:- https://colorhunt.co/
color_map = {
    'Apartment': '#FF8225',
    'Villa': '#B43F3F',
    'Duplex': '#EF5A6F'
}

fig = px.scatter_mapbox(
    filtered_df,
    lat=filtered_df['Latitude'], 
    lon=filtered_df['Longitude'],
    color='Property_Type',
    size='Size', # Size of property in sqare feet
    hover_name='Address',
    hover_data={
        'Rent': True, 
        'Cost': True, 
        'Number of rooms': True, 
        'Size': True,
        'District/Arrondissement': True,
    },
    color_discrete_map=color_map,
    zoom=12,
    height=600
)

# mapbox-layers :- https://plotly.com/python/mapbox-layers/
fig.update_layout(
    mapbox_style='carto-darkmatter',
    mapbox_center={'lat': 48.8566, 'lon': 2.3522},
    margin={'r':0,'t':0,'l':0,'b':0},
    modebar={
        'orientation': 'v',
    },
    legend_title='Property Type',
    legend_y=0.5,
    uirevision='constant'
)
fig.update_geos(
    showcountries=True
)

fig.update_mapboxes(
    bounds={
        'north': 51.138093815546775,
        'west': -5.979299805444654,
        'south': -42.11925588687173,
        'east': 8.401274768380318
    }
)

st.plotly_chart(fig)

# Display additional data about the filtered properties
if not filtered_df.empty:
    st.subheader('Top 5 options for you would be')
    st.dataframe(filtered_df[:5])

    # Download button for filtered data
    # Generate a printable PDF file with necessary information about the properties
    st.download_button(
        label='Download Filtered Data',
        data=filtered_df.to_csv(index=False),
        file_name='filtered_properties.csv',
        mime='text/csv',
    )

    # Display summary statistics
    # Could generate an statistical numeric / Index to find out which would be the best option
    # Which one would have the most:- Size, Number of rooms, Lease Length at the least cost - Use this information to plot a scatter plot
    # Example from KF24 PG54
    st.subheader('Summary Statistics')
    st.write(filtered_df.describe())

    # Histogram of property prices
    
    st.subheader('Price Distribution')
    price_column = 'Cost' if rent_or_buy == 'Buy' else 'Rent'
    fig_hist = px.histogram(filtered_df, x=price_column, nbins=20, title='Price Distribution')
    st.plotly_chart(fig_hist)