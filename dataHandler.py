import sqlite3
import re
import os


class Database:
    def __init__(self, database_filename: str):
        self.database_path = f"./data/{database_filename}"
        self.filter = r'"|{|}|\$|\\|\u00e7|\'|\<|\>|\?|\=\+'
        self.startDatabase()

    # Limpia la entrada del usuario de cualquier caracter que permita inyección SQL o XML
    def __sanitizeInput(self, user_input, alfabetico=True):
        # Debido a que el nombre no se rige por un patrón específico, es el mayor vector
        # de ataque, la regla de Regex se asegura que solo queden valores alfabeticos.
        if alfabetico:
            return re.sub("[^a-zA-Z ]","",user_input)
        # Sin embargo, los correos usan caracteres especiales, principalmente . @ y numeros
        # self.filter permite esos caracteres pero bloquea otros caracteres maliciosos.
        return re.sub(self.filter, "", user_input)

    # Toma una lista de elementos obtenidos de la database y retorna un str en formato XML
    def __XMLFormat(self, data_object: list) -> str:
        table = "contactos"
        mapa_campos = ["contacto", "Nombre", "Telefono", "Correo"]
        XML_object = ['<?xml version="1.0" encoding="UTF-8"?>', f"<{table}>"]

        for objeto in data_object:
            XML_object.append(f'  <{mapa_campos[0]} id="{objeto[0]}">')
            for i, col in enumerate(objeto[1:]):
                XML_object.append(
                    f"    <{mapa_campos[i+1]}>{objeto[i+1]}</{mapa_campos[i+1]}>"
                )
            XML_object.append(f'  </{mapa_campos[0]}="{objeto[0]}">')
        XML_object.append(f"</{table}>")

        return "\n".join(XML_object)

    def emailCheck(self, mail: str):
        # La regla de regex tiene 3 grupos, el primero es la dirección, permite palabra, puntos y guiones hasta el @
        # El segundo grupo corresponde al dominio, permite varios sub dominios
        # El último grupo se asegura que el final del correo solo sea de 2 a 4 caracteres, definiendo el TLD
        return re.fullmatch(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$", mail)

    def phoneCheck(self, number: str):
        # La regla consiste de 2 grupos de captura, el código de área lo puede tomar como 412 o 0412 por ejemplo
        # Ambos grupos pueden estar separados por un espacio, guion o no estar separado
        # El siguiente grupo compone los 7 digitos del número de teléfono
        return re.fullmatch(r"^(\d{3,4}[-| ]\d{7})|(\d{10,11})$", number)

    def nameCheck(self, nombre: str):
        # Para el nombre se requiere que no sea muy corto ni muy largo
        # Dicha comparación se realiza luego de limpiar la entrada para evitar valores vacíos
        nombre = self.__sanitizeInput(nombre)
        return True if len(nombre) < 63 and len(nombre) >= 3 else False

    def startDatabase(self):
        if not os.path.exists(self.database_path):
            self.con = sqlite3.connect(self.database_path)
            self.cur = self.con.cursor()
            self.cur.execute(
                "CREATE TABLE contactos(id INTEGER NOT NULL PRIMARY KEY, nombre TEXT, telefono TEXT, email TEXT)"
            )
            return
        self.con = sqlite3.connect(self.database_path)
        self.cur = self.con.cursor()
        return

    def getEntry(self, id: str, XML=True):
        res = self.cur.execute(f"SELECT * FROM contactos WHERE id='{id}'")
        if XML:
            return self.__XMLFormat(res.fetchall())
        return res.fetchall()

    def exists(self, id: str) -> bool:
        fetch = self.cur.execute(f"SELECT * FROM contactos WHERE id={id}").fetchall()
        return True if len(fetch) >= 1 else False

    def addEntry(self, nombre: str, telefono: str, email: str):
        nombre = self.__sanitizeInput(nombre)
        self.cur.execute(
            f"INSERT INTO contactos (nombre,telefono,email) VALUES ('{nombre}','{telefono}','{email}')"
        )
        self.con.commit()

    def listEntries(self):
        res = self.cur.execute("SELECT * FROM contactos")
        return self.__XMLFormat(res.fetchall())

    def searchContact(self, name: str):
        res = self.cur.execute(
            f"SELECT * FROM contactos WHERE LOWER(nombre) LIKE LOWER('%{name.lower()}%')"
        )
        return self.__XMLFormat(res.fetchall())

    def editContact(self, id, col_name: str, new_value: str):
        if col_name == "telefono":
            new_value = self.phoneCheck(new_value)
            new_value = re.sub("-", " ", new_value[0])
        elif col_name== "nombre":
            new_value = self.__sanitizeInput(new_value)
        else:
            new_value = self.__sanitizeInput(new_value,alfabetico=False)

        self.cur.execute(
            f"UPDATE contactos SET {col_name}='{new_value}' WHERE id='{id}'"
        )
        self.con.commit()
        return True

    def deleteContact(self, id):
        self.cur.execute(f"DELETE FROM contactos WHERE id='{id}'")
        self.con.commit()

    def exit(self):
        self.con.close()
