"""
Script de migración para actualizar la restricción ÚNICA del campo correo
en la tabla Empleado.

Este script maneja el cambio de:
- correo: str (unique=True, nullable=False)
- correo: str | None (unique=True, nullable=True)

Esto permite que múltiples empleados no tengan correo sin generar conflictos.
"""

from sqlmodel import SQLModel, Session
from app.database.config import engine
from app.models.empleado import Empleado
import sqlite3


def migrate_correo_unique():
    """Migrar la tabla Empleado para permitir correos nulos"""
    
    print("🔄 Iniciando migración de la tabla Empleado...")
    
    # Determinar el tipo de base de datos (SQLite o PostgreSQL)
    db_url = str(engine.url)
    is_postgresql = db_url.startswith("postgresql")
    
    if is_postgresql:
        print("📊 Detectada base de datos PostgreSQL")
        from sqlalchemy import text
        from sqlalchemy.exc import OperationalError
        
        try:
            # Para PostgreSQL, usamos SQLAlchemy para la migración
            with engine.connect() as conn:
                # Verificar si la tabla existe
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'empleado'
                    )
                """))
                table_exists = result.scalar()
                
                if not table_exists:
                    print("✅ La tabla Empleado no existe aún, no se requiere migración")
                    return
                
                # Verificar el esquema de la columna correo
                result = conn.execute(text("""
                    SELECT column_name, is_nullable, data_type
                    FROM information_schema.columns
                    WHERE table_name = 'empleado' AND column_name = 'correo'
                """))
                correo_column = result.fetchone()
                
                if correo_column:
                    print(f"📋 Columna actual: {correo_column}")
                    
                    # Verificar si ya es nullable
                    if correo_column[1] == 'NO':  # NOT NULL
                        print("🔧 La columna correo es NOT NULL, procediendo con la migración...")
                        
                        # Crear una tabla temporal
                        conn.execute(text("""
                            CREATE TABLE empleado_temp (
                                id INTEGER PRIMARY KEY,
                                nombre VARCHAR NOT NULL,
                                apellido VARCHAR NOT NULL,
                                area VARCHAR NOT NULL,
                                correo VARCHAR,
                                activo BOOLEAN NOT NULL DEFAULT TRUE,
                                UNIQUE (correo)
                            )
                        """))
                        
                        # Copiar datos de la tabla original a la temporal
                        # Convertir cadenas vacías a NULL
                        conn.execute(text("""
                            INSERT INTO empleado_temp (id, nombre, apellido, area, correo, activo)
                            SELECT 
                                id,
                                nombre,
                                apellido,
                                area,
                                NULLIF(correo, '') as correo,
                                activo
                            FROM empleado
                        """))
                        
                        # Eliminar restricciones de la tabla original
                        conn.execute(text("ALTER TABLE empleado DROP CONSTRAINT IF EXISTS empleado_correo_key"))
                        
                        # Eliminar la tabla original
                        conn.execute(text("DROP TABLE empleado"))
                        
                        # Renombrar la tabla temporal al nombre original
                        conn.execute(text("ALTER TABLE empleado_temp RENAME TO empleado"))
                        
                        # Recrear la restricción única
                        conn.execute(text("ALTER TABLE empleado ADD CONSTRAINT empleado_correo_key UNIQUE (correo)"))
                        
                        print("✅ Migración completada exitosamente!")
                        conn.commit()  # Asegurar que los cambios se guarden
                    else:
                        print("✅ La columna correo ya es nullable, no se requiere migración")
                else:
                    print("⚠️  No se encontró la columna correo en la tabla Empleado")
                    
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            # Intentar revertir cambios en caso de error
            try:
                with engine.connect() as conn:
                    conn.execute(text("DROP TABLE IF EXISTS empleado_temp"))
                    conn.commit()
            except:
                pass
            raise
    else:
        # Para SQLite, usar el enfoque original
        print("📊 Detectada base de datos SQLite")
        conn = sqlite3.connect(engine.url.database)
        cursor = conn.cursor()
        
        try:
            # Verificar si la tabla existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='empleado'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print("✅ La tabla Empleado no existe aún, no se requiere migración")
                return
            
            # Verificar el esquema actual
            cursor.execute("PRAGMA table_info(empleado)")
            columns = cursor.fetchall()
            
            correo_column = None
            for col in columns:
                if col[1] == 'correo':
                    correo_column = col
                    break
            
            if correo_column:
                print(f"📋 Columna actual: {correo_column}")
                
                # Verificar si ya es nullable
                if correo_column[3] == 1:  # 1 = NOT NULL, 0 = NULL
                    print("🔧 La columna correo es NOT NULL, procediendo con la migración...")
                    
                    # Crear una tabla temporal
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS empleado_temp (
                            id INTEGER PRIMARY KEY,
                            nombre TEXT NOT NULL,
                            apellido TEXT NOT NULL,
                            area TEXT NOT NULL,
                            correo TEXT,
                            activo INTEGER NOT NULL DEFAULT 1,
                            UNIQUE (correo)
                        )
                    """)
                    
                    # Copiar datos de la tabla original a la temporal
                    # Convertir cadenas vacías a NULL
                    cursor.execute("""
                        INSERT INTO empleado_temp 
                        SELECT 
                            id,
                            nombre,
                            apellido,
                            area,
                            CASE WHEN correo = '' THEN NULL ELSE correo END as correo,
                            activo
                        FROM empleado
                    """)
                    
                    # Eliminar la tabla original
                    cursor.execute("DROP TABLE empleado")
                    
                    # Renombrar la tabla temporal al nombre original
                    cursor.execute("ALTER TABLE empleado_temp RENAME TO empleado")
                    
                    print("✅ Migración completada exitosamente!")
                    conn.commit()
                    
                else:
                    print("✅ La columna correo ya es nullable, no se requiere migración")
                    
            else:
                print("⚠️  No se encontró la columna correo en la tabla Empleado")
                
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            # Intentar revertir en caso de error
            try:
                cursor.execute("DROP TABLE IF EXISTS empleado_temp")
                conn.commit()
            except:
                pass
            raise
        finally:
            conn.close()


def recreate_tables():
    """Alternativa: Recrear todas las tablas (para entornos de desarrollo)"""
    print("🔄 Recreando todas las tablas...")
    
    # Eliminar todas las tablas
    SQLModel.metadata.drop_all(engine)
    
    # Crear todas las tablas con el nuevo esquema
    SQLModel.metadata.create_all(engine)
    
    print("✅ Tablas recreadas exitosamente")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--recreate":
        # Para desarrollo, recrear todas las tablas
        recreate_tables()
    else:
        # Para producción, usar migración segura
        migrate_correo_unique()
    
    print("\n✅ Migración completada!")
