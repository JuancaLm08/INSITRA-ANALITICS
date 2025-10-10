import streamlit as st
import ceiba_client as cbc

cbc.require_login()
cbc.generarMenu(st.session_state["usuario"])

