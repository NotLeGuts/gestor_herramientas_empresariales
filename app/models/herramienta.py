from sqlmodel import SQLModel, Field


class Herramienta(SQLModel, table=True):
    id_herramienta: int | None = Field(default=None, primary_key=True)
    nombre: str
    categoria: str | None = None
    estado: bool = Field(default=True)
    codigo_interno: str | None = Field(default=None, unique=True)
    cantidad_disponible: int = Field(default=1)
    descripcion: str | None = None
    id_categoria_h: int | None = Field(default=None, foreign_key="categoria.id_categoria")
