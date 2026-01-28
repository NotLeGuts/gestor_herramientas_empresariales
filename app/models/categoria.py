from sqlmodel import SQLModel, Field


class Categoria(SQLModel, table=True):
    id_categoria: int | None = Field(default=None, primary_key=True)
    nombre: str
    estado: bool = Field(default=True)
