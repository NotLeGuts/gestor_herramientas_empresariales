# Requerimientos Funcionales Detallados
*(Gestor de Herramientas y Objetos - GHO)*

---

## 1. Gestión de Empleados
### **1.1 Registrar Empleado**
- **Campos obligatorios**:
  - `id_empleado` (PK, autoincremental).
  - `nombre` (string, max 50 caracteres).
  - `apellido` (string, max 50 caracteres).
  - `área` (string, ej: "Mantenimiento", "Producción").
  - `correo` (único, formato válido).
- **Validaciones**:
  - Correo no duplicado.
  - Área debe existir en lista predefinida (ej: ["Mantenimiento", "Logística"]).

### **1.2 Consultar Empleados**
- **Filtros disponibles**:
  - Por nombre/apellido (búsqueda parcial).
  - Por área.
  - Por préstamos activos.
- **Salida**:
  - Lista con: `id_empleado`, `nombre`, `área`, `cantidad de préstamos activos`.

### **1.3 Editar Empleado**
- **Campos editables**:
  - `nombre`, `apellido`, `área`, `correo`.
- **Restricciones**:
  - No se puede editar el `id_empleado`.
  - Validar unicidad del correo.

---

### **2.1 Registrar Herramienta**
- **Campos obligatorios**:
  - `id_herramienta` (PK, autoincremental).
  - `nombre` (string, max 50 caracteres).
  - `categoría` (string, ej: "Eléctricas", "Manuales").
  - `estado` (booleano, default: `True`).
  - `código_interno` (string, único, formato: `CAT-AAA000`).
  - **`cantidad_disponible`** (int, default: `1`).
    - Representa el stock de herramientas idénticas.
    - Ejemplo: `5` para "Llave 14mm".

- **Validaciones**:
  - `cantidad_disponible` debe ser >= `0`.
  - Si `cantidad_disponible = 0`, `estado` debe ser `False`.

### **2.2 Consultar Herramientas**
- **Filtros disponibles**:
  - Por nombre, categoría, **o cantidad disponible**.
- **Salida**:
  - Lista con: `id_herramienta`, `nombre`, `categoría`, **`cantidad_disponible`**, `estado`.

### **2.3 Editar Herramienta**
- **Campos editables**:
  - `nombre`, `categoría`, `estado`.
- **Restricciones**:
  - No se puede editar `id_herramienta` o `código_interno`.
  - Si `estado = "en mantenimiento"`, no puede prestarse.

---

### **3.1 Registrar Préstamo**
- **Validaciones adicionales**:
  - La herramienta debe tener **`cantidad_disponible > 0`**.
  - Al prestar, **restar 1** a `cantidad_disponible`.
  - Si `cantidad_disponible = 0`, cambiar `estado` a `False`.

### **3.2 Devolver Herramienta**
- **Acciones post-devolución**:
  - **Sumar 1** a `cantidad_disponible`.
  - Si `cantidad_disponible > 0`, cambiar `estado` a `True`.
### **3.3 Consultar Préstamos**

- **Filtros disponibles**:
  - Por empleado (`id_empleado`).
  - Por herramienta (`id_herramienta`).
  - Por rango de fechas.
  - Por estado (activo/devuelto).
- **Salida**:
  - Lista con: `id_préstamo`, `empleado`, `herramienta`, `fecha_préstamo`, `fecha_devolución`.

---

## 4. Reportes y Estadísticas
### **4.1 Herramientas Más Solicitadas**
- **Criterio**:
  - Top 5 herramientas con más préstamos en los últimos 30 días.
- **Salida**:
  - Tabla con: `nombre_herramienta`, `categoría`, `cantidad_préstamos`.

### **4.2 Préstamos Vencidos**
- **Criterio**:
  - Préstamos donde `fecha_devolución_estimada < hoy` y `fecha_devolución_real = NULL`.
- **Salida**:
  - Lista con: `id_préstamo`, `empleado`, `herramienta`, `días_de_retraso`.

### **4.3 Disponibilidad en Tiempo Real**
- **Criterio**:
  - Herramientas con `estado = True` (disponibles).
- **Salida**:
  - Dashboard en Streamlit con:
    - Total disponibles vs. prestadas.
    - Lista filtrable por categoría.

---

## 5. Ejemplo de Datos de Prueba
*(Para validar funcionalidades)*

### **5.1 Empleados (20 registros)**
| id_empleado | nombre      | apellido   | área          | correo                |
|-------------|-------------|------------|---------------|-----------------------|
| 1           | Juan        | Pérez      | Mantenimiento | juan.perez@empresa.com|
| 2           | María       | Gómez      | Producción    | maria.gomez@empresa.com|


### **5.2 Herramientas (20 registros)**
| id_herramienta | nombre       | categoría   | cantidad_disponible | código_interno |
|----------------|--------------|-------------|---------------------|-----------------|
| 1              | Llave 14mm   | Manuales    | 5                   | MAN-AAA001      |
| 2              | Taladro      | Eléctricas  | 2                   | ELE-AAA001      |


### **5.3 Préstamos (10 registros activos)**
| id_préstamo | id_empleado | id_herramienta | fecha_préstamo       | fecha_devolución_estimada |
|-------------|-------------|----------------|----------------------|---------------------------|
| 1           | 1           | 1              | 2026-01-10 09:00:00  | 2026-01-17 18:00:00      |

---
**Notas:**
- Usa estos datos para probar las validaciones (ej: préstamo de herramienta no disponible).
- Ajusta las fechas y categorías según tus necesidades reales.
