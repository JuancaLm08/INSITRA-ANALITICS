import streamlit as st
import requests
import utilidades as util

API = st.secrets.get("CEIBA_BASE_URL")
# ---------------------------------------------------------------------
# AUTENTICACIÓN
# ---------------------------------------------------------------------

def validarUsuario(usuario: str, clave: str):
    try:
        resp = requests.get(
            f"{API}/basic/key",
            params={"username": usuario, "password": clave},
            timeout=10,
        )
    except requests.RequestException as e:
        return False, None, f"Error de red: {e}"

    try:
        data = resp.json()
    except ValueError:
        return False, None, "Respuesta no es JSON."

    err = data.get("errorcode")
    if err == 200:
        key = (data.get("data") or {}).get("key")
        if key:
            return True, key, None
        return False, None, "Respuesta inesperada: falta 'data.key'."
    elif err == 206:
        return False, None, "Credenciales incorrectas."
    else:
        return False, None, f"Error de aplicación (errorcode={err})."

def _guardar_sesion(usuario: str, api_key: str):
    st.session_state["usuario"] = usuario
    st.session_state["api_key"] = api_key

def cerrar_sesion():
    st.session_state.clear()
    st.rerun()

def api_get(endpoint: str, params: dict):

    if "api_key" not in st.session_state:
        return False, None, "No autenticado (falta api_key)."

    p = dict(params or {})
    p["key"] = st.session_state["api_key"]

    try:
        r = requests.get(f"{API}/{endpoint.lstrip('/')}", params=p, timeout=10)
    except requests.RequestException as e:
        return False, None, f"Error de red: {e}"

    try:
        data = r.json()
    except ValueError:
        return False, None, "Respuesta no es JSON."

    return True, data, None

def api_post(endpoint: str, json: dict):

    if "api_key" not in st.session_state:
        return False, None, "No autenticado (falta api_key)."

    #p = dict(params or {})
    key = st.session_state["api_key"]
    json["key"] = key

    try:
        r = requests.post(
            f"{API}/{endpoint.lstrip('/')}",
            json=json,  
            timeout=20,
        )
    except requests.RequestException as e:
        return False, None, f"Error de red: {e}"

    # Algunas APIs devuelven siempre 200; igual parseamos JSON
    try:
        payload = r.json()
    except ValueError:
        return False, None, f"Respuesta no es JSON. HTTP {r.status_code}: {r.text[:200]}"

    return True, payload, None

@st.cache_data(ttl=300)
def listar_grupos():
    ok, payload, err = api_get("basic/groups", params={'key': st.session_state.get("api_key")})
    if not ok:
        return [], err
    grupos = payload.get("data", []) or []
    # Normaliza llaves esperadas
    out = []
    for g in grupos:
        item = {
            "groupid": g.get("groupid"),
            "groupname": g.get("groupname"),
        }
        out.append(item)

    return out, None

@st.cache_data(ttl=300)
def listar_dispositivos_simplificado():
    ok, payload, err = api_get("basic/devices", params={'key': st.session_state.get("api_key")})
    if not ok:
        return [], err
    dispositivos = payload.get("data", []) or []
    out = []
    for d in dispositivos:
        item = {
            "groupid": d.get("groupid"),
            "carlicence": d.get("carlicence"),  # así está en la doc
            "terid": d.get("terid"),
        }
        out.append(item)
        
    return out, None

def terid_por_placa(placa: str):

    ok, payload, err = api_get(f"basic/devices/{placa}")
    if not ok:
        return None, err
    data = payload.get("data") or {}
    return data.get("terid"), None

def login():
    if "usuario" in st.session_state and "api_key" in st.session_state:
        util.navegacion(st.session_state["usuario"])
    else:
        # Contenedor centrado por columnas
        c1, c2, c3 = st.columns([1, 3, 1])
        with c2:
            # Título "centrado" al ponerlo en la columna central
            st.markdown(
                "<h2 style='text-align:center;'> Iniciar Sesión </h2>",
                unsafe_allow_html=True
            )

            with st.form("frmLogin"):
                # Labels grandes (ocultamos el label nativo del input)
                st.subheader("Usuario")
                parUsuario = st.text_input("", placeholder="Ingresa tu usuario",
                                           label_visibility="collapsed")

                st.subheader("Contraseña")
                parPassword = st.text_input("", type="password", placeholder="Ingresa tu contraseña",
                                            label_visibility="collapsed")

                # Botón centrado en la columna media
                b1, b2, b3 = st.columns([1, 4, 1])
                with b2:
                    btnLogin = st.form_submit_button("Acceder", type="primary",
                                                     use_container_width=True)
                
                st.echo('Recuerda acceder con el mismo usuario y contraseña de CEIBA II ')
                    
                

        if btnLogin:
            with st.spinner("Validando..."):
                ok, key, err = validarUsuario(parUsuario, parPassword)
            if ok and key:
                _guardar_sesion(parUsuario, key)
                st.rerun()
            else:
                st.error(err or "Usuario o clave inválidos", icon=":material/gpp_maybe:")

def require_login():
    """
    Úsalo al inicio de cada página interna para forzar que haya sesión.
    """
    if "usuario" not in st.session_state or "api_key" not in st.session_state:
        #st.warning("Debes iniciar sesión para continuar.")
        st.stop()
