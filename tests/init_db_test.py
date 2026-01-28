"""Script para inicializar la base de datos con las tablas necesarias"""
from sqlmodel import SQLModel
from app.database.config import engine
from app.models.empleado import Empleado
from app.models.herramienta import Herramienta
from app.models.prestamo import Prestamo

# Crear todas las tablas
SQLModel.metadata.create_all(engine)

print("Tablas creadas exitosamente:")
print("- empleado")
print("- herramienta")
print("- prestamo")
