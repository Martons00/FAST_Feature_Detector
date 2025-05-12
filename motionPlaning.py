import osmnx as ox
import random
import heapq
import matplotlib.pyplot as plt

def style_unvisited_edge(edge):        
    G.edges[edge]["color"] = "#d36206"
    G.edges[edge]["alpha"] = 1
    G.edges[edge]["linewidth"] = 0.2

def style_visited_edge(edge):
    #G.edges[edge]["color"] = "#d36206"
    G.edges[edge]["color"] = "green"
    G.edges[edge]["alpha"] = 1
    G.edges[edge]["linewidth"] = 1

def style_active_edge(edge):
    #G.edges[edge]["color"] = '#e8a900'
    G.edges[edge]["color"] = "red"
    G.edges[edge]["alpha"] = 1
    G.edges[edge]["linewidth"] = 1

def style_path_edge(edge):
    G.edges[edge]["color"] = "white"
    G.edges[edge]["alpha"] = 1
    G.edges[edge]["linewidth"] = 5

def plot_graph():
    ox.plot_graph(
        G,
        node_size =  [ G.nodes[node]["size"] for node in G.nodes ],
        edge_color = [ G.edges[edge]["color"] for edge in G.edges ],
        edge_alpha = [ G.edges[edge]["alpha"] for edge in G.edges ],
        edge_linewidth = [ G.edges[edge]["linewidth"] for edge in G.edges ],
        node_color = "white",
        bgcolor = "#18080e"
    )

def dijkstra(orig, dest, plot=False):
    for node in G.nodes:
        G.nodes[node]["visited"] = False
        G.nodes[node]["distance"] = float("inf")
        G.nodes[node]["previous"] = None
        G.nodes[node]["size"] = 0
    for edge in G.edges:
        style_unvisited_edge(edge)
    G.nodes[orig]["distance"] = 0
    G.nodes[orig]["size"] = 50
    G.nodes[dest]["size"] = 50
    pq = [(0, orig)]
    step = 0
    while pq:
        _, node = heapq.heappop(pq)
        if node == dest:
            print("Iterations:", step)
            #plot_graph()
            return
        if G.nodes[node]["visited"]: continue
        G.nodes[node]["visited"] = True
        for edge in G.out_edges(node):
            style_visited_edge((edge[0], edge[1], 0))
            neighbor = edge[1]
            weight = G.edges[(edge[0], edge[1], 0)]["weight"]
            if G.nodes[neighbor]["distance"] > G.nodes[node]["distance"] + weight:
                G.nodes[neighbor]["distance"] = G.nodes[node]["distance"] + weight
                G.nodes[neighbor]["previous"] = node
                heapq.heappush(pq, (G.nodes[neighbor]["distance"], neighbor))
                for edge2 in G.out_edges(neighbor):
                    style_active_edge((edge2[0], edge2[1], 0))
        step += 1

def A_star(orig, dest, plot=False):
    open_set = {orig}
    closed_set = set()
    g_score = {node: float("inf") for node in G.nodes}
    g_score[orig] = 0
    f_score = {node: float("inf") for node in G.nodes}
    f_score[orig] = heuristic(orig, dest)  
    step = 0

    for node in G.nodes:
        G.nodes[node]["visited"] = False
        G.nodes[node]["distance"] = float("inf")
        G.nodes[node]["previous"] = None
        G.nodes[node]["size"] = 0

    for edge in G.edges:
        style_unvisited_edge(edge)
        
    G.nodes[orig]["distance"] = 0
    G.nodes[orig]["size"] = 50
    G.nodes[dest]["size"] = 50
    G.nodes[dest]["visited"] = True
    G.nodes[dest]["distance"] = 0 

    while open_set:
        current = min(open_set, key=lambda node: f_score[node])
        if current == dest:
            print("Iterations:", step)
            return reconstruct_path(orig, dest, plot)
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
            f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, dest)
            G.nodes[neighbor]["previous"] = current
            style_visited_edge((edge[0], edge[1], 0))
        step += 1
    return reconstruct_path(orig, dest, plot)

def heuristic(node1, node2):
    lat1, lon1 = G.nodes[node1]["y"], G.nodes[node1]["x"]
    lat2, lon2 = G.nodes[node2]["y"], G.nodes[node2]["x"]
    return ox.distance.great_circle(lat1, lon1, lat2, lon2) / 1000  # Convert to km




def reconstruct_path(orig, dest, plot=False, algorithm=None):
    for edge in G.edges:
        style_unvisited_edge(edge)
    dist = 0
    speeds = []
    curr = dest
    while curr != orig:
        prev = G.nodes[curr]["previous"]
        dist += G.edges[(prev, curr, 0)]["length"]
        speeds.append(G.edges[(prev, curr, 0)]["maxspeed"])
        style_path_edge((prev, curr, 0))
        if algorithm:
            G.edges[(prev, curr, 0)][f"{algorithm}_uses"] = G.edges[(prev, curr, 0)].get(f"{algorithm}_uses", 0) + 1
        curr = prev
    dist /= 1000

def plot_heatmap(algorithm):
    edge_colors = ox.plot.get_edge_colors_by_attr(G, f"{algorithm}_uses", cmap="hot")
    fig, _ = ox.plot_graph(
        G,
        node_size =  [ G.nodes[node]["size"] for node in G.nodes ],
        #edge_color = edge_colors,
        edge_color = [ G.edges[edge]["color"] for edge in G.edges ],
        edge_alpha = [ G.edges[edge]["alpha"] for edge in G.edges ],
        edge_linewidth = [ G.edges[edge]["linewidth"] for edge in G.edges ],
        bgcolor = "#18080e"
    )

def plot_comparison_heatmap(algorithm1, algorithm2):
    edge_colors1 = ox.plot.get_edge_colors_by_attr(G, f"{algorithm1}_uses", cmap="hot")
    edge_colors2 = ox.plot.get_edge_colors_by_attr(G, f"{algorithm2}_uses", cmap="hot")
    
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    
    # Plot for algorithm1
    ox.plot_graph(
        G,
        ax=axes[0],
        node_size=[G.nodes[node]["size"] for node in G.nodes],
        #edge_color=edge_colors1,
        edge_alpha=[G.edges[edge]["alpha"] for edge in G.edges],
        edge_linewidth=[G.edges[edge]["linewidth"] for edge in G.edges],
        bgcolor="#18080e",
        show=False,
        close=False
    )
    axes[0].set_title(f"Heatmap for {algorithm1}")
    
    # Plot for algorithm2
    ox.plot_graph(
        G,
        ax=axes[1],
        node_size=[G.nodes[node]["size"] for node in G.nodes],
        #edge_color=edge_colors2,
        edge_alpha=[G.edges[edge]["alpha"] for edge in G.edges],
        edge_linewidth=[G.edges[edge]["linewidth"] for edge in G.edges],
        bgcolor="#18080e",
        show=False,
        close=False
    )
    axes[1].set_title(f"Heatmap for {algorithm2}")
    
    plt.show()



#place_name = "Piedmont, California, USA"
place_name = "Turin, Piedmont, Italy"

G = ox.graph_from_place(place_name, network_type="drive")
F = ox.graph_from_place(place_name, network_type="drive")

for edge in G.edges:
    # Cleaning the "maxspeed" attribute, some values are lists, some are strings, some are None
    maxspeed = 40
    if "maxspeed" in G.edges[edge]:
        maxspeed = G.edges[edge]["maxspeed"]
        if type(maxspeed) == list:
            speeds = [ int(speed) for speed in maxspeed ]
            maxspeed = min(speeds)
        elif type(maxspeed) == str:
            maxspeed = maxspeed.strip(" mph")
            maxspeed = int(maxspeed)
    G.edges[edge]["maxspeed"] = maxspeed
    # Adding the "weight" attribute (time = distance / speed)
    G.edges[edge]["weight"] = G.edges[edge]["length"] / maxspeed


for edge in G.edges:
    G.edges[edge]["dijkstra_uses"] = 0
    G.edges[edge]["A_star_uses"] = 0

start = random.choice(list(G.nodes))
end = random.choice(list(G.nodes))

print("Running Dijkstra")
dijkstra(start, end)
print( "Done")

reconstruct_path(start, end, algorithm="dijkstra", plot=True)
plot_heatmap("dijkstra")


print("Running A*")
A_star(start, end)
print( "Done")

reconstruct_path(start, end, algorithm="A_star", plot=True)
plot_heatmap("A_star")

plot_comparison_heatmap("dijkstra", "A_star")

