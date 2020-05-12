from src.text_preprocessing.entities_extraction import EntitiesExtractor
from src.text_preprocessing.coreferences_resolution import Coreferences, Entity
"""
Use this script to test the EntitiesExtractor class of raw text 
"""
book_name = 'hp1'
if __name__ == "__main__":
	print("TEST ENTITIES EXTRACTOR ON RAW TEXT")
	entities_extractor = EntitiesExtractor(path_to_bert_ner="models/bert_ner_base/")

	# text = "Miss Lucas, Sir Alex Duval and Master Luc help Lady Lucas to build an algorithm. Dr Lucas is awake."
	text = " "
	output_list = entities_extractor.from_text(text)
	print(text, " is processed to :", output_list)
	list_person_names = [entity['character_name'] for entity in output_list[0]]
	print(list_person_names)

	# Apply the coref
	coref = Coreferences(list_person_names, coref_rules_folder='data/coref_rules/')
	idx_to_entity = coref.resolve()

	# Analyse result on the first 100 characters name of the novel
	print("Number of character name occurence = ", len(list_person_names))
	print("Number of unique entities =", len(set(idx_to_entity.values())))

	person_to_entities = {list_person_names[i]: str(idx_to_entity[i]) for i in range(len(list_person_names))}
	print(person_to_entities)
