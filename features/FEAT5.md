# Goal

Save changes in ontology editor and diagrams

# Requirements

En el editor visual de ontologia necesito que se active un boton para "Save" (colocar icono "Disk" a la izquierda de "Save") ante cualquier cambio (new, update, delete) de los objetos de la ontologia y en los diagramas. Colocar el boton "Save" en la barra superior del editor alineada a la derecha. Si el usuario presiona "Save" se debe guardar todos los cambios (ajustar o añadir endpoint en BFF y API para registro masivo en una transaccion de todos los cambios realizados por el usuario). Si el usuario decide abandonar el editor de ontologia presentar un formulario modal de "Confirm" (guardar todos los cambios via BFF -> API -> Base de Datos) o "Cancel" (salir e ignorar los cambios)