import xml.etree.ElementTree as ET
import math
import heapq

def parse_xml_to_graph(file_path, width, height, margin=20):
    """
    Citeste un fisier XML si construieste graful corespunzator.
    Nodurile sunt normalizate pentru a fi afisate in fereastra Pygame.

    Args:
        file_path (str): Calea catre fisierul XML.
        width (int): Latimea ferestrei Pygame.
        height (int): Inaltimea ferestrei Pygame.
        margin (int): Marginea de siguranta pentru afisarea grafului.

    Returns:
        dict: Un dictionar cu nodurile si coordonatele acestora.
        dict: Un dictionar cu muchiile si greutatile asociate.
    """
    tree = ET.parse(file_path) #parcurgere fisier XML
    root = tree.getroot() #obtinem radacina fisierului xml

    nodes = {} #dict pentru noduri
    edges = {} #dict pt muchii

    #liste temporare pentru longitudine si latitudine pt normalizare
    longitudes = []
    latitudes = []

    #parcurgem nodurile pt a obtine long/lat
    for node in root.find("nodes"):
        longitudes.append(float(node.get("longitude")))
        latitudes.append(float(node.get("latitude")))

    #det valorile minime si maxime pt normalizare
    min_lon, max_lon = min(longitudes), max(longitudes)
    min_lat, max_lat = min(latitudes), max(latitudes)

    #parcurgem din nou nodurile pt a le normaliza coordonatele
    for node in root.find("nodes"):
        node_id = int(node.get("id")) #ID-ul nodului
        lon = float(node.get("longitude")) #longitudine
        lat = float(node.get("latitude")) #latitudine

        #normalizam coordonatele in functie de dimensiunea ferestrei
        x = margin + int((lon - min_lon) / (max_lon - min_lon) * (width - 2 * margin))
        y = margin + int((lat - min_lat) / (max_lat - min_lat) * (height - 2 * margin))

        nodes[node_id] = (x, height - y)  #salvam coordonatele (inevrsam y pt pygame)
        edges[node_id] = [] #initializam lista de vecini pt fiecare nod

    #parcurgem arcele si construim graful
    for arc in root.find("arcs"):
        source = int(arc.get("from")) #nod sursa
        target = int(arc.get("to")) #nod destinatie
        length = float(arc.get("length")) #lungimea muchiei

        #adaugam muchia in graful neorientat
        edges[source].append((target, length))
        edges[target].append((source, length))  

    return nodes, edges

def dijkstra(graph, start, end):
    """
    Calculeaza drumul minim intre doua noduri folosind algoritmul Dijkstra.

    Args:
        graph (dict): Un dictionar cu lista de adiacenta si greutati.
        start (int): Nodul sursa.
        end (int): Nodul destinatie.

    Returns:
        list: Lista nodurilor din drumul minim.
        float: Costul total al drumului minim.
    """

    #initializam distantele catre toate nodurile cu infinit
    distances = {node: float('inf') for node in graph}
    previous = {node: None for node in graph} #pt reconstruirea drumului
    distances[start] = 0 #distanta catre nodul de start este 0

    #coada de prioritati pt a alege nodul cu distanta minima
    pq = [(0, start)]  # tuplu (distanta, nod)

    while pq:
        #scoatem nodul cu distanta minima
        current_distance, current_node = heapq.heappop(pq)

        #oprim daca am ajuns la nodul destinatie
        if current_node == end:
            break

        #ignoram nodurile deja procesate
        if current_distance > distances[current_node]:
            continue
        
        #parcurgem vecinii nodului curent
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight #calculam distanta
            if distance < distances[neighbor]: #verificam daca am gasit un drum mai scurt
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor)) #adaugam vecinul in coada

    # reconstruim drumul de la end la start
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse() #inversam lista pentru a obtine drumul corect

    return path, distances[end] #returnam drumul si costul total
