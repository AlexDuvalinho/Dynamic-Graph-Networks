from src.text_preprocessing.entities_extraction import EntitiesExtractor

"""
Use this script to test the EntitiesExtractor class of raw text 
"""
if __name__ == "__main__":
	print("TEST ENTITIES EXTRACTOR ON RAW TEXT")
	entities_extractor = EntitiesExtractor(path_to_bert_ner="models/bert_ner_base/")
	text = "Gael de Léséleuc knowns Alexandre Duval"
	output_list = entities_extractor.from_text(text)
	print(text, " is processed to :", output_list)
