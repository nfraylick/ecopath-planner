import streamlit as st
import pandas as pd
import altair as alt
import datetime
from PIL import Image
import matplotlib.pyplot as plt
import random
import googlemaps
import pydeck as pdk
import streamlit.components.v1 as components
from pymongo import MongoClient

# Initialize Google Maps API Client
gmaps = googlemaps.Client(key='')

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client.ecopath

# Login and Registration
def login():
    with st.expander("Login/Register"):
        st.sidebar.subheader("Login / Register")
        
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        action = st.sidebar.selectbox("Action", ["Login", "Register"])
        
        if action == "Login" and username == "admin" and password == "wafflehacks":
            return {"username": username, "password": password, "name": "Admin"}
        
        if st.sidebar.button(action):
            if action == "Login":
                user = db.users.find_one({"username": username, "password": password})
                if user:
                    return user
                else:
                    st.sidebar.error("Invalid username or password.")
            else:
                user = db.users.find_one({"username": username})
                if user:
                    st.sidebar.error("Username already exists. Please choose a different username.")
                else:
                    db.users.insert_one({"username": username, "password": password, "name": ""})
                    st.sidebar.success("Registration successful. Please log in.")
        
    return None

def carbon_footprint():
    # Generate example data for carbon emissions
    date_range = pd.date_range(start=datetime.date(2023, 6, 1), end=datetime.date(2023, 6, 30), freq='D')
    carbon_emissions = []

    # Ensure both arrays have the same length
    if len(date_range) != len(carbon_emissions):
        st.error("Error: The arrays must have the same length.")
    else:
        # Create DataFrame from the example data
        data = {'Date': date_range, 'Carbon Emissions': carbon_emissions}
        df = pd.DataFrame(data)

        # Set up the chart using Altair
        chart = alt.Chart(df).mark_circle().encode(
            x=alt.X('Date:T', title='Date'),
            y=alt.Y('Carbon Emissions:Q', title='Carbon Emissions (kgCO2e)'),
            tooltip=['Date:T', 'Carbon Emissions:Q']
        ).interactive()

        # Display Carbon Emissions Graph
        st.header("Carbon Emissions")
        st.write("Daily carbon emissions for the month of June 2023")

        # Show the chart using Streamlit
        st.altair_chart(chart, use_container_width=True)
        st.write("This data is collected from energy consumption records, transportation data, and other relevent data sources.")
        # Calculate average carbon emissions for the month
        average_emissions = sum(carbon_emissions) / len(carbon_emissions)

        # Determine carbon footprint level
        if average_emissions <= 100:
            footprint_level = "Low"
            gauge_color = "green"
        elif average_emissions <= 120:
            footprint_level = "Moderate"
            gauge_color = "yellow"
        else:
            footprint_level = "High"
            gauge_color = "red"

        # Display Carbon Footprint Gauge
        st.header("Carbon Footprint")
        st.write("Your carbon footprint level for the month of June 2023")

        gauge_chart = alt.Chart(pd.DataFrame({'level': [footprint_level], 'value': [average_emissions]})).mark_bar(
            color=gauge_color
        ).encode(
            x=alt.X('value:Q', title='Carbon Emissions (kgCO2e)'),
            y=alt.Y('level:N', title=None),
            tooltip=['value:Q', 'level:N']
        )

        st.altair_chart(gauge_chart, use_container_width=True)

# List of Ideas
def display_ideas():
    st.header("Ideas to Lower Your Carbon Footprint")
    ideas = [
        "1. Reduce energy consumption at home by using energy-efficient appliances.",
        "2. Choose renewable energy sources for electricity generation.",
        "3. Opt for energy-efficient transportation options.",
        "4. Minimize the use of personal vehicles and consider carpooling or ridesharing.",
        "5. Practice eco-friendly commuting by telecommuting or using video conferencing.",
        "6. Choose sustainable and eco-friendly products with minimal packaging.",
        "7. Reduce water consumption and fix leaks.",
    ]

    for idea in ideas:
        st.write(idea)

def calculate_points(selected_route):
    points = 0
    
    if selected_route == "Walking":
        points = 10
    elif selected_route == "Biking":
        points = 20
    elif selected_route == "Public Transportation":
        points = 30
    elif selected_route == "Carpooling":
        points = 40
    
    return points

def show_leaderboard(leaderboard_df):
    st.subheader("Leaderboard")
    st.table(leaderboard_df)

def add_friends(leaderboard_df):
    st.subheader("Add Friends")
    friend_name = st.text_input("Friend's Name:")
    add_button = st.button("Add")

    if add_button and friend_name:
        # Generate random points for the new friend
        points = random.randint(100, 1000)

        # Create a new DataFrame with the friend's data
        new_friend_df = pd.DataFrame({"Name": [friend_name], "Points": [points]})

        # Concatenate the existing leaderboard DataFrame with the new friend's DataFrame
        leaderboard_df = pd.concat([leaderboard_df, new_friend_df], ignore_index=True)

        st.success(f"Friend {friend_name} added successfully!")

    return leaderboard_df

# Function to get the best route based on start destination, final destination, and mode of transportation
def get_best_route(start_location, end_location, mode_of_transport):
    directions_result = gmaps.directions(start_location, end_location, mode=mode_of_transport)
    
    # Retrieve the first route from the directions result
    route = directions_result[0]
    
    # Extract the relevant information from the route
    distance = route['legs'][0]['distance']['text']
    duration = route['legs'][0]['duration']['text']
    steps = route['legs'][0]['steps']
    
    # Prepare the route description
    route_description = f"Best Route:\n"
    route_description += f"Start Location: {start_location}\n"
    route_description += f"End Location: {end_location}\n"
    route_description += f"Distance: {distance}\n"
    route_description += f"Duration: {duration}\n\n"
    route_description += "Route Steps:\n"
    
    for i, step in enumerate(steps):
        route_description += f"{i+1}. {step['html_instructions']} ({step['distance']['text']}, {step['duration']['text']})\n"
    
    return route_description

def demo_map():
 
    # Embed the Google Maps JavaScript API demo with 3D street map
    components.html(
        
        height=500
    )

def demo_static():
    st.title("Biking Directions")
    # Load the static map image from a local file
    map_image = Image.open("")

    # Get the image size
    image_width, image_height = map_image.size

    # Calculate the initial zoom level based on the desired percentage
    zoom_factor = 1 # 100%
    initial_width = image_width * zoom_factor
    initial_height = image_height * zoom_factor

    # Display the static map image in Streamlit with initial zoom level
    st.image(map_image, width=initial_width, use_column_width=True)

def accessibility_settings():
    st.header("Accessibility Settings")
    
    # Dropdown menu for accessibility options
    accessibility_option = st.selectbox("Select an Accessibility Option", ("High Contrast Mode", "Text-to-Speech", "Font Size"))
    
    # High Contrast Mode option
    if accessibility_option == "High Contrast Mode":
        high_contrast_mode = st.checkbox("Enable High Contrast Mode")
        if high_contrast_mode:
            # Apply high contrast mode styling to the app
            st.write("High contrast mode enabled.")
            
        else:
            # Revert to default styling
            st.write("High contrast mode disabled.")
            
    
    # Text-to-Speech option
    elif accessibility_option == "Text-to-Speech":
        text_to_speech = st.checkbox("Enable Text-to-Speech")
        if text_to_speech:
            # Implement text-to-speech functionality
            st.write("Text-to-speech enabled.")
            
        else:
            # Disable text-to-speech functionality
            st.write("Text-to-speech disabled.")
            
    
    # Font Size option
    elif accessibility_option == "Font Size":
        font_size = st.slider("Adjust Font Size", 10, 24, 16)
        # Apply the selected font size to the app
        st.write(f"Font size set to {font_size}px.")
        st.write(f"Implement your font size changes here.")


#Main app
def main():
    
    # User Registration and Login
    st.title("Ecopath Planner")
    st.write("The app that optimizes your routes, tracks your carbon footprint, and offers accessibility settings to create a greener future.")
    is_logged_in = login()
    if is_logged_in:
        st.empty()
        # Create anchor at the top of the page
        st.markdown('<a name="top"></a>', unsafe_allow_html=True)
        # Scroll to the top of the page
        st.markdown('<script>window.location.hash = "top";</script>', unsafe_allow_html=True)

        st.title("Welcome back, Admin")
        # Draw carbon footprint gauge
        carbon_footprint()

        # Display list of ideas to lower carbon footprint
        display_ideas()
        
        user = {"points": [100, 200, 300, 400, 500, 600, 700]}
        goal = 1000

        st.header("EcoPath Route Planner")

        # Start Destination
        start_location = st.text_input("Enter Start Destination:")

        # Final Destination
        end_location = st.text_input("Enter Final Destination:")

        # Mode of Transportation
        mode_of_transport = st.selectbox("Select Mode of Transportation:", ["Driving", "Walking", "Biking", "Transit"])
        demo_points_earned = 0
        if st.button("Get Best Route"):
            if start_location and end_location:
                demo_static()
                st.write(f"You earned 200 points for selecting {mode_of_transport}.")
                # route = get_best_route(start_location, end_location, mode_of_transport)
                st.success("Best route successfully generated!")
                demo_points_earned = 200
                # st.write(route)
            else:
                st.warning("Please enter both start and final destinations.")
                demo_points_earned = 0
        else:
            demo_map()

        # Points Calculation
        points_earned = calculate_points(mode_of_transport)
        
        user["points"].append(user["points"][-1] + demo_points_earned)  # Update user's points data


        

        # Redeem Points
        redemption_options = [
            {"name": "Eco-Friendly Product", "points_required": 100, "description": "Get a reusable water bottle.", "image": ""},
            {"name": "Discount", "points_required": 200, "description": "Get 20% off on eco-friendly clothing.", "image": ""},
            {"name": "Voucher", "points_required": 300, "description": "Get a voucher for a sustainable restaurant.", "image": ""}
        ]

        st.subheader("Redemption Options")
        
        

        for option in redemption_options:
            st.write(f"{option['name']} ({option['points_required']} points): {option['description']}")
            image = Image.open(option['image'])
            st.image(image, use_column_width=200)
            st.markdown("\n\n\n")

            redeem = st.button(f"Redeem {option['name']}")
            if redeem:
                if user["points"][-1] >= option['points_required']:
                    st.success(f"Congratulations! You have successfully redeemed {option['name']}.")
                    user["points"][-1] -= option['points_required'] # Update user's total points
                else:
                    st.warning(f"You do not have enough points to redeem {option['name']}.")
                

            st.markdown("\n\n\n")
        st.write("Total Points: ", user["points"][-1])
        


        st.subheader("Progress towards your goal")
        # Graph showing progress towards goal
        plt.figure(figsize=(8, 4), facecolor='black')  # Set background color to black
        plt.plot(user["points"], marker="o", color="white")
        plt.plot([0, len(user["points"]) - 1], [goal, goal], "r--", color="red")
        plt.xlabel("Time", color="white")
        plt.ylabel("Points", color="white")
        plt.title("Points Progress", color="white")
        plt.tick_params(axis='x', colors='white')  # Set tick color to white
        plt.tick_params(axis='y', colors='white')  # Set tick color to white

        # Set the background color and edge color of the plot area to black
        plt.gca().set_facecolor('black')
        plt.gca().spines['bottom'].set_color('white')  # Set bottom spine color to white
        plt.gca().spines['top'].set_color('white')  # Set top spine color to white
        plt.gca().spines['left'].set_color('white')  # Set left spine color to white
        plt.gca().spines['right'].set_color('white')  # Set right spine color to white

        # Set the color of the x and y axis labels to white
        plt.xlabel("Time", color="white")
        plt.ylabel("Points", color="white")

        # Set the title color to white
        plt.title("Points Progress", color="white")

        # Remove the background grid lines
        plt.grid(False)

        # Remove extra whitespace
        plt.tight_layout()

        # Display the plot
        st.pyplot(plt, bbox_inches='tight', pad_inches=0)

        # Show leaderboard
        leaderboard_data = {
            "Name": ["John F.", "Emily M.", "Michael S.", "Sarah D."],
            "Points": [800, 700, 600, 500]
        }
        leaderboard_df = pd.DataFrame(leaderboard_data)

        # Enable/Disable add freinds
        with st.expander("Enable Add Friends"):
            # Add friends
            leaderboard_df = add_friends(leaderboard_df)
            
        show_leaderboard(leaderboard_df)

        accessibility_settings()

if __name__ == "__main__":
    main()



