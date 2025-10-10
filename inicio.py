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
        opciones_companias = {}
        for g in grupos:
            opciones_companias[g["groupname"]] = g["groupid"]

        nombre_compania = st.selectbox("Compañía", options=sorted(opciones_companias.keys()))

        # Dispositivos
        dispositivos, err_d = cbc.listar_dispositivos_simplificado()
        if err_d:
            st.error(err_d)
            st.stop()

        groupid_sel = opciones_companias[nombre_compania]

        placas_del_grupo = []
        for d in dispositivos:
            if d["groupid"] == groupid_sel:
                placas_del_grupo.append(d["carlicence"])

        placas_sel = st.multiselect("Placas", options=sorted(placas_del_grupo))

        # Encuentra terid de la placa elegida
        terid_sel = []
        for d in dispositivos:
            if d["groupid"] == groupid_sel and d["carlicence"] in placas_sel:
                terid_sel.append(d["terid"])

        #st.caption(f"terid: **{terid_sel or '—'}**")

        options = ["Kilometraje","Conteo"]
        selection = st.pills("Seleccione reportes", options=options, selection_mode="multi")
        #st.markdown(f"Haz seleccionado: {selection}.")

        bttn_consulta = st.button("Realizar consulta")

        

    st.title("INSITRA ANALITICS")

    kilometraje = {
        "terid": terid_sel,
        "starttime": "2025-10-01",
        "endtime": "2025-10-08"
    }

    conteo_pasajeros = {
        "terid": terid_sel,
        "starttime": "2025-10-01",
        "endtime": "2025-10-08"
    }

    if bttn_consulta:

        if "Kilometraje" in selection:
            ok, payload, err = cbc.api_post("basic/mileage/count", json=kilometraje,)
            if ok:
                km = pd.DataFrame(payload.get("data"))
                st.dataframe(km, use_container_width=True)
            else:
                st.error("Por favor seleccione unidades.")
        
        if "Conteo" in selection:
            ok, payload, err = cbc.api_post("basic/passenger-count/detail", json=conteo_pasajeros,)
            if ok:
                conteo = pd.DataFrame(payload.get("data"))
                st.dataframe(conteo, use_container_width=True)
            else:
                st.error("Por favor seleccione unidades.")

