from nameparser import HumanName
from enum import Enum
from tqdm import tqdm


class Genre(Enum):
    FEMALE = 1
    MALE = 2
    UKN = 3


class Entity:
    """
    We define an entity as being a HumanName object + a genre
    """
    def __init__(self, human_name, genre=Genre.UKN):
        self.human_name = human_name
        self.genre = genre

    def __hash__(self):
        return hash((self.human_name.title, self.human_name.first, self.human_name.last, self.genre))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        return str(self.human_name)


class Coreferences:
    """
    Given a list of person name, the Coreferences class will iteratively generate a list of entities
    so that each HumanName is bind to one unique entity
    """

    def __init__(self, person_name_list, coref_rules_folder='data/coref_rules/'):
        """
        :param person_name_list: list[str] list of person name find in the book
        :param coref_rules_folder: path to folder containing list of different possible name/title for male/female
        """
        self.person_name_list = person_name_list
        self.entity_set = set()
        self.entities_match = dict()

        self.male_names = self.load_genre_rules(coref_rules_folder+'male_name.txt')
        self.female_names = self.load_genre_rules(coref_rules_folder+'female_name.txt')
        self.male_titles = self.load_genre_rules(coref_rules_folder+'male_title.txt')
        self.female_titles = self.load_genre_rules(coref_rules_folder+'female_title.txt')
        self.neutral_titles = self.load_genre_rules(coref_rules_folder + 'neutral_titles.txt')
        self.nicknames = self.load_nicknames(coref_rules_folder + 'nicknames.txt')

    @staticmethod
    def load_genre_rules(path_file):
        """
        Load in memory the genre rules defined in the text file
        """
        with open(path_file, 'r') as f:
            list_of_rules = f.read().splitlines()
        return [rule.lower() for rule in list_of_rules]

    @staticmethod
    def load_nicknames(path_file):
        """
        Load nicknames and related names in a dictionary (key:nicknames, value: list of name)
        """
        with open(path_file, 'r') as f:
            matched_nicknames = {}
            for line in f:
                name = line.strip().split(',')
                matched_nicknames[name[0]] = name[1:]
        return matched_nicknames

    @staticmethod
    def name_preprocessing(character_name):
        """
        Each character name is :
        1/ lower
        2/ parsed with HumanName parser
        3/ we remove 's from first or last name
        For step 3 : if we consider "Jade's bag"
            sometime BERT_ner will return Jade <B-PEr>, 's <I-PER> ... so the result character name will be Jade's
        :param character_name: str
        :return: HumanName object
        """
        return HumanName(character_name.lower())

    def genre_of(self, human_name):
        """
        Try to assess the genre of a HumanName object based on its first name or its title
        :param human_name: [HumanName]
        :return: [Genre]
        """
        if human_name.title in self.male_titles:
            return Genre.MALE
        if human_name.title in self.female_titles:
            return Genre.FEMALE
        # elif human_name.title in self.male_names and self.female_names:
        #     return Genre.UKN
        if human_name.first in self.female_names:
            return Genre.FEMALE
        if human_name.first in self.male_names:
            return Genre.MALE

        return Genre.UKN

    def entity_frequency(self, entity):
        """
        Compute the number of human_name that are associated to a particular entity
        :param entity: Entity
        :return: int
        """
        return list(self.entities_match.values()).count(entity)

    def most_frequent_entity(self, entity_list):
        """
        Given a list of entity, return the entity which the most frequently associated to human_name
        if the entity list is empty, return None
        :param entity_list: list[Entity]
        :return: Entity
        """
        entity_list = [(entity, self.entity_frequency(entity))
                       for entity in entity_list]
        if len(entity_list) == 0:
            return None
        else:
            return max(entity_list, key=lambda x:x[1])[0]

    def create_entity(self, idx, human_name):
        """
        Given a human_name and its index idx in the original person_name_list
        create a new entity
        :param idx: int
        :param human_name: HumanName
        """
        new_entity = Entity(human_name, self.genre_of(human_name))
        self.entity_set.add(new_entity)
        self.entities_match[idx] = new_entity

    def resolve(self, match_entity=None):
        """
        Associate each person name of self.person_name_list to an entity
        :return: dict idx_of_person_name -> entity,
        list of indexes that have to be discarded because matched entity is None
        """

        # PRE-PROCESSING STEP :
        # each person name is parsed using human name parser
        # each time we succeed to associate a human_name to an entity, we will remove it from this list
        human_name_list = [(idx, self.name_preprocessing(person_name))
                                for idx, person_name in enumerate(self.person_name_list)]

        # some name will contain just a title. For instance 'Sir' alone. It will be detected as a character name
        # by BERT NER but we won't try to associate it with an entity.
        # by default, we will associate such terms with a unique "NONE" entity
        remaining_list = []
        empty_entity = Entity(HumanName("NONE"))
        for idx, human_name in human_name_list:
            if human_name.first == "" and human_name.last == "":
                self.entities_match[idx] = empty_entity
            else:
                remaining_list.append((idx, human_name))
            if human_name.first == "``":
                human_name.first = ""
                self.entities_match[idx] = human_name
        human_name_list = remaining_list

        # STEP 1 :
        # for each human_name that are complets ie: that contains a title, a first name and last name
        #    -> for instance: Miss Elizabeth Bennet
        # if there already exists an entity which has this first and last name: associate the human_name to this entity
        # else : create a new entity
        print("Co-ref step 1 : associate character name that have title, first name and last name to entity")
        remaining_list = []  # to store the human name we have not succeed to bind to an entity
        for idx, human_name in tqdm(human_name_list):
            if human_name.title != "" and human_name.first != "" and human_name.last != "":
                try:
                    match_entity = [entity for entity in self.entity_set
                                           if human_name.first == entity.human_name.first and
                                              human_name.last == entity.human_name.last][0]
                except IndexError:
                    match_entity = None

                if match_entity is None:
                    self.create_entity(idx, human_name)
                else:
                    self.entities_match[idx] = match_entity
            else:
                remaining_list.append((idx, human_name))
        human_name_list = remaining_list

        # STEP 2 :
        # for each remaining human_names that contain at least first name and last name
        #   -> for instance : Elizabeth Bennet
        # if there already exists an entity which has this first and last name: associate the human_name to this entity
        # else : create a new entity
        print("Co-ref step 2 : associate character name that have just first name and last name to entity")
        remaining_list = []
        for idx, human_name in tqdm(human_name_list):
            if human_name.first != "" and human_name.last != "":
                try:
                    match_entity = [entity for entity in self.entity_set
                                           if human_name.first == entity.human_name.first and
                                              human_name.last == entity.human_name.last][0]
                except IndexError:
                    match_entity = None

                if match_entity is None:
                    self.create_entity(idx, human_name)
                else:
                    self.entities_match[idx] = match_entity
            else:
                remaining_list.append((idx, human_name))
        human_name_list = remaining_list


        # STEP 3 :
        # for each remaining human_names that contain a title and first name
        #   -> for instance : Miss Bennet
        # if there already exists entities which contains this first name and has the same genre (ie: Elizabeth Bennet)
        #     associate the human_name to the most common entity among those entities
        # else : create a new entity
        print("Co-ref step 3 : associate character name that have just title and first name to entity")
        remaining_list = []
        for idx, human_name in tqdm(human_name_list):
            if human_name.title != "" and human_name.first != "":
                possible_entities = []
                for entity in self.entity_set:
                    if entity.human_name.first == human_name.first:
                        if self.genre_of(human_name) == Genre.UKN or entity.genre == Genre.UKN:
                            possible_entities.append(entity)
                        else:
                            if entity.genre == self.genre_of(human_name):
                                possible_entities.append(entity)

                match_entity = self.most_frequent_entity(possible_entities)
                if match_entity is None:
                    self.create_entity(idx, human_name)
                else:
                    self.entities_match[idx] = match_entity
            else:
                remaining_list.append((idx, human_name))
        human_name_list = remaining_list

        # STEP 4 :
        # for each remaining human_names that contain a title and last name
        #   -> for instance : Mrs. Bennet
        # if there already exists entities which contains this last name and has the same genre (ie: Elizabeth Bennet)
        #     associate the human_name to the most common entity among those entities
        # else : create a new entity
        print("Co-ref step 4 : associate character name that have just title and last name to entity")
        remaining_list = []
        for idx, human_name in tqdm(human_name_list):
            if human_name.title != "" and human_name.last != "":
                possible_entities = []
                for entity in self.entity_set:
                    if entity.human_name.last == human_name.last:
                        if self.genre_of(human_name) == Genre.UKN or entity.genre == Genre.UKN:
                            possible_entities.append(entity)
                        else:
                            if entity.genre == self.genre_of(human_name):
                                possible_entities.append(entity)
                match_entity = self.most_frequent_entity(possible_entities)

                if match_entity is None:
                    self.create_entity(idx, human_name)
                else:
                    self.entities_match[idx] = match_entity
            else:
                remaining_list.append((idx, human_name))
        human_name_list = remaining_list

        # STEP 5 :
        # At this step, the human_name_list only contain first name
        # Note that this first could also corresponding to last_name, indeed both Duval or Alexandre will be parsed as
        # HumanName(first='Duval') , HumanName(first='Alexandre') by the HumanParser
        #
        # so for each of this human_name we look in the list of entities for the most common entities which contain
        print("Co-ref step 5 : associate character name that have just first name or last name to entity")
        for idx, human_name in tqdm(human_name_list):
            if human_name.first == "":
                possible_entities = [entity for entity in self.entity_set
                                     if entity.human_name.last == human_name.last or
                                     entity.human_name.first == human_name.last]
            if human_name.last == "":
                possible_entities = [entity for entity in self.entity_set
                                     if entity.human_name.first == human_name.first or
                                     entity.human_name.last == human_name.first]

            match_entity = self.most_frequent_entity(possible_entities)
            if match_entity is None:
                self.create_entity(idx, human_name)
            else:
                self.entities_match[idx] = match_entity

        return self.entities_match

    @staticmethod
    def remove_none(idx_to_entity):
        """
        :param idx_to_entity: dictionary of occurrences matched to entities
        :return: list of indexes where matched entity is None
        """
        l = []
        for index in range(len(idx_to_entity)):
            if str(idx_to_entity[index]) == 'NONE':
                l.append(index)
        return l

    def improved_matching(self, idx_to_entity):
        """
        :param idx_to_entity: dictionary of entity matching
        :return new dico, where first names being initials or nicknames have been pre-processed correctly,
        and a list of indexes where entity is None (to be discarded)
        """
        # Spot the occurrences when the first name is an initial
        # and the occurrences when first name is a nickname
        names_with_initial = {}
        names_as_nicknames = {}
        set_entities = set()
        for index in range(len(idx_to_entity)):
            parsed_name = HumanName(str(idx_to_entity[index])).as_dict()
            set_entities.add(idx_to_entity[index])
            if 0 < len(parsed_name['first']) < 4 and parsed_name['last'] != "" and "." in parsed_name['first']:
                names_with_initial[index] = parsed_name
            elif parsed_name['last'] == "" and parsed_name['first'].upper() in list(self.nicknames.keys()):
                names_as_nicknames[index] = parsed_name

        # Change entity matching for intials
        for key, name in names_with_initial.items():
            for entity in set_entities:
                entity_parsed = HumanName(str(entity)).as_dict()
                if name['last'] == entity_parsed['last'] and name['first'][0] == entity_parsed['first'][0] \
                        and name['first'] != entity_parsed['first']:
                    idx_to_entity[key] = entity  # most common

        # Change entity matching for nicknames
        for key, name in names_as_nicknames.items():
            for entity in set_entities:
                entity_parsed = HumanName(str(entity)).as_dict()
                if name['last'] == "" and name['first'].upper() in list(self.nicknames.keys()) and \
                        entity_parsed['first'].upper() in list(self.nicknames[name['first'].upper()]):
                    idx_to_entity[key] = entity
                elif name['last'] == "" and name['first'].upper() in list(self.nicknames.keys()) and \
                        name['first'] != entity_parsed['last'] and entity_parsed['title'] != "" and \
                        entity_parsed['last'].upper() in list(self.nicknames[name['first'].upper()]):
                    idx_to_entity[key] = entity

        # Remove 'NONE' entities
        l = self.remove_none(idx_to_entity)

        return idx_to_entity, l
