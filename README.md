# Pokémon CLI RPG & Web Scraper

Un motor de combate Pokémon por consola desarrollado en Python. Este fue mi proyecto fundacional para aprender programación algorítmica, estructuras de datos y extracción de información de la web. 
En lugar de usar una base de datos estática, el juego hace **web scraping** en tiempo real para construir el catálogo de Pokémon, implementando un sistema de caché local para optimizar las siguientes ejecuciones.

## ✨ Características Técnicas Destacadas

*   **Web Scraping & Caché:** Extrae dinámicamente nombres, tipos, estadísticas, ataques y niveles de evolución usando `requests_html`. Los datos se serializan y guardan localmente con `pickle` (`pokefile.pkl`) para evitar peticiones redundantes.
*   **Motor de Combate Matemático:** Implementación de una matriz bidimensional (diccionarios anidados) para calcular la efectividad y los multiplicadores de daño según el tipo de ataque y el tipo (o doble tipo) del Pokémon defensor.
*   **Gestión del Estado y Memoria:** Uso de `copy.deepcopy()` para instanciar Pokémon únicos desde la base de datos sin mutar los datos originales.
*   **Sistema de Progresión:** Algoritmo dinámico de experiencia que escala según el nivel del rival, gestionando subidas de nivel de stats y evoluciones automáticas al alcanzar el umbral necesario.
*   **Interfaz CLI:** Interacción fluida por terminal mediante `readchar` y limpieza de pantalla (`os.system("cls")`), incluyendo arte ASCII.

## 🛠️ Tecnologías Utilizadas

*   **Lenguaje:** Python 3
*   **Librerías principales:** 
    *   `requests_html` (Web Scraping y parseo del DOM)
    *   `pickle` (Serialización y persistencia de datos)
    *   `copy` (Manejo de referencias en memoria)
    *   `readchar` (Captura de eventos de teclado en CLI)

## 🚀 Instalación y Ejecución

1. Clona este repositorio:
git clone https://github.com/tu-usuario/pokemon-cli-rpg.git

2. Instala las dependencias necesarias:
pip install requests-html readchar

3. Ejecuta el juego:
python combatPokemon.py
*Nota: En la primera ejecución, el sistema tardará unos segundos mientras extrae los datos de los 151 Pokémon originales de la web para generar la caché local.*

---
> **Nota del Desarrollador:** Este fue el primer proyecto completo con el que aprendí a programar. Aunque hoy en día estructuraría el código en múltiples módulos (POO) y usaría commits atómicos, lo mantengo en su estado original como muestra de mi evolución lógica y algorítmica.
