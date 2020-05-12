from enum import Enum

class NodeType(Enum):
    OCCURENCE = 1
    ENTITY = 2
    CHAPTER = 3

    def __str__(self):
        if self == NodeType.OCCURENCE:
            return "occurence_node"

        if self == NodeType.ENTITY:
            return "entity_node"

        if self == NodeType.CHAPTER:
            return "chapter_node "

