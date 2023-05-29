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
    


#####
image = Image.open('artwork/metert logo.png')
st.image(image,width=50,output_format="PNG")
st.title("Welkom op uw MeterT Dashboard! 👋",anchor=False)
metcol1,metcol2,metcol3 = st.columns(3)
metcol1.metric("Energie verbruik",f"22 kWh","+2%")
metcol2.metric("CO2 uitstoot",f"110 g","-25%")
metcol3.metric("Energie injectie",f"115 kWh", "-13%")
if st.button("Toon verbruik",type="secondary",use_container_width=True):
    sttk.navigate_page("Verbruik")





