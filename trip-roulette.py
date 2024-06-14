import pandas as pd
import streamlit as st
import random
import datetime as dt
import urllib.parse
from streamlit_folium import st_folium
import folium


def load_dataset(path):
    df = pd.read_csv(path, sep=',').rename(
        columns={"lat": "LAT", "lng": "LON"}).sort_values('country')
    return df


def choose_random_city(df: pd.DataFrame, countries_selected=None, admin_name_selected=None):
    if countries_selected != []:
        df = df.loc[df['country'].isin(
            countries_selected)].reset_index(drop=True)
        if admin_name_selected != []:
            df = df.loc[df['admin_name'].isin(
                admin_name_selected)].reset_index(drop=True)

    random_index = random.choice(df.index)
    df = df.iloc[random_index]
    return df, pd.DataFrame({"LAT": [float(df["LAT"])], "LON": [float(df["LON"])]})


def booking_options_expedia(city_chosen):
    now = dt.datetime.now()
    tommorow = now + dt.timedelta(days=2)

    with st.sidebar:
        @st.experimental_fragment
        def show_options():
            dates = st.date_input(
                "Trip dates", value=(now.date(), tommorow.date()), min_value=now)
            check_in = lambda: dates[0] if len(dates) > 1 else now
            check_out = lambda: dates[1] if len(dates) > 1 else tommorow
            travelers = st.number_input(
                "Travellers", min_value=1, value=2, placeholder="hello world")
            url = f"https://www.expedia.ca/Hotel-Search?destination={city_chosen['city']}%2C%20{city_chosen['country']}&startDate={check_in()}&endDate={check_out()}&adults={travelers}&rooms=1&theme=&userIntent=&semdtl=&useRewards=false&sort=RECOMMENDED&clickref=1101lyBFty4W&affcid=CA.DIRECT.PHG.1101l354964.0&ref_id=1101lyBFty4W&my_ad=AFF.CA.DIRECT.PHG.1101l354964.0&afflid=1101lyBFty4W"
        
            st.link_button("See available booking", url, use_container_width=True)

        show_options()
    return


def normalize_city_name(city_name: str):
    return urllib.parse.quote(city_name)


def main():
    st.set_page_config(page_title="Trip Roulette", 
                       page_icon=None,
                       layout="centered", 
                       initial_sidebar_state="expanded", 
                       menu_items=None)
    
    st.logo("data/logo.png")

    # Get the font Roboto from Google api
    streamlit_style = """
			<style>
			@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100&display=swap');

			html, body, [class*="css"]  {
			font-family: 'Roboto', sans-serif;
			}
			</style>
			"""

    st.markdown(streamlit_style, unsafe_allow_html=True) # Apply the font to the app

    df = load_dataset("data/worldcities.csv") # Load the worldcities data as a pandas df

    st.markdown("<h1 style='text-align: center;'>Trip Roulette</h1>", unsafe_allow_html=True) # Add centered title

    # Possibility of narrowing down the choice
    countries_selected = st.multiselect("Narrow down the possibilities by countries",
                                         options=df['country'].unique(), 
                                         placeholder="Choose an option (or not and hope for the best)")
    
    admin_name_selected = []
    if countries_selected != []:
        admin_name_selected = st.multiselect("Narrow down the possibilities by regions", 
                                             options=df[df['country'].isin(countries_selected)].sort_values('admin_name')['admin_name'].unique(), 
                                             placeholder="Choose an option (or not and hope for the best)")
    
    _1, col2, _3 = st.columns((0.3, 0.3, 0.3))

    # Placeholder for the map
    map_placeholder = st.empty()
    btn_placeholder = col2.empty()

    # Define the base map
    mo = folium.Map(location=[0, 0], zoom_start=2, tiles="OpenStreetMap")
    with map_placeholder:
        st_folium(mo, use_container_width=True,
                  returned_objects=[], height=500)
    
    # Explanation of the concept
    explanation: str = '''
    Trip Roulette is the ideal way to go out and explore the world like the true adventurer that you really are with this simple concept that randomize 137 000 possible destination around the world.
    - Narrow down the randomness by country or sub region (or not and hope for the best)
    - Click to uncover right away where you're going next!
    '''

    with st.expander("What is Trip Roulette?"):
        st.markdown(explanation)

    if btn_placeholder.button("Uncover your destination!", use_container_width=True, type="primary"):
        city_chosen, df_city = choose_random_city(
            df, countries_selected=countries_selected, admin_name_selected=admin_name_selected)

        m = folium.Map(location=[df_city.iloc[0]["LAT"],
                                 df_city.iloc[0]["LON"]], zoom_start=8, tiles="OpenStreetMap")

        folium.Marker(location=[df_city.iloc[0]["LAT"], df_city.iloc[0]["LON"]],
                      tooltip=f"{city_chosen['city']}, {city_chosen['country']}").add_to(m)

        btn_placeholder.empty()  # Make the button disapear

        with map_placeholder:
            st_folium(m, use_container_width=True,
                      returned_objects=[], height=500)  # Show the map with the datapoint

        st.sidebar.title("You're going to...") # Sidebar title
        st.sidebar.subheader(f"[{city_chosen['city']}, {city_chosen['country']}](https://en.wikipedia.org/wiki/{normalize_city_name(str(city_chosen['city']))})", 
                             divider="gray") # Sidebar subheader containing link to Wikipedia

        st.sidebar.header("Your next adventure is just a couple clicks away!")
        
        booking_options_expedia(city_chosen=city_chosen) # Link to Expedia websites containing booking options


if __name__ == "__main__":
    main()
