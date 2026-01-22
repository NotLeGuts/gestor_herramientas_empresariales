# Gestor de Herramientas y Objetos (GHO)

**Sistema para controlar préstamos de herramientas/objetos a empleados en empresas o talleres.**

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](LICENSE)

---

## 🎯 Propósito
Automatizar el registro de:
- **¿Quién** lleva cada herramienta.
- **Cuándo** se prestó y devolvió.
- **Disponibilidad** en tiempo real.

**Objetivo:** Evitar pérdidas, optimizar recursos y eliminar registros manuales (ej: Excel o papel).

---

## 🔧 Alcance
✅ **Gestionar:**
- Empleados, herramientas y préstamos.
- Reportes de uso y disponibilidad.

❌ **No incluye:**
- Compras, proveedores o integración con ERP.

---

## 👥 Público
Empresas/talleres con equipos compartidos (ej: mantenimiento, producción, TI).

---

## 📜 Licencia
Este proyecto está bajo la **Licencia MIT**. Ver el archivo [LICENSE](LICENSE) para más detalles.

**¿Qué permite esta licencia?**
- ✅ Usar el software para fines comerciales
- ✅ Modificar el código según tus necesidades
- ✅ Distribuir copias modificadas o originales
- ✅ Sublicenciar el software

**Obligaciones:**
- ⚠️ Incluir el aviso de copyright y esta licencia en todas las copias
- ⚠️ No reclamar propiedad del código original

**Sin garantías:**
- ❌ El software se proporciona "tal cual" sin garantías explícitas o implícitas
- ❌ Los autores no son responsables por daños derivados del uso del software

---
## 🛠 Tecnologías
- **Backend:** Python + SQLModel (SQLite/PostgreSQL).
- **Frontend:** Streamlit (interfaz web local).
- **Base de Datos:** SQLite (por defecto, compatible con PostgreSQL).
- **Paquetes Principales:**
  - `streamlit` - Interfaz de usuario web
  - `sqlmodel` - ORM para base de datos
  - `pydantic` - Validación de datos

---
## 🚀 Ejecución de la Aplicación

### 1. Instalar dependencias

```bash
# Crear entorno virtual (opcional pero recomendado)
python -m venv env
source env/bin/activate  # Linux/Mac
# env\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Inicializar la base de datos

```bash
python tests/init_db_test.py
```

### 3. Ejecutar la aplicación

```bash
streamlit run frontend/Inicio.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

### 4. Ejecutar tests

```bash
# Ejecutar todos los tests
python tests/test_stock_simple.py
python tests/test_empleado.py
python tests/test_herramienta.py
python tests/test_prestamo.py
```

## 📋 Requerimientos Funcionales

### **1. Gestión de Empleados**
- Registrar/editar empleados (`nombre`, `área`, `contacto`).
- Consultar préstamos activos por empleado.

### **2. Gestión de Herramientas**
- Registrar herramientas (`nombre`, `categoría`, `estado`, `código único`).
- Filtrar por disponibilidad o categoría.

### **3. Préstamos y Devoluciones**
- Registrar préstamos (validar disponibilidad).
- Registrar devoluciones (actualizar estado a *disponible*).
- Historial de préstamos por herramienta/empleado.

### **4. Reportes**
- Herramientas más solicitadas (top 5).
- Préstamos vencidos (alertas).
- Disponibilidad en tiempo real (dashboard).

