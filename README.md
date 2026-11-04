# 🎮 DotaTwin ![Version](https://img.shields.io/badge/version-v3.2.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Language](https://img.shields.io/badge/language-Python-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Architecture](https://img.shields.io/badge/architecture-modular-brightgreen)

## � Índice

- [🚀 ¡Nuevo en v3.0! - Rebranding como DotaTwin](#-nuevo-en-v30---rebranding-como-dotatwin)
- [✨ ¿Qué es DotaTwin?](#-qué-es-dotatwin)
- [🎯 Características Principales](#-características-principales-de-v30)
- [📋 Descripción](#-descripción)
- [🔥 Características Destacadas](#-características-principales)
- [🖥️ Interfaz de Usuario](#️-interfaz-de-usuario)
- [🛠️ Requisitos del Sistema](#️-requisitos-del-sistema)
- [📦 Instalación](#-instalación)
  - [Opción 1: Ejecutable (Recomendado)](#opción-1-ejecutable-recomendado-para-usuarios)
  - [Opción 2: Portable](#opción-2-portable)
  - [Opción 3: Código Fuente](#opción-3-código-fuente-recomendado-para-desarrolladores)
- [�️ Alerta de Seguridad de Windows](#️-alerta-de-seguridad-de-windows)
- [�🚀 Uso](#-uso)
  - [Pasos Básicos](#pasos-básicos)
  - [Funciones Avanzadas](#funciones-avanzadas)
- [📁 Estructura del Proyecto](#-estructura-de-archivos)
- [⚙️ Configuración](#️-configuración)
- [🔒 Seguridad](#-seguridad)
- [🐛 Solución de Problemas](#-solución-de-problemas)
- [🤝 Contribuciones](#-contribuciones)
- [📄 Licencia](#-licencia)
- [👨‍💻 Autor](#-autor)
- [🙏 Agradecimientos](#-agradecimientos)
- [📞 Contacto y Soporte](#-contacto-y-soporte)
- [📈 Roadmap](#-roadmap)

---

## �🚀 ¡Nuevo en v3.0! - Rebranding como DotaTwin

**DotaTwin** es la evolución de Dota 2 Config Copier con un nuevo nombre que refleja perfectamente su propósito: **crear gemelos perfectos de tus configuraciones de Dota**.

### ✨ **¿Qué es DotaTwin?**
Una aplicación de escritorio que permite **duplicar configuraciones de Dota 2** entre cuentas de Steam de manera sencilla y eficiente. Como tener un "gemelo digital" de tu setup perfecto.

**Twin your Dota experience** - Copia configuraciones entre cuentas de Steam

### 🎯 **Características Principales de v3.0**
- **Interfaz moderna y limpia**: Rediseñada con el nuevo branding DotaTwin
- **Arquitectura modular sólida**: Base técnica robusta y mantenible
- **Configuración avanzada de Steam**: Detección automática y configuración manual
- **Layout responsive**: Se adapta perfectamente a cualquier tamaño de ventana
- **Sistema de copia completa**: Garantiza que todos los archivos .vcfg se copien correctamente
- **Desarrollo asistido por IA**: Evolucionado desde v2.0 usando pair programming con GitHub Copilot

## 🚀 ¡Nuevo en v2.0! - Arquitectura Modular

La versión 2.0 presenta una **refactorización completa** con arquitectura modular que mejora significativamente la mantenibilidad, extensibilidad y robustez del código:

### 🏗️ Beneficios de la Nueva Arquitectura
- **Código Modular**: Separación clara de responsabilidades
- **Fácil Mantenimiento**: Estructura organizada y documentada
- **Testing Automatizado**: Suite completa de tests unitarios
- **Logging Avanzado**: Sistema de logging detallado para debugging
- **Extensibilidad**: Base sólida para futuras mejoras
- **Principios SOLID**: Aplicación de mejores prácticas de desarrollo

### 📊 Mejoras Técnicas
- **Servicios de Negocio**: Lógica separada en servicios especializados
- **Modelos de Dominio**: Entidades robustas con validaciones integradas
- **Componentes UI Reutilizables**: Widgets modulares y consistentes
- **Configuración Centralizada**: Settings unificados y flexibles
- **Manejo de Errores**: Sistema robusto de manejo de excepciones

## 📋 Descripción

**Dota 2 Config Copier** es una herramienta que permite transferir configuraciones completas de Dota 2 (controles, configuraciones de video, audio, hotkeys, etc.) desde una cuenta de Steam a otra. Ideal para usuarios que tienen múltiples cuentas o que quieren compartir su configuración optimizada.

## ✨ Características Principales

### 🔍 **Detección Automática**
- Detecta automáticamente todas las cuentas de Steam con Dota 2 instalado
- Extrae nombres de usuario y avatares de Steam
- Muestra información detallada de cada cuenta (SteamID, nombre)

### 🎯 **Interfaz Intuitiva**
- **Pestañas organizadas**: Cuentas disponibles y cuentas ignoradas
- **Iconos descriptivos**: Facilitan la identificación de funciones
- **Paginación inteligente**: Maneja eficientemente listas grandes de cuentas
- **Selección visual**: Colores distintivos para origen y destino
- **Layout responsive**: Todos los controles siempre visibles y accesibles
- **Scrollbar automática**: Lista de cuentas se desplaza automáticamente cuando es necesario

### 📄 **Paginación Avanzada**
- Control personalizable de elementos por página (10, 15, 20, 25, 30)
- Navegación con botones numerados
- Auto-navegación a cuentas seleccionadas
- Persistencia de preferencias de visualización

### 🚫 **Gestión de Cuentas**
- **Ignorar cuentas**: Oculta cuentas no utilizadas del listado principal
- **Restaurar cuentas**: Devuelve cuentas ignoradas cuando sea necesario
- **Persistencia**: Las preferencias se guardan automáticamente

### 💾 **Configuración Persistente**
- Recuerda última selección de origen y destino
- Guarda lista de cuentas ignoradas
- Mantiene preferencias de paginación
- Archivo JSON para configuraciones de usuario

## 🖥️ Interfaz de Usuario

### Botones Principales
- **📤 Origen**: Selecciona la cuenta fuente de la configuración
- **📥 Destino**: Selecciona la cuenta que recibirá la configuración
- **🚫 Ignorar**: Oculta la cuenta del listado principal
- **↩️ Restaurar**: Devuelve cuenta ignorada al listado
- **📋 Copiar configuración**: Ejecuta la transferencia
- **❌ Cancelar selección**: Limpia selecciones actuales

### Navegación
- **⬅️ Anterior / ➡️ Siguiente**: Navegación entre páginas
- **Botones numerados**: Acceso directo a páginas específicas
- **📄 Control de elementos**: Personaliza cuántas cuentas mostrar por página

## 🛠️ Requisitos del Sistema

- **Sistema Operativo**: Windows 7/8/10/11
- **Python**: 3.7 o superior (para ejecutar desde código fuente)
- **Steam**: Instalado con al menos una cuenta autenticada
- **Librerías Python** (instalación automática con `pip install -r requirements.txt`):
  - `tkinter` (incluida con Python)
  - `Pillow` (PIL) - Para manejo de imágenes
  - `json` (incluida con Python)

### Dependencias Opcionales de Desarrollo
- `pytest` - Para ejecutar tests automatizados
- `black` - Para formateo de código
- `mypy` - Para verificación de tipos

## 📦 Instalación

### Opción 1: Ejecutable (Recomendado para usuarios)
1. **Descargar** el archivo `DotaTwin_v3.2.0.exe` desde [GitHub Releases](https://github.com/sadohu/DotaTwin/releases)
2. **Colocar** en cualquier carpeta
3. **Ejecutar** haciendo doble clic

> ⚠️ **Nota**: Puede aparecer una alerta de Windows SmartScreen (ver sección de [Alerta de Seguridad](#️-alerta-de-seguridad-de-windows))

### Opción 2: Portable
**🆕 ¡Nuevo en v3.1.0!** - Versión portable que no requiere instalación

1. **Descargar** el archivo `DotaTwin_v3.1.0_Portable.zip` desde [GitHub Releases](https://github.com/sadohu/DotaTwin/releases)
2. **Extraer** en cualquier carpeta
3. **Ejecutar** `run.bat` para iniciar

**✅ Ventajas del portable**:
- No requiere instalación
- Código fuente visible y auditable
- Incluye Python embebido (~21 MB)
- Portable entre sistemas Windows

**📋 Requisitos**:
- Windows 7 o superior
- Para GUI completa: Python con tkinter (o usar Python del sistema)

### Opción 3: Código Fuente (Recomendado para desarrolladores)

```bash
# Clonar repositorio
git clone https://github.com/sadohu/DotaTwin.git
cd DotaTwin

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py
```

## 🛡️ Alerta de Seguridad de Windows

**⚠️ IMPORTANTE**: Al descargar y ejecutar DotaTwin por primera vez, Windows puede mostrar una alerta de seguridad.

### 🔍 **¿Por qué aparece esta alerta?**

Windows SmartScreen puede mostrar mensajes como:
- *"Windows protegió su PC"*
- *"Aplicación no reconocida"*
- *"El editor no pudo ser verificado"*

Esto puede ocurrir y normalmente se debe a que:
- DotaTwin es un ejecutable **no firmado digitalmente** (requiere certificado costoso ~$300/año)
- Es una aplicación **nueva** sin suficiente "reputación" en Windows
- Windows SmartScreen evalúa la reputación del editor y del archivo descargado

El formato no es la causa principal: convertir el ejecutable a MSI no elimina la alerta si el instalador tampoco está firmado. Un ZIP portable también puede mostrar advertencias al descargar o extraer archivos.

### ✅ **¿Es seguro DotaTwin?**

**Verifica el origen antes de ejecutarlo.** El código fuente está disponible en GitHub y la aplicación está diseñada para leer y escribir configuraciones locales de Steam. Aun así, ninguna aplicación sin firma debe considerarse automáticamente segura.

### 🚀 **Cómo proceder con seguridad**

Si aparece la alerta de Windows SmartScreen:

1. **Hacer clic en "Más información"**
2. **Hacer clic en "Ejecutar de todas formas"**
3. **¡Listo!** DotaTwin se ejecutará normalmente

**Captura de pantalla del proceso**:
```
[Windows protegió su PC]
[Más información] ← Hacer clic aquí
[Ejecutar de todas formas] ← Después hacer clic aquí
```

### 🤝 **Alternativas si prefieres mayor seguridad**

- **Usar versión portable**: Descarga `DotaTwin_v3.1.0_Portable.zip` - no requiere instalación, pero puede seguir mostrando una advertencia
- **Ejecutar desde código fuente**: Descargar el proyecto y ejecutar con `python main.py`
- **Revisar el código**: Todo está disponible en GitHub para inspección
- **Usar antivirus**: Escanear el archivo con tu antivirus preferido

### 📞 **¿Dudas sobre seguridad?**

Si tienes preguntas adicionales:
- 💬 **Discord**: [Únete a nuestra comunidad](https://discord.gg/MYNyKQvk)
- 📧 **GitHub Issues**: [Reportar consultas](https://github.com/sadohu/DotaTwin/issues)

---

## 🚀 Uso

### Pasos Básicos
1. **Ejecutar la aplicación**
2. **Seleccionar origen**: Hacer clic en "📤 Origen" de la cuenta que tiene la configuración deseada
3. **Seleccionar destino**: Hacer clic en "📥 Destino" de la cuenta que recibirá la configuración
4. **Copiar**: Hacer clic en "📋 Copiar configuración"
5. **Confirmar**: Aceptar la confirmación de copia

### Funciones Avanzadas

#### Gestión de Cuentas
- **Ignorar cuenta**: Usar "🚫 Ignorar" para ocultar cuentas no utilizadas
- **Restaurar cuenta**: Ir a pestaña "Cuentas Ignoradas" y usar "↩️ Restaurar"

#### Paginación
- **Cambiar elementos por página**: Usar el dropdown "📄 Mostrar"
- **Navegar**: Usar botones numerados o "⬅️ Anterior / ➡️ Siguiente"

## 📁 Estructura de Archivos

### v2.0 - Arquitectura Modular
```
dota2-config-copier/
├── main.py                      # 🚀 Punto de entrada principal
├── src/                         # 📦 Código fuente modular
│   ├── models/                  # 🏗️ Modelos de dominio
│   │   └── domain_models.py     # Entidades y objetos de valor
│   ├── core/                    # 💼 Lógica de negocio
│   │   ├── steam_service.py     # Servicios de Steam
│   │   └── config_service.py    # Servicios de configuración
│   ├── gui/                     # 🖥️ Interfaz de usuario
│   │   ├── main_app.py         # Aplicación principal
│   │   ├── main_tab.py         # Componentes pestaña principal
│   │   └── ignored_tab.py      # Componentes pestaña ignoradas
│   └── utils/                   # 🔧 Utilidades
│       ├── logging_utils.py     # Sistema de logging
│       └── ui_utils.py         # Utilidades de interfaz
├── config/                      # ⚙️ Configuración
│   └── settings.py             # Constantes y configuraciones
├── tests/                       # 🧪 Tests automatizados
│   └── test_refactor.py        # Tests de validación
├── docs/                        # 📚 Documentación
│   ├── ARQUITECTURA_MODULAR.md  # Documentación técnica
│   ├── ICONOS_IMPLEMENTADOS.md
│   ├── PAGINACION_IMPLEMENTADA.md
│   └── CAMBIOS_IMPLEMENTADOS.md
├── requirements.txt             # 📋 Dependencias
├── dota_main_config.py         # 🔄 Versión legacy (v1.3)
├── ultima_seleccion.json       # 💾 Configuración del usuario
├── dota2.ico                   # 🎨 Icono de la aplicación
├── README.md                   # 📖 Este archivo
├── CHANGELOG.md                # 📝 Historial de cambios
└── LICENSE                     # 📄 Licencia MIT
```

### Migración de v1.3 a v2.0
- ✅ **Compatibilidad completa**: Tus configuraciones se migran automáticamente
- ✅ **Funcionalidad idéntica**: Todas las características de v1.3 están disponibles
- ✅ **Ambas versiones**: Puedes usar v1.3 (`dota_main_config.py`) o v2.0 (`main.py`)
- ✅ **Datos conservados**: Configuraciones, cuentas ignoradas y preferencias se mantienen

## ⚙️ Configuración

### Archivo `ultima_seleccion.json`
```json
{
  "origen": "steamid_origen",
  "destino": "steamid_destino",
  "cuentas_ignoradas": ["steamid1", "steamid2"],
  "items_por_pagina": 10
}
```

### Rutas por Defecto
- **Steam UserData**: `C:\Program Files (x86)\Steam\userdata`
- **Avatar Cache**: `C:\Program Files (x86)\Steam\config\avatarcache`
- **Dota 2 Config**: `[userdata]\[steamid]\570\`

## 🔒 Seguridad

- ✅ **Solo lectura/escritura**: No modifica archivos de Steam core
- ✅ **Backup automático**: Steam mantiene backups en la nube
- ✅ **Validación**: Confirma rutas antes de copiar
- ✅ **Error handling**: Manejo seguro de errores de E/O

## 🐛 Solución de Problemas

### Problemas Comunes

**No detecta cuentas:**
- Verificar que Steam esté instalado en la ruta estándar
- Asegurar que las cuentas tengan Dota 2 instalado
- Ejecutar como administrador

**Error al copiar:**
- Cerrar Steam antes de copiar
- Verificar permisos de escritura
- Comprobar espacio en disco

**No aparecen avatares:**
- Los avatares se cargan desde caché de Steam
- Algunos usuarios pueden no tener avatar

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💻 Autor

**Sadohu**
- Desarrollo y mantenimiento principal

## 🙏 Agradecimientos

- **[EpziTecho](https://github.com/EpziTecho)** por sugerir el nombre "DotaTwin" que captura perfectamente la esencia del proyecto
- **GitHub Copilot** por el apoyo continuo en la generación de código desde la v2.0 usando *pair programming* asistido por IA
- Comunidad de Dota 2 por feedback y testing
- Valve por la estructura abierta de configuraciones
- Usuarios beta por reportes de bugs y sugerencias

### 🤖 Desarrollo Asistido por IA
Este proyecto utiliza **pair programming** con GitHub Copilot desde la v2.0, combinando experiencia humana con asistencia de IA para un desarrollo más eficiente y código de mayor calidad.

## � Contacto y Soporte

### 🎮 **Comunidad Discord**
**¡Únete a nuestra comunidad oficial!**
- 💬 **Discord**: [https://discord.gg/MYNyKQvk](https://discord.gg/MYNyKQvk)
- 👥 Ayuda de la comunidad y soporte técnico
- 🔄 Intercambio de configuraciones y tips
- 📢 Anuncios de nuevas versiones

### 🔗 **Desarrollo y Código**
- 📂 **GitHub**: [https://github.com/sadohu/DotaTwin](https://github.com/sadohu/DotaTwin)
- 🐛 **Issues**: Para reportar bugs y solicitar características
- 📝 **Pull Requests**: Contribuciones bienvenidas
- 📚 **Wiki**: Documentación adicional y FAQ

### 💬 **Desarrollador**
- 🎯 **Discord Personal**: `Sadohu`
- 📧 **GitHub**: [@sadohu](https://github.com/sadohu)

### 🆘 **Tipos de Soporte**
- ✅ **Bugs y errores**: GitHub Issues
- ✅ **Preguntas generales**: Discord community
- ✅ **Solicitudes de características**: GitHub Issues
- ✅ **Documentación**: Wiki del proyecto
- ✅ **Contribuciones**: Pull Requests

## �📈 Roadmap

### v2.1 (Próxima) - Mejoras Incrementales
- [ ] Sistema de plugins para extensibilidad
- [ ] Configuración avanzada por archivo YAML
- [ ] Tests automatizados completos con CI/CD
- [ ] Optimizaciones de rendimiento

### v2.2 - Funcionalidades Avanzadas
- [ ] Backup automático antes de copiar
- [ ] Soporte para configuraciones específicas (solo hotkeys, solo video, etc.)
- [x] ~~Modo portable (sin instalación)~~ ✅ **Implementado en v3.1.0**
- [ ] Perfiles de configuración múltiples

### v2.5 - Expansión Multi-Juego
- [ ] Soporte para otros juegos de Steam
- [ ] Sistema de plantillas de configuración
- [ ] Sincronización automática entre cuentas

### v3.0 - Arquitectura Distribuida
- [ ] Interfaz web opcional
- [ ] API REST para integración
- [ ] Soporte para múltiples plataformas (Linux, macOS)
- [ ] Base de datos externa opcional

---

## 🎯 **DotaTwin v3.0.0** - *Twin your Dota experience*

**Desarrollado con ❤️ por [Sadohu](https://github.com/sadohu)**

🔗 **Enlaces importantes:**
- 📂 [Repositorio en GitHub](https://github.com/sadohu/DotaTwin)
- 💬 [Únete al Discord](https://discord.gg/MYNyKQvk)
- 📋 [Reportar Issues](https://github.com/sadohu/DotaTwin/issues)
- 📚 [Documentación](https://github.com/sadohu/DotaTwin/wiki)

*Simplificando la gestión de configuraciones de Dota 2 desde 2025*
