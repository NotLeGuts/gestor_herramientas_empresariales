from sqlmodel import Session, select
from app.models.herramienta import Herramienta


def generate_codigo_interno(nombre: str) -> str:
    """Generar código interno automático basado en el nombre de la herramienta."""
    # Extraer las primeras 3 letras del nombre y convertirlas a mayúsculas
    codigo = nombre[:3].upper()
    # Si el nombre es muy corto, rellenar con números
    if len(nombre) < 3:
        codigo = nombre.upper() + "0" * (3 - len(nombre))
    
    # Generar un número aleatorio de 4 dígitos
    import random
    numero = random.randint(1000, 9999)
    
    return f"{codigo}-{numero}"


def create_herramienta(
    session: Session,
    nombre: str,
    categoria: int = None,
    estado: bool = True,
    codigo_interno: str = None,
    cantidad_disponible: int = 1,
    descripcion: str = None,
):
    "Crear una nueva herramienta"
    # Generar código interno automático si no se proporciona
    if not codigo_interno:
        codigo_interno = generate_codigo_interno(nombre)
    
    herramienta = Herramienta(
        nombre=nombre,
        id_categoria_h=categoria,
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

    # Si se está actualizando el nombre y no se proporciona código interno,
    # generar uno automáticamente
    if 'nombre' in kwargs and kwargs['nombre'] and 'codigo_interno' not in kwargs:
        kwargs['codigo_interno'] = generate_codigo_interno(kwargs['nombre'])
    elif 'codigo_interno' in kwargs and not kwargs['codigo_interno']:
        # Si el código interno está vacío, generar uno nuevo
        if 'nombre' in kwargs and kwargs['nombre']:
            kwargs['codigo_interno'] = generate_codigo_interno(kwargs['nombre'])
        elif db_herramienta.nombre:
            kwargs['codigo_interno'] = generate_codigo_interno(db_herramienta.nombre)

    # Manejar el campo categoria (que ahora es id_categoria_h)
    if 'categoria' in kwargs:
        kwargs['id_categoria_h'] = kwargs.pop('categoria')

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
