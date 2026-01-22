# Lista de Acontecimientos del Sistema GHO

---

## 1. Registrar Empleado
- **Actor**: ADMIN.
- **Entradas**:
  - `nombre`, `apellido`, `área`, `correo`.
- **Validaciones**:
  - `correo` único.
  - `área` válida (ej: "Mantenimiento").
- **Salidas**:
  - Empleado registrado en la base de datos.

---

## 2. Registrar Herramienta
- **Actor**: ADMIN.
- **Entradas**:
  - `nombre`, `categoría`, `cantidad_disponible` (default: 1).
- **Validaciones**:
  - `código_interno` único.
- **Salidas**:
  - Herramienta registrada con stock inicial.

---

## 3. Registrar Préstamo
- **Actor**: Empleado/ADMIN.
- **Entradas**:
  - `id_empleado`, `id_herramienta`, `fecha_devolucion_estimada` (opcional).
- **Validaciones**:
  - `herramienta.cantidad_disponible > 0`.
  - `herramienta.estado = True`.
- **Acontecimientos**:
  1. Valida disponibilidad de la herramienta.
  2. Resta 1 a `cantidad_disponible`.
  3. Si `cantidad_disponible = 0`, actualiza `estado = False`.
  4. Registra préstamo con fechas.
- **Salidas**:
  - Préstamo registrado.
  - Stock actualizado.

---

## 4. Devolver Herramienta
- **Actor**: Empleado/ADMIN.
- **Entradas**:
  - `id_prestamo`.
- **Validaciones**:
  - Préstamo existe y no está devuelto.
- **Acontecimientos**:
  1. Valida préstamo activo.
  2. Registra `fecha_devolucion`.
  3. Suma 1 a `cantidad_disponible`.
  4. Si `cantidad_disponible > 0`, actualiza `estado = True`.
- **Salidas**:
  - Devolución registrada.
  - Stock actualizado.

---

## 5. Consultar Disponibilidad
- **Actor**: ADMIN.
- **Entradas**:
  - Filtros: `categoría`, `nombre`, `estado`.
- **Acontecimientos**:
  1. Filtra herramientas según criterios.
  2. Muestra lista con `nombre`, `cantidad_disponible`, `estado`.
- **Salidas**:
  - Reporte de herramientas disponibles.

---
