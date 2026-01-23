"""
Página para gestionar herramientas.

Permite:
- Ver lista de herramientas
- Crear nuevas herramientas
- Editar herramientas existentes
- Inhabilitar/habilitar herramientas
- Filtrar por categoría y disponibilidad
"""

import streamlit as st
from sqlmodel import Session
from app.database.config import engine
from app.crud import (
    create_herramienta,
    get_herramientas,
    get_herramienta_by_id,
    update_herramienta,
    inhabilitar_herramienta,
    habilitar_herramienta,
    get_herramientas_disponibles,
    get_herramientas_por_categoria
)
from frontend.utils import show_success, show_error, show_info, validate_required_fields


# Cachear el motor de base de datos (no la sesión)
@st.cache_resource
def get_db_engine():
    """Obtener el motor de base de datos."""
    return engine


def render_herramienta_form(herramienta=None):
    """Renderizar formulario para crear/editar herramienta."""
    if herramienta:
        st.markdown(
            f"""
            <div class="page-title">
                <span class="icon">✏️</span>
                <h2>Editar Ferramenta: {herramienta.nombre}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="page-title">
                <span class="icon">➕</span>
                <h2>Adicionar Nova Ferramenta</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with st.form(key="herramienta_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nome", value=herramienta.nombre if herramienta else "")
            categoria = st.text_input("Categoria", value=herramienta.categoria if herramienta else "")
            codigo_interno = st.text_input(
                "Código Interno",
                value=herramienta.codigo_interno if herramienta else "",
                help="Código único para identificar a ferramenta"
            )
        
        with col2:
            cantidad_disponible = st.number_input(
                "Quantidade Disponível",
                min_value=0,
                value=herramienta.cantidad_disponible if herramienta else 1,
                step=1
            )
            # estado = st.checkbox("Ativa", value=herramienta.estado if herramienta else True)
            descripcion = st.text_area(
                "Descrição (opcional)",
                value=herramienta.descripcion if herramienta else "",
                height=100
            )
        
        submitted = st.form_submit_button("Salvar", type="primary")
        
        if submitted:
            # Validar campos requeridos
            required_fields = {
                "Nome": nombre,
                "Categoria": categoria,
                "Código Interno": codigo_interno
            }
            is_valid, message = validate_required_fields(**required_fields)
            
            if not is_valid:
                show_error(message)
                return None
            
            engine = get_db_engine()
            
            try:
                with Session(engine) as session:
                    if herramienta:
                        # Actualizar herramienta existente
                        update_herramienta(
                            session,
                            herramienta.id_herramienta,
                            nombre=nombre,
                            categoria=categoria,
                            estado=herramienta.estado,
                            codigo_interno=codigo_interno,
                            cantidad_disponible=cantidad_disponible,
                            descripcion=descripcion
                        )
                        show_success(f"Ferramenta {nombre} atualizada com sucesso")
                    else:
                        # Crear nueva herramienta
                        create_herramienta(
                            session,
                            nombre=nombre,
                            categoria=categoria,
                            estado=True,
                            codigo_interno=codigo_interno,
                            cantidad_disponible=cantidad_disponible,
                            descripcion=descripcion
                        )
                        show_success(f"Ferramenta {nombre} criada com sucesso")
                
                # Recargar la página para ver los cambios
                st.rerun()
                
            except Exception as e:
                show_error(f"Erro ao salvar ferramenta: {str(e)}")
    
    return None


def render_herramienta_details(herramienta):
    """Renderizar detalles de una herramienta."""
    # Icono diferente para herramientas fuera de servicio
    icono = "🔧" if herramienta.estado else "⚠️"
    estado_texto = " (Em Serviço)" if herramienta.estado else " (Fora de Serviço)"
    
    with st.expander(f"{icono} {herramienta.nombre}{estado_texto}", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**ID:** {herramienta.id_herramienta}")
            st.write(f"**Categoria:** {herramienta.categoria}")
            st.write(f"**Código:** {herramienta.codigo_interno}")
        
        with col2:
            st.write(f"**Estoque:** {herramienta.cantidad_disponible}")
            st.write(f"**Estado:** {'✅ Em Serviço' if herramienta.estado else '⚠️ Fora de Serviço'}")
            st.write(f"**Disponível:** {'✅ Sim' if herramienta.cantidad_disponible > 0 else '❌ Não'}")
        
        with col3:
            if herramienta.descripcion:
                st.write(f"**Descrição:** {herramienta.descripcion[:50]}...")
            
            # Botones de acción
            if st.button("📝 Editar", key=f"edit_herramienta_{herramienta.id_herramienta}"):
                st.session_state["editing_herramienta_id"] = herramienta.id_herramienta
                st.rerun()
            
            if herramienta.estado:
                if st.button("❌ Desabilitar", key=f"disable_herramienta_{herramienta.id_herramienta}"):
                    engine = get_db_engine()
                    with Session(engine) as session:
                        inhabilitar_herramienta(session, herramienta.id_herramienta)
                    show_success(f"Ferramenta {herramienta.nombre} desabilitada")
                    st.rerun()
            else:
                if st.button("✅ Habilitar", key=f"enable_herramienta_{herramienta.id_herramienta}"):
                    engine = get_db_engine()
                    with Session(engine) as session:
                        habilitar_herramienta(session, herramienta.id_herramienta)
                    show_success(f"Ferramenta {herramienta.nombre} habilitada")
                    st.rerun()


def render_herramientas_list(herramientas):
    """Renderizar lista de herramientas."""
    if not herramientas:
        # Verificar si hay herramientas en la base de datos pero no se muestran por el filtro
        herramientas_en_servicio = len([h for h in herramientas if h.estado == True])
        herramientas_fuera_servicio = len([h for h in herramientas if h.estado == False])
        
        if herramientas_en_servicio == 0 and herramientas_fuera_servicio == 0:
            st.info("Não há ferramentas registradas. Adicione uma usando o formulário.")
        elif filter_estado == "Em Serviço":
            st.info("Não há ferramentas **Em Serviço**. Você pode habilitar ferramentas que estejam atualmente **Fora de Serviço** ou adicionar novas.")
        elif filter_estado == "Fora de Serviço":
            st.info("Não há ferramentas **Fora de Serviço**. Todas as ferramentas registradas estão atualmente **Em Serviço**.")
        elif filter_estado == "Todos":
            st.info("Não há ferramentas registradas. Adicione uma usando o formulário.")
        else:
            st.info("Não há ferramentas registradas. Adicione uma usando o formulário.")
        return
    
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Filtro de estado (en servicio vs fuera de servicio)
        filter_estado = st.selectbox(
            "📋 Estado",
            ["Em Serviço", "Fora de Serviço", "Todos"],
            index=0
        )
    
    with col2:
        search_term = st.text_input("🔍 Buscar", placeholder="Nome ou código...")
    
    with col3:
        filter_disponibilidad = st.selectbox(
            "📊 Disponibilidade",
            ["Todos", "Disponíveis", "Não Disponíveis"],
            index=1
        )
    
    with col4:
        # Obtener categorías únicas
        categorias = sorted(list(set(h.categoria for h in herramientas)))
        filter_categoria = st.selectbox(
            "📁 Categoria",
            ["Todas"] + categorias
        )
    
    # Filtrar herramientas
    filtered_herramientas = herramientas
    
    # Primero filtrar por estado (en servicio vs fuera de servicio)
    if filter_estado == "Em Serviço":
        filtered_herramientas = [h for h in filtered_herramientas if h.estado == True]
    elif filter_estado == "Fora de Serviço":
        filtered_herramientas = [h for h in filtered_herramientas if h.estado == False]
    
    # Luego aplicar otros filtros
    if search_term:
        search_term_lower = search_term.lower()
        filtered_herramientas = [
            h for h in filtered_herramientas
            if (search_term_lower in h.nombre.lower() or
                search_term_lower in h.codigo_interno.lower())
        ]
    
    # Filtrar por disponibilidad - solo aplica a herramientas En Servicio
    if filter_disponibilidad != "Todos":
        # Solo aplicar filtro de disponibilidad si estamos viendo herramientas En Servicio
        if filter_estado == "Em Serviço":
            if filter_disponibilidad == "Disponíveis":
                filtered_herramientas = [h for h in filtered_herramientas if h.cantidad_disponible > 0]
            elif filter_disponibilidad == "Não Disponíveis":
                filtered_herramientas = [h for h in filtered_herramientas if h.cantidad_disponible <= 0]
        # Si estamos viendo Fuera de Servicio, ignorar el filtro de disponibilidad
    
    if filter_categoria != "Todas":
        filtered_herramientas = [h for h in filtered_herramientas if h.categoria == filter_categoria]
    
    # Mostrar resultados
    st.write(f"**Total: {len(filtered_herramientas)} ferramentas**")
    
    # Estadísticas rápidas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Total de herramientas en servicio
        herramientas_en_servicio = len([h for h in herramientas if h.estado == True])
        st.metric("🔧 Em Serviço", herramientas_en_servicio)
    
    with col2:
        # Total de herramientas fuera de servicio
        herramientas_fuera_servicio = len([h for h in herramientas if h.estado == False])
        st.metric("⚠️ Fora de Serviço", herramientas_fuera_servicio)
    
    with col3:
        # Total general
        st.metric("📊 Total Registradas", len(herramientas))
    
    # Mensajes informativos según el filtro de estado
    if filter_estado == "Em Serviço" and len(filtered_herramientas) > 0:
        st.success("📋 Mostrando ferramentas **Em Serviço**. Estas são as ferramentas ativas e disponíveis para empréstimo.")
    elif filter_estado == "Fora de Serviço" and len(filtered_herramientas) > 0:
        st.info("💡 Estas ferramentas foram marcadas como **Fora de Serviço** (não são mais utilizadas ou foram retiradas). O filtro de disponibilidade não se aplica a esta seção.")
    elif filter_estado == "Todos" and len(filtered_herramientas) > 0:
        st.info("📊 Mostrando todas as ferramentas registradas, tanto em serviço como fora de serviço.")

    st.markdown("---")
    
    for herramienta in filtered_herramientas:
        render_herramienta_details(herramienta)


def main():
    """Punto de entrada principal de la página."""
    # Establecer página actual
    st.session_state.current_page = "herramientas"
    
    # Sidebar con título
    with st.sidebar:
        st.title("🔧 Gestor de Herramientas")
        st.markdown("---")
    
    # Título con ícono minimalista
    st.markdown(
        """
        <div class="page-title">
            <span class="icon">🔧</span>
            <h1>Gestão de Ferramentas</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Obtener herramientas
    engine = get_db_engine()
    with Session(engine) as session:
        herramientas = get_herramientas(session)
    
    # Verificar si estamos editando una herramienta
    if "editing_herramienta_id" in st.session_state:
        editing_id = st.session_state["editing_herramienta_id"]
        with Session(engine) as session:
            herramienta_to_edit = get_herramienta_by_id(session, editing_id)
        
        if herramienta_to_edit:
            render_herramienta_form(herramienta_to_edit)
        else:
            del st.session_state["editing_herramienta_id"]
            show_error("Ferramenta não encontrada")
    else:
        # Mostrar formulario para nueva herramienta
        render_herramienta_form()
        
        st.markdown("---")
        
        # Mostrar lista de herramientas
        render_herramientas_list(herramientas)


if __name__ == "__main__":
    main()
