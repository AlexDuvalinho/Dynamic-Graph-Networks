import networkx as nx
from .node_type import NodeType
from tqdm import tqdm

"""
In this file are defined the functions that will be used to export the different character graph
into a gexf format readable by gephi 
"""


def export_full_graph(full_graph, path, name):
    """
    Export the full graph it in GEXF format
    It is mandatory to convert Enum value that characterize EdgeType and NodeType to string before performing
    the writing in gext format
    :param full_graph : nxGraph representing the full character graph
    :param path: folder where to save the graph
    :param name: name of the file that will be create

    """
    gephi_graph = nx.Graph()
    for node, data in full_graph.nodes(data=True):
        color = {}
        if data['type'] == NodeType.CHAPTER:
            color = {'color': {'r': 255, 'g': 0, 'b': 0, 'a': 0}}
        if data['type'] == NodeType.ENTITY:
            color = {'color': {'r': 0, 'g': 255, 'b': 0, 'a': 0}}
        if data['type'] == NodeType.OCCURENCE:
            color = {'color': {'r': 0, 'g': 0, 'b': 255, 'a': 0}}

        gephi_graph.add_node(node, label=str(data["type"]), viz=color)

    for u_node, v_node, data in full_graph.edges(data=True):
        gephi_graph.add_edge(u_node, v_node, label=str(data["type"]))

    nx.write_gexf(gephi_graph, path + name + '.gexf', prettyprint=True)


def export_entity_graph(entity_graph, path, name):
    """
    Export the entity graph it in GEXF format
    It is mandatory to convert Enum value that characterize EdgeType and NodeType to string before performing
    the writing in gext format
    :param entity_graph: nxGraph representing the entity interaction graph
    :param path: folder where to save the graph
    :param name: name of the file that will be create

    """
    gephi_graph = nx.Graph()
    for node, data in entity_graph.nodes(data=True):
        gephi_graph.add_node(node, label=str([node]))

    for u_node, v_node, data in entity_graph.edges(data=True):
        gephi_graph.add_edge(u_node, v_node, label=str(data["type"]), weight=data["weight"])

    nx.write_gexf(gephi_graph, path + name + '.gexf', prettyprint=True)

def export_dynamic_graph(dynamic_graph, path, name):
    """
    Export the dynamic graph in GEXF format
    The idea is to use a MultiGraph representation to facilitate the transcription.
    Consider a given edge from the dynamic_graph that connect ent1 and ent2
    This edge contains a positions feature: list of interaction position between the ent1 and ent2 in the novel
    For each interaction in this list, we will create an edge in the MultiGraph between ent1 and ent2, that will
    contain 3 features :
        - start : occurence position of the interaction
        - end : occurence position of following interaction
        - weight : number of interaction between ent1 and ent2 so far

    Thus, when GEPHI will read the MultiGraph, it will successively plot all of those edge, however
    a particular edge will only be plot between start and end in the timeline
    As a result, you will simply see one unique edge that is constantly growing with time

    We used this trick because we did not manage to create an edge attribute which vary over time
        -> Here in fact, we delete the edge and create a new one each time the attribute changes

    :param dynamic_graph: nx.Graph representating the dynamic graph
    :param path: folder where to save the graph
    :param name: name of the file that will be create
    """
    gephi_graph = nx.MultiGraph()
    for node, data in dynamic_graph.nodes(data=True):
        gephi_graph.add_node(node, label=str([node]), start=float(data['start']))

    print('Export dynamic graph')
    for u_node, v_node, data in tqdm(dynamic_graph.edges(data=True)):
        nb_of_interaction = 1
        i = 0
        while i < len(data["positions"]):
            edge_dict = {'start': float(data["positions"][i]),
                         'weight': nb_of_interaction}
            if i + 1 < len(data["positions"]):
                edge_dict['end'] = float(data["positions"][i+1])
            gephi_graph.add_edge(u_node, v_node, **edge_dict)
            i += 1
            nb_of_interaction += 1

    nx.write_gexf(gephi_graph, path + name + '.gexf', prettyprint=True)

