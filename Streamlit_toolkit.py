###this is a toolkit of functions to be used by Sébastien Mauroo
import streamlit as st
import pyrebase
from streamlit.components.v1 import html

def firebase_get_db():
    return st.session_state['firebase'].database()


def get_firebase_db_data(*childs):
    db = st.session_state['firebase'].database()
    for child in childs:
         db = db.child(child)         
    return db.get().val()


def set_firebase_db_data(load,*childs):
    db = st.session_state['firebase'].database()
    for child in childs:
         db = db.child(child)         
    return db.set(load)

@st.cache_data
def get_userID():
    return st.session_state['userID']



def set_css_style(style):
    with open(style) as f:
        st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)

    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def navigate_page(page_name, timeout_secs=3):
    nav_script = """
        <script type="text/javascript">
            function attempt_nav_page(page_name, start_time, timeout_secs) {
                var links = window.parent.document.getElementsByTagName("a");
                for (var i = 0; i < links.length; i++) {
                    if (links[i].href.toLowerCase().endsWith("/" + page_name.toLowerCase())) {
                        links[i].click();
                        return;
                    }
                }
                var elasped = new Date() - start_time;
                if (elasped < timeout_secs * 1000) {
                    setTimeout(attempt_nav_page, 100, page_name, start_time, timeout_secs);
                } else {
                    alert("Unable to navigate to page '" + page_name + "' after " + timeout_secs + " second(s).");
                }
            }
            window.addEventListener("load", function() {
                attempt_nav_page("%s", new Date(), %d);
            });
        </script>
    """ % (page_name, timeout_secs)
    html(nav_script)

def firebase_login_screen_init():
    if 'firebase' not in st.session_state:
            st.session_state['firebase'] = pyrebase.initialize_app(st.secrets['FirebaseCredentials'])

    if 'userID' not in st.session_state:
            st.session_state['userID'] = "Unknown"

    if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False

    if 'password_reset' not in st.session_state:
            st.session_state['password_reset'] = False

    if 'create_account' not in st.session_state:
            st.session_state['create_account'] = False

    if st.session_state['logged_in'] == False and st.session_state['create_account'] == False:  ###sign in screen 
        with st.form("Inloggen"):
            st.subheader("Login",anchor=False)
            email = st.text_input("Emailadres")
            pw = st.text_input("Wachtwoord", type="password")
            login = st.form_submit_button("Login",type="primary")
        

        if login:
            try:
                signin = st.session_state['firebase'].auth().sign_in_with_email_and_password(email,pw)
                st.session_state['logged_in'] = True
                st.session_state['password_reset'] = False
                st.session_state['userID'] = signin['localId']
            except:
                st.error("verkeerd wachtwoord")
                st.session_state['password_reset'] = True

        if st.session_state['password_reset'] == True:
            if st.button("Verander je wachtwoord"):
                try:
                    st.session_state['firebase'].auth().send_password_reset_email(email)
                    st.markdown(f"Email verzonden naar {email}")
                    st.caption(f"Deze email kan ook in je spam folder te vinden zijn")
                except:
                    st.info(f"Niet mogelijk om een email te sturen naar: {email}, probeer later opnieuw")
        

        ####button to show create account instead
        if st.button("Account aanmaken"):
            st.session_state['password_reset'] = False
            st.session_state['create_account'] = True
            st.experimental_rerun()

        
        ####rerun script to show real page after succesfull login
        if st.session_state['logged_in'] == True:
            st.experimental_rerun()
        else:
            st.stop()

    elif st.session_state['logged_in'] == False and st.session_state['create_account'] == True:  ###create password button
        with st.form("Account aanmaken"):
            st.subheader("Account aanmaken",anchor=False)
            email = st.text_input("Emailadres")
            pw = st.text_input("Wachtwoord", type="password")
            pw_confirm = st.text_input("Bevestig wachtwoord", type="password")
            accept_terms_and_conditions = st.checkbox("Ik accepteer de [gebruikersvoorwaarden](https://1drv.ms/b/s!AkQC5Uz0X-XxgQC3NDi3Od4Z-isp?e=Q2YfGs)")
            #accept_mail_info = st.checkbox("Ik wil gecontacteerd worden")
            login = st.form_submit_button("Enter",type="primary")

        ####button to show login screen instead

        if st.button("Inloggen met bestaand account"):
            st.session_state['password_reset'] = False
            st.session_state['create_account'] = False
            st.experimental_rerun()

        ####check email and password
        if login:
            if '@' not in email or '.' not in email:
                st.warning("Vul een geldig emailadres in")
                st.stop()
            elif len(pw)<6:
                st.info("Wachtwoord moet minimaal 7 karakters lang zijn")
                st.stop()
            elif pw != pw_confirm:
                st.info("Er werden 2 verschillende wachtwoorden ingevuld")
                st.stop()
            elif accept_terms_and_conditions == False:
                st.info("Gelieve de gebruikersvoorwaarden te accepteren")
                st.stop()
            else:
                try:
                    signin = st.session_state['firebase'].auth().create_user_with_email_and_password(email,pw)
                    set_firebase_db_data(accept_terms_and_conditions,"users",signin['localId'],"Accepted terms and conditions")
                    st.session_state['logged_in'] = True
                    st.session_state['password_reset'] = False
                    st.session_state['userID'] = signin['localId']
                except:
                    st.info("Aanmaken van een account niet gelukt, probeer later opnieuw")
                    st.stop()
            st.experimental_rerun()
        else:
            st.stop()