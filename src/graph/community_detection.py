import pandas as pd
import numpy as np
import networkx as nx
import networkx.algorithms.community as nxcom
import matplotlib.pyplot as plt


def community_detection(full_g, entities_importance):
	"""
	:param full_g: entity graph
	entities_importance: ordered list of characters from most important to least
	Detects the different communities that exist in the graph and plots them
	"""

	# Create the subgraph based on importance, k_core or interactions
	subgraph_entities = entities_importance[:50]
	g_imp = full_g.subgraph(subgraph_entities)

	# Based on k_core
	k_core = list(nx.k_core(full_g))
	g_core = full_g.subgraph(k_core)

	# Based on interactions
	sub_nodes = []
	for el in full_g.degree():
		if el[1] > 5:
			sub_nodes.append(el[0])
	g = full_g.subgraph(sub_nodes)

	# Girvan newman method to find communities
	result = nxcom.girvan_newman(g_core)
	communities = next(result)

	# Set node and edge communities
	set_node_community(g_core, communities)
	set_edge_community(g_core)

	# Visualisation
	df = (pd.DataFrame(list(g_core.degree), columns=['node','degree'])
	        .set_index('node'))
	df['community'] = pd.Series({node:data['community']
	                        for node,data in g_core.nodes(data=True)})
	df['color'] = df.groupby('community')['degree'].transform(lambda c: c/c.max())
	df.loc[df['community']=='Officer', 'color'] *= -1

	plt.figure(figsize=(20, 14))
	layout = nx.fruchterman_reingold_layout(g_core)
	vmin = df['color'].min()
	vmax = df['color'].max()
	cmap = plt.cm.coolwarm

	nx.draw_networkx(g_core, pos=layout, with_labels=True, node_color=df['color'],
	                 cmap=cmap, vmin=vmin, vmax=vmax)
	sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
	sm.set_array([])
	cbar = plt.colorbar(sm)
	plt.savefig('data/results/cluster&degree.png')

	# Plot based on betweeness centrality
	# Above community detection is based on this measure
	plt.figure(figsize=(20, 15))
	layout = nx.fruchterman_reingold_layout(g)
	c_betweenness = nx.betweenness_centrality(g)
	c_betweenness = list(c_betweenness.values())
	# Betweenness Centrality
	nx.draw(g, node_color=c_betweenness, with_labels=True, layout=layout)
	plt.savefig('data/results/betweeness_centrality.png')

	# Other type of community detection
	com = nxcom.asyn_fluidc(g, k=4, max_iter=1000, seed=None)

	# Set node and edge communities
	set_node_community(g, com)
	set_edge_community(g)

	# Attribute a value to each cluster
	val_map = []
	for node in g.nodes(data=True):
		val_map.append(node[1]['community'])

	# Plot params
	plt.figure(figsize=(20, 15))
	layout = nx.fruchterman_reingold_layout(g)
	nx.draw(g, node_color=val_map, pos=layout, with_labels=True, font_color='black', cmap=plt.cm.coolwarm)
	plt.savefig('data/results/fluid_clustering.png')


def set_node_community(g, communities):
    """
    :param g: graph
    :param communities: community to which the node belong
    Add community to node attributes
    """
    for i, v_c in enumerate(communities):
        for v in v_c:
            # Add 1 to save 0 for external edges
            g.nodes[v]['community'] = i + 1

def set_edge_community(g):
    """
    :param g: graph
    Find internal edges and add their community to their attributes
    """
    for v, w, in g.edges:
        if g.nodes[v]['community'] == g.nodes[w]['community']:
            # Internal edge, mark with community
            g.edges[v, w]['community'] = g.nodes[v]['community']
        else:
            # External edge, mark as 0
            g.edges[v, w]['community'] = 0


def big_network_community_detection(full_g):
	"""
	:param full_g: graph
	community detection and visualisation nice for large and dense networks
	"""

	plt.rcParams.update(plt.rcParamsDefault)
	plt.rcParams.update({'figure.figsize': (20, 15)})
	plt.style.use('dark_background')

	# Find communities
	communities = sorted(nxcom.greedy_modularity_communities(full_g), key=len, reverse=True)
	print(f" Book has {len(communities)} communities.")

	# Set node and edge communities
	set_node_community(full_g, communities)
	set_edge_community(full_g)

	# Set community color for internal edges
	pos = nx.spring_layout(full_g, k=0.1)
	external = [(v, w) for v, w in full_g.edges if full_g.edges[v, w]['community'] == 0]
	internal = [(v, w) for v, w in full_g.edges if full_g.edges[v, w]['community'] > 0]
	internal_color = ["black" for e in internal]
	node_color = [get_color(full_g.nodes[v]['community']) for v in full_g.nodes]

	# External edges
	nx.draw_networkx(
		full_g,
		pos=pos,
		node_size=0,
		edgelist=external,
		edge_color="silver",
		node_color=node_color,
		alpha=0.2,
		with_labels=False)
	# Internal edges
	nx.draw_networkx(
		full_g,
		pos=pos,
		edgelist=internal,
		edge_color=internal_color,
		node_color=node_color,
		alpha=0.05,
		with_labels=False)



