"""
Matplotlib example
"""

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
G.add_nodes_from([1, 2, 3, 4])
G.add_edges_from([(1, 2), (1, 3), (2, 3), (3, 4)])

st.title('Graph Visualization')
pos = nx.planar_layout(G)
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=500, edge_color='black', linewidths=1, font_size=15)
plt.title("Example Graph Visualization")
st.pyplot(plt)