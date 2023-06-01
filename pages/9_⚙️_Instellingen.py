import streamlit as st
import pyrebase
import pandas as pd
import time
import Streamlit_toolkit as sttk
from PIL import Image

energy_suppliers_info = {'Geen energieleverancier geselecteerd':["Geen contract geselecteerd"],
                         'Engie Electrabel':["Geen contract geselecteerd","Easy Variabel","Easy Vast","Flow Variabel","Direct Variabel","Dynamic Variabel"],
                         'Luminus':["Geen contract geselecteerd","ComfyFlex Variabel","Comfy Vast","Comfy+ Vast"],
                         "Mega":["Geen contract geselecteerd","Cosy Green Flex Variabel","Online Green Flex Variabel","Cosy Green Fixed Vast","Smart Green Flex Variabel","Online Flex Variabel","Group Green Flex Variabel"],
                         "Total Energies":["Geen contract geselecteerd","Pixel Variabel","Pixel Blue Variabel"],
                         "Eneco":["Geen contract geselecteerd","Flex Variabel","Vast"],
                         "Bolt":["Geen contract geselecteerd","Bolt Variabel","Bolt Online Variabel","Bolt Go Variabel"],
                         "Octa+":["Geen contract geselecteerd","Clear Variabel","Eco Clear Variabel","Dynamic Variabel"],
                         "Energie.be":["Geen contract geselecteerd","Energie.be Variabel"],
                         'Andere':[""]
                         }
meter_types = ["Geen meter type geselecteerd","Dag/nacht teller","Dag teller","Uitsluitend nacht teller","budget teller"]
                         
no_supplier_selected = 'Geen energieleverancier geselecteerd'
no_contract_selected = "Geen contract geselecteerd"
no_meter_type_selected = "Geen meter type geselecteerd"

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

user_id = sttk.get_userID()
user_settings = sttk.get_firebase_db_data("users",user_id)
if user_settings == None:
    user_settings = {} 

### value = str(x or y) ==> if x is None (False) then y is return (""), if x is string, this string is returned


tab1, tab2, tab3 = st.tabs(["Algemene instellingen", "Mijn electriciteits leverancier", "Mijn elektrische installatie"])



with tab1:
    st.subheader("Algemene gegevens",anchor=False)
    Address = st.text_input('Mijn adres',placeholder='Bijvoorbeeld: Koekoekstraat 70, Melle',value=str(user_settings.get("Address") or ""))
    Postcode = st.text_input('Postcode',placeholder='9090',value=str(user_settings.get("Postcode") or ""))



with tab2:

    ##select the energy sources name terms for the cases where no supplier was selected
    db_supplier = str(user_settings.get("Energy Supplier") or no_supplier_selected)
    db_contract = str(user_settings.get("Energy Contract") or no_contract_selected)
    db_meter_type = str(user_settings.get("Meter Type") or no_meter_type_selected)


    #show on streamlit app
    st.subheader("Mijn energie leverancier",anchor=False)
    Energy_supplier = st.selectbox('Wie is uw huidige energie leverancier',list(energy_suppliers_info.keys()),index=list(energy_suppliers_info.keys()).index(db_supplier))
    
    if Energy_supplier != no_contract_selected: ##only show if supplier was shown
        Energy_contract = st.selectbox('Wat is uw huidig contract?',energy_suppliers_info[Energy_supplier],index=energy_suppliers_info[db_supplier].index(db_contract))

    Meter_type = st.selectbox('Wat voor meet regime heeft u?',meter_types,index=meter_types.index(db_meter_type))
with tab3:
    
    st.subheader("Mijn elektrische toestellen",anchor=False)
    Fridges = st.number_input("Aantal frigo's",help="Hoeveel frigo's heb je?",min_value=0,max_value=6,value=(user_settings.get("Fridges") or 0))
    Freezers = st.number_input("Aantal diepvriezers",help="Hoeveel diepvriezers heb je?",min_value=0,max_value=6,value=(user_settings.get("Freezers") or 0))
    Washing_Machines = st.number_input("Aantal wasmachines",help="Heb je een wasmachine?",min_value=0,max_value=2,value=(user_settings.get("Washing Machines") or 0))
    Drying_Machines = st.number_input("Aantal droogkasten",help="Heb je een droogkast?",min_value=0,max_value=2,value=(user_settings.get("Drying Machines") or 0))
    Electric_Cars = st.number_input("Aantal elektrische wagens",help="Heb je een elektrische wagen?",min_value=0,max_value=6,value=(user_settings.get("Electric Cars") or 0))
    
    
    st.subheader("Mijn hernieuwbare energie installatie",anchor=False)
    Solar_Panels = st.number_input("Aantal zonnepanelen",help="Het gemiddelde zonnepaneel heeft een capaciteit van 350W",min_value=0,max_value=100,value=(user_settings.get("Solar Panels") or 0))
    Battery_Capacity = st.number_input("Thuisbatterij capaciteit (kWh)",help="Vul hier de capaciteit in van je thuisbatterij indien je er 1 hebt",min_value=0.0,max_value=100.0,step=0.5,value=(user_settings.get("Battery Capacity") or 0.0))

st.write('#')

if st.button("Gegevens opslaan",type='primary'):
        user_settings["Address"] = Address
        user_settings["Postcode"] = Postcode

        user_settings["Energy Supplier"] = Energy_supplier
        user_settings["Energy Contract"] = Energy_contract
        user_settings["Meter Type"] = Meter_type

        user_settings["Solar Panels"] = Solar_Panels
        user_settings["Battery Capacity"] = Battery_Capacity

        user_settings["Washing Machines"] = Washing_Machines
        user_settings["Drying Machines"] = Drying_Machines
        user_settings["Electric Cars"] = Electric_Cars
        user_settings["Fridges"] = Fridges
        user_settings["Freezers"] = Freezers
        sttk.set_firebase_db_data(user_settings,"users",user_id)
        st.balloons()

if st.button("Home",):
     sttk.navigate_page("Energie_audit")

st.divider()
st.markdown("💡 We vragen deze informatie een beter zicht te krijgen op hoe jouw energieverbruik er uit ziet,   \nop deze manier kunnen we op basis van jouw elektrische apparaten nog beter advies geven")