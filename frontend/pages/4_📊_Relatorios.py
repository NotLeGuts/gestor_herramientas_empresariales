"""
Página para visualizar reportes y estadísticas.

Permite:
- Ver herramientas más solicitadas
- Ver préstamos vencidos
- Estadísticas de uso por empleado
- Disponibilidad de herramientas
"""

import streamlit as st
from sqlmodel import Session
from datetime import datetime, timedelta
from collections import Counter
from app.database.config import engine
from app.crud import (
    get_prestamos,
    get_prestamos_activos,
    get_prestamos_vencidos,
    get_prestamos_por_empleado,
    get_prestamos_por_herramienta,
    get_empleados,
    get_herramientas,
    get_empleado_by_id,
    get_herramienta_by_id
)
from app.models.empleado import Empleado
from frontend.utils import format_date_short


# Cachear el motor de base de datos (no la sesión)
@st.cache_resource
def get_db_engine():
    """Obtener el motor de base de datos."""
    return engine


def get_herramientas_mas_solicitadas(session, top_n=5):
    """Obtener las herramientas más solicitadas."""
    prestamos = get_prestamos(session)
    
    # Contar préstamos por herramienta y recolectar IDs de empleados
    herramienta_data = {}
    for prestamo in prestamos:
        if prestamo.id_herramienta_h not in herramienta_data:
            herramienta_data[prestamo.id_herramienta_h] = {
                'count': 0,
                'empleados': set()
            }
        herramienta_data[prestamo.id_herramienta_h]['count'] += 1
        herramienta_data[prestamo.id_herramienta_h]['empleados'].add(prestamo.id_empleado_h)
    
    # Obtener las herramientas más solicitadas
    top_herramientas = sorted(herramienta_data.items(), key=lambda x: x[1]['count'], reverse=True)[:top_n]
    
    # Obtener detalles de las herramientas y nombres de empleados
    resultado = []
    for herramienta_id, data in top_herramientas:
        herramienta = get_herramienta_by_id(session, herramienta_id)
        if herramienta:
            # Obtener nombres de empleados
            empleados_nombres = []
            for empleado_id in data['empleados']:
                empleado = session.get(Empleado, empleado_id)
                if empleado:
                    empleados_nombres.append(f"{empleado.nombre} {empleado.apellido}")
            
            resultado.append({
                "herramienta": herramienta,
                "prestamos": data['count'],
                "empleados": empleados_nombres
            })
    
    return resultado


def get_empleados_mas_activos(session, top_n=5):
    """Obtener los empleados con más préstamos."""
    prestamos = get_prestamos(session)
    
    # Contar préstamos por empleado
    empleado_counts = Counter()
    for prestamo in prestamos:
        empleado_counts[prestamo.id_empleado_h] += 1
    
    # Obtener los empleados más activos
    top_empleados = empleado_counts.most_common(top_n)
    
    # Obtener detalles de los empleados
    resultado = []
    for empleado_id, count in top_empleados:
        empleado = get_empleado_by_id(session, empleado_id)
        if empleado:
            resultado.append({
                "empleado": empleado,
                "prestamos": count
            })
    
    return resultado


def get_estadisticas_generales(session):
    """Obtener estadísticas generales."""
    prestamos = get_prestamos(session)
    prestamos_activos = get_prestamos_activos(session)
    prestamos_vencidos = get_prestamos_vencidos(session)
    empleados = get_empleados(session)
    herramientas = get_herramientas(session)
    
    return {
        "total_prestamos": len(prestamos),
        "prestamos_activos": len(prestamos_activos),
        "prestamos_vencidos": len(prestamos_vencidos),
        "prestamos_devueltos": sum(1 for p in prestamos if p.estado == "devuelto"),
        "prestamos_cancelados": sum(1 for p in prestamos if p.estado == "cancelado"),
        "total_empleados": len(empleados),
        "empleados_activos": sum(1 for e in empleados if e.activo),
        "total_herramientas": len(herramientas),
        "herramientas_activas": sum(1 for h in herramientas if h.estado),
        "herramientas_disponibles": sum(h.cantidad_disponible for h in herramientas)
    }


def render_reporte_herramientas_solicitadas():
    """Renderizar reporte de herramientas más solicitadas."""
    st.markdown(
        """
        <div class="page-title">
            <span class="icon">🔝</span>
            <h2>Ferramentas Mais Solicitadas</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    engine = get_db_engine()
    with Session(engine) as session:
        herramientas = get_herramientas_mas_solicitadas(session, top_n=10)
    
    if not herramientas:
        st.info("Não há empréstimos registrados ainda.")
        return
    
    # Mostrar en tabla
    st.dataframe(
        [{
            "Posição": i + 1,
            "Ferramenta": h["herramienta"].nombre,
            "Código": h["herramienta"].codigo_interno,
            "Categoria": h["herramienta"].categoria,
            "Empréstimos": ", ".join(h["empleados"]) if h["empleados"] else "Nenhum",
            "Estoque": h["herramienta"].cantidad_disponible
        } for i, h in enumerate(herramientas)],
        hide_index=True,
        use_container_width=True
    )


def render_reporte_prestamos_vencidos():
    """Renderizar reporte de préstamos vencidos."""
    st.markdown(
        """
        <div class="page-title">
            <span class="icon">⚠️</span>
            <h2>Empréstimos Vencidos</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    engine = get_db_engine()
    with Session(engine) as session:
        prestamos_vencidos = get_prestamos_vencidos(session)
    
    if not prestamos_vencidos:
        st.success("✅ Não há empréstimos vencidos")
        return
    
    # Ordenar por fecha de vencimiento (más antiguos primero)
    prestamos_vencidos.sort(key=lambda p: p.fecha_devolucion_estimada)
    
    # Mostrar alerta
    st.warning(f"🚨 Há {len(prestamos_vencidos)} empréstimos vencidos")
    
    # Mostrar en tabla
    for prestamo in prestamos_vencidos:
        empleado = get_empleado_by_id(session, prestamo.id_empleado_h)
        herramienta = get_herramienta_by_id(session, prestamo.id_herramienta_h)
        
        with st.expander(
            f"Empréstimo #{prestamo.id_prestamo} - {empleado.nombre} {empleado.apellido} → {herramienta.nombre}",
            expanded=True
        ):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Funcionário:** {empleado.nombre} {empleado.apellido}")
                st.write(f"**Departamento:** {empleado.area}")
                st.write(f"**E-mail:** {empleado.correo}")
            
            with col2:
                st.write(f"**Ferramenta:** {herramienta.nombre}")
                st.write(f"**Código:** {herramienta.codigo_interno}")
                st.write(f"**Categoria:** {herramienta.categoria}")
            
            with col3:
                st.write(f"**Data do Empréstimo:** {format_date_short(prestamo.fecha_prestamo)}")
                st.write(f"**Data de Vencimento:** {format_date_short(prestamo.fecha_devolucion_estimada)}")
                dias_vencidos = (datetime.now() - prestamo.fecha_devolucion_estimada).days
                st.write(f"**Dias Vencidos:** {dias_vencidos} dias")


def render_reporte_empleados_activos():
    """Renderizar reporte de empleados más activos."""
    st.markdown(
        """
        <div class="page-title">
            <span class="icon">👥</span>
            <h2>Funcionários Mais Ativos</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    engine = get_db_engine()
    with Session(engine) as session:
        empleados = get_empleados_mas_activos(session, top_n=10)
    
    if not empleados:
        st.info("Não há empréstimos registrados ainda.")
        return
    
    # Mostrar en tabla
    st.dataframe(
        [{
            "Posição": i + 1,
            "Funcionário": f"{e['empleado'].nombre} {e['empleado'].apellido}",
            "Área": e["empleado"].area,
            "Empréstimos": e["prestamos"],
            "Estado": "✅ Ativo" if e["empleado"].activo else "❌ Inativo"
        } for i, e in enumerate(empleados)],
        hide_index=True,
        use_container_width=True
    )


def render_estadisticas_generales():
    """Renderizar estadísticas generales."""
    st.markdown(
        """
        <div class="page-title">
            <span class="icon">📊</span>
            <h2>Estatísticas Gerais</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    engine = get_db_engine()
    with Session(engine) as session:
        stats = get_estadisticas_generales(session)
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Empréstimos", stats["total_prestamos"])
        st.metric("Ativos", stats["prestamos_activos"])
        st.metric("Empréstimos Vencidos", stats["prestamos_vencidos"], delta_color="inverse")
    
    with col2:
        st.metric("Empréstimos Devolvidos", stats["prestamos_devueltos"])
        st.metric("Empréstimos Cancelados", stats["prestamos_cancelados"])
    
    with col3:
        st.metric("Total Funcionários", stats["total_empleados"])
        st.metric("Funcionários Ativos", stats["empleados_activos"])
        st.metric("Total Ferramentas", stats["total_herramientas"])
    
    st.markdown("---")
    
    # Gráficos adicionales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            <div class="page-title">
                <span class="icon">📦</span>
                <h3>Estado dos Empréstimos</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.bar_chart({
            "Ativos": stats["prestamos_activos"],
            "Vencidos": stats["prestamos_vencidos"],
            "Devolvidos": stats["prestamos_devueltos"],
            "Cancelados": stats["prestamos_cancelados"]
        })
    
    with col2:
        st.markdown(
            """
            <div class="page-title">
                <span class="icon">🔧</span>
                <h3>Estado das Ferramentas</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.bar_chart({
            "Ativas": stats["herramientas_activas"],
            "Disponíveis": stats["herramientas_disponibles"]
        })


def render_reporte_por_fecha():
    """Renderizar reporte filtrado por fecha."""
    st.markdown(
        """
        <div class="page-title">
            <span class="icon">📅</span>
            <h2>Filtro por Data</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    engine = get_db_engine()
    with Session(engine) as session:
        prestamos = get_prestamos(session)
    
    if not prestamos:
        st.info("Não há empréstimos registrados ainda.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Convertir datetime a date para el min_value y manejar el caso de lista vacía
        min_date = min(p.fecha_prestamo.date() for p in prestamos) if prestamos else datetime.now().date()
        
        # Asegurar que el valor por defecto sea al menos min_date
        default_start = datetime.now() - timedelta(days=30)
        if default_start.date() < min_date:
            default_start = datetime.combine(min_date, datetime.min.time())
        
        fecha_inicio = st.date_input(
            "Data Inicial",
            value=default_start,
            min_value=min_date
        )
    
    with col2:
        fecha_fin = st.date_input(
            "Data Final",
            value=datetime.now(),
            min_value=fecha_inicio
        )
    
    # Filtrar préstamos por fecha
    prestamos_filtrados = [
        p for p in prestamos
        if fecha_inicio <= p.fecha_prestamo.date() <= fecha_fin
    ]
    
    if not prestamos_filtrados:
        st.info("Não há empréstimos no período selecionado.")
        return
    
    st.write(f"**Total de empréstimos no período: {len(prestamos_filtrados)}**")
    
    # Mostrar estadísticas del período
    col1, col2, col3 = st.columns(3)
    
    with col1:
        activos = sum(1 for p in prestamos_filtrados if p.estado == "activo")
        st.metric("Ativos", activos)
    
    with col2:
        devueltos = sum(1 for p in prestamos_filtrados if p.estado == "devuelto")
        st.metric("Devolvidos", devueltos)
    
    with col3:
        cancelados = sum(1 for p in prestamos_filtrados if p.estado == "cancelado")
        st.metric("Cancelados", cancelados)
    
    # Mostrar préstamos
    for prestamo in prestamos_filtrados:
        empleado = get_empleado_by_id(session, prestamo.id_empleado_h)
        herramienta = get_herramienta_by_id(session, prestamo.id_herramienta_h)
        
        with st.expander(
            f"Empréstimo #{prestamo.id_prestamo} - {empleado.nombre} {empleado.apellido} → {herramienta.nombre}",
            expanded=False
        ):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Data:** {format_date_short(prestamo.fecha_prestamo)}")
                st.write(f"**Estado:** {prestamo.estado}")
            
            with col2:
                st.write(f"**Ferramenta:** {herramienta.nombre}")
                st.write(f"**Categoria:** {herramienta.categoria}")
            
            with col3:
                st.write(f"**Funcionário:** {empleado.nombre} {empleado.apellido}")
                st.write(f"**Departamento:** {empleado.area}")


def main():
    """Punto de entrada principal de la página."""
    # Establecer página actual
    st.session_state.current_page = "reportes"
    
    # Sidebar con título
    with st.sidebar:
        st.title("🔧 Gestor de Ferramentas")
        st.markdown("---")
    
    # Título con ícono minimalista
    st.markdown(
        """
        <div class="page-title">
            <span class="icon">📊</span>
            <h1>Relatórios e Estatísticas</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Obtener datos
    engine = get_db_engine()
    
    # Mostrar estadísticas generales
    render_estadisticas_generales()
    
    st.markdown("---")
    
    # Mostrar reportes
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔝 Ferramentas Solicitadas",
        "⚠️ Empréstimos Vencidos",
        "👥 Funcionários Ativos",
        "📅 Filtro por Data"
    ])
    
    with tab1:
        render_reporte_herramientas_solicitadas()
    
    with tab2:
        render_reporte_prestamos_vencidos()
    
    with tab3:
        render_reporte_empleados_activos()
    
    with tab4:
        render_reporte_por_fecha()


if __name__ == "__main__":
    main()
