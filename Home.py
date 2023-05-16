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
st.write("test")





st.text_area("",key="usage",disabled=True,height=75,placeholder="Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")





