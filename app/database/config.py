from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener la URL de la base de datos desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///gestor_herramientas.db")

# Configurar el motor de la base de datos
# Para producción con PostgreSQL, recomendamos:
# - pool_size=5 (o más según la carga)
# - max_overflow=10
# - pool_timeout=30
# - pool_recycle=1800 (30 minutos)
# - pool_pre_ping=True para verificar conexiones antes de usarlas
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "False") == "True",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)

# Función para obtener una nueva sesión cada vez
# Esto es importante para Streamlit ya que reejecuta el script
# y puede dejar conexiones en estado abortado
def get_session():
    """
    Obtiene una nueva sesión de base de datos.
    Cada llamada a esta función debe crear una nueva sesión.
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise e
