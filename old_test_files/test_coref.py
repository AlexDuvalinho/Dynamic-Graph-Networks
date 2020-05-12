import pickle
from src.text_preprocessing.coreferences_resolution import Coreferences, Entity

"""
Use this script to test coreference modul on price prejudice novel.
This novel has already been chapterize and the character names were extracted and stored in data/entity-list
"""

if __name__ == '__main__':
    # Load the entity list
    list_of_entities = pickle.load(open('data/entity_list/price-prejudice.pkl', 'rb'))

    list_person_names = [entity['character_name'] for entity in list_of_entities]

    # Apply the coref
    coref = Coreferences(list_person_names, coref_rules_folder='data/coref_rules/')
    idx_to_entity = coref.resolve()

    # Analyse result on the first 100 characters name of the novel
    print("Number of character name occurence = ", len(list_person_names))
    print("Number of unique entities =", len(set(idx_to_entity.values())))

    person_to_entities = {list_person_names[i]: str(idx_to_entity[i]) for i in range(100)}
    print(person_to_entities)

