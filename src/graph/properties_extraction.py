import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def importance_full_graph(full_g):
	"""
	:param full_g: full entity graph
	Computes importance of characters in the final entity graph
	"""

	# Compute degree (or weighted betweenness) centrality
	# deg_centrality = nx.degree_centrality(full_g)
	# deg_centrality = nx.betweenness_centrality(full_g, weight='weight')
	deg_centrality = nx.pagerank(full_g, weight='weight')

	print('character importance of full entity graphs',
	      dict(sorted(deg_centrality.items(), key=lambda kv: (kv[1]), reverse=True)[:10]))

	entities_importance = list(dict(sorted(deg_centrality.items(),
	                                          key=lambda kv: (kv[1]),
	                                          reverse=True)).keys())

	print('most important characters of the novel', entities_importance[:10])

	return entities_importance


def importance_subraphs(g):
	"""
	:param g: list of entity by chapter graphs
	:returns: list of dicts with 10 most important characters
	for the overall book (with centrality score)
	and list of the book's 10 most important characters by chapter,
	"""

	# Compute degree (or weighted betweenness)  centrality for each graph
	# deg_centrality = [nx.degree_centrality(graph) for graph in g]
	# deg_centrality = [nx.betweenness_centrality(graph, weight = 'weight') for graph in g]
	deg_centrality = [nx.pagerank(graph, weight='weight') for graph in g]

	# Keep 10 most important characters per chapter
	sorted_deg_centrality = [sorted(deg_centrality[i].items(), key=lambda x: x[1], reverse=True)[0:10]
	                         for i in range(len(deg_centrality))]
	print('Most central characters per chapter', sorted_deg_centrality)

	# Creating a DataFrame from the list of degree centralities in all the books
	degree_evol_df = pd.DataFrame.from_records(deg_centrality)
	degree_evol_df = degree_evol_df.fillna(0)

	# Plotting the degree centrality evolution some characters
	print('PLOT importance of some characters')

	# Keep only most influent characters
	dico = {}
	for column in degree_evol_df:
		dico[column] = np.sum(degree_evol_df[column])
	sorted_dico = dict(sorted(dico.items(), key=lambda kv: (kv[1]), reverse=True)[:10])
	most_important_entities = list(sorted_dico.keys())

	# Plotting the degree centrality evolution some characters
	print('PLOT evolving importance of 10 main characters across the book')
	degree_evol_df[most_important_entities].plot()
	plt.savefig('data/results/character_importance.png')

	return sorted_dico, sorted_deg_centrality


def properties_full_graph(full_g, most_central_characters):
	"""
	:param full_g: full entity graph
	:param most_important_entities: list of book's main characters
	Retrieves properties of the graphs
	"""
	print('-- FULL ENTITY GRAPH PROPERTIES --')

	# Number of nodes and edges
	print('number of entities: ', full_g.number_of_nodes())
	print('number of interactions:: ', full_g.number_of_edges())

	# Connectedness
	print('is connected ?', nx.is_connected(full_g))
	if nx.is_connected(full_g) == True:
		print(nx.diameter(full_g))

	# Degree graph - connectedness
	count = 0
	for edge in full_g.edges(data=True):
		count += edge[2]['weight']
	print('average weighted degree of the graph', count / full_g.number_of_edges())

	# Isolated nodes - connectedness
	isolated_nodes = list(nx.isolates(full_g))
	print('number of isolated nodes', len(isolated_nodes))

	# Cliques - connectedness
	print('size largest clique: ', nx.graph_clique_number(full_g))
	cliques = list(nx.find_cliques(full_g))
	length = 0
	for element in cliques:
		if len(element) > length:
			max_element = element
			length = len(element)
	print('largest clique: ', max_element)
	# Visualise clique
	# subgraph_entities = most_central_characters[:50]
	# clique_visu(full_g.subgraph(subgraph_entities), max_element)

	# Clustering
	most_important_entities = list(most_central_characters.keys())
	print('clustering coef', nx.average_clustering(full_g))
	cc = sorted(nx.clustering(full_g, nodes=most_important_entities, weight='weight'))
	print('characters with highest clustering coef', cc)
	# k core
	k_core = list(nx.k_core(full_g))
	# k_core_visu(full_g, nx.k_core(full_g))
	print('k core', list(k_core))

	# Distance between first and second most important characters
	m = most_central_characters[most_important_entities[0]]
	s = most_central_characters[most_important_entities[1]]
	dist_importance = (m - s) / m
	if dist_importance > 1 / 3:
		print('one-main-character type novel')
	else:
		print('several main characters type novel')


def properties_subgraphs(full_g, g, most_central_characters, mcc_by_chapter):
	"""
	:param full_g: entity graph
	:param g: list of chapter entity graphs
	:param most_central_characters: list of book's main characters
	:param mcc_by_chapter: book's main characters for each chapter
	Retrieves properties of the graphs
	"""
	print('-- ENTITY CHAPTER GRAPH PROPERTIES --')
	# List of most important characters in novel and in each chapter
	most_important_entities = list(most_central_characters.keys())
	mie_by_chapter = [[item[0] for item in sublist] for sublist in mcc_by_chapter]
	n_chap = len(mie_by_chapter)

	# Number of characters mentioned (nodes) and interactions (edges)
	# Info on varying number of entities and interactions
	nodes = [graph.number_of_nodes() for graph in g]
	edges = [graph.number_of_edges() for graph in g]

	# Number of characters among 10 most influential mentioned in each chap
	prop_important_entities_seen = \
		[len(set(most_important_entities).intersection(mie_by_chapter[i])) / 10
		 for i in range(len(mie_by_chapter))]
	# Number of central characters in each chapter, wrt k-core
	full_k_core = list(nx.k_core(full_g))
	k_core = [list(nx.k_core(graph)) for graph in g]
	print('k-core: ', k_core)
	# Proportion of full graph k core in each chapter k_core
	prop_k_core = [len(set(k_core[i]).intersection(full_k_core)) / len(full_k_core) for i in range(len(k_core))]

	# Store when each entity is introduced and disappears
	dict_entities = {}  # key = entity, value = [chap_intro, chap_last_seen]
	for entity in list(full_g.nodes()):
		dict_entities[entity] = [0, 0]
	introduced = []
	for i, graph in enumerate(g):
		seen_entities = list(graph.nodes())
		for ent in seen_entities:
			dict_entities[ent][1] = i + 1
			if ent not in set(introduced):
				dict_entities[ent][0] = i + 1
		introduced += seen_entities
	# Compute statistics
	existing_ent = []
	introduced_ent = []
	disappeared_ent = []
	for j in range(1, n_chap + 1):
		exist = intro = disap = 0
		for entity, val in dict_entities.items():
			if val[0] == j: intro += 1
			if val[1] == j - 1: disap += 1
			if val[0] <= j and val[1] >= j: exist += 1
		existing_ent.append(exist)  # list of existing entities at each chapter
		introduced_ent.append(intro)  # list of all introduced entities in each chapter
		disappeared_ent.append(disap)  # list of all entities that disappear from next chapter

	# Distance between first and second most important characters
	dist_importance = []
	for i in range(len(mie_by_chapter)):
		m = mcc_by_chapter[i][0][1]
		s = mcc_by_chapter[i][1][1]
		dist_importance.append((m - s) / m)

	# Find strongest edges for each chapter
	# Help us follow plot and study relations
	connexions = []
	for graph in g:
		connexion = 0
		weight = 0
		for edge in graph.edges(data=True):
			if edge[2]['weight'] > weight:
				connexion = (edge[0], edge[1])
				weight = edge[2]['weight']
		connexions.append(connexion)
	print('strongest edges', connexions)

	# Av weighted degree graph
	weighted_degree = []
	for graph in g:
		count = 0
		for edge in graph.edges(data=True):
			count += edge[2]['weight']
		weighted_degree.append(count / graph.number_of_edges())

	# Isolated nodes
	number_isolated_nodes = [len(list(nx.isolates(graph))) for graph in g]

	# Cliques
	# Info about relation between characters and evolution interactions
	cliques = [list(nx.find_cliques(graph)) for graph in g]  # list all cliques
	number_of_cliques = [len(item) for item in cliques]
	largest_clique = [nx.graph_clique_number(graph) for graph in g]
	max_cliques = []
	for clique in cliques:
		length = 0
		for element in clique:
			if len(element) > length:
				max_element = element
				length = len(element)
		max_cliques.append(max_element)
	print('biggest clique per chapter', max_cliques)
	# Visualise cliques (gephi)

	# Compute a measure of how similar cliques are
	cliques_sim = []
	for i in range(len(max_cliques)):
		sim = 0
		for j in range(len(max_cliques)):
			if i != j:
				sim += len(set(max_cliques[i]).intersection(max_cliques[j]))
		cliques_sim.append(sim / (len(max_cliques) - 1))
	# Av number of similar characters accross clique
	clique_similarity = np.sum(cliques_sim) / len(max_cliques)
	print('overall clique similarity', clique_similarity)

	# Clustering
	av_clustering_coef = [nx.average_clustering(graph) for graph in g]
	cc = [sorted(nx.clustering(graph, nodes=most_important_entities, weight='weight')) for graph in g]
	# Overlap with clustering and cliques (iou)
	inter_cc_cliques = [set(max_cliques[i]).intersection(cc[i]) for i in range(len(cc))]
	overlap = np.average([len(set(max_cliques[i]).intersection(cc[i])) / len(set(max_cliques[i]).union(cc[i]))
	                      for i in range(len(cc))])
	print('core part of each graph', inter_cc_cliques)

	# PLOTS
	print('PLOTS entity chapter graph properties')
	# plot_prop([nodes, edges], ['nodes', 'edges'], n_chap)
	plot_prop([nodes, edges, number_of_cliques, existing_ent, introduced_ent, disappeared_ent],
	          ['entities', 'interactions', 'cliques', 'existing ent', 'introduced_ent', 'disappeared_ent'],
	          n_chap, num = 1)
	plot_prop([prop_k_core, prop_important_entities_seen, dist_importance, av_clustering_coef],
	          ['proportion core entities','proportion important entities',
	           'importance diff 1st/2nd character', 'clustering coef'],
	          n_chap, num = 2)
	plot_prop([weighted_degree, number_isolated_nodes, largest_clique, cliques_sim],
	          ['graph weighted degree', 'number of isolated nodes', 'largest clique size', 'clique similarity'],
	          n_chap, num = 3)

	# Visualise cc, k_core, connexions, important nodes on graph


def plot_prop(params_val_list, labels, n_chap, num):
	"""
	:param params_val_list: list of values of the variables to plot
	:param labels: list of names of those variables
	Plots them on the same graph, with chapters as x-axis
	"""
	plt.figure()
	x = list(range(1, n_chap+1))
	y = params_val_list
	plt.xlabel("chapters")
	for i in range(len(y)):
		plt.plot(x, y[i], label=labels[i])
	plt.title("Entity chapter graph properties")
	plt.legend()
	plt.show()
	if num == 1:
		plt.savefig('data/results/Prop1.png')
	elif num ==2:
		plt.savefig('data/results/Prop2.png')
	else:
		plt.savefig('data/results/Prop3.png')



def clique_visu(graph, clique):
	"""
	Enables to visualise a clique in a graph
	"""
	# Set parameters
	plt.figure()
	pos = nx.spring_layout(graph, k=0.2, weight='weight') # k:optimal distance between nodes
	plt.rcParams.update(plt.rcParamsDefault)
	plt.rcParams.update({'figure.figsize': (15, 10)})

	# Find clique
	node_color = [(0.5, 0.5, 0.5) for v in graph.nodes()]
	for i, v in enumerate(graph.nodes()):
		if v in clique:
			node_color[i] = (0.5, 0.5, 0.9)
	# Plot
	nx.draw_networkx(graph, node_color=node_color, pos=pos)
	plt.savefig('data/results/cliques_vizu.png')


def k_core_visu(graph, k_core):
	"""
	Enables a nice visualisation of the k_core of the graph
	"""
	# Param
	plt.figure()
	plt.rcParams.update(plt.rcParamsDefault)
	plt.rcParams.update({'figure.figsize': (15, 10)})
	plt.style.use('dark_background')
	pos = nx.spring_layout(graph, k=0.2)
	# Visualize network and k-cores
	nx.draw_networkx(graph, pos=pos, node_size=0, edge_color="#333333", alpha=0.05, with_labels=False)
	nx.draw_networkx(k_core, pos=pos, node_size=0, edge_color="red", alpha=0.05, with_labels=False)
	plt.savefig('data/results/k_core.png')

