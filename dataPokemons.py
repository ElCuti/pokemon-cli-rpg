import pickle
from requests_html import HTMLSession
import os

#Diccionario basico de datos del pokemon
dataPokemon = {
    "name": "",
    "health": 100,
    "baseHealth": 100,
    "level": 1,
    "type": None,
    "currentExp": 1,
    "numberPokedex": 0,
    "numberEvo": 0,
    "lvlToEvo": 0,
    "lvlMinEvo": 0,
}

#Url de donde extraemos todos los pokemons
URL_BASE = "https://pokexperto.net/index2.php?seccion=nds/nationaldex/movimientos_nivel&pk="
session = HTMLSession()

def getPokemon(index):
    """
    Función para extraer de la URL base todos los pokemons
    :param index: Contador del 1 al 151
    :return: El pokemon solicitado que tenga número de pokedex = index
    """
    try:
        url= "{}{}".format(URL_BASE, index) #Url completa del pokemon


        newPokemon = dataPokemon.copy()
        pokemonPage = session.get(url)
        newPokemon["numberPokedex"] = index                                     #Le ponemos el numero de la pokedex
        newPokemon["name"] = pokemonPage.html.find(".mini", first=True).text    #Extraemos el nombre del pokemon
        imgType = pokemonPage.html.find('img[src*="sprites/tipos"]')            #Sacamos el tipo:
        firstType = imgType[0].attrs.get("alt", "")                             #Tipo1: Tipo base del pokemon
        secondType = imgType[1].attrs.get("alt", "")                            #Tipo2: En caso de que tenga*
        if secondType == firstType or secondType == "Fairy":                    #Comprobamos si su segundo tipo es igual al primero o es "Fairy" (bug cuando se extrae la información de las evoluciones de Eevee)
            newPokemon["type"] = "{}".format(firstType)                         #Si es asi, solo mostramos su primer tipo
        else:
            newPokemon["type"] = "{}/{}".format(firstType, secondType)    #En caso de tener dos, le enseñamos las dos separadas por /

        newPokemon["attacks"] = []
        for attackItem in pokemonPage.html.find(".pkmain")[-1].find(".check3"): #Extraemos los ataques del pokemon
            minLevelActual = attackItem.find("th", first=True).text             # y comprobamos el nivel mínimo para usarlo

            if minLevelActual == "":                                            # en caso de no tener minimo, le ponemos un 1 para evitar problemas
                minLevelActual = 1
            #Guardamos el ataque en este diccionario
            attack = {
                "name": attackItem.find("td", first=True).find("a", first=True).text,
                "type":attackItem.find("td")[1].find("img", first=True).attrs["alt"],
                "minLevel": minLevelActual,
                "attackdamage": int(attackItem.find("td")[3].text.replace("--", "0")),
            }
            newPokemon["attacks"].append(attack)

        evos = pokemonPage.html.find(".bordeambos")[-1] #Localizamos la cadena evolutiva

        evosLevel = evos.find("tr", first=True).find("td:nth-child(even)") # Sacamos las secciones de niveles para las evoluciones


        if 0 < len(evosLevel):
            evosName = evos.find("tr")[1].find("td:nth-child(odd)") # Sacamos la seccion de nombre de las evoluciones
            evoIndex = 0
            for evo in evosName:
                if newPokemon["name"] in evo.text: #Si el pokemon tiene evo
                    if 0 < evoIndex:
                        prevEvoLevelParts = evosLevel[evoIndex - 1].text.split(" ")
                        if prevEvoLevelParts[0] == "Nivel":
                            newPokemon["lvlMinEvo"] = int(prevEvoLevelParts[1])
                    if evoIndex < len(evosLevel):
                        nextEvoNameParts = evosName[evoIndex+1].text.split(" ")
                        if 1 < len(nextEvoNameParts): # Caso Fearow 22, tiene un caracter vacío. Para evitar que falle, solo lo aceptamos si hay dos elementos (la palabra nivel y el valor)

                            currentEvoLevelParts = evosLevel[evoIndex].text.split(" ")

                            if currentEvoLevelParts[0] == "Nivel": # Solo si evoluciona mediante nivel, guardamos la evolución
                                newPokemon["numberEvo"] = int(nextEvoNameParts[0])
                                newPokemon["lvlToEvo"] = int(currentEvoLevelParts[1])
                evoIndex +=1

                if newPokemon["lvlToEvo"] == 0: #Si el pokemon no tiene evolución, le asignamos el 99
                    newPokemon["lvlToEvo"] = 99



        return newPokemon
    except AttributeError: #En caso de error pasar,
        pass               #COMENTARIO: Durante la realización de este código, la base de datos del pokemon 018 Pidgeot era inexistente
                           # y para evitar ese fallo de información, saltábamos al siguiente pokemon
def getAllPokemon():
    """
    Función encargada de mostrar la pantalla de inicio y de descargarlos en una base de datos como cache
    :return: Te devuelve una lista con todos los pokemons
    """
    percentage2 = 0
    try:
        print("Cargando...")
        os.system("cls")
        with open("pokefile.pkl", "rb") as pokefile: #Si tiene la caché de anteriores veces, usa esa base de datos
            allPokemon = pickle.load(pokefile)
    except FileNotFoundError:                       #En caso de no tenerla, la descarga
        print("Descargando los datos de los Pokemons")
        allPokemon = []
        for index in range(151):        #Ejecuta la función "getPokemon" para descargar todos los pokemons y mostrar una imagen
            count = index+1
            actualPokemon = getPokemon(count)
            if actualPokemon is not None:
                allPokemon.append(actualPokemon)

            percentage1 = int((count / 151) * 100)  #Porcentaje del total descargado
            if percentage1 != percentage2:
                percentage2 = percentage1
                os.system("cls")
                print("{}%".format(percentage1), end="\n")
                print("""░░░░█░▀▄░░░░░░░░░░▄▄███▀░░
░░░░█░░░▀▄░▄▄▄▄▄░▄▀░░░█▀░░
░░░░░▀▄░░░▀░░░░░▀░░░▄▀░░░░
░░░░░░░▌░▄▄░░░▄▄░▐▀▀░░░░░░
░░░░░░▐░░█▄░░░▄█░░▌▄▄▀▀▀▀█
░░░░░░▌▄▄▀▀░▄░▀▀▄▄▐░░░░░░█
░░░▄▀▀▐▀▀░░░░░░░▀▀▌▄▄▄░░░█
░░░█░░░▀▄░░░░░░░▄▀░░░░█▀▀▀
           __             ___          __    __  _____  ___  _ 
 /\ /\  /\ \ \   /\/\    /___\/\/\    /__\/\ \ \/__   \/___\/ 
/ / \ \/  \/ /  /    \  //  //    \  /_\ /  \/ /  / /\//  //  /
\ \_/ / /\  /  / /\/\ \/ \_// /\/\ \//__/ /\  /  / / / \_//\_/ 
 \___/\_\ \/   \/    \/\___/\/    \/\__/\_\ \/   \/  \___/\/   
                                                              """)


        with open("pokefile.pkl", "wb") as pokefile: #Creamos la cache
            pickle.dump(allPokemon, pokefile)
        os.system("cls")
        print("\n¡Todos los Pokemons han sido descargados!")

    print("""\n
        _.----.        ____         ,'  _\   ___    ___     ____
    _,-'       `.     |    |  /`.   \,-'    |   \  /   |   |    \  |`.
    \      __    \    '-.  | /   `.  ___    |    \/    |   '-.   \ |  |
     \.    \ \   |  __  |  |/    ,','_  `.  |          | __  |    \|  |
       \    \/   /,' _`.|      ,' / / / /   |          ,' _`.|     |  |
        \     ,-'/  /   \    ,'   | \/ / ,`.|         /  /   \  |     |
         \    \ |   \_/  |   `-.  \    `'  /|  |    ||   \_/  | |\    |
          \    \ \      /       `-.`.___,-' |  |\  /| \      /  | |   |
           \    \ `.__,'|  |`-._    `|      |__| \/ |  `.__,'|  | |   |
            \_.-'       |__|    `-._ |              '-.|     '-.| |   |
                                    `'                            '-._|                        
                                                            By @ElCutix""")
    return allPokemon

