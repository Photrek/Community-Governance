"""
Gravis example
"""
import gravis as gv
import streamlit.components.v1 as components

graph = {'graph': {'nodes': {'A': {}, 'B': {}}, 'edges': [{'source': 'A', 'target': 'B'}]}}
fig = gv.d3(graph)
# fig.display()

# graph = nx.powerlaw_cluster_graph(n=120, m=2, p=0.95)
# fig = gv.three(graph)

components.html(fig.to_html(), height=600)
