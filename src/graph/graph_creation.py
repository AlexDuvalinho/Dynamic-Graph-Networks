import networkx as nx
from tqdm import tqdm
from itertools import product
import pickle

from .edge_type import EdgeType
from .node_type import NodeType
from .export_to_gephi import export_full_graph, export_dynamic_graph, export_entity_graph

class CharacterGraph:
    """
    CharacterGraph is used to construct a networkx graph which contains :
    - 3 types of nodes :
        - NodeType.OCCURENCE represented by a tuple [str], [int] : character_name, position
        - NodeType.CHAPTER represented by a [int]: chapter_id
        - NoteType.ENTITY represented by a [str]: entity_name

    - 4 types of edges :
        - EdgeType.TIME
        - EdgeType.INTERACT_WITH
        - EdgeType.BELONG_TO
        - EdgeType.IS_ENTITY
    """
    def __init__(self, book_name, windows_size=20):
        """
        Genere a ChacterGraph from a occurence list (must be present as a pickle file in data/entity_list
        :param book_name : str. Except to have a book_name_occ_list.pkl file in data/entity_list which contains
            occurence_list: list[dict ('character_name':[str], 'position':[int], 'chapter':[int], 'entities':[str]])
        :param windows_size: [int] size of the co-occurence windows
            -> 2 occurence nodes will be connected by an interaction edges if they appears together within a windows
            of windows_size tokens
        """
        self.book_name = book_name
        self.full_graph = nx.Graph()
        self.windows_size = windows_size
        self.chapter_nodes = set()
        self.occurence_nodes = set()
        self.entity_nodes = set()

        self.occurence_list = pickle.load(open('data/entity_list/' + book_name + '_occ_list.pkl', 'rb'))
        self.generate_full_graph()

    def generate_full_graph(self):
        """
        Generate a networkx graph from the occurence_list as describe in report
        :return: the networkx graph
        """
        print("-- GENERATE FULL GRAPH --")
        # Generate occurence nodes
        self.occurence_nodes = set((occurence['character_name'], occurence['position'])
                                   for occurence in self.occurence_list)
        for node in self.occurence_nodes:
            self.full_graph.add_node(node, type=NodeType.OCCURENCE)

        # Generate chapter nodes
        self.chapter_nodes = set(occurence['chapter'] for occurence in self.occurence_list)
        for node in self.chapter_nodes:
            self.full_graph.add_node(node, type=NodeType.CHAPTER)

        # Generate entity nodes
        self.entity_nodes = set(occurence['entity'] for occurence in self.occurence_list)
        for node in self.entity_nodes:
            self.full_graph.add_node(node, type=NodeType.ENTITY)

        # Generate belong_to (chapter) and is_entity edges
        for occurence in self.occurence_list:
            self.full_graph.add_edge((occurence['character_name'], occurence['position']),
                                     (occurence['entity']),
                                     type=EdgeType.IS_ENTITY)

            self.full_graph.add_edge((occurence['character_name'], occurence['position']),
                                     (occurence['chapter']),
                                     type=EdgeType.BELONG_TO)

        # Generate time edges
        for entity_node in self.entity_nodes:
            list_of_occurence_nodes = self.full_graph.neighbors(entity_node)
            occurence_nodes_sort_by_pos = sorted(list_of_occurence_nodes, key=lambda x: x[1])
            for idx in range(len(occurence_nodes_sort_by_pos) - 1):
                self.full_graph.add_edge(occurence_nodes_sort_by_pos[idx],
                                         occurence_nodes_sort_by_pos[idx+1],
                                         type=EdgeType.TIME)

        # Generate interaction edges
        occurence_nodes_sort_by_pos = sorted(list(self.occurence_nodes), key=lambda x: x[1])
        for idx_current_node in tqdm(range(len(occurence_nodes_sort_by_pos))):
            idx_other_node = idx_current_node + 1
            current_pos = occurence_nodes_sort_by_pos[idx_current_node][1]
            while idx_other_node < len(occurence_nodes_sort_by_pos) and \
                  occurence_nodes_sort_by_pos[idx_other_node][1] - current_pos < self.windows_size:
                self.full_graph.add_edge(occurence_nodes_sort_by_pos[idx_current_node],
                                         occurence_nodes_sort_by_pos[idx_other_node],
                                         type=EdgeType.INTERACT_WITH)
                idx_other_node += 1

        return self.full_graph

    def filter_nodes(self, node_type):
        """
        :param node_type: [NodeType]
        :return: all the node from the fullgraph that have the given type
        """
        return [node for node, data in self.full_graph.nodes(data=True) if data["type"] == node_type]

    def subgraph_from_chapter(self, chapter_idx):
        """
        Extract the subgraph corresponding to one chapter of the novel in the full graph
        More precisely, return a subgraph containing :
        - the given chapter node
        - all occurence nodes that are directly connected to this chapter node
        - all entity nodes that are directly connected to those occurence nodes
        :param chapter_idx: [int]
        :return: nxGraph
        """
        occurence_nodes_in_chapter = list(self.full_graph.neighbors(chapter_idx))
        entity_nodes_in_chapter = set(node for occurence in occurence_nodes_in_chapter
                                      for node in self.full_graph.neighbors(occurence)
                                      if self.full_graph.nodes[node]["type"] == NodeType.ENTITY)
        return self.full_graph.subgraph([chapter_idx] + occurence_nodes_in_chapter + list(entity_nodes_in_chapter))

    def entity_graph_by_chapter(self):
        """
        Compute the entity interaction graph, chapter by chapter
        :return: list[nxGraph]
        """
        print('Chapter Entity graph')
        chapter_nodes = self.filter_nodes(NodeType.CHAPTER)
        return [self.entity_interaction_graph(self.subgraph_from_chapter(chapter)) for chapter in chapter_nodes]

    @staticmethod
    def entity_interaction_graph(graph):
        """
        Given a graph of chapter, occurence, and entity nodes, compute  the entity interaction graph.
        Following the interaction definition we used, two entities interacted if there exist two occurence_nodes
        that are each connected to those entity are linked together by a edge of type INTERACT_WITH
        As a result, the number of interaction between two entities is the number of path of size 3 between the
        two entity node in the graph

        :param graph: nxGraph
        :return: a undirected weight nxGraph where the node represent the entity and the weight the number of time
        the entities interacted between each other
        """
        entity_nodes = [node for node, data in graph.nodes(data=True) if data["type"] == NodeType.ENTITY]
        # entity_nodes = self.entity_nodes
        entity_graph = nx.Graph()

        print("-- GENERATE ENTITY INTERACTION GRAPH --")

        for entity in entity_nodes:
            entity_graph.add_node(entity,type=NodeType.ENTITY)

        for entity_1, entity_2 in tqdm(list(product(entity_nodes, entity_nodes))):
            if entity_1 != entity_2:
                nb_interactions = len(list(nx.all_simple_paths(graph, source=entity_1, target=entity_2, cutoff=3)))
                if nb_interactions > 0:
                    entity_graph.add_edge(entity_1, entity_2, weight=nb_interactions, type=EdgeType.INTERACT_WITH)

        return entity_graph

    def dynamic_entity_interaction_graph(self):
        """
        From the full character graph, compute a dynamic entity interaction graph.
        This graph will only be composed of Entity node and INTERACT_WTI Edge.
        The timeline will be defined using the position in the text, ie from [0, nb_token_in_the_novel]
        Each entity node will comporte a start attribute : first time it appears in the ext
        Each interaction edge will  comporte a postions of attribute : list of each interaction position in the text
        :return: nxGraph - dynamic entity interaction graph.
        """
        dynamic_graph = nx.Graph()

        entity_nodes = [node for node, data in self.full_graph.nodes(data=True) if data["type"] == NodeType.ENTITY]
        for entity_node in entity_nodes:
            first_occurence = min(list(self.full_graph.neighbors(entity_node)), key=lambda x: x[1])[1]
            dynamic_graph.add_node(entity_node, start=first_occurence)

        entity_nodes_with_occ = list(dynamic_graph.nodes(data=True))

        print("-- GENERATE DYNAMIC GRAPH --")
        for (entity_1, data_1), (entity_2, data_2) in tqdm(list(product(entity_nodes_with_occ, entity_nodes_with_occ))):
            if entity_1 != entity_2 and data_1["start"] < data_2["start"]:
                interactions = (list(nx.all_simple_paths(self.full_graph, source=entity_1, target=entity_2, cutoff=3)))
                # By construction of the full graph each, interaction of the list interactions is a list or 4 nodes :
                # ent_1 -> occurence of ent_1 -> occurence of ent_2 -> ent_2
                # we will store for each interaction the position value of (occurence of ent_1)
                if len(interactions) > 0:
                    interaction_positions = list(map(lambda interaction: interaction[1][1], interactions))
                    dynamic_graph.add_edge(entity_1, entity_2,
                                           positions=interaction_positions,
                                           type=EdgeType.INTERACT_WITH)

        return dynamic_graph

    def generate_and_save(self):

        # Full graph
        export_full_graph(self.full_graph, 'data/graph/', name=self.book_name + "-full-graph")

        # Entity graph
        entity_graph = self.entity_interaction_graph(self.full_graph)
        pickle.dump(entity_graph, open('data/graph/' + self.book_name + '-entity-graph.pkl', 'wb'))
        export_entity_graph(entity_graph, path='data/graph/', name=self.book_name + "-entity-graph")

        # Dynamic graph
        dynamic_graph = self.dynamic_entity_interaction_graph()
        export_dynamic_graph(dynamic_graph, path='data/graph/', name=self.book_name + "-dynamic-graph")

        # Chapters graph
        chapters_graph = [self.subgraph_from_chapter(chapter)
                          for chapter in range(len(self.chapter_nodes))]

        # Entity chapter graph
        entity_chapter_graph = self.entity_graph_by_chapter()

        return self.full_graph, entity_graph, dynamic_graph, chapters_graph, entity_chapter_graph

    def create_graphs(self, character_graph):
        """
        Creates
		1/ Nodes
		2/ Full graph
		3/ Entity graph
		4/ Dynamic graph
		5/ Chapter graph
		6/ Chapter Entity graph
		"""
        # Load full character graph
        full_graph = character_graph.full_graph
        # Info
        print('number of node in the full graph :', full_graph.number_of_nodes())
        print('number of edges in the full graph :', full_graph.number_of_edges())

        # Define each type of node
        entities_node = [node for node, data in full_graph.nodes(data=True) if data["type"] == NodeType.ENTITY]
        chapters_node = [node for node, data in full_graph.nodes(data=True) if data["type"] == NodeType.CHAPTER]
        occurence_node = [node for node, data in full_graph.nodes(data=True) if data["type"] == NodeType.OCCURENCE]
        print('entities_node :', entities_node)
        print('number of entity nodes :', len(entities_node))
        print('chapter_node :', chapters_node)
        print('type chapter nodes', type(chapters_node))

        # Create entity graph (nx)
        entity_graph = character_graph.entity_interaction_graph(full_graph)

        # Create dynamic graph (nx)
        dynamic_graph = character_graph.dynamic_entity_interaction_graph()

        # Create chapter graph
        chapters_graph = [character_graph.subgraph_from_chapter(chapter) for chapter in range(len(chapters_node))]

        # Entity chapter graph
        entity_chapter_graph = character_graph.entity_graph_by_chapter()

        return full_graph, entity_graph, dynamic_graph, chapters_graph, entity_chapter_graph
