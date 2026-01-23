from sqlmodel import Session, select
from app.models.empleado import Empleado


def create_empleado(
    session: Session,
    nombre: str,
    apellido: str,
    area: str,
    correo: str | None = None,
    activo: bool = True,
):
    "Crear empleado nuevo"
    empleado = Empleado(
        nombre=nombre,
        apellido=apellido,
        area=area,
        correo=correo,
        activo=activo,
    )
    session.add(empleado)
    session.commit()
    session.refresh(empleado)

    return empleado


def get_empleado_by_id(session: Session, empleado_id: int):
    "Obtener un empleado por su ID"
    statement = select(Empleado).where(Empleado.id == empleado_id)
    return session.exec(statement).first()


def get_empleados(session: Session, skip: int = 0, limit: int = 100):
    "Obtener todos los empleados con paginación"
    statement = select(Empleado).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_empleados_activos(session: Session):
    "Obtener solo empleados activos"
    statement = select(Empleado).where(Empleado.activo == True)
    return session.exec(statement).all()


def get_empleados_por_area(session: Session, area: str):
    "Obtener empleados por área"
    statement = select(Empleado).where(Empleado.area == area)
    return session.exec(statement).all()


def update_empleado(session: Session, empleado_id: int, **kwargs):
    "Actualizar empleado"
    db_empleado = get_empleado_by_id(session, empleado_id)
    if not db_empleado:
        return None

    for key, value in kwargs.items():
        setattr(db_empleado, key, value)

    session.commit()
    session.refresh(db_empleado)
    return db_empleado


def inhabilitar_empleado(session: Session, empleado_id: int):
    "Inhabilitar un empleado (marcarlo como inactivo)"
    db_empleado = get_empleado_by_id(session, empleado_id)
    if not db_empleado:
        return False

    db_empleado.activo = False
    session.commit()
    session.refresh(db_empleado)
    return True


def habilitar_empleado(session: Session, empleado_id: int):
    "Habilitar un empleado (marcarlo como activo)"
    db_empleado = get_empleado_by_id(session, empleado_id)
    if not db_empleado:
        return False

    db_empleado.activo = True
    session.commit()
    session.refresh(db_empleado)
    return True
