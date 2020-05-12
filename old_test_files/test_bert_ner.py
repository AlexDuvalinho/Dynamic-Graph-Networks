from src.third_party.bert_ner.bert import Ner
from src.text_preprocessing.entities_extraction import EntitiesExtractor

"""
Use this script to test that bert_ner works correctly 
"""

if __name__ == "__main__":
	print("TEST BERT NER")
	bert_ner = Ner("models/bert_ner_base/")
	input_txt = 'Lady Diana will help Miss Lucas to develop an algorithm'
	# with open('data/book_by_chapter/hp1/01.txt') as f:
	#	 text = f.read()
	output = bert_ner.predict(input_txt)
	print('input :', input_txt)
	print('ouput of BERT NER :', output)

