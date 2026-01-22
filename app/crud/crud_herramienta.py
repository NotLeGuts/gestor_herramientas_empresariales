from sqlmodel import Session, select
from app.models.herramienta import Herramienta


def create_herramienta(
    session: Session,
    nombre: str,
    categoria: str,
    estado: bool,
    codigo_interno: str,
    cantidad_disponible: int,
    descripcion: str = None,
):
    "Crear una nueva herramienta"
    herramienta = Herramienta(
        nombre=nombre,
        categoria=categoria,
        estado=estado,
        codigo_interno=codigo_interno,
        cantidad_disponible=cantidad_disponible,
        descripcion=descripcion,
    )
    session.add(herramienta)
    session.commit()
    session.refresh(herramienta)

    return herramienta


def get_herramienta_by_id(session: Session, herramienta_id: int):
    "Obtener herramienta por su ID"
    statement = select(Herramienta).where(Herramienta.id_herramienta == herramienta_id)
    return session.exec(statement).first()


def get_herramientas(session: Session, skip: int = 0, limit: int = 100):
    "Obtener todas las herramientas con paginación"
    statement = select(Herramienta).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_herramientas_disponibles(session: Session):
    "Obtener solo herramientas disponibles"
    statement = select(Herramienta).where(Herramienta.estado == True)
    return session.exec(statement).all()


def get_herramientas_por_categoria(session: Session, categoria: str):
    "Obtener herramientas por categoría"
    statement = select(Herramienta).where(Herramienta.categoria == categoria)
    return session.exec(statement).all()


def update_herramienta(session: Session, herramienta_id: int, **kwargs):
    "Actualizar herramienta"
    db_herramienta = get_herramienta_by_id(session, herramienta_id)
    if not db_herramienta:
        return None

    for key, value in kwargs.items():
        setattr(db_herramienta, key, value)

    session.commit()
    session.refresh(db_herramienta)
    return db_herramienta


def inhabilitar_herramienta(session: Session, herramienta_id: int):
    "Inhabilitar una herramienta (marcarla como inactiva)"
    db_herramienta = get_herramienta_by_id(session, herramienta_id)
    if not db_herramienta:
        return False

    db_herramienta.estado = False
    session.commit()
    session.refresh(db_herramienta)
    return True


def habilitar_herramienta(session: Session, herramienta_id: int):
    "Habilitar herramienta (marcarla como activa)"
    db_herramienta = get_herramienta_by_id(session, herramienta_id)
    if not db_herramienta:
        return False

    db_herramienta.estado = True
    session.commit()
    session.refresh(db_herramienta)
    return True
