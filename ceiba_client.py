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


def generarMenu(usuario):
     
    with st.sidebar:
        
        st.write(f"Hola **:blue-background[{usuario}]** ")
        # Mostramos los enlaces de páginas
        st.page_link("inicio.py", label="Inicio", icon=":material/home:")
        st.subheader("Tableros")
        st.page_link("pages/pagina1.py", label="Pagina 1", icon=":material/sell:")

        
        if st.button("Salir"):
            cerrar_sesion()

def login():
    if "usuario" in st.session_state and "api_key" in st.session_state:
        generarMenu(st.session_state["usuario"])
    else:

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