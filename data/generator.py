# MEMBER 5: Implement the logic. Use the `random` library. Ensure nodes do not overlap too much.
import random
import colorsys

class RandomGraphGenerator:
    def __init__(self, seed = None):
        if seed is not None:
            random.seed(seed)

    def generate_random_graph(self, num_nodes, canvas_width, canvas_height):
        """
        Generates random nodes and edges.
        
        Args:
            num_nodes (int): The number of nodes to generate.
            canvas_width (int/float): The width of the canvas.
            canvas_height (int/float): The height of the canvas.
            
        Returns:
            tuple: (node_data_list, edge_data_list)
                - node_data_list: List of dicts or tuples representing node data (id, x, y).
                - edge_data_list: List of dicts or tuples representing edge data (start_id, end_id, weight).
                
        Note: Ensure nodes are within canvas bounds (0 to width/height).
        """
        #Generate Nodes
        padding = 40
        node_data_list = []
        
        for i in range(1, num_nodes + 1):
            x = random.randint(padding, int(canvas_width) -  padding)
            y = random.randint(padding, int(canvas_height) - padding)
            node_data_list.append((i,x,y))
        
        # Generate Edges
        edge_data_list = []
        edge_set = set()

        max_edges = num_nodes * 2 
        num_edges = random.randint(num_nodes - 1, max_edges)

        while len(edge_data_list) < num_edges:
            u = random.randint(1, num_nodes)
            v = random.randint(1, num_nodes)

            if u == v:
                continue

            edge_key = tuple(sorted((u,v)))
            if edge_key in edge_set:
                continue

            weight = random.randint(1,9)
            edge_data_list.append((u, v, weight))
            edge_set.add(edge_key)
        return node_data_list, edge_data_list
        

    def generate_color_gradient(self,n):
        """
        (Optional) Generates a list of n hex color codes for visual effects.
        
        Args:
            n (int): The number of colors to generate.
            
        Returns:
            list: A list of hex color strings.
        """
        colors = []
        for i in range(n):
            hue = i / n
            r, g, b = colorsys.hsv_to_rgb(hue, 0.6, 0.9)
            hex_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
            colors.append(hex_color)
        return colors
