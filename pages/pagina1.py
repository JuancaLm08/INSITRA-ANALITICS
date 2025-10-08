import streamlit as st
import ceiba_client as cbc

cbc.require_login()
cbc.generarMenu(st.session_state["usuario"])

st.header("Ventas")

# Ejemplo: consultar otro recurso
ok, data, err = cbc.api_get("sales/summary", params={"from":"2025-10-01", "to":"2025-10-08"})
if ok:
    st.json(data)
else:
    st.error(err)
