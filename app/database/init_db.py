from sqlmodel import SQLModel
from app.database.config import engine
from app.models.empleado import Empleado
from app.models.herramienta import Herramienta
from app.models.prestamo import Prestamo
from app.models.categoria import Categoria


def create_table():
    """
    Crea todas las tablas en la base de datos si no existen.
    
    Esta función es idempotente y puede ejecutarse múltiples veces
    sin causar errores.
    """
    try:
        SQLModel.metadata.create_all(engine)
        print("Tablas creadas/verificadas exitosamente")
    except Exception as e:
        print(f"Error al crear tablas: {e}")
        raise


if __name__ == "__main__":
    create_table()
