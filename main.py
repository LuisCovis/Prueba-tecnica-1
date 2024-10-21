from dataHandler import Database
from UIHandler import UIManager
import json
import os
import datetime


def getMenus(handler):
    menu_file = open("./menuDefinition.json")
    obj = json.load(menu_file)
    menu_file.close()
    for uid in obj["static-menu"]:
        handler.createMenu(int(uid), obj["static-menu"][uid])
    for uid in obj["dynamic-menu"]:
        handler.createMenu(int(uid), obj["dynamic-menu"][uid], dynamic=True)


if __name__ == "__main__":
    # Asegurando la existencia de las carpetas de salida y data
    div = "/" if os.name != "nt" else "\\"
    try:
        os.mkdir(f".{div}logs")
        os.mkdir(f".{div}exports")
        os.mkdir(f".{div}data")
    except:
        pass

    # Configuración inicial
    timestamp = datetime.datetime.now().strftime("%a %d %b %Y @ %H:%M")
    logfile = f".{div}logs{div}{timestamp}.log"
    dh = Database("contactos.db")
    interfaz_de_usuario = UIManager(dh,logfile)
    getMenus(interfaz_de_usuario)

    # Main loop
    while True:
        interfaz_de_usuario.mainLoop()
