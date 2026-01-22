from sqlmodel import SQLModel, Field


class Empleado(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    area: str
    correo: str = Field(unique=True)
    activo: bool = Field(default=True)
