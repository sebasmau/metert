import streamlit as st
import pyrebase
import time
import pandas as pd
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
    
def interpret_csv_dataset(uploaded_file):
        ###translate fluvius csv into dataframe and create dict to be save
        dt = pd.read_csv(uploaded_file,delimiter=';',decimal=',')
        EAN_data = {}

        ###get start period
        dt['start_time'] = pd.to_datetime(dt.iloc[:,0] + " " + dt.iloc[:,1],format='%d-%m-%Y %H:%M:%S')

        ###get end period
        dt['end_time'] = pd.to_datetime(dt.iloc[:,2] + " " + dt.iloc[:,3],format='%d-%m-%Y %H:%M:%S')

        #get file parameters
        EAN_data['EAN_code'] = dt["EAN"].iloc[0].replace('=','').replace('"','')
        EAN_data['Meter_code'] = dt["Meter"].iloc[0]
        EAN_data['Meter_type'] = dt["Metertype"].iloc[0]
        EAN_data['Power_unit'] = dt["Eenheid"].iloc[0]
        EAN_data['Time_unit (m)'] = (dt["end_time"].iloc[0] - dt["start_time"].iloc[0]).seconds/60 ##15 bij kwartier waarden, 60 bij uurwaarden
        EAN_data['Available_period (d)'] = (dt["start_time"].iloc[-1] - dt["start_time"].iloc[0]).round('d').days
        EAN_data['start_time'] = dt["start_time"].iloc[0].strftime('%d-%m-%Y %H:%M:%S')
        EAN_data['end_time'] = dt["end_time"].iloc[-1].strftime('%d-%m-%Y %H:%M:%S')

        #get rid of useless columns
        dt = dt.dropna()[['start_time','end_time','Volume','Register']]

        #get calulated parameters
        largest_injections = dt[dt['Register'].str.contains('Injectie')]['Volume'].nlargest(5) ###largest 5 injections found
        EAN_data['Estimated_generation_capacity (kW)'] = largest_injections.mean()*60/EAN_data['Time_unit (m)'] ###60/Time_unit converts kWh towards kW
        EAN_data['Has_solar_panels'] = True if EAN_data['Estimated_generation_capacity (kW)'] >= 0.6 else False  ###2 solar panels = +-600W


        #get injection and usage
        EAN_data['Afname Dag (kWh)'] = dt[dt['Register'].str.contains('Afname Dag')]['Volume'].sum()
        EAN_data['Afname Nacht (kWh)'] = dt[dt['Register'].str.contains('Afname Nacht')]['Volume'].sum()
        EAN_data['Injectie Dag (kWh)'] = dt[dt['Register'].str.contains('Injectie Dag')]['Volume'].sum()
        EAN_data['Injectie Nacht (kWh)'] = dt[dt['Register'].str.contains('Injectie Nacht')]['Volume'].sum()
        vart = dt.set_index('start_time').between_time('10:00','16:00')
        EAN_data['Afname Dag 10_16 (kWh)'] = vart[vart['Register'].str.contains('Afname Dag')]['Volume'].sum()
        EAN_data['Injectie Dag 10_16 (kWh)'] = vart[vart['Register'].str.contains('Injectie Dag')]['Volume'].sum()

        #get peak percentile sensitivity
        sensitivity = [0.9,0.95,0.99,0.999,0.9999,1]
        afname_piek = []
        for i in sensitivity:
            afname_piek.append(dt[dt['Register'].str.contains('Afname')]['Volume'].quantile(i)*60/EAN_data['Time_unit (m)'])
        EAN_data['Afname piek percentielen (kW)'] = afname_piek


        sensitivity = [0,0.01,0.05,0.1,0.2,0.3]
        afname_nacht_dal = []
        for i in sensitivity:
            afname_nacht_dal.append(dt[dt['Register'].str.contains('Afname')]['Volume'].quantile(i)*60/EAN_data['Time_unit (m)'])
        EAN_data['Afname Nacht dal percentielen (kW)'] = afname_nacht_dal



        #write to database
        sttk.set_firebase_db_data(EAN_data,"fluvius_data",EAN_data['EAN_code'])
        sttk.set_firebase_db_data(EAN_data['EAN_code'],"users",sttk.get_userID(),"EAN_code")
        sttk.set_firebase_db_data(True,"users",sttk.get_userID(),"Uploaded fluvius file")
        

@st.cache_data(show_spinner="Analyseren hoe je geld kan besparen...")
def create_graph_data(dt):
        graphtable = dt.pivot_table(index='end_time', columns='Register', values='Volume',aggfunc='mean').fillna(0)
        graphtable['Afname'] = graphtable['Afname Dag'] + graphtable['Afname Nacht']
        graphtable['Injectie'] = graphtable['Injectie Dag'] + graphtable['Injectie Nacht']
        return graphtable[['Afname','Injectie']]


###ACTUAL APP
image = Image.open('artwork/metert logo.png')
st.image(image,width=50,output_format="PNG")


tab1, tab2 = st.tabs(["Fluvius - Digitale meter", "Invencado - Smart Meter"])


with tab1:
    if "fluvius_process_step" not in st.session_state:
         st.session_state["fluvius_process_step"] = 1
    if "show_upload_widget" not in st.session_state:
         st.session_state["show_upload_widget"] = False


    if st.session_state["fluvius_process_step"] == 1:
        with st.form("fluvius_process_step1"):
            st.subheader("Stap 1: Registreer je op Mijn Fluvius",anchor=False)
            st.markdown("""
                - MeterT werkt samen met de Vlaamse netbeheerder Fluvius om op zoek te gaan naar hoe jij groenere en goedkopere energie kan gebruiken
                - Registeer je op [mijn.fluvius.be](https://mijn.fluvius.be) om inzicht te krijgen in je energieverbruik via je digitale meter
                """)
            st.markdown("_Klik [hier](https://vimeo.com/829388810) voor een instructievideo met meer uitleg over hoe je dit kan doen_")
            
            if st.form_submit_button("Volgende",use_container_width=True):
                st.session_state["fluvius_process_step"] = 2
                st.experimental_rerun()


    if st.session_state["fluvius_process_step"] == 2:
        with st.form("fluvius_process_step2"):
            st.subheader("Stap 2: Vraag je energieverbruik aan bij Fluvius",anchor=False)
            st.markdown("""
                - Nu je toegang hebt tot Mijn Fluvius kan je [hier](https://mijn.fluvius.be/verbruik/aanvragen) toegang vragen tot het energieverbruik van je digitale meter
                - Vul daar de EAN code in van je digitale meter, of selecteer je adres in de lijst hieronder, en volg erna de stappen van Fluvius
                - Het is belangrijk dat je zowel jaar/maand/dag🗓️ verbruiken als kwartier🕓 verbruiken aanvraagt, in een volgende stap kies je er dan ook best voor om voor de maximale periode deze data aan te vragen
                """)
            st.markdown("_Klik [hier](https://vimeo.com/481701965/e9b2e9956e) voor een instructievideo met meer uitleg over hoe je dit kan doen_")


            col1,col2 = st.columns(2)
            if col1.form_submit_button("Terug",use_container_width=True):
                st.session_state["fluvius_process_step"] = 1
                st.experimental_rerun()
            if col2.form_submit_button("Volgende",use_container_width=True):
                st.session_state["fluvius_process_step"] = 3
                st.experimental_rerun()

    if st.session_state["fluvius_process_step"] == 3:
        with st.form("fluvius_process_step3"):
            st.subheader("Stap 3: Raadpleeg je energieverbruik",anchor=False)
            st.markdown("""
                - test
                """)
            st.markdown("_Klik [hier](https://vimeo.com/481728163/25ab26dd13) voor een instructievideo met meer uitleg over hoe je dit kan doen_")
            col1,col2 = st.columns(2)
            if col1.form_submit_button("Terug",use_container_width=True):
                st.session_state["fluvius_process_step"] = 2
                st.session_state["show_upload_widget"] = False
                st.experimental_rerun()
            if col2.form_submit_button("Connecteren",type="primary",use_container_width=True):
                st.session_state["show_upload_widget"] = True

        if st.session_state["show_upload_widget"] == True:
            uploaded_file = st.file_uploader("Plaats hier je Fluvius verbruik bestand",accept_multiple_files=False,type=["csv"],help="Je kan je verbruik vinden op de website van [Fluvius](https://www.fluvius.be/nl/thema/meters-en-meterstanden/digitale-meter/hoe-mijn-energieverbruik-online-raadplegen) ")
            if uploaded_file is not None:
                try:
                    with st.spinner("Analyseren hoe je geld kan besparen..."):
                        interpret_csv_dataset(uploaded_file)
                    st.success("Analyse naar hoe je geld kan besparen was succesvol, de resultaten kan je zien bij '"'🔎 Energie audit'"'")
                except:
                    st.warning("Deze data kon niet ingelezen worden, de juiste data kan je vinden op de website van [Fluvius](https://www.fluvius.be/nl/thema/meters-en-meterstanden/digitale-meter/hoe-mijn-energieverbruik-online-raadplegen)")
            st.divider()




with tab2:
    with st.form("Maak verbinding met je '"'Invencado Smart Meter'"'"):
        st.subheader("Maak verbinding met je '"'Invencado Smart Meter'"'")
        mac_address = st.text_input("Meternummer",placeholder="Bijvoorbeeld: '7ab0ae642979'",help="Je meternummer kan je terugvinden op je Invencado Smart Meter, het is de code die op de kabel geschreven is")
        challenge_code = st.text_input("challengecode", type="password",help="De beveiligingscode kan je terugvinden op het instructieformulier die bij de meter in de doos zat (momenteel is dit 123)")
        connect_to_meter = st.form_submit_button("Verbinding maken",type="primary")

    if connect_to_meter:
        try:
            all_existing_meter_macs = list(st.session_state['firebase'].database().child("metermac").shallow().get().val()) ##get all key values (shallow), and then make a readable list out of the val() you read
            if mac_address in all_existing_meter_macs:
                st.success("Deze meter is actief, maar kan nog geen data doorsturen naar deze website")
            elif challenge_code != "123":
                st.error("Verkeerde challenge code (tip het is 123)")
        except:
            st.error("Onbekend meternummer")
         