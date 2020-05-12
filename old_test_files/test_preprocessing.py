from src.third_party.chapterize import Book
from src.text_preprocessing.entities_extraction import EntitiesExtractor
from src.text_preprocessing.coreferences_resolution import Coreferences

import shutil
import os
import pickle

"""
Use this script to test the preprocessing step on the book 1984 from Orwell and on Price-Prejudice book 
This book must be download from gutemberg library and stored in the folder data/raw_text
"""

def preprocess(book_name):
    """
    1/ Chapterize the book
    2/ Apply NER
    3/ Apply COREF
    4/ Print first hundred name -> entity
    :param book_name: str of the book, must be present as txt file in data/raw/text
    """
    # STEP 1 : Split the book in chapter by using chapterize
    if not os.path.exists('data/book_by_chapter/'+ book_name):
        book = Book(filename='data/raw_text/'+ book_name +'.txt', nochapters=False, stats=False)
        # this will create a new folder named 'book_name-chapter', containing all the chapter in the current folder
        # so we move this folder in data/book_by_chapter
        os.rename(book_name+'-chapters', book_name)
        shutil.move(book_name, '../data/book_by_chapter/')

    # STEP 2 : Apply NER on each chapter
    if not os.path.exists('data/entity_list/' + book_name + '.pkl'):
        entities_extractor = EntitiesExtractor(path_to_bert_ner='models/bert_ner_large/')
        NER_list = entities_extractor.from_chapter_folder(folder_path='data/book_by_chapter/'+book_name+'/')
        pickle.dump(NER_list, open('data/entity_list/'+book_name+'.pkl', 'wb'))

    # STEP 3 : Associate an entity to each character name
    NER_list = pickle.load(open('data/entity_list/'+book_name+'.pkl', 'rb'))
    character_name_list = [occurence['character_name'] for occurence in NER_list]
    coref = Coreferences(character_name_list, coref_rules_folder='data/coref_rules/')
    idx_to_entity = coref.resolve()

    print("Number of character name occurence = ", len(character_name_list))
    print("Number of unique entities =", len(set(idx_to_entity.values())))

    for i in range(500,700):
        print(character_name_list[i], '->', idx_to_entity[i])


if __name__ == '__main__':
    # preprocess('hp1')
    # preprocess('1984')
    preprocess('price-prejudice')
