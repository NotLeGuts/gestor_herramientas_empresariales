"""
Punto de entrada principal para la aplicación Gestor de Herramientas.

Este archivo configura la aplicación Streamlit y define la estructura base.
"""

import streamlit as st
from sqlmodel import Session
from app.database.config import engine
from app.crud import get_empleados, get_herramientas, get_prestamos_activos


# Configuración inicial de la aplicación
st.set_page_config(
    page_title="Dashboard - Gestor de Herramientas",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)




# Cachear la sesión de base de datos
@st.cache_resource
def get_db_session():
    """Obtener una sesión de base de datos."""
    return Session(engine)


# Función para obtener datos iniciales
def get_dashboard_data():
    """Obtener datos para el dashboard principal."""
    session = get_db_session()
    
    empleados = get_empleados(session)
    herramientas = get_herramientas(session)
    prestamos_activos = get_prestamos_activos(session)
    
    return {
        "empleados": empleados,
        "herramientas": herramientas,
        "prestamos_activos": prestamos_activos,
        "herramientas_disponibles": sum(h.cantidad_disponible for h in herramientas if h.estado),
        "herramientas_no_disponibles": sum(h.cantidad_disponible for h in herramientas if not h.estado)
    }


# Sidebar con navegación
def render_sidebar():
    """Renderizar el sidebar con la navegación."""
    with st.sidebar:
        st.title("🔧 Gestor de Herramientas")
        st.markdown("---")
        
        st.markdown("---")
        
        # # Solo mostrar enlaces en la página de inicio
        # if "current_page" not in st.session_state or st.session_state.current_page == "home":
        #     st.page_link("pages/1_📋_Empleados.py", label="📋 Empleados")
        #     st.page_link("pages/2_🔧_Herramientas.py", label="🔧 Herramientas")
        #     st.page_link("pages/3_📦_Prestamos.py", label="📦 Préstamos")
        #     st.page_link("pages/4_📊_Reportes.py", label="📊 Reportes")
        #

# Dashboard principal
def render_dashboard():
    """Renderizar el dashboard principal."""
    # Título del dashboard
    st.title("Bem-vindo")
    
    # Mensaje de bienvenida
    st.info(
        f"👋 Bem-vindo ao Gestor de Ferramentas! "
        f"Este painel fornece uma visão geral do estado atual do sistema."
    )
    
    # Obtener datos
    data = get_dashboard_data()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Funcionários",
            len(data["empleados"]),
            help="Total de funcionários no sistema"
        )
    
    with col2:
        st.metric(
            "Ferramentas",
            len(data["herramientas"]),
            help="Total de ferramentas registradas"
        )
    
    with col3:
        st.metric(
            "Disponível",
            data["herramientas_disponibles"],
            help="Ferramentas disponíveis para empréstimo"
        )
    
    with col4:
        st.metric(
            "Empréstimos",
            len(data["prestamos_activos"]),
            help="Empréstimos atualmente ativos",
            delta_color="off"
        )
    
    st.markdown("---")


# Página principal
def main():
    """Punto de entrada principal de la aplicación."""
    
    # Establecer página actual
    st.session_state.current_page = "home"
    
    # Renderizar sidebar
    render_sidebar()
    
    # Renderizar dashboard principal
    render_dashboard()


if __name__ == "__main__":
    main()
