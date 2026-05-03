# Knowledge Management Center

Un sistema y herramienta personal para la gestión del conocimiento (Personal Knowledge Management - PKM) diseñado para organizar, buscar y procesar información de manera inteligente.

## Objetivo

Desarrollar una Plataforma completa de gestión del conocimiento organizado en dominios de conocimiento que permita gestionar el conocimiento que ingresa (ingesta desde folder, S3, API Rest asincrona, topico Kafka y RabbitMQ) a la base de conocimientos y expone dicho conocimiento a través de APIs Restfull. La plataforma debe tener una Interfaz Web robusta basada en Vue + Pinea usando un BFF en NodeJS (API Rest y Websocket para comunicacion bidireccional) e integrada en su seguridad con Keycloak. El BFF debe consumir una serie de APIs Rest desarrolladas sobre Python 1.13+ usando uv, FastAPI y FastMCP que expondrá hacia BFF todas las funcionalidades requeridas por Front End Web (Vue + Pinia) y facilidades de busquedas via API Rest sobre los dominios definidos expuestos para terceras aplicaciones que requieran el conocimiento siempre de forma segura".

## Descripción

**Knowledge Management Center** es un proyecto en sus fases iniciales que permite estructurar y mantener un repositorio personal de información. Se apoya en técnicas avanzadas de recuperación de información y el uso de Modelos de Lenguaje (LLMs) para facilitar la búsqueda y vinculación de conceptos, entidades y resúmenes.

## Arquitectura y Características

El proyecto está configurado para trabajar con el sistema `llmwikidoc` y utiliza el modelo `gemini-2.5-flash`. Sus características principales planeadas/configuradas incluyen:

- **Estructura basada en Wiki:** La información se organiza de manera lógica en diferentes categorías dentro de la carpeta `wiki/` (`concepts`, `entities`, `summaries`).
- **Búsqueda Híbrida Avanzada:** Implementa un sistema de búsqueda ponderado que combina:
  - Búsqueda léxica (BM25)
  - Búsqueda semántica (Vectores)
  - Búsqueda basada en relaciones (Grafos)
- **Gestión de Confianza del Conocimiento:** Incorpora un sistema de puntuación de confianza para la información, con mecánicas de refuerzo por repetición, penalización por contradicción y decaimiento en el tiempo.

## Estructura de Directorios

```text
25-KnowledgeManagement/
├── .llmwikidoc.toml      # Configuración principal del sistema y parámetros de búsqueda
├── CLAUDE.md             # Guías y reglas del proyecto
└── wiki/                 # Directorio raíz de la base de conocimiento
    ├── concepts/         # Conceptos, ideas y definiciones
    ├── entities/         # Entidades específicas (personas, proyectos, herramientas, etc.)
    └── summaries/        # Resúmenes de información o documentos
```

## Próximos Pasos

- Inicializar el sistema base y las herramientas de ingesta de conocimiento.
- Desarrollar e integrar scripts para la validación y actualización de la confianza.
- Implementar la interfaz o endpoints de consulta.
