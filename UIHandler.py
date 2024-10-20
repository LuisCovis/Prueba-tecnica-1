import os

try:
    import readline
except:
    pass
import json
import datetime

# UIHandler: manages both the application flow and the UI.
# UIManager is the core of the application, There are three types of menu
#   MenuObject: Its main purpose is tho allow navigation and give info.
#   EditScreen: It prints some info but expect some input to take over the flow.
# All the menus are written in a json file, each with an Unique ID and separated by the type of each menu.


class UIManager:
    class MenuObject:
        def __init__(self, handler, title, info, keys, opt={}):
            self.handler = handler
            self.title = title
            self.info = info
            self.keys = keys
            self.keys["Q"] = ["Volver", "BCK"]
            self.optional = opt

        def green(self, string):
            return f"\033[32m{string}\033[39m"

        def manageExtraInfo(self):
            if not self.optional:
                return
            extra_text = list(self.optional.keys())[0]
            print(
                extra_text.format(
                    *list(map(self.green, (map(eval, self.optional[extra_text]))))
                )
            )

        def show(self):
            self.handler.titleBox(self.title)
            print(self.info)
            self.handler.printSuccess()
            print(self.handler.lastErr)
            self.manageExtraInfo()
            print("")
            for key in self.keys:
                print(f"[{key}] {self.keys[key][0]}")
            print("")
            return input("Opción:  ")

    class EditScreen:
        def __init__(self, handler, title, info, aux, prompt, args):
            self.handler = handler
            self.title = title
            self.info = info
            self.aux = aux
            self.prompt = prompt
            self.args = args

        def show(self):
            self.handler.titleBox(self.title)
            print(self.info)
            print(self.aux.format(*list(map(eval, self.args))))
            print(self.handler.lastErr)
            print("")
            return "Q"

    class SelectionMenu:
        def __init__(self, handler, title, specialAction):
            self.handler = handler
            self.maxPages = 0
            self.maxLen = 0
            self.page = 0
            self.title = title
            self.desc = "Introduce el numero correspondiente para la expresion deseada"
            self.keys = dict()
            self.max = 5
            self.specialAction = specialAction
            self.__update()

        def __update(self):
            # if int(self.specialAction) % 2 == 0:
            #     self.iterable = self.handler.dh.getHistory()
            #     self.iterable.reverse()
            # else:
            #     vault = self.handler.dh.getVault()
            #     vault.reverse()
            #     self.maxPages = len(vault) - 1
            #     self.iterable = vault[self.page]
            pass

        def __populateKeys(self):
            self.__update()
            self.keys = {}
            for i, element in enumerate(self.iterable):
                self.keys.update({str(i): [element, f"AS{self.specialAction}:{i}"]})
            if self.paginated:
                self.keys.update({"S": ["Siguiente pagina", "AC9"]})
                self.keys.update({"A": ["Pagina Anterior", "AC10"]})
            self.keys.update({"Q": ["Volver", "BCK"]})

        def nextPage(self):
            if self.page == self.maxPages:
                self.handler.Error("Ya se encuentra en la última página.")
                return
            self.page += 1

        def prevPage(self):
            if self.page == 0:
                self.handler.Error("Ya se encuentra en la primera página.")
                return
            self.page -= 1

        def show(self):
            self.paginated = eval("self.maxPages != 0")

            self.handler.titleBox(self.title)
            print(self.desc)
            if self.paginated:
                print(f"Página {self.page+1} de {self.maxPages+1}")
            print(self.handler.lastErr)
            self.__populateKeys()
            for key in self.keys:
                if key.isnumeric():
                    print(f"[{key}] ({self.keys[key][0][1]}) {self.keys[key][0][0]}")
                else:
                    print(f"[{key}] {self.keys[key][0]}")
            print("")
            return input("Opción:  ")

    def __init__(self, dh):
        self.debug = False
        self.unix = True if os.name != "nt" else False
        self.dh = dh
        self.current_action = 0
        self.lastErr = ""
        self.menus = dict()
        self.pointer = 0
        self.stack = [0]
        self.infoQueue = list()
        self.successQueue = list()

    def __clearError(self):
        self.lastErr = ""

    def __exitAction(self, clear_last_error=True):
        if clear_last_error:
            self.lastErr = ""
        self.current_action = 0
        self.decode("BCK")

    def titleBox(self, title):
        title_len = len(title)
        margin = 5
        corner = "+"
        horizontal = "-"
        vertical = "|"
        print(corner + horizontal * (title_len + 2 * margin) + corner)
        print(vertical + " " * margin + title + " " * margin + vertical)
        print(corner + horizontal * (title_len + 2 * margin) + corner)

    def clear(self):
        if self.unix:
            os.system("clear")
        else:
            os.system("cls")

    def success(self, msg):
        self.successQueue.append(msg)

    def printSuccess(self):
        try:
            msg = self.successQueue.pop()
        except:
            return
        print(f"\033[32m[!] {msg}\033[39m")

    def Info(self, msg, desc):
        self.infoQueue.append(f"{msg} <~~ {desc}")

    def printInfo(self):
        if self.allowInfo:
            for msg in self.infoQueue:
                print(f"\033[33m[!] {msg}\033[39m")
            self.infoQueue = []

    def Error(self, msg):
        self.lastErr = f"\033[31m[⚠] {msg}\033[39m"

    def createMenu(self, UID, dataList, dynamic=False, selection=False):
        if dynamic:
            newUI = UIManager.EditScreen(self, *dataList)

        elif selection:
            newUI = UIManager.SelectionMenu(self, *dataList)

        else:
            newUI = UIManager.MenuObject(self, *dataList)
            if UID == 0:
                newUI.keys["Q"] = ["\033[31mSalir\033[39m", "EXT"]
        self.menus[UID] = newUI

    def selectMenu(self, ptr):
        self.stack.append(ptr)

    # The navigation is based on codes, each action or valid key returns a code:
    #   EXT: Exit code, closes database and exits the program
    #   BCK: Back code, pops a pointer from the stack, so the cursor will be set to the previous ID
    #   Jxx: Jump code, navigates to the menu with the ID specified in the end of the code.
    #       JM0:  Normal jump: jumps to MenuObject with ID 0
    #       JE10: Edit jump: jumps to the EditScreen with ID 10
    #   Axx: Action code, executes an action specified at the end of the code
    #       AC1: Normal action: executes the action() number 1
    def decode(self, code):
        if code == "EXT":
            self.dh.exit()
            exit()
        elif code == "BCK":
            self.stack.pop()
        elif code[0] == "J":
            self.selectMenu(int(code[2:]))
            if code[1] == "E":
                return code[2:]
        elif code[0] == "A":
            if code[1] == "S":
                parsedCode = code.split(":")
                self.specialAction(parsedCode[0][2:], parsedCode[1])
                return 0
            self.action(int(code[2:]))
        else:
            self.Error("Esa funcionalidad aún no está implementada.")
        return 0

    def readInput(self, prompt):
        if self.unix:
            readline.set_startup_hook(
                lambda: readline.insert_text(prompt)
            )  # Set initial prompt
            try:
                return input()
            finally:
                readline.set_startup_hook()  # Reset prompt
        else:
            return input("~~>  ")

    # All ACX codes jump there
    def getID(self):
        self.titleBox("Ingrese el ID de contacto")
        print("")
        return input("ID de contacto:   ")

    def action(self, action_number):
        ######################################### Accion #10
        if action_number == 10:  # Cambiar nombre
            id = self.getID()
            sw = True
            antiguo_nombre = self.dh.getEntry(id, XML=False)[0][1]
            while sw:
                self.reDraw()
                nuevo_nombre = self.readInput(antiguo_nombre)
                sw = not eval("len(nuevo_nombre) < 63")
                if sw:
                    self.Error("Introduce un nombre válido.")
            self.dh.editContact(id, "nombre", nuevo_nombre)
            self.__exitAction()
            return

        ######################################### Accion #11
        if action_number == 11:  # Cambiar telefono
            id = self.getID()
            sw = True
            antiguo_numero = self.dh.getEntry(id, XML=False)[0][2]
            while sw:
                self.reDraw()
                nuevo_numero = self.readInput(antiguo_numero)
                sw = not self.dh.phoneCheck(nuevo_numero)
                if sw:
                    self.Error("Introduce un número válido.")
            self.dh.editContact(id, "telefono", nuevo_numero)
            self.__exitAction()
            return

        ######################################### Accion #12
        if action_number == 12:  # Cambiar correo
            id = self.getID()
            sw = True
            antiguo_correo = self.dh.getEntry(id, XML=False)[0][3]
            while sw:
                self.reDraw()
                nuevo_correo = self.readInput(antiguo_correo)
                sw = not self.dh.emailCheck(nuevo_correo)
                if sw:
                    self.Error("Introduce un e-mail válido.")
            self.dh.editContact(id, "email", nuevo_correo)
            self.__exitAction()
            return

        ######################################### Accion #13
        if action_number == 13:  # Añadir nuevo contacto
            nombre = str()
            telefono = str()
            email = str()
            sw = True
            # Obtención del nombre
            while sw:
                self.reDraw()
                print("Nombre:")
                nombre = self.readInput("")
                sw = not self.dh.nameCheck(nombre)
                if sw:
                    self.Error("Introduce un nombre válido.")

            # Obtención del telefono
            self.__clearError()
            sw = True
            while sw:
                self.reDraw()
                print("Telefono:")
                telefono = self.readInput("")
                sw = not self.dh.phoneCheck(telefono)
                if sw:
                    self.Error("Introduce un número de teléfono válido.")

            # Obtención del correo
            self.__clearError()
            sw = True
            while sw:
                self.reDraw()
                print("Email:")
                email = self.readInput("")
                sw = not self.dh.emailCheck(email)
                if sw:
                    self.Error("Introduce una dirección de correo válida.")

            # Creación del nuevo contacto
            self.dh.addEntry(nombre, telefono, email)
            self.__exitAction()
            return

        ######################################### Accion #14
        if action_number == 14:  # Buscar contacto
            sw = True
            while sw:
                self.reDraw()
                nombre = self.readInput("")
                if nombre == "":
                    self.__exitAction()
                    return
                self.clear()
                self.titleBox(f'Resultados para "{nombre}". Guardar? [S/n]')
                query_result = self.dh.searchContact(nombre)
                print(query_result)
                res = input()
                sw = False if res == "" or res.lower() == "s" else True
            self.__exitAction()
            timestamp = datetime.datetime.now()
            with open(
                f"./exports/XML_Export_{timestamp.strftime('%d%m%Y %H:%M%S')}.xml", "w"
            ) as export_path:
                export_path.write(query_result)
            return

        ######################################### Accion #15
        if action_number == 15:  # Mostrar todos los contactos
            self.clear()
            self.titleBox("Mostrando todos los contactos, guardar archivo XML? [S/n]")
            query_result = self.dh.listEntries()
            print(query_result)
            response = input()
            if response == "" or response.lower() == "s":
                timestamp = datetime.datetime.now()
                with open(
                    f"./exports/XML_Exportar_Todos @ {timestamp.strftime('%d%m%Y %H:%M%S')}.xml",
                    "w",
                ) as export_path:
                    export_path.write(query_result)
            return

        ######################################### Accion #16
        if action_number == 16:  # Eliminar un contacto
            sw = True
            while sw:
                self.reDraw()
                id = self.readInput("")
                if not id.isnumeric():
                    self.Error("Inserte un valor numérico")
                    continue
                sw = not self.dh.exists(id)
                if sw:
                    self.Error("No hay ningún contacto con ese ID")
            contacto = self.dh.getEntry(id)
            self.clear()
            self.titleBox("Confirmación")
            print("")
            print(f"Se eliminará el siguiente contecto:")
            print(contacto)
            print()
            res = input("Continuar? [S/n]   ")

            if res == "" or res.lower() == "s":
                self.dh.deleteContact(id)
                self.success(f"Se eliminó exitosamente el contacto {id}")

            self.__exitAction()
            return

        # Default option
        self.Error("Acción no reconocida.")

    def reDraw(self):
        self.clear()
        current_menu = self.menus[self.pointer]
        current_menu.show()
        print(self.menus[self.pointer].prompt)

    def mainLoop(self):
        if self.debug:
            input("continue")
        self.clear()
        self.pointer = self.stack[-1]  # Update pointer
        current_menu = self.menus[self.pointer]  # Select menu to display
        value = current_menu.show()  # Display menu and store the value (Code)
        if self.current_action:
            self.action(int(self.current_action))
            return
        self.__clearError()

        if value.upper() not in current_menu.keys:
            self.Error("Por favor, selecciona una opción de la lista.")
        else:
            self.current_action = self.decode(current_menu.keys[value.upper()][1])
