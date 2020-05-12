# Import files
from src.third_party.chapterize import Book
from src.text_preprocessing.entities_extraction import EntitiesExtractor
from src.text_preprocessing.coreferences_resolution import Coreferences

# Import libraries
import shutil
import os
import pickle


def text_preprocessing(book_name, reprocess=False, bert_large=False):
    """
    Apply end-to-end text preprocessing from raw text to occurence list as detailled below :
    1/ Chapterize the book
    2/ Apply NER
    3/ Apply COREF
    4/ Create the final occurence list which is a list of dict :
        {character_name -> [str] name of the character detected by BERT NER
         position -> [int] position of the occurence in the text (nb of bert-tokens since text beginning
         chapter -> [int] chapter corresponding to the positon
         entity -> [str] name of the entity that have been link to by CO-REF module}
    5/ Dump the occurence list using pickle in data/entity_list/book_name.pkl

    If the preprocess has always been done, don't do anything unless reprocess = True

    :param book_name: str of the book, must be present as txt file in data/raw/text
    :param reprocess: boolean, use True to force the re-preprocessing of a book
    :param bert_large: True to use bert_large, by default bert_base
    """
    # STEP 1 : Split the book in chapter by using chapterize
    if not os.path.exists('data/book_by_chapter/' + book_name) or reprocess:
        print("-- SPLIT BOOK BY CHAPTER --")
        book = Book(filename='data/raw_text/' + book_name + '.txt', nochapters=False, stats=False)
        # this will create a new folder named 'book_name-chapter', containing all the chapter in the current folder
        # so we move this folder in data/book_by_chapter
        os.rename(book_name + '-chapters', book_name)
        shutil.move(book_name, 'data/book_by_chapter/')
    else:
        print("-- LOAD CHAPTER FROM CACHE --")

    # STEP 2 : Apply NER on each chapter
    if not os.path.exists('data/entity_list/' + book_name + '.pkl') or reprocess:
        print("-- APPLY BERT-NER ON EACH CHAPTER --")
        if bert_large:
            entities_extractor = EntitiesExtractor(path_to_bert_ner='models/bert_ner_large/')
        else:
            entities_extractor = EntitiesExtractor(path_to_bert_ner='models/bert_ner_base/')

        NER_list = entities_extractor.from_chapter_folder(folder_path='data/book_by_chapter/' + book_name + '/')
        pickle.dump(NER_list, open('data/entity_list/' + book_name + '.pkl', 'wb'))
    else:
        print("-- LOAD CHARACTER NAMES FROM CACHE --")

    # STEP 3 : Associate an entity to each character name
    # if not os.path.exists('data/entity_list/'+book_name+'.pkl'):
    if not os.path.exists('data/entity_list/' + book_name + '_occ_list.pkl') or reprocess:
        print("-- APPLY CO-REF RULES TO GENERATE ENTITIES")
        NER_list = pickle.load(open('data/entity_list/' + book_name + '.pkl', 'rb'))
        character_name_list = [occurence['character_name'] for occurence in NER_list]
        coref = Coreferences(character_name_list, coref_rules_folder='data/coref_rules/')
        idx_to_entity = coref.resolve()
        idx_to_entity, l = coref.improved_matching(idx_to_entity)
        occurence_list = [{'character_name': NER_list[i]['character_name'],
                           'position': NER_list[i]['position'],
                           'chapter': NER_list[i]['chapter'],
                           'entity': str(idx_to_entity[i]).upper()}
                          for i in range(len(NER_list)) if i not in l]
        # Save final occurrence list
        pickle.dump(occurence_list, open('data/entity_list/' + book_name + '_occ_list.pkl', 'wb'))
    else:
        print("-- LOAD OCCURENCE LIST FROM CACHE --")

