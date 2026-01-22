from sqlmodel import SQLModel
from app.database.config import engine
from app.models.empleado import Empleado
from app.models.herramienta import Herramienta
from app.models.prestamo import Prestamo


def create_table():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_table()
