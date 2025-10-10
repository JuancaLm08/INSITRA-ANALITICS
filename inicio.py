import streamlit as st
import ceiba_client as cbc
import pandas as pd


st.set_page_config(page_title="Inicio", layout="centered")
cbc.login()

if 'usuario' in st.session_state and "api_key" in st.session_state:

    with st.sidebar:
        st.subheader("Filtros")

        grupos, err_g = cbc.listar_grupos()
        if err_g:
            st.error(err_g)
            st.stop()

        # Mapea id→nombre y nombre→id para usar selectbox por nombre
        opciones_companias = {g["groupname"]: g["groupid"] for g in grupos}
        nombre_compania = st.selectbox("Compañía", options=sorted(opciones_companias.keys()))

        # Dispositivos
        dispositivos, err_d = cbc.listar_dispositivos_simplificado()
        if err_d:
            st.error(err_d)
            st.stop()

        groupid_sel = opciones_companias[nombre_compania]
        placas_del_grupo = [d["carlicence"] for d in dispositivos if d["groupid"] == groupid_sel]
        placa_sel = st.selectbox("Placa", options=sorted(placas_del_grupo))

        # Encuentra terid de la placa elegida
        terid_sel = next((d["terid"] for d in dispositivos
                          if d["groupid"] == groupid_sel and d["carlicence"] == placa_sel), None)

        st.caption(f"terid: **{terid_sel or '—'}**")

        bttn_consulta = st.button("Realizar consulta")

    st.title("INSITRA ANALITICS")

    kilometraje = {
        "terid": [terid_sel],
        "starttime": "2025-10-01",
        "endtime": "2025-10-08"
    }

    if bttn_consulta:

        ok, payload, err = cbc.api_post("basic/mileage/count", json=kilometraje,)
        km = pd.DataFrame(payload.get("data", []))
        st.dataframe(km, use_container_width=True)

