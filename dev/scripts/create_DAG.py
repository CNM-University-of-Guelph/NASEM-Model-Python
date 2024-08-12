import ast

import pandas as pd
from graph_tool.all import Graph, graph_draw, sfdp_layout, arf_layout


dag_data = pd.read_csv("./dev/data/DAG_data.csv")

dag_data['Arguments'] = dag_data['Arguments'].apply(ast.literal_eval)
dag_data['Inputs'] = dag_data['Inputs'].apply(ast.literal_eval)
dag_data['Constants'] = dag_data['Constants'].apply(ast.literal_eval)

# Initialize a directed graph
g = Graph(directed=True)

# Create a dictionary to map variable names to graph vertices
name_to_vertex = {}
vertex_labels = g.new_vertex_property("string")
vertex_colors = g.new_vertex_property("vector<double>")

# Define a color map for modules, uses RGBA mapping
module_color_map = {
    "amino_acid": [1.0, 0.0, 0.0, 0.7],             # Bright Red
    "animal": [0.0, 0.5, 1.0, 0.7],                # Sky Blue
    "body_composition": [0.0, 1.0, 0.0, 0.7],      # Bright Green
    "coefficient_adjustment": [0.6, 0.2, 0.8, 0.7], # Lavender
    "dry_matter_intake": [1.0, 0.5, 0.0, 0.7],     # Orange
    "energy_requirement": [0.2, 0.7, 0.2, 0.7],    # Forest Green
    "fecal": [0.8, 0.4, 0.0, 0.7],                 # Burnt Orange
    "gestation": [1.0, 0.2, 0.6, 0.7],             # Pink
    "infusion": [0.4, 0.0, 0.8, 0.7],              # Deep Purple
    "manure": [0.55, 0.27, 0.07, 0.7],             # Brown
    "methane": [0.2, 0.8, 0.8, 0.7],               # Aqua
    "microbial_protein": [0.6, 0.6, 0.2, 0.7],     # Olive Green
    "micronutrient_requirement": [0.8, 0.2, 0.0, 0.7], # Rust
    "milk": [0.5, 1.0, 0.5, 0.7],                  # Light Green
    "nutrient_intakes": [0.0, 0.4, 0.8, 0.7],      # Royal Blue
    "protein_requirement": [1.0, 0.7, 0.0, 0.7],   # Amber
    "protein": [0.8, 0.0, 0.8, 0.7],               # Magenta
    "report": [0.3, 0.3, 0.3, 0.7],                # Charcoal Gray
    "rumen": [0.2, 0.8, 1.0, 0.7],                 # Cyan
    "urine": [0.4, 0.8, 0.4, 0.7],                 # Sage Green
    "water": [0.0, 0.5, 1.0, 0.7],                 # Deep Sky Blue
    "Constants": [0.6, 0.6, 0.6, 1.0],             # Light Gray
    "Inputs": [0.2, 0.2, 0.2, 1.0]                 # Dark Gray
}

# Add vertices for each unique variable name in the Name column
for index, row in dag_data.iterrows():
    name = row['Name']
    module = row['Module']
    v = g.add_vertex()
    name_to_vertex[name] = v
    vertex_labels[v] = name  # Set the vertex label
    vertex_colors[v] = module_color_map.get(module, [0, 0, 0, 0])

# Add vertices for Constants and Inputs
for column in ["Constants", "Inputs"]:
    for values in dag_data[column]:
        for value in values:
            if value not in name_to_vertex:
                v = g.add_vertex()
                name_to_vertex[value] = v
                vertex_labels[v] = value
                vertex_colors[v] = module_color_map.get(column, [0.5, 0.5, 0.5, 0.5])

# Add edges based on the Arguments column
for index, row in dag_data.iterrows():
    src_vertex = name_to_vertex[row['Name']]
    arguments = row['Arguments']
    constants = row["Constants"]
    inputs = row["Inputs"]

    for arg in arguments:
        if arg in name_to_vertex:
            dst_vertex = name_to_vertex[arg]
            g.add_edge(dst_vertex, src_vertex)

    for constant in constants:
        if constant in name_to_vertex:
            dst_vertex = name_to_vertex[constant]
            g.add_edge(dst_vertex, src_vertex)

    for input_val in inputs:
        if input_val in name_to_vertex:
            dst_vertex = name_to_vertex[input_val]
            g.add_edge(dst_vertex, src_vertex)

# Output the graph to verify (for debugging purposes)
print("Graph has", g.num_vertices(), "vertices and", g.num_edges(), "edges.")

# Calculate the layout for the graph
pos = sfdp_layout(g)

output_image_path = './dev/data/DAG.png'
graph_draw(g, 
           pos=pos,
           vertex_text=vertex_labels, 
           vertex_font_size=12, 
           vertex_size=10,
           vertex_fill_color=vertex_colors,
           output_size=(8000, 8000), 
           bg_color=[0.9, 0.9, 0.9, 1],
           output=output_image_path)

print(f"Graph image saved to {output_image_path}")

# NOTE There are cases where a name is used for both a constant and a calculated value. 
# This leads to issues in the DAG as there are circular dependencies as a vertex is
# only made for the calcualted value and not the constant

# Easiest solution is to add a suffix to the constant, ex. mPrt_k_EAA2_constant
