import copy
import os
import sys
from dataPokemons import getAllPokemon
import random
import readchar
from time import sleep

#Efectos potenciados dependiendo del tipo del Pokemon
TYPE_CHART = {
    "normal":   {"roca": 0.5, "fantasma": 0.0},
    "lucha":    {"normal": 2.0, "roca": 2.0, "hielo": 2.0, "fantasma": 0.0, "volador": 0.5, "veneno": 0.5, "bicho": 0.5, "psiquico": 0.5},
    "volador":  {"lucha": 2.0, "bicho": 2.0, "planta": 2.0, "roca": 0.5, "electrico": 0.5, "hielo": 0.5},
    "veneno":   {"planta": 2.0, "tierra": 0.5, "roca": 0.5, "fantasma": 0.5},
    "tierra":   {"veneno": 2.0, "roca": 2.0, "fuego": 2.0, "electrico": 2.0, "volador": 0.0, "planta": 0.5, "bicho": 0.5},
    "roca":     {"volador": 2.0, "bicho": 2.0, "fuego": 2.0, "hielo": 2.0, "lucha": 0.5, "tierra": 0.5, "acero": 0.5, "agua": 0.5, "planta": 0.5},
    "bicho":    {"planta": 2.0, "psiquico": 2.0, "volador": 0.5, "lucha": 0.5, "veneno": 0.5, "fantasma": 0.5, "fuego": 0.5},
    "fantasma": {"fantasma": 2.0, "normal": 0.0, "psiquico": 0.0, "veneno": 0.5, "bicho": 0.5},
    "fuego":    {"bicho": 2.0, "planta": 2.0, "hielo": 2.0, "fuego": 0.5, "roca": 0.5, "agua": 0.5, "tierra": 0.5},
    "agua":     {"tierra": 2.0, "roca": 2.0, "fuego": 2.0, "agua": 0.5, "planta": 0.5, "hielo": 0.5},
    "planta":   {"tierra": 2.0, "roca": 2.0, "agua": 2.0, "fuego": 0.5, "planta": 0.5, "volador": 0.5, "veneno": 0.5, "bicho": 0.5, "hielo": 0.5},
    "electrico":{"volador": 2.0, "agua": 2.0, "tierra": 0.0, "electrico": 0.5, "planta": 0.5, "dragon": 0.5},
    "psiquico": {"lucha": 2.0, "veneno": 2.0, "psiquico": 0.5, "bicho": 0.5, "fantasma": 0.0},
    "hielo":    {"volador": 2.0, "tierra": 2.0, "planta": 2.0, "dragon": 2.0, "fuego": 0.5, "hielo": 0.5, "agua": 0.5, "roca": 0.5},
    "dragon":   {"dragon": 2.0, "acero": 0.5, "agua": 0.5, "fuego": 0.5, "planta": 0.5, "electrico": 0.5},
    "hada":     {"dragon": 2.0},
}




def getTypeMultiplier(moveType, defenderTypes):
    """
    Obtenemos el multiplicador del daño que hacer dependiendo del tipo
    :param moveType: Ataque escogido
    :param defenderTypes: Tipo del pokemon atacado
    :return: Multiplicador que aplicar al daño
    """
    if isinstance(defenderTypes, str):
        defender_types = [t.strip().lower() for t in defenderTypes.split("/")]
    else:
        defender_types = [t.strip().lower() for t in defenderTypes]

    mult = 1.0
    moveT = moveType.strip().lower()
    for dt in defender_types:
        if moveT in TYPE_CHART and dt in TYPE_CHART[moveT]:
            mult *= TYPE_CHART[moveT][dt]
        else:
            mult *= 1.0
    return mult

def offerNextCombat():
    """
    Función usada al final del combate para que el usuario elija que hacer
    """
    print("""¿Que desea hacer?
                        Pulse "H" para ver el historial de contrincantes derrotados
                        Pulse "A" para el siguiente combate
                        Pulse cualquier otra tecla para salir""")
    respuesta = str(readchar.readchar()).upper()
    return respuesta

def getPokemonPlayer(pokemonList):
    """
    Función para extraer 3 pokemons aleatorios para el usuario y asignarles la experiencia dependiendo de su fase evolutiva
    :param pokemonList: Base de datos de los pokemons de la 1º GEN (151)
    :return: 3 pokemons aleatorios con niveles randoms
    """
    inventory = []
    for _ in range(3):
        original = random.choice(pokemonList) #Extraemos los pokemons de la base de datos
        p = copy.deepcopy(original)
        nivel = random.randint(int(p["lvlMinEvo"])+1, int(p["lvlToEvo"]-1)) #Les asignamos un nivel por encima de su mínimo y por debajo de su máximo
        p["level"] = nivel                                                  #Por ejemplo, un Bulbasaur evoluciona al LVL 16, no tendría sentido un Bulbasaur LVL20


        base_original = p["baseHealth"]
        p["baseHealth"] = base_original + 5 * (nivel - 1) #Adaptamos la vida al nivel del pokemon

        p["health"] = p["baseHealth"]
        p["currentExp"] = 0
        inventory.append(p) #Lo guardamos en la lista "inventory"
    return {
        "playerName": input("¿Cuál es tu nombre de usuario?: ").strip(), #Nombre del usuario, no lo usamos para nada, solo para dinamizar la pantalla de inicio
        "pokemonInventory": inventory, #Asignamos al diccionario los pokemons aleatorios
        "combats": 0, #Numero de combates realizados
        "pokeballs": 1,
        "healthPotion": 2,
    }

def levelUp(pokemon, pokemonList):
    """
    Función sucesiva a "assignExperience", se ejecuta cuando un Pokemon sube de nivel, así le asignamos el aumento de Stats y vida. Aparte también comprobamos si le corresponde evolucionar
    :param pokemon: Diccionario con el pokemon al que se le atribuye el LVL
    :param pokemonList: Base de datos de todos los Pokemons
    :return: Devuelve la variable pokemon con el nuevo pokemon evolucionado
    """
    if pokemon["level"] >= 100: #Filtro para que no suban los Pokemons superiores a LVL 100
        return pokemon
    pokemon["level"] += 1
    pokemon["baseHealth"] += 5  # +5 por nivel subido
    pokemon["health"] +=5
    if pokemon["level"] >= pokemon["lvlToEvo"]: #Si el LVL es igual al LVL de evolución, evolucionamos al Pokemon
        pokemonLevel = pokemon["level"]             #Guardamos ciertos datos
        pokemonCurrentEXP = pokemon["currentExp"]        # para luego asignarle la XP
        pokemonName = pokemon["name"]              # que le toca al Pokemon evolucionado
        pokemon = pokemonList[pokemon["numberEvo"]-1] #Cambiamos al pokemon actual por el pokemon evolucionado
        pokemon["level"] = pokemonLevel         #Asignamos LVL y XP
        pokemon["currentExp"] = pokemonCurrentEXP    # previa a la Evo
        print("Tu pokemon {} ha evolucionado a {}".format(pokemonName, pokemon["name"]))




    sleep(0.8)
    print("¡Tu Pokémon {} ha subido al nivel {}!".format(pokemon["name"], pokemon["level"]))
    return pokemon

def basicInfoPokemon(pokemon):
    """
    Función para extraer información básica del pokemon que le adjuntes
    :param pokemon: Pokemon que quieres analizar
    :return: Datos más estéticos y básicos del pokemon insertado
    """
    return "{} | lvl {} | Tipo: {} | hp {}/{}".format(pokemon["name"],
                                           pokemon["level"],
                                            pokemon["type"],
                                           pokemon["health"],
                                           pokemon["baseHealth"])

def basicInfoAttack(ataques):
    """
    Función para extraer información básica del ataque que le adjuntes
    :param ataques: Ataque que quieres simplificar
    :return: Datos más estéticos y básicos del ataque insertado
    """
    return "{} | tipo: {} | lvl necesario: {} | Daño: {}".format(ataques["name"],
                                                                 ataques["type"],
                                                                 ataques["minLevel"],
                                                                 ataques["attackdamage"]
                                                                 )

def choosePokemon(pokemonUser, enemyPokemon):
    """
    Función para que el usuario escoja que Pokemon usar en el combate
    :param pokemonUser: Pokemon disponibles del usuario
    :param enemyPokemon: Pokemon activo del enemigo
    :return: Te devuelve la opción que hayas escogido entre los vivos
    """
    while True:
        vivos = [p for p in pokemonUser["pokemonInventory"] if p["health"] > 0] #Chequeamos todos los pokemons vivos
        if not vivos:                                                           # en caso de que no haya ninguno retornamos None
            return None

        print("Elige el Pokémon con el que lucharás contra: {}".format(basicInfoPokemon(enemyPokemon)))
        sleep(2)
        for idx, p in enumerate(vivos):
            sleep(0.5)
            print("{} - {}".format(idx, basicInfoPokemon(p))) #Enumeramos a los pokemons del usuario usando la función "basiInfoPokemon"
        try:                                                        #adjuntandole cada Pokemon vivo del usuario
            sleep(1)
            print("¿Cuál eliges?: ")
            choice = int(readchar.readchar())
            return vivos[choice]
        except (ValueError, IndexError):    #Evitamos que el usuario dé una respuesta errónea
            print("Opción inválida")

def playerAttack(playerPokemon, enemyPokemon):
    """
    Función troncal de ataque del usuario
    :param playerPokemon: Información del Pokemon del usuario
    :param enemyPokemon: Información del Pokemon rival
    :return: Un diccionario con el ataque escogido
    """
    while True:
        # disponibles: lista de ataques que puede usar el Pokémon (cumplen nivel mínimo y daño > 0)
        disponibles = [atk for atk in playerPokemon.get("attacks", []) if int(playerPokemon["level"]) >= int(atk.get("minLevel", 1)) and int(atk.get("attackdamage", 0)) > 0]
        if not disponibles:
            print("Tu {} no tiene ataques disponibles a su nivel.".format(playerPokemon['name'],)) #Si no tiene ataques acorde a su nivel, se retorna None
            return None

        print("Elige el ataque:")
        for idx, atk in enumerate(disponibles):
            sleep(0.2)
            print("{} - {}".format(idx, basicInfoAttack(atk))) #Enumeramos los ataques usando la función "basicInfoAttack" para simplificar cada movimiento

        try:
            sleep(1)
            print("¿Cuál eliges?: ")
            choice = int(readchar.readchar())
            atk = disponibles[choice]
            baseDamage = int(atk.get("attackdamage", 0)) #Sacamos el daño base sin multiplicador del tipo

            enemyTypeField = enemyPokemon.get("type", "") #Extraemos el tipo del pokemon rival
            mult = getTypeMultiplier(atk["type"], enemyTypeField) #Usamos nuestra función "getTypeMultiplier" para sacar el multiplicador
            realDamage = int(baseDamage * mult) #Daño realizado real (Con potenciador de los tipos)

            enemyPokemon["health"] -= realDamage
            if enemyPokemon["health"] < 0:
                enemyPokemon["health"] = 0 #Si le dejamos por debajo de 0, le ponemos directamente 0

            efectText = "" #La variable efectText sirve para posteriormente enseñar al usuario si su ataque fue más o menos efectivo en relación con el tipo
            if mult > 1:
                efectText = "¡Es súper efectivo!"
            elif 0 < mult < 1:
                efectText = "No es muy efectivo…"
            elif mult == 0:
                efectText = "No surte efecto."

            sleep(2)
            os.system("cls")
            print("Tu {} usa {} que hace {} daño → daño real: {} puntos de daño a {}. Vida restante de {}: {}/{}. {}".format(playerPokemon["name"],atk["name"],baseDamage, realDamage,enemyPokemon["name"],enemyPokemon["name"],enemyPokemon["health"],enemyPokemon["baseHealth"], efectText))
            sleep(3)
            return atk

        except (ValueError, IndexError): #Aseguramos de que el usuario escoja la opción correcta
            print("→ Opción inválida, vuelve a intentarlo.")

def captureWithPokeball(enemyPokemon, pokemonUser):
    """
    Función que añade la posibilidad de capturar a los pokemons rivales adaptada al porcentaje de vida restante y añadirlos a tu equipo
    :param enemyPokemon: Pokemon enemigo
    :param pokemonUser: Información del usuario
    :return: True en caso de capturarlo y False en caso de no capturarlo
    """
    if pokemonUser["pokeballs"] <= 0: #Si el usuario no tiene pokeballs le retornamos como intento fallido
        sleep(1)
        print("No tienes Pokéballs disponibles.")
        return False

    pokemonUser["pokeballs"] -= 1
    current = enemyPokemon["health"]
    base = enemyPokemon["baseHealth"]
    probCapture = 1 - (current / base) #Probabilidad de capturar al pokemon basándonos en el porcentaje de vida del pokemon

    # Forzar mínimo 5% y máximo 80%, por si current/base es muy cercano a 0 o 1
    if probCapture < 0.05:
        probCapture = 0.05
    elif probCapture > 0.8:
        probCapture = 0.8

    roll = random.random() #Numero del 0 al 1 random
    if roll < probCapture:
        nuevo = copy.deepcopy(enemyPokemon)
        nuevo["health"] = enemyPokemon["baseHealth"]            #En caso de que caiga dentro de la prob de captura
        nuevo["currentExp"] = random.randint(1,4)         # guardamos el pokemon en el inventario de pokemons del usuario
        pokemonUser["pokemonInventory"].append(nuevo)           # con toda la vida subida y con el LVL que tuviera
        sleep(1)
        print("¡Has capturado a {} con éxito!".format(enemyPokemon["name"]))
        return True
    else:
        print("¡Fallaste la captura de {}!".format(enemyPokemon["name"]))       #En caso de que falle le enseñamos al usuario
        sleep(2)                                                                # las pokeballs restantes
        print("Pokéballs restantes: {}".format(pokemonUser["pokeballs"]))
        sleep(2)
        os.system("cls")
        return False

def assignExperience(attackHistory, enemyLevel, pokemonList):
    """
    Función encargada de asignarle la experiencia a nuestros pokemons después de un combate
    :param attackHistory: Historial de ataques para saber que pokemon a participado
    :param enemyLevel: Nivel rival para asignar más o menos experiencia dependiendo de su nivel
    :param pokemonList: Base de datos de pokemons
    """
    # Obtenemos una lista “unicos” con cada Pokémon de attackHistory solo una vez,
    # usando un conjunto “vistos” de IDs para evitar duplicados basados en identidad.
    vistos = set()
    unicos = []
    for p in attackHistory:
        pid = id(p)                  # id(p) distingue cada instancia concreta de Pokémon
        if pid not in vistos:        # si aún no lo hemos visto...
            vistos.add(pid)          # marcamos esta instancia como vista
            unicos.append(p)         # y la incluimos en la lista de únicos

    for pokemon in unicos:
        if pokemon["health"] != 0:                  #Si el pokemon esta vivo le asignamos experiencia
            xp = enemyLevel/len(unicos)             #Repartimos la experiencia entre todos los pokemons participantes
            pokemon["currentExp"] += int(xp)        #Damos la experiencia basándonos en el LVL del pokemon rival
            sleep(1)
            print("{} recibe {} puntos de experiencia (Total: {}).".format(pokemon['name'], int(xp), pokemon['currentExp']))

            lvl = pokemon["level"] #Establecemos una cantidad de exp por tramos del 0-20, 21-50 y 50-99
            if lvl <= 20:
                umbral = 5
            elif lvl <= 50:
                umbral = 10
            else:
                umbral = 15

            while pokemon["currentExp"] >= umbral and pokemon["health"] != 0: #Creamos un ciclo para subir todos los niveles que haya conseguido nuestro pokemon
                pokemon["currentExp"] -= umbral                               #Si nuestro pokemon lvl20 le gana a uno lvl 70, va a subir muchas veces
                pokemon = levelUp(pokemon, pokemonList)                       #Llamamos a nuestra función que resta XP y suma LVL
                lvl = pokemon["level"]
                if lvl <= 20:
                    umbral = 5
                elif lvl <= 50:
                    umbral = 10
                else:
                    umbral = 15

def curePokemon(playerPokemon, pokemonUser):
    """
    Función para curar al pokemon del usuario en proporción a su vida máxima
    :param playerPokemon: Pokemon del usuario activo
    :param pokemonUser: Información del usuario y sus recursos
    """
    if pokemonUser["healthPotion"] <= 0:
        sleep(1)
        print("No tienes pociones de curación disponibles.") #Si no tienes pociones no te cura y te devuelve a la función troncal
        return

        # En caso de usar una poción
    pokemonUser["healthPotion"] -= 1
    healed_amount = int(playerPokemon["baseHealth"]/2)   #Calculamos cual es la mitad de la vida de tu Pokemon
    nueva_vida = playerPokemon["health"] + healed_amount # y se la sumamos al pokemon
    if nueva_vida > playerPokemon["baseHealth"]:
        nueva_vida = playerPokemon["baseHealth"]        #Si nos pasamos... Le dejamos en su vida máxima
    healed = nueva_vida - playerPokemon["health"]       #healed = cantidad curada
    playerPokemon["health"] = nueva_vida                #"playerPokemon["health"]" = Vida después de curación


    print("{} ha recuperado {} puntos de vida. Vida actual: {}/{}".format(
        playerPokemon["name"],
        healed,
        playerPokemon["health"],
        playerPokemon["baseHealth"]))
    sleep(2)
    print("Pociones restantes: {}".format(pokemonUser["healthPotion"])) #Le enseñamos al usuario sus pociones restantes
    sleep(2)
    os.system("cls")

def enemyAttack(enemyPokemon, playerPokemon):
    """
    Función de ataque del pokemon rival contra el pokemon del usuario
    :param enemyPokemon: Pokemon rival y sus datos
    :param playerPokemon: Pokemon del usuario
    """
    #Miramos sus ataques basándonos en el nivel del pokemon
    posibles = [atk for atk in enemyPokemon.get("attacks", []) if int(enemyPokemon.get("level", 1)) >= int(atk.get("minLevel", 1)) and int(atk.get("attackdamage", 0)) > 0]
    if not posibles:
        print("{} no tiene ataques disponibles.".format(enemyPokemon["name"])) #Si no tiene ataques disponibles pasa el turno al usuario
        return
    ataque = random.choice(posibles)                    #Seleccionamos un ataque al azar
    base_damage = int(ataque.get("attackdamage", 0))    # asignamos el daño de ese ataque
    attacker_type = ataque["type"]                      # y guardamos el tipo del ataque

    player_type_field = playerPokemon.get("type", "")                   #Sacamos el tipo del pokemon del usuario
    multiplier = getTypeMultiplier(attacker_type, player_type_field)    #Calculamos el multiplicador de daño basándonos en el tipo del pokemon del usuario
    realDamage = int(base_damage * multiplier)                          # mediante nuestra función "getTypeMultiplier" y definimos en una variable el daño realizado

    playerPokemon["health"] -= realDamage               #realizamos el daño al pokemon del usuario
    if playerPokemon["health"] < 0:
        playerPokemon["health"] = 0

    efectText = ""          #Al igual que hemos hecho antes, guardamos la efectividad del ataque para mostrársela al usuario
    if multiplier > 1:
        efectText = " ¡Es súper efectivo!"
    elif 0 < multiplier < 1:
        efectText = " No es muy efectivo…"
    elif multiplier == 0:
        efectText = " No surte efecto."

    print("El enemigo {} usa {} ({}). Daño base: {} → daño real: {} a {}. Vida actual de {}: {}/{}{}".format(enemyPokemon["name"],
            ataque["name"],
            attacker_type,
            base_damage,
            realDamage,
            playerPokemon["name"],
            playerPokemon["name"],
            playerPokemon["health"],
            playerPokemon["baseHealth"],
            efectText))
    sleep(3)

    if playerPokemon["health"] == 0:
        print("Tu Pokémon {} se ha debilitado!".format(playerPokemon['name'])) #Si nuestro pokemon se debilita, se lo enseñamos al usuario

def fight(pokemonUser, rawEnemyPokemon, pokemonList, pokemonDefeateds):
    """
    Función troncal del combate pokemon, encargada de llevar a cabo el bucle del combate y llevar el orden, también define el nivel del pokemon rival
    :param pokemonUser: Información del usuario
    :param rawEnemyPokemon: Pokemon rival escogido, sin aplicar el nivel
    :param pokemonList: Lista de pokemons de la base de datos
    :param pokemonDefeateds: Pokemons derrotados por el usuario
    """
    print("--- NUEVO COMBATE ---")
    sleep(1)
    attackHistory = []
    enemyOriginal = rawEnemyPokemon
    enemyPokemon = copy.deepcopy(enemyOriginal)                                                             #Hacemos una copia del rival
    nivel_enemigo = random.randint(int(enemyPokemon["lvlMinEvo"])+1, int(enemyPokemon["lvlToEvo"]-1))       # y le ponemos un nivel aleatorio dentro de su margen evolutivo
    enemyPokemon["level"] = nivel_enemigo
    base_original = enemyPokemon["baseHealth"]
    enemyPokemon["baseHealth"] = base_original + 5 * (nivel_enemigo - 1) #Le adaptamos la vida a su nivel
    enemyPokemon["health"] = enemyPokemon["baseHealth"]                  # y le ponemos al máximo de vida
    playerPokemon = choosePokemon(pokemonUser, enemyPokemon)    #Activamos la función choosePokemon para que el usuario escoja con que pokemon jugar
    if playerPokemon is None:                                   # si el usuario no tiene pokemons, se finaliza
        return

    os.system("cls")
    print("{} vs {}".format(basicInfoPokemon(playerPokemon),basicInfoPokemon(enemyPokemon))) #Printamos la batalla usando la función basicInfoPokemon para ambos pokemon
    sleep(2)

    while anyPlayerPokemonLives(pokemonUser) and enemyPokemon["health"] >= 0: #Bucle de combate hasta que se debilite algún pokemon
        action = None

        while action not in ["A", "P", "V", "C"]: #Mientras el usuario no escoja bien se repite
            if playerPokemon["health"] == 0:
                siguiente = choosePokemon(pokemonUser, enemyPokemon) #Si el usuario tiene el pokemon activo debilitado, se activa la función choosePokemon
                if siguiente is None:
                    print("\n¡Se han debilitado todos tus Pokémon!") # si no tiene más, pues se sale del bucle
                    return
                print("\nTu Pokémon anterior se debilitó. Entra {}".format(siguiente['name']))
                playerPokemon = siguiente
            sleep(1)
            print("Que deseas hacer: [A]tacar, [P]okeball, Poción de [V]ida, [C]ambiar: ") #Ofrecemos al jugador sus posibilidades en el combate
            action = str(readchar.readchar()).upper()
            os.system("cls")



        if action == "A": #Si selecciona A desarrollamos la función de "playerAttack"
            sleep(1)
            playerAttack(playerPokemon, enemyPokemon)
            attackHistory.append(playerPokemon) #Añadimos a los pokemons partícipes en el combate para asignarle la XP después

            if enemyPokemon["health"] == 0 and 100 > playerPokemon["level"]: #Si el pokemon tiene 0 de vida y tiene LVL por debajo de 100 le asignamos la experiencia
                sleep(1)
                print("Has ganado!")
                pokemonDefeateds.append(basicInfoPokemon(enemyPokemon)) #Guardamos al pokemon derrotado para luego mostrárselo al usuario con nuestra función "basicInfoPokemon"
                assignExperience(attackHistory, enemyPokemon["level"], pokemonList) #Usamos nuestra función "assignExperience" para asignarle experiencia a los pokemons
                answer = offerNextCombat() #Usamos la función "offerNextCombat"
                sleep(1)
                if answer == "A":   #Si la respuesta a "offerNextCombat" es A le damos otro combate
                    return
                elif answer =="H":  #Si la respuesta a "offerNextCombat" es H, le enseñamos el historial de pokemons derrotados
                    os.system("cls")
                    pokemonDefeated(pokemonDefeateds)
                    return
                else:           #Si pulsa cualquier otra tecla el programa finaliza
                    print("Gracias por jugar!")
                    sys.exit()

        elif action == "V": #Volviendo a la variable action, si el usuario escoge V, usamos la función "curePokemon" para curar al pokemon del usuario)
            curePokemon(playerPokemon, pokemonUser)

        elif action == "P": #Si la variable action es P, usamos una pokeball mediante la función "captureWithPokeball"
            captured = captureWithPokeball(enemyPokemon, pokemonUser)
            sleep(2)
            if captured:
                return

        elif action == "C": # Si action es C, ofrecemos al usuario sus otros pokemons mediante choosePokemon
            nuevo = choosePokemon(pokemonUser, enemyPokemon)
            if nuevo is None: #Si el usuario no tiene mas pokemons, pierde el turno
                return
            if nuevo != playerPokemon: #Si el pokemon es distinto al escogido, se lo asignamos como el nuevo activo
                playerPokemon = nuevo
            else:
                print("Ese Pokémon ya está en combate, elige otro.") #Si vuelve a escoger el mismo pokemon se lo decimos y se lo volvemos a ofrecer
                sleep(2)
                os.system("cls")
                playerPokemon = choosePokemon(pokemonUser, enemyPokemon)
                if playerPokemon is None:
                    return

        enemyAttack(enemyPokemon, playerPokemon) #Al final del bucle, activamos "enemyAttack" para recibir el ataque del rival

    enemyPokemon["health"] = enemyPokemon["baseHealth"] #Volvemos a poner la vida del pokemon rival al máximo despues del combate


def pokemonDefeated(pokemonDefeateds):
    """
    Función para comprobar todos los pokemons derrotados
    :param pokemonDefeateds: Lista de pokemons derrotados
    """
    print("Te has enfrentado con los siguientes rivales:")
    for pokemonDefeated in pokemonDefeateds: #Mostramos todos los rivales (recordemos que vienen ya adaptados por la función: "basicInfoPokemon")
        print(pokemonDefeated)
    print("Pulse cualquier tecla para seguir")
    readchar.readchar()



def itemLottery(pokemonUser):
    """
    Función para asignar una recompensa al usuario después del combate
    :param pokemonUser: Información del usuario
    """
    chance = random.random()
    #Prob: 25% de conseguir una Pokeball, 50% de conseguir una poción y 25% de no conseguir nada
    if chance < 0.25:
        pokemonUser["pokeballs"] += 1
        print("¡Has obtenido 1 Pokéball! (Total: {})".format(pokemonUser["pokeballs"]))
    elif chance < 0.75:
        pokemonUser["healthPotion"] += 1
        print("¡Has obtenido 1 poción de vida! (Total: {})".format(pokemonUser["healthPotion"]))
    else:
        print("No has obtenido ningún objeto esta vez.")

def anyPlayerPokemonLives(pokemonUser):
    """
    Función que comprueba que el usuario tenga algún pokemon vivo
    :param pokemonUser: Información del usuario, para comprobar sus pokemons
    :return: True en caso de que algún pokemon tenga vida y False en caso de que ninguno tenga vida
    """
    return sum([pokemon["health"] for pokemon in pokemonUser["pokemonInventory"]]) > 0


def main():
    pokemonList = getAllPokemon()                   #Guardamos a los pokemons en la variable pokemonList
    pokemonUser = getPokemonPlayer(pokemonList)     #Asignamos los pokemons del usuario mediante "getPokemonPlayer"
    sleep(2)
    os.system("cls")
    while anyPlayerPokemonLives(pokemonUser):       #Comprobamos si hay algun pokemon vivo mediante "anyPlayerPokemonLives"
        pokemonDefeateds = []
        enemyPokemon = random.choice(pokemonList)   #Asignamos un pokemon random al rival
        fight(pokemonUser, enemyPokemon, pokemonList, pokemonDefeateds) #Desarrollamos la función del combate "fight"
        os.system("cls")
        sleep(1)
        itemLottery(pokemonUser)                    #Después del combate usamos la función "itemLottery" para asignarle una recompensa
        input("Presiona ENTER para continuar")
        os.system("cls")
        pokemonUser["combats"] += 1


    print("Has perdido en el combate nº{}".format(pokemonUser["combats"]))
if __name__ == "__main__":
    main()