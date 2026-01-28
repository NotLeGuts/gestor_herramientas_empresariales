"""
Operaciones CRUD para gestionar categorías de herramientas.

Las categorías están asociadas a herramientas específicas y permiten
organizar y categorizar las herramientas en el sistema.
"""

from sqlmodel import Session, select
from app.models.categoria import Categoria


def create_categoria(
    session: Session,
    nombre: str,
    estado: bool = True,
):
    """
    Crear una nueva categoría.
    
    Args:
        session: Sesión de base de datos
        nombre: Nombre de la categoría
        estado: Estado activo/inactivo de la categoría (default: True)
    
    Returns:
        La categoría creada
    """
    try:
        categoria = Categoria(
            nombre=nombre,
            estado=estado,
        )
        session.add(categoria)
        session.commit()
        session.refresh(categoria)

        return categoria
    except Exception as e:
        # Hacer rollback en caso de error
        session.rollback()
        # Re-lanzar la excepción para que el llamador pueda manejarla
        raise Exception(f"Error al crear categoría: {str(e)}")


def get_categoria_by_id(session: Session, categoria_id: int):
    """
    Obtener categoría por su ID.
    
    Args:
        session: Sesión de base de datos
        categoria_id: ID de la categoría a buscar
    
    Returns:
        La categoría encontrada o None si no existe
    """
    statement = select(Categoria).where(Categoria.id_categoria == categoria_id)
    return session.exec(statement).first()


def get_categorias(session: Session, skip: int = 0, limit: int = 100):
    """
    Obtener todas las categorías con paginación.
    
    Args:
        session: Sesión de base de datos
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
    
    Returns:
        Lista de categorías
    """
    statement = select(Categoria).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_herramientas_por_categoria(session: Session, id_categoria_h: int):
    """
    Obtener todas las herramientas asociadas a una categoría específica.
    
    Args:
        session: Sesión de base de datos
        id_categoria_h: ID de la categoría padre
    
    Returns:
        Lista de herramientas asociadas a esa categoría
    """
    from app.models.herramienta import Herramienta
    statement = select(Herramienta).where(Herramienta.id_categoria_h == id_categoria_h)
    return session.exec(statement).all()


def get_categorias_activas(session: Session):
    """
    Obtener solo las categorías activas.
    
    Args:
        session: Sesión de base de datos
    
    Returns:
        Lista de categorías activas
    """
    statement = select(Categoria).where(Categoria.estado == True)
    return session.exec(statement).all()


def update_categoria(session: Session, categoria_id: int, **kwargs):
    """
    Actualizar una categoría existente.
    
    Args:
        session: Sesión de base de datos
        categoria_id: ID de la categoría a actualizar
        **kwargs: Campos a actualizar (nombre, id_herramienta_h, estado)
    
    Returns:
        La categoría actualizada o None si no existe
    """
    try:
        db_categoria = get_categoria_by_id(session, categoria_id)
        if not db_categoria:
            return None

        for key, value in kwargs.items():
            setattr(db_categoria, key, value)

        session.commit()
        session.refresh(db_categoria)
        return db_categoria
    except Exception as e:
        # Hacer rollback en caso de error
        session.rollback()
        # Re-lanzar la excepción para que el llamador pueda manejarla
        raise Exception(f"Error al actualizar categoría: {str(e)}")


def inhabilitar_categoria(session: Session, categoria_id: int):
    """
    Inhabilitar una categoría (marcarla como inactiva).
    
    Args:
        session: Sesión de base de datos
        categoria_id: ID de la categoría a inhabilitar
    
    Returns:
        True si se inhabilitó correctamente, False si no existe
    """
    db_categoria = get_categoria_by_id(session, categoria_id)
    if not db_categoria:
        return False

    db_categoria.estado = False
    session.commit()
    session.refresh(db_categoria)
    return True


def habilitar_categoria(session: Session, categoria_id: int):
    """
    Habilitar una categoría (marcarla como activa).
    
    Args:
        session: Sesión de base de datos
        categoria_id: ID de la categoría a habilitar
    
    Returns:
        True si se habilitó correctamente, False si no existe
    """
    db_categoria = get_categoria_by_id(session, categoria_id)
    if not db_categoria:
        return False

    db_categoria.estado = True
    session.commit()
    session.refresh(db_categoria)
    return True


def delete_categoria(session: Session, categoria_id: int):
    """
    Eliminar una categoría de la base de datos.
    
    Args:
        session: Sesión de base de datos
        categoria_id: ID de la categoría a eliminar
    
    Returns:
        True si se eliminó correctamente, False si no existe
    """
    db_categoria = get_categoria_by_id(session, categoria_id)
    if not db_categoria:
        return False

    session.delete(db_categoria)
    session.commit()
    return True
