from sqlmodel import SQLModel, Field
from datetime import datetime, timedelta
from typing import Optional


class Prestamo(SQLModel, table=True):
    id_prestamo: int | None = Field(default=None, primary_key=True)
    id_empleado_h: int = Field(foreign_key="empleado.id")
    id_herramienta_h: int = Field(foreign_key="herramienta.id_herramienta")
    fecha_prestamo: datetime = Field(default_factory=datetime.now)
    fecha_devolucion_estimada: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(days=1)
    )
    fecha_devolucion: datetime | None = None
    observaciones: str | None = None
    estado: str = Field(default="activo")
