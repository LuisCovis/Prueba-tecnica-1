# Prueba técnica #1
prueba técnica que evaluará la lógica de un programador en Python y XML, además de su capacidad para trabajar con SQLite. Esta prueba se centra en la creación de una aplicación simple de gestión de contactos. El objetivo es que el candidato desarrolle un programa que permita agregar, listar y buscar contactos almacenados en una base de datos SQLite utilizando XML para representar los datos de contacto.

### Instrucciones:
* Cree una base de datos SQLite llamada "contactos.db" con una tabla llamada "contactos" que tenga los siguientes campos:
    * id (entero, clave primaria)
    * nombre (texto)
    * teléfono (texto)
    * email (texto)
        
### Desarrolle una aplicación en Python que permita al usuario realizar las siguientes operaciones:
* Agregar un nuevo contacto con nombre, teléfono y correo electrónico.
* Listar todos los contactos almacenados en la base de datos.
* Buscar contactos por nombre.
* Utilice XML para representar los datos de contacto. Cada contacto debe ser representado como un elemento <contacto> con atributos para el nombre, teléfono y correo electrónico.
* La aplicación debe mostrar un menú interactivo que permita al usuario seleccionar las operaciones a realizar.

* **Asegúrese de manejar excepciones y errores de manera adecuada en su código.**

## Puntos adicionales (opcional):
* Implemente la capacidad de editar y eliminar contactos.
* Utilice funciones y clases para organizar su código de manera eficiente.
* Cree un archivo de registro (log) para registrar las operaciones realizadas por la aplicación.
* Esta prueba técnica evaluará la capacidad del candidato para diseñar y desarrollar una aplicación Python que utilice SQLite para el almacenamiento de datos y XML para representarlos. Además, se evaluará su capacidad para manejar entradas de usuario y errores de manera efectiva.
