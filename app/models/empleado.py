from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String


class Empleado(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    area: str
    # Correo es opcional y único solo para valores no nulos
    correo: str | None = Field(
        default=None,
        sa_column=Column(String, unique=True, nullable=True)
    )
    activo: bool = Field(default=True)
