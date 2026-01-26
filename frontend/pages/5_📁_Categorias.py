"""
Página para gerenciar categorias de ferramentas.

Permite:
- Ver lista de categorias
- Criar novas categorias
- Editar categorias existentes
- Inabilitar/abilitar categorias
- Excluir categorias
"""

import streamlit as st
from sqlmodel import Session
from app.database.config import engine
from app.crud import (
    create_categoria,
    get_categorias,
    get_categoria_by_id,
    update_categoria,
    inhabilitar_categoria,
    habilitar_categoria,
    delete_categoria,
    get_categorias_activas,
)
from frontend.utils import show_success, show_error, show_info, validate_required_fields


# Cachear o motor de base de dados (não a sessão)
@st.cache_resource
def get_db_engine():
    """Obter o motor de base de dados."""
    return engine


def render_categoria_form(categoria=None):
    """Renderizar formulário para criar/editar categoria."""
    if categoria:
        st.markdown(
            f"""
            <div class="page-title">
                <span class="icon">✏️</span>
                <h2>Editar Categoria: {categoria.nombre}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="page-title">
                <span class="icon">➕</span>
                <h2>Agregar Nova Categoria</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Botão de voltar (fora do formulário, apenas para edições)
    if categoria:
        if st.button("⬅️ Voltar", use_container_width=True, key=f"voltar_categoria_{categoria.id_categoria}"):
            # Voltar para a lista de categorias
            del st.session_state["editing_categoria_id"]
            st.rerun()
    
    with st.form(key=f"categoria_form_{categoria.id_categoria if categoria else 'new'}"):
        nombre = st.text_input("Nome da Categoria", value=categoria.nombre if categoria else "")
        # estado = st.checkbox("Ativa", value=categoria.estado if categoria else True)
        
        # Botão de salvar dentro do formulário
        submitted = st.form_submit_button("Salvar", type="primary")
        
        if submitted:
            # Validar campos obrigatórios
            required_fields = {
                "Nome da Categoria": nome,
            }
            is_valid, message = validate_required_fields(**required_fields)
            
            if not is_valid:
                show_error(message)
                return None
            
            engine = get_db_engine()
            
            try:
                with Session(engine) as session:
                    if categoria:
                        # Atualizar categoria existente
                        update_categoria(
                            session,
                            categoria.id_categoria,
                            nome=nome,
                            estado=estado,
                        )
                        show_success(f"Categoria {nome} atualizada com sucesso")
                    else:
                        # Criar nova categoria
                        create_categoria(
                            session,
                            nome=nome,
                            estado=estado,
                        )
                        show_success(f"Categoria {nome} criada com sucesso")
                
                # Recarregar a página para ver as alterações
                st.rerun()
                
            except Exception as e:
                show_error(f"Erro ao salvar categoria: {str(e)}")
    
    return None


def render_categoria_details(categoria):
    """Renderizar detalhes de uma categoria."""
    # Ícone diferente para categorias inativas
    icono = "📁" if categoria.estado else "🗑️"
    estado_texto = " (Ativa)" if categoria.estado else " (Inativa)"
    
    with st.expander(f"{icono} {categoria.nombre}{estado_texto}", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**ID:** {categoria.id_categoria}")
            
            # Obter ferramentas associadas a esta categoria
            engine = get_db_engine()
            with Session(engine) as session:
                # Importar aqui para evitar circular imports
                from app.crud import get_herramientas_por_categoria
                herramientas = get_herramientas_por_categoria(session, categoria.id_categoria)
            
            # if herramientas:
            #     st.write(f"**Ferramentas:** {len(herramientas)}")
            # else:
            #     st.write("**Ferramentas:** Nenhuma")
        
        with col2:
            st.write(f"**Estado:** {'✅ Ativa' if categoria.estado else '⚠️ Inativa'}")
        
        with col3:
            # Botões de ação
            if st.button("📝 Editar", key=f"edit_categoria_{categoria.id_categoria}"):
                # Salvar que viemos da lista para voltar depois de salvar
                st.session_state["editing_categoria_id"] = categoria.id_categoria
                st.rerun()
            
            if categoria.estado:
                if st.button("❌ Desativar", key=f"disable_categoria_{categoria.id_categoria}"):
                    engine = get_db_engine()
                    with Session(engine) as session:
                        inhabilitar_categoria(session, categoria.id_categoria)
                    show_success(f"Categoria {categoria.nombre} desativada")
                    st.rerun()
            else:
                if st.button("✅ Ativar", key=f"enable_categoria_{categoria.id_categoria}"):
                    engine = get_db_engine()
                    with Session(engine) as session:
                        habilitar_categoria(session, categoria.id_categoria)
                    show_success(f"Categoria {categoria.nombre} ativada")
                    st.rerun()
            
            # Botão para eliminar categoria
            if st.button("🗑️ Excluir", key=f"delete_categoria_{categoria.id_categoria}"):
                # Usar um formulário para manejar a confirmação
                with st.form(key=f"delete_form_{categoria.id_categoria}"):
                    st.warning(f"Tem certeza que deseja excluir a categoria '{categoria.nombre}'? Esta ação não pode ser desfeita.")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("❌ Cancelar", key=f"cancel_delete_{categoria.id_categoria}"):
                            st.rerun()
                    with col2:
                        if st.form_submit_button("✅ Confirmar", key=f"confirm_delete_{categoria.id_categoria}"):
                            engine = get_db_engine()
                            with Session(engine) as session:
                                # Eliminar a categoria
                                delete_categoria(session, categoria.id_categoria)
                                # Limpar o session_state para forçar recarga completa
                                for key in list(st.session_state.keys()):
                                    if key.startswith("delete_form_") or key.startswith("confirm_delete_") or key.startswith("cancel_delete_"):
                                        del st.session_state[key]
                            show_success(f"Categoria {categoria.nombre} excluída com sucesso")
                            # Forçar recarga completa
                            st.rerun()


def render_categorias_list():
    """Renderizar lista de todas as categorias."""
    engine = get_db_engine()
    with Session(engine) as session:
        categorias = get_categorias(session)
    
    if not categorias:
        st.info("Não há categorias registradas. Adicione uma usando o formulário.")
        return
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtro por estado
        filter_estado = st.selectbox(
            "📋 Estado",
            ["Todos", "Ativas", "Inativas"],
            index=1
        )
    
    with col2:
        # Estatísticas rápidas
        categorias_activas = len([c for c in categorias if c.estado == True])
        st.metric("📁 Ativas", categorias_activas)
    
    with col3:
        # Estatísticas rápidas
        categorias_inactivas = len([c for c in categorias if c.estado == False])
        st.metric("⚠️ Inativas", categorias_inactivas)
    
    # Filtrar categorias segundo a seleção
    if filter_estado == "Ativas":
        categorias_filtradas = [c for c in categorias if c.estado == True]
    elif filter_estado == "Inativas":
        categorias_filtradas = [c for c in categorias if c.estado == False]
    else:
        categorias_filtradas = categorias
    
    # Mostrar total filtrado
    st.info(f"Mostrando {len(categorias_filtradas)} de {len(categorias)} categorias")
    
    st.markdown("---")
    
    # Mostrar categorias filtradas
    for categoria in categorias_filtradas:
        render_categoria_details(categoria)


def main():
    """Ponto de entrada principal da página."""
    # Estabelecer página atual
    st.session_state.current_page = "categorias"
    
    # Sidebar com título
    with st.sidebar:
        st.title("📁 Gestor de Categorias")
        st.markdown("---")
    
    # Título com ícone minimalista
    st.markdown(
        """
        <div class="page-title">
            <span class="icon">📁</span>
            <h1>Gestão de Categorias</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Verificar se estamos editando uma categoria
    if "editing_categoria_id" in st.session_state:
        categoria_id = st.session_state["editing_categoria_id"]
        engine = get_db_engine()
        with Session(engine) as session:
            categoria_to_edit = get_categoria_by_id(session, categoria_id)
        
        if categoria_to_edit:
            render_categoria_form(categoria_to_edit)
        else:
            del st.session_state["editing_categoria_id"]
            show_error("Categoria não encontrada")
    else:
        # Mostrar formulário para nova categoria e lista de categorias
        render_categoria_form()
        
        st.markdown("---")
        
        # Mostrar lista de categorias
        render_categorias_list()


if __name__ == "__main__":
    main()
