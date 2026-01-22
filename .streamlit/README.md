# Configuración de Streamlit

Esta carpeta contiene la configuración personalizada para la aplicación Gestor de Herramientas.

## Archivos

### `config.toml`
Configuración principal de Streamlit que define:
- **Tema visual**: Colores primarios, fondos, texto
- **Configuración del servidor**: Puerto, CORS, etc.
- **Comportamiento de la aplicación**: Cache, sesiones, etc.

**Colores definidos:**
- `primaryColor`: `#1E88E5` (Azul principal - Material Design)
- `backgroundColor`: `#F5F5F5` (Fondo claro)
- `secondaryBackgroundColor`: `#FFFFFF` (Fondo secundario - blanco)
- `textColor`: `#263238` (Texto oscuro para buena legibilidad)

### `custom.css`
Estilos CSS personalizados para mejorar la apariencia de la aplicación:
- Botones con efectos hover y sombras
- Tarjetas con bordes redondeados
- Mensajes de alerta con colores consistentes
- Tablas con mejor formato
- Scrollbars personalizados
- Animaciones suaves

### `secrets.toml`
**⚠️ Este archivo NO debe ser versionado en git**

Contiene configuraciones sensibles como:
- Credenciales de base de datos
- Claves de API
- Configuración de email
- Tokens de analítica

**Importante:** Este archivo debe estar en `.gitignore` para mantener la seguridad.

## Uso

### Configuración del tema

Los colores definidos en `config.toml` se aplican automáticamente a:
- Botones primarios
- Enlaces
- Títulos
- Componentes de Streamlit

### Personalización adicional

Para personalizar aún más la apariencia:

1. **Modificar colores**: Edite los valores en `config.toml`
2. **Añadir estilos CSS**: Edite `custom.css`
3. **Configurar el servidor**: Modifique la sección `[server]` en `config.toml`

### Ejemplo de uso de colores en el código

```python
# En cualquier archivo del frontend, puede usar los colores del tema
st.markdown(
    f"""
    <div style="background-color: #E3F2FD; padding: 15px; border-radius: 8px;">
        Este es un contenedor con el color azul claro del tema
    </div>
    """,
    unsafe_allow_html=True
)
```

## Estructura recomendada

```
.streamlit/
├── config.toml          # Configuración principal
├── custom.css           # Estilos CSS personalizados
├── secrets.toml         # Configuración sensible (NO versionar)
└── README.md            # Este archivo
```

## Buenas prácticas

1. **No versionar secrets**: Asegúrese de que `secrets.toml` esté en `.gitignore`
2. **Documentar cambios**: Comente los cambios en `config.toml` y `custom.css`
3. **Pruebas**: Pruebe los cambios visuales antes de deployar
4. **Consistencia**: Use los mismos colores en toda la aplicación
5. **Accesibilidad**: Asegúrese de que los colores tengan suficiente contraste

## Colores recomendados

Basados en Material Design y accesibles:

- **Azul (primario)**: `#1E88E5` - Para acciones principales
- **Verde (éxito)**: `#4CAF50` - Para mensajes positivos
- **Amarillo (advertencia)**: `#FFC107` - Para advertencias
- **Rojo (error)**: `#F44336` - Para errores
- **Gris (neutral)**: `#9E9E9E` - Para texto secundario
- **Blanco**: `#FFFFFF` - Para fondos
- **Gris claro**: `#F5F5F5` - Para fondos secundarios

## Recursos

- [Documentación de Streamlit](https://docs.streamlit.io/)
- [Material Design Colors](https://material.io/resources/color/)
- [Guía de accesibilidad de colores](https://webaim.org/resources/contrastchecker/)
