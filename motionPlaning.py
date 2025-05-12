import osmnx as ox
import random
import heapq
import argparse
import os
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd


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
            print("Iterations:", step)
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

def A_star(G,orig, dest, plot=False):
    open_set = {orig}
    closed_set = set()
    g_score = {node: float("inf") for node in G.nodes}
    g_score[orig] = 0
    f_score = {node: float("inf") for node in G.nodes}
    f_score[orig] = heuristic(G,orig, dest)  
    step = 0

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
    G.nodes[dest]["visited"] = True
    G.nodes[dest]["distance"] = 0 

    while open_set:
        current = min(open_set, key=lambda node: f_score[node])
        if current == dest:
            print("Iterations:", step)
            return step
        open_set.remove(current)
        closed_set.add(current)
        for edge in G.out_edges(current):
            neighbor = edge[1]
            if neighbor in closed_set:
                continue
            tentative_g_score = g_score[current] + G.edges[(edge[0], edge[1], 0)]["weight"]
            if neighbor not in open_set:
                open_set.add(neighbor)
            elif tentative_g_score >= g_score[neighbor]:
                continue
            g_score[neighbor] = tentative_g_score
            f_score[neighbor] = g_score[neighbor] + heuristic(G,neighbor, dest)
            G.nodes[neighbor]["previous"] = current
            style_visited_edge(G,(edge[0], edge[1], 0))
        step += 1
    return step

def heuristic(G,node1, node2):
    lat1, lon1 = G.nodes[node1]["y"], G.nodes[node1]["x"]
    lat2, lon2 = G.nodes[node2]["y"], G.nodes[node2]["x"]
    return ox.distance.great_circle(lat1, lon1, lat2, lon2) / 1000 




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

def plot_heatmap(G, algorithm, place_name=None):
    fig, ax = ox.plot_graph(
        G,
        node_size=[G.nodes[n]["size"] for n in G.nodes],
        edge_alpha=[G.edges[e]["alpha"] for e in G.edges],
        edge_linewidth=[G.edges[e]["linewidth"] for e in G.edges],
        bgcolor="#18080e",
        show=False,
        close=False
    )
    title = f"Heatmap for {algorithm}"
    if place_name:
        title += f" - {place_name}"
    ax.set_title(title, fontsize=16, color="white")

    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    key = place_name.replace(", ", "_").replace(" ", "_") if place_name else "heatmap"
    fig.savefig(
        os.path.join(results_dir, f"{key}_{algorithm}_heatmap.png"),
        dpi=300, bbox_inches="tight"
    )

    plt.show()
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

    plt.show()
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


    for place_name in place_names:
        print("Place:", place_name)
        G = ox.graph_from_place(place_name, network_type="drive")
            
        for edge in G.edges:
            maxspeed = 40
            
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
        distaces.append(heuristic(G,start,end))

        print("Running Dijkstra")
        step_D = dijkstra(G, start, end, plot=args.plot)
        interations_Dijkstra.append(step_D)
        print("Done")

        reconstruct_path(G, start, end, algorithm="dijkstra", plot=args.plot)

        F = ox.graph_from_place(place_name, network_type="drive")

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
        print("Done")

        reconstruct_path(F, start, end, algorithm="A_star", plot=args.plot)
        
        if args.plot:
            plot_heatmap(G, "dijkstra", place_name)
            plot_heatmap(F, "A_star", place_name)
            plot_overlay_heatmap(G, F, "dijkstra", "A_star", place_name=place_name, save=args.plot, figsize=(20, 10), cmap1="Reds", cmap2="Blues")

    with open("results.txt", "w") as file:
        for i in range(len(place_names)):
            result = f"Place: {place_names[i]}, Distance {(distaces[i]):.2f}km \nDijkstra: {interations_Dijkstra[i]}, A*: {interations_A_star[i]}\n"
            comparison = (
                f"Dijkstra e' {((interations_Dijkstra[i] - interations_A_star[i]) * 100 / interations_A_star[i]):.2f}% piu' lento di A*\n"
                if interations_A_star[i] != 0 
                else "A* non ha completato, confronto non possibile.\n"
            )
            print(result.strip())
            print(comparison.strip())
            file.write(result)
            file.write(comparison)
            file.write("\n")
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
