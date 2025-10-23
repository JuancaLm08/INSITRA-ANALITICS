# ------------------ Configuración y imports ------------------
from datetime import date, timedelta
import streamlit as st
import pandas as pd
import ceiba_client as cbc
import utilidades as util
import procesed as pcd
import Graphics as graph

st.set_page_config(
    page_title='Insitra Analytics: Unidades',
    page_icon="img/INSITRA_LOGO.png",
    layout='wide',
)

# ------------------ Autenticación y sidebar ------------------
cbc.login()
cbc.require_login()

dispositivos, err_d = cbc.listar_dispositivos_simplificado()
if err_d:
    st.error(err_d)
    st.stop()

with st.sidebar:
    st.subheader("Filtros")
    comp_nombres, comp_ids,_ = util.selector_companias(container=st.sidebar, key_prefix="sb")

terids_todos = util.terid_grupo(dispositivos, comp_ids)

# ------------------ Vista principal ------------------
st.title('INSITRA ANALYTICS: Unidades 🚍')
st.header('Conteo de pasajeros')

placas_sel_p, terids_sel_p, mapeo_p = util.selector_placas(
    dispositivos, comp_ids,key_prefix="sb")

iniciop, finalp, rango_fechas = util.fecha_default(6)

# ---------- Llamada a la API ----------
conteo_pasajeros = {
    "terid": terids_sel_p or terids_todos,
    "starttime": f"{iniciop} 00:00:00",
    "endtime": f"{finalp} 23:59:59",
}

ok, payload, err = cbc.api_post("basic/passenger-count/detail", json=conteo_pasajeros)
if not ok:
    st.error(err or "Error consultando CEIBA")
    st.stop()

# ---------- Procesamiento y vista ----------
conteo = pd.DataFrame(payload.get('data') or [])
if conteo.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

pud = pcd.construir_pud(conteo)  # tu función de procesado por unidad/día
pud["Unidad"] = pud["Unidad"].map(mapeo_p)

#G R A F I C A M O S
pfig, pud_plot = graph.pasajeros_unidad_dia(
    df = pud,
    unidades = placas_sel_p,
    rango_fechas = rango_fechas,
    valor = 'Ascensos'
)

#Excepsiones
if pfig is None or pud_plot.empty:
    st.warning('No hay datos de las fechas seleccionadas')
else:
    st.plotly_chart(pfig,use_container_width=True)
    with st.expander('Ver los datos mostrados en la gráfica'):
        st.dataframe(pud_plot,use_container_width=True)


#Kilometraje


placas_sel_k, terids_sel_k, mapeo_k = util.selector_placas(
    dispositivos, comp_ids,key_prefix="sb1")

# ---------- Rango de fechas ----------
iniciok, finalk, rango_fechask = util.fecha_default(6, 2)

kilometraje = {
        "terid": terids_sel_k or terids_todos,
        "starttime": f"{iniciok} 00:00:00",
        "endtime": f"{finalk} 23:59:59"
        }

ok, payload, err = cbc.api_post("basic/mileage/count", json=kilometraje)
if not ok:
    st.error(err or "Error consultando CEIBA")
    st.stop()

# ---------- Procesamiento y vista ----------
kilometraje = pd.DataFrame(payload.get('data') or [])
if kilometraje.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

kud = pcd.construir_kud(kilometraje)
kud["Unidad"] = kud["Unidad"].map(mapeo_k)

kfig, kud_plot = graph.kilometros_unidad_dia(
    df = kud,
    unidades = placas_sel_k,
    rango_fechas = rango_fechask,
    valor = 'Kilometraje',
)

#Excepsiones
if kfig is None or kud_plot.empty:
    st.warning('No hay datos de las fechas seleccionadas')
else:
    st.plotly_chart(kfig,use_container_width=True)
    with st.expander('Ver los datos mostrados en la gráfica'):
        st.dataframe(kud_plot,use_container_width=True)