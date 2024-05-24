import pandas as pd
import streamlit as st
import random
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


def booking_options(location):
    pass


def main():
    df = load_dataset("data/worldcities.csv")
    st.markdown("<h1 style='text-align: center;'>Trip Roulette</h1>",
                unsafe_allow_html=True)
    countries_selected = st.multiselect("Narrow down the possibilities by countries", options=df['country'].unique(
    ), placeholder="Choose an option (or not and hope for the best)")
    admin_name_selected = []
    if countries_selected != []:
        admin_name_selected = st.multiselect("Narrow down the possibilities by regions", options=df[df['country'].isin(
            countries_selected)].sort_values('admin_name')['admin_name'].unique(), placeholder="Choose an option (or not and hope for the best)")
    col1, col2, col3 = st.columns((0.3, 0.3, 0.3))

    # Placeholder for the map
    map_placeholder = st.empty()
    mo = folium.Map(location=[0, 0], zoom_start=2, tiles="OpenStreetMap")
    with map_placeholder:
        st_folium(mo, use_container_width=True,
                  returned_objects=[], height=500)

    if col2.button("Discover your destiny!", use_container_width=True, type="primary"):
        city_chosen, df_city = choose_random_city(
            df, countries_selected=countries_selected, admin_name_selected=admin_name_selected)

        m = folium.Map(location=[df_city.iloc[0]["LAT"],
                                 df_city.iloc[0]["LON"]], zoom_start=8, tiles="OpenStreetMap")

        folium.Marker(location=[df_city.iloc[0]["LAT"], df_city.iloc[0]["LON"]],
                      tooltip=f"{city_chosen['city']}, {city_chosen['country']}").add_to(m)

        with map_placeholder:
            st_folium(m, use_container_width=True,
                      returned_objects=[], height=500)

        st.sidebar.title("You're going to...")
        st.sidebar.subheader(f"[{city_chosen['city']}, {city_chosen['country']}](https://en.wikipedia.org/wiki/{str(city_chosen['city']).replace(' ', '_')})", divider="gray")

        st.sidebar.header("Pack you bag, the adventure awaits")
        with st.sidebar.form("Booking", border=False):
            start_date = st.date_input("Strating date of the trip")
            end_date = st.date_input("End date of the trip")
            number_of_guest = st.number_input(
                "Number of travellers", min_value=1)
            
            book = st.form_submit_button("Lookup Booking", use_container_width=True)
            if book:
                pass



if __name__ == main():
    main()
