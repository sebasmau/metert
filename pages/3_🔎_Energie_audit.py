import streamlit as st
import pyrebase
import time
import webbrowser
import altair as alt
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
    



###ACTUAL APP
image = Image.open('artwork/metert logo.png')
st.image(image,width=50,output_format="PNG")

def solarpanels(fixed_investment,variable_investment,price_high,price_low,self_consumption,kWh_year_solarpanel,CO2_kWh):
    years = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]

    with st.expander(label='Zonnepanelen'):
        solarcol1,solarcol2 = st.columns([1.1,2])

        solarcol1.write("### Zonnepanelen")
        solarpanels = solarcol1.number_input('Optimaal aantal zonnepanelen',min_value= 6,max_value=30, value=12)

        
        solarinvestment = solarpanels * variable_investment + fixed_investment
        profit = [round(i * (solarpanels*kWh_year_solarpanel*(price_high*self_consumption+price_low*(1-self_consumption)))-solarinvestment) for i in years]
        solarcol2.write("### Terugverdientijd")
        source = pd.DataFrame({"Jaren":years,"Winst (€)":profit})#.set_index("Jaren")
        chartalt = alt.Chart(source).mark_bar().encode(
            x="Jaren:O",
            y="Winst (€):Q",
            # The highlight will be set on the result of a conditional statement
            color=alt.condition(
                alt.datum["Winst (€)"] > 0,  # If the year is 1810 this test returns True,
                alt.value('#90ee90'),     # which sets the bar orange.
                alt.value('red')   # And if it's not true it sets the bar steelblue.
            )
        ).properties(height=450)
        solarcol2.altair_chart(chartalt, use_container_width=True)
        #solarcol2.bar_chart(source.set_index("Jaren"),height=500)


        solarcol1.metric("Geschatte prijs voor deze installatie",f"{solarinvestment} €")
        solarcol1.metric("Terugverdientijd",f"{round(solarinvestment / (solarpanels*kWh_year_solarpanel*(price_high*self_consumption+price_low*(1-self_consumption))),1)} jaar")
        solarcol1.metric("Winst na 25 jaar",f"{round(profit[24])} €")
        solarcol1.metric("CO2 besparing na 25 jaar",f"{round(solarpanels*kWh_year_solarpanel*CO2_kWh*25/1000)} kg")
        solarcol1.info("Meer info kan je [hier](https://addestino.be/privacy-policy/) vinden")



def day_night_meter(day_price,night_price,day_night_price,day_usage,night_usage,available_period):
    with st.expander(label='Dag/nacht tarief'):
        prijs_enkel_dag = ((day_usage+night_usage)*day_night_price) * 365 / available_period
        prijs_dag_nacht = ((day_usage*day_price+night_usage*night_price)) * 365 / available_period


        dnmetercol1,dnmetercol2 = st.columns([1.1,2])


        dnmetercol1.write("### Electriciteitsmeter")
        type_tarief = dnmetercol1.selectbox('Ik heb momenteel een...',['Dag- en nachttarief','Dagtarief'])
        

        if type_tarief == 'Dag- en nachttarief' and prijs_enkel_dag<prijs_dag_nacht:
            dnmetercol1.metric("Uit te sparen bedrag door over te schakelen naar een dag teller",(f"{round(prijs_dag_nacht-prijs_enkel_dag)} €/jaar"))
            dnmetercol1.metric("Dit is een besparing van",(f"{round(prijs_enkel_dag/prijs_dag_nacht)} %/jaar"))
            dnmetercol1.info("Klik [hier](https://mijnpostcode.fluvius.be/?lang=nl&applicatie=Aansluiting-aanvragen) om te schakelen naar een beter tarief")

        elif type_tarief == 'Dag- en nachttarief' and prijs_enkel_dag>=prijs_dag_nacht:
            dnmetercol1.metric("Goeie keuze, dit is goedkoper dan een dagtarief",(f"{round(prijs_enkel_dag-prijs_dag_nacht)} €/jaar"))

        elif type_tarief == 'Dagtarief' and prijs_enkel_dag>prijs_dag_nacht:
            dnmetercol1.metric("Uit te sparen bedrag door over te schakelen naar een dag nacht teller",(f"{round(prijs_enkel_dag-prijs_dag_nacht)} €/jaar"))
            dnmetercol1.metric("Dit is een besparing van",(f"{round(prijs_dag_nacht/prijs_enkel_dag)} %/jaar"))
            dnmetercol1.info("Klik [hier](https://mijnpostcode.fluvius.be/?lang=nl&applicatie=Aansluiting-aanvragen) om te schakelen naar een beter tarief")

        elif type_tarief == 'Dagtarief' and prijs_enkel_dag<=prijs_dag_nacht:
            dnmetercol1.metric("Goeie keuze, dit is goedkoper dan een dag- en nacht tarief",(f"{round(prijs_dag_nacht-prijs_enkel_dag)} €/jaar"))

        dnmetercol2.write(("### Dag/nacht tarief"))
        

        if(prijs_enkel_dag>prijs_dag_nacht): 
            day_night_graph_radius = 80 
            day_graph_radius = 60 
        else: 
            day_night_graph_radius = 60 
            day_graph_radius = 80 

        if type_tarief == 'Dag- en nachttarief':
            source = pd.DataFrame({"tarief": ["Dag tarief", "Nacht tarief"], "€": [round(day_usage*day_price* 365 / available_period), round(night_usage*night_price* 365 / available_period)]})
            day_night_graph = alt.Chart(source).mark_arc(innerRadius=day_night_graph_radius).encode(
                theta=alt.Theta(field="€", type="quantitative"),
                color=alt.Color(field="tarief", type="nominal"),
            ).configure_range(
                    category=alt.RangeScheme(['#E5DE44', '#5148b2'])
            )


            dnmetercol2.altair_chart(day_night_graph,theme=None,use_container_width=True)
        if type_tarief == 'Dagtarief':
            source = pd.DataFrame({"tarief": ["Dag tarief", "Nacht tarief"], "€": [round((day_usage+night_usage)*day_night_price* 365 / available_period),0]})
            colors = ['#7fc97f']
            day_night_graph = alt.Chart(source).mark_arc(innerRadius=day_graph_radius).encode(
                theta=alt.Theta(field="€", type="quantitative"),
                color=alt.Color(field="tarief", type="nominal"),
            ).configure_range(
                    category=alt.RangeScheme(['#E5DE44', '#5148b2'])
            )

            dnmetercol2.altair_chart(day_night_graph,theme=None,use_container_width=True)
    
st.subheader("Top besparingstips voor jou",anchor=False)
solarpanels(2130,422,0.5,0.3,0.3,293,300)
day_night_meter(0.134,0.113,0.127,126,80.2,30)

st.info("Wij bouwen volop verder aan MeterT om verder energie advies te kunnen geven, binnenkort bekijken we ook als volgende zaken voordelig zijn voor jou; energiedelen, EMS systemen, slimme boilers, dynamische energietarieven, slimme batterijen, nieuwe energiecontracten,...",icon="🏗️")