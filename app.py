import streamlit as st
import ceiba_client as cbc
import pandas as pd
import procesed as pcd
import Graphics as graph
import utilidades as util
# ----------------------------- P A G E   C O N F I G U R A T I O N -----------------------------

st.set_page_config(page_title="Inicio", page_icon="img/INSITRA_LOGO.png", layout="wide")
cbc.login()
cbc.require_login()

# Trae una sola vez la lista de dispositivos simplificada
dispositivos, err_d = cbc.listar_dispositivos_simplificado()
if err_d:
    st.error(err_d)
    st.stop()

# -------------------- F I L T R O S   E N   B A R R A   L A T E R A L ------------------------

with st.sidebar:
    st.subheader("Filtros")
    comp_nombres, comp_ids,_ = util.selector_companias(container=st.sidebar, key_prefix="sb")
terids_todos = util.terid_grupo(dispositivos, comp_ids)

# ------------------------------ T I T U L O   P R I N C I P A L --------------------------

st.title('INSITRA ANALYTICS: Totales 📊')

# --------------------- C O N T E O   D E   P A S A J E R O S ------------------------

st.header('Conteo de pasajeros')

iniciop, finalp, _ = util.fecha_default(6)

conteo_pasajeros = {
    "terid": terids_todos,
    "starttime": f"{iniciop} 00:00:00",
    "endtime": f"{finalp} 23:59:59"
    }

ok, payload, err = cbc.api_post("basic/passenger-count/detail", json=conteo_pasajeros)
if ok:
    conteo = pd.DataFrame(payload.get('data'))
    pdap = pcd.construir_padp(conteo,30)

else:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

#Graficamos pdapfig1 = Total de ascensos por dia
pdapfig1 = graph.pasajeros_por_unidad_dia_promedio(
    df = pdap,
    valor = 'Total de ascensos',
)

pdapfig2 = graph.pasajeros_por_unidad_dia_promedio(
    df = pdap,
    valor = 'Promedio por unidad',
)

if pdapfig1 is None or pdap.empty:
    st.warning('No hay datos en las fechas seleccionadas')  
else:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(pdapfig1, use_container_width=True)
    with c2:
        st.plotly_chart(pdapfig2, use_container_width=True)
    with st.expander('Ver los datos mostrados en la gráfica'):
        st.dataframe(pdap)


# ------------------------------ KILOMETRAJE ---------------------------------

#Título de la sección
st.header('Kilometraje')

#Barra de selección de fecha.
iniciok, finalk, _ = util.fecha_default(6,2)

#Declaramos el json
kilometraje = {
        "terid": terids_todos,
        "starttime": f"{iniciok} 00:00:00",
        "endtime": f"{finalk} 23:59:59"
        }

#Pasajeros unidad dia promedio
ok, payload, err = cbc.api_post('basic/mileage/count',json=kilometraje)

#Verificamos que la respuesta haya sido exitosa
if ok:
    conteo = pd.DataFrame(payload.get('data'))
    kipd = pcd.construir_kipd(conteo,30)
    

#Graficamos pdapfig1 = Total de ascensos por dia
kipdfig1 = graph.pasajeros_por_unidad_dia_promedio(
    df = kipd,
    valor = 'Kilometraje',
)

kipdfig2 = graph.pasajeros_por_unidad_dia_promedio(
    df = kipd,
    valor = 'Promedio por unidad',
)

if kipdfig1 is None or kipd.empty:
    st.warning('No hay datos en las fechas seleccionadas')  
else:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(kipdfig1, use_container_width=True)
    with c2:
        st.plotly_chart(kipdfig2, use_container_width=True)
    with st.expander('Ver los datos mostrados en la gráfica'):
        st.dataframe(kipd)