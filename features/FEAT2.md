# Goal

Registrar un nuevo dominio de conocimiento.

# Requirements

- Map Domain -> "Create New Domain" con el nodo Stitch "d593a1d14d0241dc85245656b8e9b4ad"
- Se requiere alinear completamente el formulario actual con el formulario en Stitch

# Acceptance Criteria

- Cuando se selecciona la opcion "Create New Domain" se debe abrir un formulario para crear un nuevo dominio
- El formulario debe tener los siguientes campos:
    - Imagen representativa: se debe poder abrir un archivo de imagen (.png) o arrartrar y soltar un archivo desde el sistema de archivos, debe mostrar una vista previa de la imagen y permitir recortarla o rotarla.
    - En "Detalles del Dominio" se debe mostrar los idiomas ES y EN que al activarlo debe permitir editar los campos Name, Description en el idioma seleccionado.
    - Name: Nombre del dominio
    - Description: Descripcion del dominio
    - Visibility: Visibilidad del dominio (Publico o Privado)
    - Tags: Etiquetas del dominio (separadas por coma)
    - Flujo de Ingesta: Se debe mostrar un dropdown con los flujos de ingesta disponibles.
    - Flujo de Ingesta: Se debe permitir Crear un Nuevo Flujo de Trabajo con el nombre por default el nombre del dominio (el diseño del flujo se definirá posteriormente a través de la Opcion de menu "Ingestion" en el sidebar)
- Cuando se pide registrar el dominio se debe guardar en la base de datos.
- El dominio creado debe estar visible en la lista de dominios.
- El dominio creado debe quedar en estado "draft".