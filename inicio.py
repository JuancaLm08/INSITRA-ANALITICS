import streamlit as st
import ceiba_client as cbc
import pandas as pd
import procesed as pcd
import Graphics as graph
from PIL import Image


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
        
        map_terid_to_placa = {}
        for d in dispositivos:
            map_terid_to_placa[d["terid"]] = d["carlicence"]


        #st.caption(f"terid: **{terid_sel or '—'}**")

        options = ["Kilometraje","Conteo"]
        selection = st.pills("Seleccione reportes", options=options, selection_mode="multi")
        #st.markdown(f"Haz seleccionado: {selection}.")

        feche_inicio = st.date_input("Fecha inicio")
        feche_final = st.date_input("Fecha final")
        



        bttn_consulta = st.button("Realizar consulta")

    st.title("INSITRA ANALITICS")

    kilometraje = {
        "terid": terid_sel,
        "starttime": f"{feche_inicio} 00:00:00",
        "endtime": f"{feche_final} 23:59:59"
        }

    conteo_pasajeros = {
        "terid": terid_sel,
        "starttime": f"{feche_inicio} 00:00:00",
        "endtime": f"{feche_final} 23:59:59"
        }
    
    rango_fechas = (feche_inicio, feche_final)


    if bttn_consulta:

        if "Kilometraje" in selection:
            ok, payload, err = cbc.api_post("basic/mileage/count", json=kilometraje,)
            if ok:
                km = pd.DataFrame(payload.get("data"))
                kud = pcd.construir_kud(km)
                kud["Unidad"] = kud["Unidad"].map(map_terid_to_placa)
                data_kud = kud
                #st.dataframe(kud, use_container_width=True)
            else:
                st.error("Por favor seleccione unidades.")
        
        if "Conteo" in selection:
            ok, payload, err = cbc.api_post("basic/passenger-count/detail", json=conteo_pasajeros,)
            if ok:
                conteo = pd.DataFrame(payload.get("data"))
                pud = pcd.construir_pud(conteo)
                pud["Unidad"] = pud["Unidad"].map(map_terid_to_placa)
                data_pud = pud
                #st.dataframe(pud, use_container_width=True)
            else:
                st.error("Por favor seleccione unidades.")
    
        pfig, pud_plot = graph.pasajeros_unidad_dia(
        df=data_pud,
        unidades = placas_sel,
        rango_fechas = rango_fechas,
        valor = 'Ascensos')

        #    E X C E P C I O N E S: pasajeros por unidad y dia
        if pfig is None or pud_plot.empty:
            st.warning('No hay datos en las fechas seleccionadas')
        else:
            st.plotly_chart(pfig, use_container_width=True)
            with st.expander('Ver datos mostrados en la grafica'):
                st.dataframe(pud_plot, use_container_width=True)
        
            #    G R A F I C A M O S: kilometros por unidad y dia
        kfig, kud_plot = graph.kilometros_unidad_dia(
            df = data_kud,
            unidades = placas_sel,
            rango_fechas = rango_fechas,
            valor = 'Kilometraje',
        )

            #    E X C E P C I O N E S: pasajeros por unidad y dia
        if kfig is None or kud_plot.empty:
            st.warning('No hay datos en las fechas seleccionadas')
        else:
            st.plotly_chart(kfig, use_container_width=True)
            with st.expander('Ver datos mostrados en la grafica'):
                st.dataframe(kud_plot, use_container_width=True)