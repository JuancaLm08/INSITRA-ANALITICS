import streamlit as st
import ceiba_client as cbc

st.header('Página :orange[principal]')

cbc.login()

if 'usuario' in st.session_state and "api_key" in st.session_state:
    st.subheader('Información página principal')

