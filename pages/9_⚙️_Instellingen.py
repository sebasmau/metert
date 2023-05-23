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
tab1, tab2, tab3 = st.tabs(["Algemene instellingen", "Mijn electriciteits leverancier", "Mijn elektrische installatie"])


with tab1:
    st.write("#### Algemene gegevens")
    st.text_input('Mijn adres',placeholder='Bijvoorbeeld: Koekoekstraat 70, Melle')
    st.selectbox("Energie audit: details",options=["Normaal","Geef me alle technische details!"])



with tab2:
    st.write("#### Energie leverancier")
    lev = st.selectbox('Wie is uw huidige energie leverancier',['Engie Electrabel','Luminus',"Mega","Total Energies","Eneco","Bolt",'Ik weet het niet','Andere'])
    if lev == "Luminus":
        contract = st.selectbox('Wat is uw huidig contract?',['Afzetterij ECO','Afzetterij Premium'])

    st.select_slider("Bent u tevreden van uw huidige energie leverancier?",['Niet tevreden','Eerder niet tevreden',"Neutraal","Tevreden","Zeer tevreden"],value='Neutraal')

    st.write("#### Energie prijs")
    typetarief = st.selectbox('Heeft u een dag/nacht tarief of een dag tarief',['Dag/Nacht tarief','Dag tarief','Ik weet het niet','Andere'])

    if typetarief == 'Dag/Nacht tarief':
        st.slider("Dag tarief (€)",min_value=0.0,max_value=1.5,value=0.90)
        st.slider("Nacht tarief (€)",min_value=0.0,max_value=1.5,value = 0.60)
        st.slider("Injectie tarief (€)",min_value=0.0,max_value=1.5,value = 0.40)
    elif typetarief == 'Dag tarief':
        st.slider("tarief (€)",min_value=0.0,max_value=1.5,value=0.70)
        st.slider("Injectie tarief (€)",min_value=0.0,max_value=1.5,value = 0.40)

with tab3:
    st.write("#### Zonnepanelen")
    zonp = st.selectbox('Heeft u zonnepanelen',['Ik heb geen zonnepanelen','Ik heb zonnepanelen','ik wil graag zonnepanelen'])
    if zonp == 'Ik heb zonnepanelen':
        st.number_input('Aantal zonnepanelen', 0,20)
        st.slider('Vermogen per zonnepaneel (Wp)',200,500,step=10,value=350)

    st.write("#### Thuisbatterij")
    zonp = st.selectbox('Heeft u een thuisbatterij',['Ik heb geen thuisbatterij','Ik heb een thuisbatterij','ik wil graag een thuisbatterij'])

if st.button("Gegevens opslaan"): 
    #with open('users.yaml', 'w') as f:
    #data = yaml.dump(config, f)
    st.balloons()