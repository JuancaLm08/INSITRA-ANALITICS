import streamlit as st
import requests

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

def generarMenu(usuario):
     
    with st.sidebar:
        
        st.write(f"Hola **:blue-background[{usuario}]** ")
        
        if st.button("Salir"):
            cerrar_sesion()

def login():
    if "usuario" in st.session_state and "api_key" in st.session_state:
        generarMenu(st.session_state["usuario"])
    else:
        st.header("INICIAR SESIÓN")

        with st.form("frmLogin"):
            parUsuario = st.text_input("Usuario")
            parPassword = st.text_input("Password", type="password")
            btnLogin = st.form_submit_button("Ingresar", type="primary")

        if btnLogin:
            with st.spinner("Validando..."):
                ok, key, err = validarUsuario(parUsuario, parPassword)
            if ok and key:
                _guardar_sesion(parUsuario, key)
                # Navegación: si tienes Streamlit reciente puedes cambiar de página
                #if redirect_to: 
                #    st.switch_page(redirect_to)
                st.rerun()
            else:
                st.error(err or "Usuario o clave inválidos", icon=":material/gpp_maybe:")

def require_login():
    """
    Úsalo al inicio de cada página interna para forzar que haya sesión.
    """
    if "usuario" not in st.session_state or "api_key" not in st.session_state:
        st.warning("Debes iniciar sesión para continuar.")
        st.stop()

