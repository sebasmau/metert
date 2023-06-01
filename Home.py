import streamlit as st
import pyrebase
import pandas as pd
import time
import Streamlit_toolkit as sttk
from PIL import Image

####PAGE CONFIG

st.set_page_config(
    page_title="MeterT",
    page_icon="⚡",
    layout='wide'
)

sttk.set_css_style("style.css")
sttk.firebase_login_screen_init()
    

image = Image.open('artwork/metert logo.png')
st.image(image,width=50,output_format="PNG")
st.title("Welkom op uw MeterT Dashboard! 👋",anchor=False)

#####get data on user
user_data = sttk.get_firebase_db_data("users",sttk.get_userID())
try:
    EAN_data = sttk.get_firebase_db_data("fluvius_data",user_data["fluvius_data"])
    x = round(EAN_data["Afname Dag (kWh)"],0)
    y = round(EAN_data["Afname Nacht (kWh)"],0)
    z = round(EAN_data["Available_period (d)"],0)
    metcol1,metcol2,metcol3 = st.columns(3)
    metcol1.metric("Afname dag",f"{x} kWh","+10")
    metcol2.metric("Afname dag",f"{y} kWh","-10")
    metcol3.metric("Beschikbare periode",f"{z} dagen","0")
except:
    if st.button("Connecteer je digitale meter",type="secondary",use_container_width=True):
        sttk.navigate_page("Verbruik")

if st.button("Toon verbruik",type="secondary",use_container_width=True):
    sttk.navigate_page("Verbruik")





