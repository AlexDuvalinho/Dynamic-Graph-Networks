from src.graph import CharacterGraph, NodeType
from src.graph.export_to_gephi import *
from src.text_preprocessing import Coreferences

import os
import pickle
import argparse
import networkx as nx

"""
Use to test CharacterGraph full graph creation 
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--re", action="store_true", help="to reconstruct again and re-save graph")
    args = parser.parse_args()

    if args.re or not os.path.exists('../data/graph/hp1.pkl'):
        # We will test from an already NER-preprocessed novel
        # Retrieve info preprocessed book
        book_name = 'hp1'
        NER_list = pickle.load(open('data/entity_list/' + book_name + '.pkl', 'rb'))
        character_name_list = [character['character_name'] for character in NER_list]
        coref = Coreferences(character_name_list, coref_rules_folder='data/coref_rules/')
        idx_to_entity = coref.resolve()
        idx_to_entity, l = coref.improved_matching(idx_to_entity)
        occurence_list = [{'character_name':NER_list[i]['character_name'],
                           'position':NER_list[i]['position'],
                           'chapter':NER_list[i]['chapter'],
                           'entity':str(idx_to_entity[i]).upper()}
                            for i in range(len(NER_list)) if i not in l]

        # Generate full graph in nx, and store it
        character_graph = CharacterGraph(occurence_list)
        character_graph.generate_full_graph()
        pickle.dump(character_graph, open('../data/graph/price-prejudice.pkl', 'wb'))

    # Load existing character graph
    character_graph = pickle.load(open('../data/graph/price-prejudice.pkl', 'rb'))
    full_graph = character_graph.full_graph
    # Info
    print('number of node in the full graph :', full_graph.number_of_nodes())
    print('number of edges in the full graph :', full_graph.number_of_edges())

    # Entity and chapter graphs
    entities_node = [node for node, data in full_graph.nodes(data=True) if data["type"] == NodeType.ENTITY]
    chapters_node = [node for node, data in full_graph.nodes(data=True) if data["type"] == NodeType.CHAPTER]
    occurence_node = [node for node, data in full_graph.nodes(data=True) if data["type"] == NodeType.OCCURENCE]
    print('entities_node :', entities_node)
    print('number of entity nodes :', len(entities_node))
    print('chapter_node :', chapters_node)

    # Export to Gephi
    export_full_graph(full_graph, '../data/graph/', name="hp1-full-graph")

    # Create entity graph (nx) and export to gephi
    entity_graph = character_graph.entity_interaction_graph(full_graph)
    export_entity_graph(entity_graph, path='../data/graph/', name="price-prejudice-entity-graph")
    print('number of entity nodes', entity_graph.number_of_nodes())

    # Create dynamic graph (nx) and export to gephi
    dynamic_graph = character_graph.dynamic_entity_interaction_graph()
    export_dynamic_graph = export_dynamic_graph(dynamic_graph, path='../data/graph/', name="price-prejudice-dynamic-graph")

    # entity_chap_graph = character_graph.entity_graph_by_chapter()
    # chap_graph = character_graph.subgraph_from_chapter(1)

