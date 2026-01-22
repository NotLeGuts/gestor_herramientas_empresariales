from sqlmodel import SQLModel, Field


class Herramienta(SQLModel, table=True):
    id_herramienta: int | None = Field(default=None, primary_key=True)
    nombre: str
    categoria: str
    estado: bool = Field(default=True)
    codigo_interno: str = Field(unique=True)
    cantidad_disponible: int = Field(default=1)
    descripcion: str | None = None
