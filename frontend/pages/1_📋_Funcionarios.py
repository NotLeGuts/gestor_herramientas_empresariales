"""
Página para gestionar empleados.

Permite:
- Ver lista de empleados
- Crear nuevos empleados
- Editar empleados existentes
- Inhabilitar/habilitar empleados
"""

import streamlit as st
from sqlmodel import Session
from app.database.config import engine
from app.crud import (
    create_empleado,
    get_empleados,
    get_empleado_by_id,
    update_empleado,
    inhabilitar_empleado,
    habilitar_empleado,
    get_empleados_activos,
    get_empleados_por_area
)
from frontend.utils import show_success, show_error, show_info, validate_required_fields


# Cachear el motor de base de datos (no la sesión)
@st.cache_resource
def get_db_engine():
    """Obtener el motor de base de datos."""
    return engine


def render_empleado_form(empleado=None):
    """Renderizar formulario para crear/editar empleado."""
    if empleado:
        st.markdown(
            f"""
            <div class="page-title">
                <span class="icon">✏️</span>
                <h2>Editar funcionário: {empleado.nombre} {empleado.apellido}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="page-title">
                <span class="icon">➕</span>
                <h2>Adicionar funcionário</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with st.form(key="empleado_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nome", value=empleado.nombre if empleado else "")
            apellido = st.text_input("Sobrenome", value=empleado.apellido if empleado else "")
                    
        with col2:
            area = st.text_input("Departamento", value=empleado.area if empleado else "")

            correo = st.text_input("E-mail", value=empleado.correo if empleado else "")
            # Solo mostrar checkbox de activo en edición, no en creación
            if empleado:
                activo = st.checkbox("Ativo", value=empleado.activo)
            else:
                activo = True  # Siempre activo por defecto al crear
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submitted = st.form_submit_button("Salvar", type="primary")
        
        # Botón de cancelar solo en edición
        if empleado:
            with col2:
                if st.form_submit_button("Cancelar"):
                    # Eliminar el estado de edición y recargar
                    if "editing_empleado_id" in st.session_state:
                        del st.session_state["editing_empleado_id"]
                    st.rerun()
        
        with col3:
            st.write("")  # Espacio en blanco para alinear los botones
        
        if submitted:
            # Validar campos requeridos (solo nombre es obligatorio)
            if not nombre or str(nombre).strip() == "":
                show_error("O campo Nome é obrigatório")
                return None
            
            engine = get_db_engine()
            
            try:
                with Session(engine) as session:
                    if empleado:
                        # Actualizar empleado existente
                        update_empleado(
                            session,
                            empleado.id,
                            nombre=nombre,
                            apellido=apellido,
                            area=area,
                            correo=correo,
                            activo=activo
                        )
                        show_success(f"Funcionário {nombre} {apellido} atualizado com sucesso")
                    else:
                        # Crear nuevo empleado
                        create_empleado(
                            session,
                            nombre=nombre,
                            apellido=apellido,
                            area=area,
                            correo=correo,
                            activo=activo
                        )
                        show_success(f"Funcionário {nombre} {apellido} criado com sucesso")
                
                # Eliminar estado de edición si existe y recargar
                if "editing_empleado_id" in st.session_state:
                    del st.session_state["editing_empleado_id"]
                st.rerun()
                
            except Exception as e:
                show_error(f"Erro ao salvar funcionário: {str(e)}")
    
    return None


def render_empleado_details(empleado, expanded=False):
    """Renderizar detalles de un empleado."""
    with st.expander(f"📋 {empleado.nombre} {empleado.apellido}", expanded=expanded):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**ID:** {empleado.id}")
            st.write(f"**Departamento:** {empleado.area}")
        
        with col2:
            st.write(f"**E-mail:** {empleado.correo}")
            st.write(f"**Estado:** {'✅ Ativo' if empleado.activo else '❌ Inativo'}")
        
        with col3:
            if st.button("Editar", key=f"edit_{empleado.id}"):
                st.session_state["editing_empleado_id"] = empleado.id
                st.rerun()
            
            if empleado.activo:
                if st.button("Desabilitar", key=f"disable_{empleado.id}"):
                    engine = get_db_engine()
                    with Session(engine) as session:
                        inhabilitar_empleado(session, empleado.id)
                    show_success(f"Funcionário {empleado.nombre} desabilitado")
                    st.rerun()
            else:
                if st.button("Habilitar", key=f"enable_{empleado.id}"):
                    engine = get_db_engine()
                    with Session(engine) as session:
                        habilitar_empleado(session, empleado.id)
                    show_success(f"Funcionário {empleado.nombre} habilitado")
                    st.rerun()


def render_empleados_list(empleados):
    """Renderizar lista de empleados."""
    if not empleados:
        st.info("Não há funcionários registrados. Adicione um usando o formulário.")
        return
    
    # Estado para expandir/contraer todos
    if "expand_all_empleados" not in st.session_state:
        st.session_state.expand_all_empleados = False
    
    # Estado para filtros
    if "empleado_search_term" not in st.session_state:
        st.session_state.empleado_search_term = ""
    
    if "empleado_filter_activo" not in st.session_state:
        st.session_state.empleado_filter_activo = "Activo"
    
    # Filtros
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        search_term = st.text_input(
            "Buscar", 
            placeholder="Buscar funcionário",
            value=st.session_state.empleado_search_term
        )
        # Actualizar session state cuando cambia el valor
        if search_term != st.session_state.empleado_search_term:
            st.session_state.empleado_search_term = search_term
    
    with col2:
        # Usar el valor del session state como valor predeterminado
        filter_activo = st.selectbox(
            "Filtrar por estado",
            ["Todos", "Ativo", "Inativo"],
            # key="empleado_filter_activo",
            index=1
        )
        # Actualizar session state cuando cambia el valor
        if filter_activo != st.session_state.empleado_filter_activo:
            st.session_state.empleado_filter_activo = filter_activo
    
    # with col3:
    #     # Botón para expandir/contraer todos
    #     expand_button = st.button(
    #         "📑 Expandir Todo" if not st.session_state.expand_all_empleados else "📐 Contraer Todo",
    #         key="expand_all_button"
    #     )
    #     if expand_button:
    #         st.session_state.expand_all_empleados = not st.session_state.expand_all_empleados
    #         st.rerun()
    # 
    # Filtrar empleados
    filtered_empleados = empleados
    
    # Usar los valores del session state para filtrar
    if st.session_state.empleado_search_term:
        search_term_lower = st.session_state.empleado_search_term.lower()
        filtered_empleados = [
            e for e in filtered_empleados
            if (search_term_lower in str(e.nombre).lower() if e.nombre else "") or
               (search_term_lower in str(e.apellido).lower() if e.apellido else "") or
               (search_term_lower in str(e.correo).lower() if e.correo else "") or
               (search_term_lower in str(e.area).lower() if e.area else "")
        ]
    
    if st.session_state.empleado_filter_activo == "Ativo":
        filtered_empleados = [e for e in filtered_empleados if e.activo]
    elif st.session_state.empleado_filter_activo == "Inativo":
        filtered_empleados = [e for e in filtered_empleados if not e.activo]
    
    # Mostrar resultados
    st.write(f"**Total: {len(filtered_empleados)} funcionários**")
    
    # Mostrar mensaje si no se encontraron resultados
    if st.session_state.empleado_search_term and len(filtered_empleados) == 0:
        st.warning("Não foram encontrados funcionários que coincidam com a busca.")
    
    for empleado in filtered_empleados:
        render_empleado_details(empleado, expanded=st.session_state.expand_all_empleados)


def main():
    """Punto de entrada principal de la página."""
    # Establecer página actual
    st.session_state.current_page = "empleados"
    
    # Sidebar con título
    with st.sidebar:
        st.title("🔧 Gestor de Ferramentas")
        st.markdown("---")
    
    # Título con ícono minimalista
    st.markdown(
        """
        <div class="page-title">
            <span class="icon">👤</span>
            <h1>Gestão de Funcionários</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Obtener empleados
    engine = get_db_engine()
    with Session(engine) as session:
        empleados = get_empleados(session)
    
    # Verificar si estamos editando un empleado
    if "editing_empleado_id" in st.session_state:
        editing_id = st.session_state["editing_empleado_id"]
        with Session(engine) as session:
            empleado_to_edit = get_empleado_by_id(session, editing_id)
        
        if empleado_to_edit:
            render_empleado_form(empleado_to_edit)
        else:
            del st.session_state["editing_empleado_id"]
            show_error("Funcionário não encontrado")
    else:
        # Mostrar formulario para nuevo empleado
        render_empleado_form()
        
        st.markdown("---")
        
        # Mostrar lista de empleados
        render_empleados_list(empleados)


if __name__ == "__main__":
    main()
