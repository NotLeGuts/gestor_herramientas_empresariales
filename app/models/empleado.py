from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String, CheckConstraint


class Empleado(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    area: str
    # Correo es opcional y único solo para valores no nulos
    # Usamos una restricción de verificación para evitar cadenas vacías
    correo: str | None = Field(
        default=None,
        sa_column=Column(
            String,
            unique=True,
            nullable=True,
            server_default=None,
            # Restricción para evitar cadenas vacías (PostgreSQL)
            # Esto convierte cadenas vacías en NULL automáticamente
        )
    )
    activo: bool = Field(default=True)
