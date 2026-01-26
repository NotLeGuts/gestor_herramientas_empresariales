"""
Página para gestionar préstamos de herramientas.

Permite:
- Registrar nuevos préstamos
- Ver préstamos activos
- Devolver herramientas
- Cancelar préstamos
- Filtrar por empleado, herramienta y estado
"""

import streamlit as st
from sqlmodel import Session
from datetime import datetime, timedelta
from app.database.config import engine
from app.crud import (
    create_prestamo,
    get_prestamos,
    get_prestamos_activos,
    get_prestamos_por_empleado,
    get_prestamos_por_herramienta,
    get_prestamos_vencidos,
    devolver_prestamo,
    cancelar_prestamo,
    get_empleados_activos,
    get_herramientas_disponibles,
    get_empleado_by_id,
    get_herramienta_by_id
)
from frontend.utils import (
    show_success,
    show_error,
    show_info,
    validate_required_fields,
    format_date,
    format_date_short
)


# Cachear el motor de base de datos (no la sesión)
@st.cache_resource
def get_db_engine():
    """Obtener el motor de base de datos."""
    return engine


def render_prestamo_form():
    """Renderizar formulario para crear nuevo préstamo."""
    st.markdown(
        """
        <div class="page-title">
            <span class="icon">➕</span>
            <h2>Registrar Novo Empréstimo</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    engine = get_db_engine()
    
    # Obtener datos antes del formulario para evitar problemas con la sesión
    with Session(engine) as session:
        empleados = get_empleados_activos(session)
        herramientas = get_herramientas_disponibles(session)
        herramientas_disponibles = [h for h in herramientas if h.cantidad_disponible > 0]
    
    if not empleados:
        st.warning("Não há funcionários ativos para atribuir empréstimos")
        return
    
    if not herramientas_disponibles:
        st.warning("Não há ferramentas disponíveis para empréstimo")
        return
    
    empleado_options = {f"{e.nombre} {e.apellido} ({e.area})": e.id for e in empleados}
    herramienta_options = {f"{h.nombre} ({h.codigo_interno}) - Estoque: {h.cantidad_disponible}": h.id_herramienta for h in herramientas_disponibles}
    
    with st.form(key="prestamo_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            selected_empleado_id = st.selectbox(
                "Funcionário",
                options=list(empleado_options.keys()),
                format_func=lambda x: x
            )
            empleado_id = empleado_options[selected_empleado_id]
            
            selected_herramienta_id = st.selectbox(
                "Ferramenta",
                options=list(herramienta_options.keys()),
                format_func=lambda x: x
            )
            herramienta_id = herramienta_options[selected_herramienta_id]
        
        with col2:
            fecha_prestamo = st.date_input(
                "Data do Empréstimo",
                value=datetime.now(),
                min_value=datetime.now()
            )
            
            dias_prestamo = st.number_input(
                "Dias do Empréstimo",
                min_value=1,
                value=1,
                step=1,
                help="Dias estimados para a devolução"
            )
            
            fecha_devolucion_estimada = fecha_prestamo + timedelta(days=dias_prestamo)
            st.write(f"**Data Estimada de Devolução:** {fecha_devolucion_estimada.strftime('%d/%m/%Y')}")
            
            observaciones = st.text_area(
                "Observações (opcional)",
                height=100,
                placeholder="Notas adicionais sobre o empréstimo..."
            )
        
        submitted = st.form_submit_button("Registrar Empréstimo", type="primary")
        
        if submitted:
            try:
                # Crear una nueva sesión para el envío del formulario
                with Session(engine) as session:
                    # Crear el préstamo
                    prestamo = create_prestamo(
                        session,
                        id_empleado_h=empleado_id,
                        id_herramienta_h=herramienta_id,
                        fecha_prestamo=datetime.combine(fecha_prestamo, datetime.min.time()),
                        fecha_devolucion_estimada=datetime.combine(fecha_devolucion_estimada, datetime.min.time()),
                        observaciones=observaciones
                    )
                    
                    if prestamo:
                        show_success(f"Empréstimo registrado com sucesso (ID: {prestamo.id_prestamo})")
                        st.rerun()
                    else:
                        show_error("Não foi possível registrar o empréstimo. Verifique se a ferramenta está disponível.")
                        
            except Exception as e:
                show_error(f"Erro ao registrar empréstimo: {str(e)}")


def render_prestamo_details(prestamo):
    """Renderizar detalles de un préstamo."""
    engine = get_db_engine()
    
    # Obtener información del empleado y herramienta
    with Session(engine) as session:
        empleado = get_empleado_by_id(session, prestamo.id_empleado_h)
        herramienta = get_herramienta_by_id(session, prestamo.id_herramienta_h)
    
    nombre_empleado = f"{empleado.nombre} {empleado.apellido}" if empleado else "Funcionário não encontrado"
    nombre_herramienta = herramienta.nombre if herramienta else "Ferramenta não encontrada"
    
    # Determinar color de fondo según estado
    # Usamos colores consistentes con el tema definido en config.toml
    if prestamo.estado == "activo":
        if prestamo.fecha_devolucion_estimada < datetime.now():
            bg_color = "#fff3cd"  # Amarillo (vencido) - fondo claro con texto oscuro
            estado_text = "⚠️ Vencido"
        else:
            bg_color = "#e3f2fd"  # Azul muy claro (activo) - usando la paleta del tema
            estado_text = "🟢 Activo"
    elif prestamo.estado == "devuelto":
        bg_color = "#e8f5e9"  # Verde muy claro (devuelto) - consistente con el tema
        estado_text = "🔵 Devuelto"
    else:
        bg_color = "#ffebee"  # Rojo muy claro (cancelado) - consistente con el tema
        estado_text = "🔴 Cancelado"
    
    with st.expander(
        f"📋 Empréstimo #{prestamo.id_prestamo} - {nombre_empleado} → {nombre_herramienta}",
        expanded=(prestamo.estado == "activo" and prestamo.fecha_devolucion_estimada < datetime.now())
    ):
        st.markdown(f"""
        <div style="background-color: {bg_color}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <strong>Estado:</strong> {estado_text} | 
            <strong>Data do Empréstimo:</strong> {format_date_short(prestamo.fecha_prestamo)} | 
            <strong>Data Estimada:</strong> {format_date_short(prestamo.fecha_devolucion_estimada)}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Funcionário:** {nombre_empleado}")
            st.write(f"**Departamento:** {empleado.area if empleado else 'N/A'}")
            st.write(f"**E-mail:** {empleado.correo if empleado else 'N/A'}")
        
        with col2:
            st.write(f"**Ferramenta:** {nombre_herramienta}")
            st.write(f"**Código:** {herramienta.codigo_interno if herramienta else 'N/A'}")
            st.write(f"**Categoria:** {herramienta.categoria if herramienta else 'N/A'}")
        
        with col3:
            if prestamo.fecha_devolucion:
                st.write(f"**Data da Devolução:** {format_date_short(prestamo.fecha_devolucion)}")
            
            if prestamo.observaciones:
                st.write(f"**Observações:** {prestamo.observaciones[:50]}...")
        
        # Botones de acción
        if prestamo.estado == "activo":
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Devolver", key=f"devolver_{prestamo.id_prestamo}"):
                    # Usar st.session_state para confirmar la acción
                    if st.session_state.get(f"confirm_devolver_{prestamo.id_prestamo}", False):
                        devolver_prestamo(session, prestamo.id_prestamo)
                        show_success("Empréstimo marcado como devolvido")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_devolver_{prestamo.id_prestamo}"] = True
                        st.warning("Tem certeza de que deseja marcar este empréstimo como devolvido?")
                        st.button("Cancelar", key=f"cancel_confirm_devolver_{prestamo.id_prestamo}", 
                                  on_click=lambda: st.session_state.pop(f"confirm_devolver_{prestamo.id_prestamo}", None))
            
            with col2:
                if st.button("❌ Cancelar", key=f"cancelar_{prestamo.id_prestamo}"):
                    if st.session_state.get(f"confirm_cancelar_{prestamo.id_prestamo}", False):
                        cancelar_prestamo(session, prestamo.id_prestamo)
                        show_success("Empréstimo cancelado")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_cancelar_{prestamo.id_prestamo}"] = True
                        st.warning("Tem certeza de que deseja cancelar este empréstimo?")
                        st.button("Cancelar", key=f"cancel_confirm_cancelar_{prestamo.id_prestamo}",
                                  on_click=lambda: st.session_state.pop(f"confirm_cancelar_{prestamo.id_prestamo}", None))


def render_prestamos_list(prestamos):
    """Renderizar lista de préstamos."""
    if not prestamos:
        st.info("Não há empréstimos registrados.")
        return
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Buscar", placeholder="Funcionário, ferramenta ou código...")
    
    with col2:
        # Por defecto, mostrar solo préstamos activos (esto es lo más lógico)
        filter_estado = st.selectbox(
            "📊 Estado",
            ["Ativos", "Todos", "Vencidos", "Devolvidos", "Cancelados"],
            index=0  # Activos seleccionado por defecto
        )
    
    with col3:
        # Obtener empleados para filtro
        engine = get_db_engine()
        with Session(engine) as session:
            empleados = get_empleados_activos(session)
        empleado_options = {f"{e.nombre} {e.apellido}": e.id for e in empleados}
        filter_empleado = st.selectbox(
            "👤 Funcionário",
            ["Todos"] + list(empleado_options.keys())
        )
    
    # Filtrar préstamos
    filtered_prestamos = prestamos
    
    if search_term:
        search_term_lower = search_term.lower()
        filtered_prestamos = [
            p for p in filtered_prestamos
            if (search_term_lower in str(p.id_prestamo) or
                search_term_lower in str(p.id_empleado_h) or
                search_term_lower in str(p.id_herramienta_h))
        ]
    
    if filter_estado == "Ativos":
        filtered_prestamos = [p for p in filtered_prestamos if p.estado == "activo"]
    elif filter_estado == "Vencidos":
        filtered_prestamos = [
            p for p in filtered_prestamos
            if p.estado == "activo" and p.fecha_devolucion_estimada < datetime.now()
        ]
    elif filter_estado == "Devolvidos":
        filtered_prestamos = [p for p in filtered_prestamos if p.estado == "devuelto"]
    elif filter_estado == "Cancelados":
        filtered_prestamos = [p for p in filtered_prestamos if p.estado == "cancelado"]
    
    if filter_empleado != "Todos":
        empleado_id = empleado_options[filter_empleado]
        filtered_prestamos = [p for p in filtered_prestamos if p.id_empleado_h == empleado_id]
    
    # Mostrar resultados
    st.write(f"**Total: {len(filtered_prestamos)} empréstimos**")
    
    # Estadísticas rápidas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        activos = sum(1 for p in filtered_prestamos if p.estado == "activo")
        st.metric("Ativos", activos)
    with col2:
        vencidos = sum(1 for p in filtered_prestamos if p.estado == "activo" and p.fecha_devolucion_estimada < datetime.now())
        st.metric("Vencidos", vencidos, delta_color="inverse")
    with col3:
        devueltos = sum(1 for p in filtered_prestamos if p.estado == "devuelto")
        st.metric("Devolvidos", devueltos)
    with col4:
        cancelados = sum(1 for p in filtered_prestamos if p.estado == "cancelado")
        st.metric("Cancelados", cancelados)
    
    st.markdown("---")
    
    for prestamo in filtered_prestamos:
        render_prestamo_details(prestamo)


def main():
    """Punto de entrada principal de la página."""
    # Establecer página actual
    st.session_state.current_page = "prestamos"
    
    # Sidebar con título
    with st.sidebar:
        st.title("🔧 Gestor de Ferramentas")
        st.markdown("---")
    
    # Título con ícono minimalista
    st.markdown(
        """
        <div class="page-title">
            <span class="icon">📦</span>
            <h1>Gestão de Empréstimos</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Obtener préstamos
    engine = get_db_engine()
    with Session(engine) as session:
        prestamos = get_prestamos(session)
    
    # Mostrar formulario para nuevo préstamo
    render_prestamo_form()
    
    st.markdown("---")
    
    # Mostrar lista de préstamos
    render_prestamos_list(prestamos)
    
    # Inicializar estado de sesión para confirmaciones
    if "confirm_devolver" not in st.session_state:
        st.session_state.confirm_devolver = {}
    if "confirm_cancelar" not in st.session_state:
        st.session_state.confirm_cancelar = {}


if __name__ == "__main__":
    main()
