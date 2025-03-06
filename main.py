import pygame
from graph_parser import parse_xml_to_graph, dijkstra

WIDTH, HEIGHT = 800, 600

def get_closest_node(click_pos, nodes):
    """
    Gaseste nodul cel mai apropiat de pozitia click-ului.
    
    Args:
        click_pos (tuple): Pozitia (x, y) unde s-a dat click.
        nodes (dict): Dictionar cu coordonatele nodurilor.

    Returns:
        int: ID-ul nodului cel mai apropiat de click.
    """
    min_dist = float('inf')
    closest_node = None
    for node, coord in nodes.items():

        #calc distanta patratica pt a evita folosirea radicalului
        dist = (click_pos[0] - coord[0])**2 + (click_pos[1] - coord[1])**2  # distanta patratica
        if dist < min_dist:
            min_dist = dist
            closest_node = node
    return closest_node

def draw_graph(screen, nodes, edges, path=None, draw_edges=False):
    """
    Deseneaza graful pe ecran.

    Args:
        screen (pygame.Surface): Suprafata Pygame pe care desenam.
        nodes (dict): Coordonatele nodurilor.
        edges (dict): Lista de adiacenta cu greutatile muchiilor.
        path (list, optional): Lista nodurilor din drumul minim.
        draw_edges (bool): Daca muchiile trebuie desenate.
    """

    #desenam muchiile
    if draw_edges:
        for node, neighbors in edges.items():
            for neighbor, _ in neighbors:
                pygame.draw.line(screen, (200, 200, 200), nodes[node], nodes[neighbor], 1)

    #desenam nodurile
    for node, coord in nodes.items():
        pygame.draw.circle(screen, (0, 0, 255), coord, 3)

    #deesenam drumul minim daca exista
    if path:
        for i in range(len(path) - 1):
            pygame.draw.line(screen, (255, 0, 0), nodes[path[i]], nodes[path[i + 1]], 3)

def scale_coordinates(nodes, zoom_factor, offset_x, offset_y):
    """
    Scaleaza coordonatele nodurilor pentru zoom si deplasare.

    Args:
        nodes (dict): Coordonatele originale ale nodurilor.
        zoom_factor (float): Factorul curent de zoom.
        offset_x (int): Offset-ul orizontal.
        offset_y (int): Offset-ul vertical.

    Returns:
        dict: Coordonatele scalate ale nodurilor.
    """
    scaled_nodes = {}
    for node, (x, y) in nodes.items():
        #aplicam scalarea si deplasarea
        scaled_x = int(x * zoom_factor + offset_x)
        scaled_y = int(y * zoom_factor + offset_y)
        scaled_nodes[node] = (scaled_x, scaled_y)
    return scaled_nodes

def main():
    """
    Functia principala care ruleaza aplicatia.
    """
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dijkstra - Harta Luxembourg")
    clock = pygame.time.Clock()

    # parse XML si incarcam nodurile si muchiile
    nodes, edges = parse_xml_to_graph("hartaLuxembourg.xml", width=WIDTH, height=HEIGHT)
    print(f"Graful contine {len(nodes)} noduri si {sum(len(neigh) for neigh in edges.values())} muchii.")

    #variabile pt starea aplicatiei

    running = True
    start_node = None
    end_node = None
    path = None

    zoom_factor = 1.0  #factor de zoom
    offset_x, offset_y = 0, 0  #deplasarea graficului pe ecran/offset

    while running:
        screen.fill((255, 255, 255)) #curatam ecranul
        scaled_nodes = scale_coordinates(nodes, zoom_factor, offset_x, offset_y)
        draw_graph(screen, scaled_nodes, edges, path, draw_edges=True)

        #evenimente
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if event.button == 4:  # zoom in (scroll up)
                    new_zoom = zoom_factor * 1.1
                    offset_x -= (mouse_x - offset_x) * (new_zoom - zoom_factor) / zoom_factor
                    offset_y -= (mouse_y - offset_y) * (new_zoom - zoom_factor) / zoom_factor
                    zoom_factor = new_zoom
                elif event.button == 5:  # zoom out (scroll down)
                    new_zoom = zoom_factor / 1.1
                    offset_x -= (mouse_x - offset_x) * (new_zoom - zoom_factor) / zoom_factor
                    offset_y -= (mouse_y - offset_y) * (new_zoom - zoom_factor) / zoom_factor
                    zoom_factor = new_zoom
                else:  # selectare noduri prin click
                    click_pos = pygame.mouse.get_pos()
                    if start_node is None:
                        start_node = get_closest_node(click_pos, scaled_nodes)
                        print(f"Nod sursa selectat: {start_node}")
                    elif end_node is None:
                        end_node = get_closest_node(click_pos, scaled_nodes)
                        print(f"Nod destinatie selectat: {end_node}")
                        path, cost = dijkstra(edges, start_node, end_node)
                        print(f"Drumul minim: {path}, Cost total: {cost}")

            elif event.type == pygame.KEYDOWN:
                # deplasare graf cu tastele sageti
                if event.key == pygame.K_LEFT:
                    offset_x += 20
                elif event.key == pygame.K_RIGHT:
                    offset_x -= 20
                elif event.key == pygame.K_UP:
                    offset_y += 20
                elif event.key == pygame.K_DOWN:
                    offset_y -= 20

        pygame.display.flip() #actualizare ecran
        clock.tick(30) #controlam viteza de rulare

    pygame.quit()

if __name__ == "__main__":
    main()
