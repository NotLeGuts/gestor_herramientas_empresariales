from sqlmodel import Session, select
from app.models.prestamo import Prestamo
from app.models.herramienta import Herramienta
from datetime import datetime, timedelta


def create_prestamo(
    session: Session,
    id_empleado_h: int,
    id_herramienta_h: int,
    fecha_prestamo: datetime = None,
    fecha_devolucion_estimada: datetime = None,
    observaciones: str = None,
    estado: str = "activo",
):
    """Crear un nuevo préstamo"""
    try:
        # Obtener la herramienta para validar stock y estado
        herramienta = session.get(Herramienta, id_herramienta_h)
        if not herramienta:
            return None  # Herramienta no existe
        
        # Validar que la herramienta esté activa
        if not herramienta.estado:
            return None  # Herramienta inactiva
        
        # Validar que haya stock disponible
        if herramienta.cantidad_disponible <= 0:
            return None  # No hay stock disponible
        
        # Crear el préstamo
        prestamo = Prestamo(
            id_empleado_h=id_empleado_h,
            id_herramienta_h=id_herramienta_h,
            fecha_prestamo=fecha_prestamo or datetime.now(),
            fecha_devolucion_estimada=fecha_devolucion_estimada or (datetime.now() + timedelta(days=1)),
            observaciones=observaciones,
            estado=estado,
        )
        session.add(prestamo)
        
        # Descontar del stock
        herramienta.cantidad_disponible -= 1
        
        session.commit()
        session.refresh(prestamo)

        return prestamo
    except Exception as e:
        # Hacer rollback en caso de error
        session.rollback()
        # Re-lanzar la excepción para que el llamador pueda manejarla
        raise Exception(f"Error al crear préstamo: {str(e)}")


def get_prestamo_by_id(session: Session, prestamo_id: int):
    """Obtener préstamo por su ID"""
    statement = select(Prestamo).where(Prestamo.id_prestamo == prestamo_id)
    return session.exec(statement).first()


def get_prestamos(session: Session, skip: int = 0, limit: int = 100):
    """Obtener todos los préstamos con paginación"""
    statement = select(Prestamo).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_prestamos_activos(session: Session):
    """Obtener solo préstamos activos (no devueltos)"""
    statement = select(Prestamo).where(Prestamo.estado == "activo")
    return session.exec(statement).all()


def get_prestamos_por_empleado(session: Session, empleado_id: int):
    """Obtener préstamos de un empleado específico"""
    statement = select(Prestamo).where(Prestamo.id_empleado_h == empleado_id)
    return session.exec(statement).all()


def get_prestamos_por_herramienta(session: Session, herramienta_id: int):
    """Obtener préstamos de una herramienta específica"""
    statement = select(Prestamo).where(Prestamo.id_herramienta_h == herramienta_id)
    return session.exec(statement).all()


def get_prestamos_vencidos(session: Session):
    """Obtener préstamos vencidos (fecha_devolucion_estimada < hoy)"""
    hoy = datetime.now()
    statement = select(Prestamo).where(
        (Prestamo.fecha_devolucion_estimada < hoy) &
        (Prestamo.estado == "activo")
    )
    return session.exec(statement).all()


def update_prestamo(session: Session, prestamo_id: int, **kwargs):
    """Actualizar préstamo"""
    try:
        db_prestamo = get_prestamo_by_id(session, prestamo_id)
        if not db_prestamo:
            return None

        for key, value in kwargs.items():
            setattr(db_prestamo, key, value)

        session.commit()
        session.refresh(db_prestamo)
        return db_prestamo
    except Exception as e:
        # Hacer rollback en caso de error
        session.rollback()
        # Re-lanzar la excepción para que el llamador pueda manejarla
        raise Exception(f"Error al actualizar préstamo: {str(e)}")


def devolver_prestamo(session: Session, prestamo_id: int, fecha_devolucion: datetime = None):
    """Marcar un préstamo como devuelto"""
    try:
        db_prestamo = get_prestamo_by_id(session, prestamo_id)
        if not db_prestamo:
            return False

        # Obtener la herramienta para actualizar el stock
        herramienta = session.get(Herramienta, db_prestamo.id_herramienta_h)
        if herramienta:
            # Sumar al stock al devolver
            herramienta.cantidad_disponible += 1

        db_prestamo.estado = "devuelto"
        db_prestamo.fecha_devolucion = fecha_devolucion or datetime.now()
        session.commit()
        session.refresh(db_prestamo)
        return True
    except Exception as e:
        # Hacer rollback en caso de error
        session.rollback()
        # Re-lanzar la excepción para que el llamador pueda manejarla
        raise Exception(f"Error al devolver préstamo: {str(e)}")


def cancelar_prestamo(session: Session, prestamo_id: int):
    """Cancelar un préstamo"""
    try:
        db_prestamo = get_prestamo_by_id(session, prestamo_id)
        if not db_prestamo:
            return False

        # Obtener la herramienta para actualizar el stock
        herramienta = session.get(Herramienta, db_prestamo.id_herramienta_h)
        if herramienta:
            # Sumar al stock al cancelar (porque el préstamo nunca se concretó)
            herramienta.cantidad_disponible += 1

        db_prestamo.estado = "cancelado"
        session.commit()
        session.refresh(db_prestamo)
        return True
    except Exception as e:
        # Hacer rollback en caso de error
        session.rollback()
        # Re-lanzar la excepción para que el llamador pueda manejarla
        raise Exception(f"Error al cancelar préstamo: {str(e)}")
