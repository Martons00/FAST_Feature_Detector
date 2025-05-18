import osmnx as ox
import random
import heapq
import argparse
import os
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd

MAX_SPEED = 40

def style_unvisited_edge(G, edge):        
    G.edges[edge]["color"] = "#d36206"
    G.edges[edge]["alpha"] = 1
    G.edges[edge]["linewidth"] = 0.2

def style_visited_edge(G, edge):
    G.edges[edge]["color"] = "green"
    G.edges[edge]["alpha"] = 1
    G.edges[edge]["linewidth"] = 1

def style_active_edge(G, edge):
    G.edges[edge]["color"] = "red"
    G.edges[edge]["alpha"] = 1
    G.edges[edge]["linewidth"] = 1

def style_path_edge(G, edge):
    G.edges[edge]["color"] = "white"
    G.edges[edge]["alpha"] = 1
    G.edges[edge]["linewidth"] = 5

def plot_graph(G):
    ox.plot_graph(
        G,
        node_size =  [ G.nodes[node]["size"] for node in G.nodes ],
        edge_color = [ G.edges[edge]["color"] for edge in G.edges ],
        edge_alpha = [ G.edges[edge]["alpha"] for edge in G.edges ],
        edge_linewidth = [ G.edges[edge]["linewidth"] for edge in G.edges ],
        node_color = "white",
        bgcolor = "#18080e"
    )

def dijkstra(G,orig, dest, plot=False):
    for node in G.nodes:
        G.nodes[node]["visited"] = False
        G.nodes[node]["distance"] = float("inf")
        G.nodes[node]["previous"] = None
        G.nodes[node]["size"] = 0
    for edge in G.edges:
        style_unvisited_edge(G,edge)
    G.nodes[orig]["distance"] = 0
    G.nodes[orig]["size"] = 50
    G.nodes[dest]["size"] = 50
    pq = [(0, orig)]
    step = 0
    while pq:
        _, node = heapq.heappop(pq)
        if node == dest:
            print("Iterations of the alg:", step)
            return step
        if G.nodes[node]["visited"]: continue
        G.nodes[node]["visited"] = True
        for edge in G.out_edges(node):
            style_visited_edge(G,(edge[0], edge[1], 0))
            neighbor = edge[1]
            weight = G.edges[(edge[0], edge[1], 0)]["weight"]
            if G.nodes[neighbor]["distance"] > G.nodes[node]["distance"] + weight:
                G.nodes[neighbor]["distance"] = G.nodes[node]["distance"] + weight
                G.nodes[neighbor]["previous"] = node
                heapq.heappush(pq, (G.nodes[neighbor]["distance"], neighbor))
                for edge2 in G.out_edges(neighbor):
                    style_active_edge(G,(edge2[0], edge2[1], 0))
        step += 1

import heapq

def A_star(G, orig, dest, plot=False):
    open_heap = []
    g_score = {node: float('inf') for node in G.nodes}
    g_score[orig] = 0
    f_score = {node: float('inf') for node in G.nodes}
    f_score[orig] = heuristic(G, orig, dest)
    
    entry_map = {}  
    entry_count = 0  

    entry = [f_score[orig], entry_count, orig]
    heapq.heappush(open_heap, entry)
    entry_map[orig] = entry
    entry_count += 1

    closed_set = set()
    step = 0

    for node in G.nodes:
        G.nodes[node]["visited"] = False
        G.nodes[node]["distance"] = float('inf')
        G.nodes[node]["previous"] = None
        G.nodes[node]["size"] = 0
    
    for edge in G.edges:
        style_unvisited_edge(G, edge)

    G.nodes[orig]["distance"] = 0
    G.nodes[orig]["size"] = 50
    G.nodes[dest]["size"] = 50

    while open_heap:
        current_f, count, current = heapq.heappop(open_heap)
        
        if current not in entry_map or entry_map[current][0] < current_f:
            continue
            
        del entry_map[current]
        
        if current == dest:
            print("Iterations of the alg:", step)
            return step

        closed_set.add(current)
        G.nodes[current]["visited"] = True
        step += 1  

        for u, v, k in G.out_edges(current, keys=True):
            neighbor = v
            if neighbor in closed_set:
                continue
                
            edge_weight = G.edges[(u, v, k)].get("weight", float('inf'))
            tentative_g = g_score[current] + edge_weight
            
            if tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                new_f = tentative_g + heuristic(G, neighbor, dest)
                
                if neighbor in entry_map:
                    old_f = entry_map[neighbor][0]
                    if new_f >= old_f:
                        continue
                    entry_map[neighbor][2] = 'REMOVED'  
                entry = [new_f, entry_count, neighbor]
                entry_count += 1
                heapq.heappush(open_heap, entry)
                entry_map[neighbor] = entry
                
                G.nodes[neighbor]["previous"] = current
                G.nodes[neighbor]["distance"] = tentative_g
                style_visited_edge(G, (u, v, k))

    return step




def heuristic(G,node1, node2):
    lat1, lon1 = G.nodes[node1]["y"], G.nodes[node1]["x"]
    lat2, lon2 = G.nodes[node2]["y"], G.nodes[node2]["x"]
    return ox.distance.great_circle(lat1, lon1, lat2, lon2) / MAX_SPEED 




def reconstruct_path(G,orig, dest, plot=False, algorithm=None):
    for edge in G.edges:
        style_unvisited_edge(G,edge)
    dist = 0
    speeds = []
    curr = dest
    while curr != orig:
        prev = G.nodes[curr]["previous"]
        dist += G.edges[(prev, curr, 0)]["length"]
        speeds.append(G.edges[(prev, curr, 0)]["maxspeed"])
        style_path_edge(G,(prev, curr, 0))
        if algorithm:
            G.edges[(prev, curr, 0)][f"{algorithm}_uses"] = G.edges[(prev, curr, 0)].get(f"{algorithm}_uses", 0) + 1
        curr = prev
    dist /= 1000
    return dist

def plot_heatmap(G, algorithm, place_name=None, save=True, figsize=(10, 10), cmap="Reds"):
    nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#18080e")
    ax.set_facecolor("#18080e")
    ax.axis("off")

    edges.plot(
        ax=ax,
        column=f"{algorithm}_uses" if f"{algorithm}_uses" in edges.columns else None,
        cmap=cmap,
        linewidth=edges.get("linewidth", 1),
        alpha=edges.get("alpha", 0.7),
        legend=False
    )

    nodes.plot(
        ax=ax,
        markersize=nodes.get("size", 10),
        color="white",
        alpha=1
    )

    title = f"Heatmap for {algorithm}"
    if place_name:
        title += f" – {place_name}"
    ax.set_title(title, color="white", fontsize=16)
    
    if save:
        results_dir = os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(results_dir, exist_ok=True)
        key = place_name.replace(", ", "_").replace(" ", "_") if place_name else "heatmap"
        outpath = os.path.join(results_dir, f"{key}_{algorithm}_heatmap.png")
        fig.savefig(outpath, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())

    #plt.show()
    plt.close(fig)

    

def plot_overlay_heatmap(G, F,
                         algorithm1, algorithm2,
                         place_name=None,
                         save=True,
                         figsize=(10, 10),
                         cmap1="Reds", cmap2="Blues"):

    nodesG, edgesG = ox.graph_to_gdfs(G, nodes=True, edges=True)
    nodesF, edgesF = ox.graph_to_gdfs(F, nodes=True, edges=True)

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#18080e")
    ax.set_facecolor("#18080e")
    ax.axis("off")

    edgesG.plot(
        ax=ax,
        column=f"{algorithm1}_uses",
        cmap=cmap1,
        linewidth=edgesG.get("linewidth", 1),
        alpha=edgesG.get("alpha", 0.7),
        legend=False
    )

    edgesF.plot(
        ax=ax,
        column=f"{algorithm2}_uses",
        cmap=cmap2,
        linewidth=edgesF.get("linewidth", 1),
        alpha=edgesF.get("alpha", 0.7),
        legend=False
    )

    nodesG.plot(
        ax=ax,
        markersize=nodesG.get("size", 10),
        color="white",
        alpha=1
    )

    title = f"{algorithm1} vs {algorithm2}"
    if place_name:
        title += f" – {place_name}"
    ax.set_title(title, color="white", fontsize=16)

    if save:
        results_dir = os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(results_dir, exist_ok=True)
        key = place_name.replace(", ", "_").replace(" ", "_") if place_name else "overlay"
        outpath = os.path.join(
            results_dir,
            f"{key}_{algorithm1}_vs_{algorithm2}_overlay.png"
        )
        fig.savefig(outpath, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())

    #plt.show()
    plt.close(fig)
    

    


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run Dijkstra and A* algorithms on various locations.")
    
    parser.add_argument(
        "--plot", dest="plot", action="store_true",
        help="Enable plotting."
    )
    
    parser.add_argument(
        "--no-plot", dest="plot", action="store_false",
        help="Disable plotting."
    )
    
    parser.set_defaults(plot=True)

    args = parser.parse_args()

    place_names = ["Paris, France", "Piedmont, California, USA", "Turin, Piedmont, Italy", "Berlin, Germany", "Rome, Italy", "Barcelona, Spain", "Madrid, Spain", "London, England", "New York City, New York, USA"]
    interations_A_star = []
    interations_Dijkstra = []  
    distaces = []
    number_of_nodes = []
    number_of_edges = []
    number_of_edges_algorithm = []


    for place_name in place_names:
        G = ox.graph_from_place(place_name, network_type="drive")
        F = ox.graph_from_place(place_name, network_type="drive")
        number_of_nodes.append(len(G.nodes))
        number_of_edges.append(len(G.edges))
        print("Place:", place_name)
        print("Number of nodes:", len(G.nodes))
        print("Number of edges:", len(G.edges))
        for i in range(3):
            print("Iteration on this city :", i)
            print("\n")
            for edge in G.edges:
                maxspeed = MAX_SPEED
                
                if "maxspeed" in G.edges[edge] and G.edges[edge]["maxspeed"] is not None:
                    raw = G.edges[edge]["maxspeed"]
                    
                    if isinstance(raw, list):
                        speeds = []
                        for s in raw:
                            try:
                                speeds.append(int(s))
                            except (ValueError, TypeError):
                                pass
                        if speeds:
                            maxspeed = min(speeds)
                    
                    elif isinstance(raw, str):
                        s = raw.lower().replace("mph", "").strip()
                        try:
                            maxspeed = int(s)
                        except ValueError:
                            pass
                    
                    elif isinstance(raw, (int, float)):
                        maxspeed = int(raw)
                    
                G.edges[edge]["maxspeed"] = maxspeed
                length = G.edges[edge].get("length", 1)
                G.edges[edge]["weight"] = length / maxspeed if maxspeed > 0 else float("inf")

            
            for edge in G.edges:
                G.edges[edge]["dijkstra_uses"] = 0

            start = random.choice(list(G.nodes))
            end = random.choice(list(G.nodes))

            print("Running Dijkstra")
            step_D = dijkstra(G, start, end, plot=args.plot)
            interations_Dijkstra.append(step_D)

            dist_D = reconstruct_path(G, start, end, algorithm="dijkstra", plot=args.plot)
            print("Distance Dijkstra:", dist_D)
            print("Dijkstra edge in path:", len([edge for edge in G.edges if G.edges[edge].get("dijkstra_uses", 0) > 0]))
            print("Done \n ")



            for edge in F.edges:
                maxspeed = 40
                
                if "maxspeed" in F.edges[edge] and F.edges[edge]["maxspeed"] is not None:
                    raw = F.edges[edge]["maxspeed"]
                    
                    if isinstance(raw, list):
                        speeds = []
                        for s in raw:
                            try:
                                speeds.append(int(s))
                            except (ValueError, TypeError):
                                pass
                        if speeds:
                            maxspeed = min(speeds)
                    
                    elif isinstance(raw, str):
                        s = raw.lower().replace("mph", "").strip()
                        try:
                            maxspeed = int(s)
                        except ValueError:
                            pass
                    
                    elif isinstance(raw, (int, float)):
                        maxspeed = int(raw)
                
                F.edges[edge]["maxspeed"] = maxspeed
                length = F.edges[edge].get("length", 1)
                F.edges[edge]["weight"] = length / maxspeed if maxspeed > 0 else float("inf")

            for edge in F.edges:
                F.edges[edge]["A_star_uses"] = 0

            
            print("Running A*")
            step_A = A_star(F, start, end, plot=args.plot)
            interations_A_star.append(step_A)

            dist_A= reconstruct_path(F, start, end, algorithm="A_star", plot=args.plot)
            distaces.append(dist_A)
            print("Distance A*:", dist_A)
            print("A* edge in path:", len([edge for edge in F.edges if F.edges[edge].get("A_star_uses", 0) > 0]))
            number_of_edges_algorithm.append(len([edge for edge in F.edges if F.edges[edge].get("A_star_uses", 0) > 0]))
            print("Done \n ")

            
            if args.plot:
                name_place = place_name + str(i)
                plot_heatmap(G, "dijkstra", name_place , save=args.plot)
                plot_heatmap(F, "A_star", name_place, save=args.plot)
                plot_overlay_heatmap(G, F, "dijkstra", "A_star", place_name=name_place, save=args.plot, figsize=(20, 10), cmap1="Reds", cmap2="Blues")
        
        
        print("------------------------------------------------------")
            

    with open("results.txt", "w") as file:
        for i in range(len(place_names)):
                for j in range(3):
                    index = i * 3 + j 
                    result = (
                        f"Place: {place_names[i]}, Iteration: {j}, "
                        f"Distance {distaces[index]:.2f}km\n"
                        f"Dijkstra: {interations_Dijkstra[index]}, "
                        f"A*: {interations_A_star[index]}\n"
                    )

                    if interations_A_star[index] != 0:
                        slowdown = (
                            (interations_Dijkstra[index] - interations_A_star[index])
                            * 100
                            / interations_A_star[index]
                        )
                        comparison = f"Dijkstra è {slowdown:.2f}% più lento di A*\n"
                    else:
                        comparison = "A* non ha completato, confronto non possibile.\n"

                    information = (
                        f"Number of nodes: {number_of_nodes[i]}, "
                        f"Number of edges: {number_of_edges[i]}, "
                        f"Number of edges algorithm: {number_of_edges_algorithm[index]}\n\n"
                    )

                    print(result.strip())
                    print(comparison.strip())
                    print(information.strip())

                    file.write(result)
                    file.write(comparison)
                    file.write(information)
        dijkstra_iterations = f"Dijkstra iterations: {interations_Dijkstra}\n"
        a_star_iterations = f"A* iterations: {interations_A_star}\n"
        dijkstra_avg = f"Dijkstra average iterations: {sum(interations_Dijkstra) / len(interations_Dijkstra)}\n"
        a_star_avg = f"A* average iterations: {sum(interations_A_star) / len(interations_A_star)}\n"
        print(dijkstra_iterations.strip())
        print(a_star_iterations.strip())
        print(dijkstra_avg.strip())
        print(a_star_avg.strip())
        file.write("\n")
        file.write("--------------------------------\n")
        file.write(dijkstra_iterations)
        file.write(a_star_iterations)
        file.write(dijkstra_avg)
        file.write(a_star_avg)
