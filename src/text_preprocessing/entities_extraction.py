from src.third_party.bert_ner.bert import Ner
import os
import re
from tqdm import tqdm

class EntitiesExtractor:
    """
    Class EntitiesExtractor is used to extract all the NER-PER from a novel.
    The novel can be given in two forms :
        1- raw text, then use raw_test method
        2- a path to folder containing a set of chapter. Each chapter being a raw text file
        and the name of a file being the index of the chapter

    From the novel, EntitiesExtractor will output a list of dict:
        [{character_name:[str], position:[int], chapter[int]}]
    By default, if there is no information on the chapters (case 1 above) the chapter value will be -1
    """
    def __init__(self, path_to_bert_ner):
        """
        :param path_to_bert_ner: path to the bert ner model
        """
        self.bert_ner = Ner(path_to_bert_ner)

    @staticmethod
    def split_text(string, batch_size=256):
        """
        1/ the string is tokenize using space as separator
        2/ the token_list is split in batch of batch_size
        3/ from the batches, a generator of substring is generated
        :param string: input_string
        :param batch_size: int
        :return: a generator of substring of size batch_size (batch_size = nb of tokens in the substring)
        """
        token_list = string.split(" ")

        for i in range(len(string) // batch_size):
            yield " ".join(token_list[i * batch_size: (i + 1) * batch_size])

        if len(string) % batch_size != 0:
            yield " ".join(token_list[(len(token_list) // batch_size) * batch_size:])

    def from_text(self, text, initial_position=0, chapter=-1):
        """
        From a text from a given chapter, return a list of dict(character_name, position, chapter)
        :param text: string
        :param initial_position: int, the index of first word in the global novel
        :param chapter: int, the index of the current chapter
        :return: list [dict(character_name, position, chapter)]
        """

        # Apply BERT-NER on each substring
        token_list = []
        bar_text = "Process of chapter " + str(chapter) if chapter != -1 \
                   else "Process of text"
        for subtext in tqdm(list(EntitiesExtractor.split_text(text, batch_size=200)),
                            desc=bar_text):
            token_list += self.bert_ner.predict(subtext)

        # Select only the PER entities + merge B-PER with I-PER
        output_list = []
        i = 0
        while i < len(token_list):
            if token_list[i]['tag'] != 'B-PER':
                i += 1
            else:
                position = initial_position + i
                character_name = token_list[i]['word']
                i += 1
                while i < len(token_list) and token_list[i]['tag'] == 'I-PER':
                    if token_list[i]['word'] != "'s":
                        # Because we noticed that sometime BERT_NER will parsed name's as name <B-PER>, 's <I-PER>
                        character_name += ' ' + token_list[i]['word']
                    i += 1
                output_list.append({'character_name':character_name,
                                    'position':position,
                                    'chapter': chapter})
        return output_list, i

    def from_chapter_folder(self, folder_path):
        """
        :param folder_path: path to folder which contain a set of raw text chapter
        :return: list [dict(character_name, position, chapter)]
        """

        def extract_chapter_number(string):
            return int(re.search('([0-9]+)\.txt', string).group(1))

        def sort_by_chapter(file_list):
            return sorted(file_list, key=extract_chapter_number, reverse=False)

        chapter_list = sort_by_chapter(os.listdir(folder_path))
        print("Number of chapter to process: ", len(chapter_list))

        novel_NER_list = []
        initial_position = 0
        for idx, chapter in tqdm(list(enumerate(chapter_list)), desc='Advance progression'):
            with open(folder_path + chapter) as f:
                text = f.read()
                chapter_NER_list, nb_of_tokens = self.from_text(text,
                                                                initial_position,
                                                                chapter=idx)
                initial_position += nb_of_tokens
                novel_NER_list += chapter_NER_list

        return novel_NER_list

