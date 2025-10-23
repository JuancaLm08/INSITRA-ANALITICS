import streamlit as st
import ceiba_client as cbc
from datetime import date, timedelta

def navegacion(usuario):
    with st.sidebar:
        st.write(f"Hola **:blue-background[{usuario}]** ¿Que vamos a hacer hoy? ")

        if st.button('Cerrar Sesión', width="stretch"):
            cbc.cerrar_sesion()

        st.title('Paneles')
        st.page_link('app.py',label=' Totales',icon='📊')
        st.page_link('pages/Unidades.py',label=' Unidades',icon='🚍')
        st.page_link('pages/Ruta.py',label=' Ruta',icon='🚦')

def selector_companias(container=st, key_prefix="comp"):

    grupos, err = cbc.listar_grupos()
    if err:
        container.error(err)
        return [], [], {}

    mapa_nombre_a_id = {g["groupname"]: g["groupid"] for g in grupos}
    nombres = sorted(mapa_nombre_a_id.keys())

    sel_nombres = container.multiselect(
        "Compañías",
        options=nombres,
        key=f"{key_prefix}_companias",
        default=nombres[0]
    )
    sel_ids = [mapa_nombre_a_id[n] for n in sel_nombres]
        
    return sel_nombres, sel_ids, mapa_nombre_a_id

def terid_grupo(dispositivos: list[dict], groupids: int, return_mapping: bool = False):
    gids = set(groupids or [])
    terids = [d["terid"] for d in dispositivos if d["groupid"] in gids]

    if return_mapping:
        map_terid_to_placa = {d["terid"]: d["carlicence"] for d in dispositivos if d["groupid"] in gids}
        return terids, map_terid_to_placa

    return terids

def selector_placas(dispositivos, groupids, sel_default = None,container=st, key_prefix="placas"):

    # Opciones de placas (únicas) para los grupos elegidos
    placas_opciones = sorted({
        d["carlicence"] for d in dispositivos if d["groupid"] in (groupids or [])
    })

    sel_placas = container.multiselect(
        "Placas",
        options=placas_opciones,
        key=f"{key_prefix}_placas",
        default=sel_default
    )

    terids_sel = [
        d["terid"] for d in dispositivos
        if d["groupid"] in (groupids or []) and d["carlicence"] in sel_placas
    ]

    map_terid_to_placa = {d["terid"]: d["carlicence"] for d in dispositivos}

    return sel_placas, terids_sel, map_terid_to_placa

def fecha_default(dias: int, num_key: int = 1):
    date_presetp = date.today() - timedelta(days=dias)

    c1, c2 = st.columns([1,1])
    with c1:
        feche_inicio = st.date_input("Inicio", date_presetp, key=f"fecha_inicio {num_key}")
    with c2:
        feche_final = st.date_input("Final", key=f"fecha_final {num_key}")

    rango_fechas = (feche_inicio, feche_final)

    if  feche_inicio > feche_final:
        st.error("La fecha de inicio no puede ser mayor a la fecha final.")
        st.stop()
    
    return feche_inicio, feche_final, rango_fechas