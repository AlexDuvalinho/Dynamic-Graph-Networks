from enum import Enum

class EdgeType(Enum):
    TIME = 1
    IS_ENTITY = 2
    BELONG_TO = 3
    INTERACT_WITH = 4

    def __str__(self):
        if self == EdgeType.TIME:
            return "time_edge"

        if self == EdgeType.IS_ENTITY:
            return "is_entity_edge"

        if self == EdgeType.BELONG_TO:
            return "belong_to_edge"

        if self == EdgeType.INTERACT_WITH:
            return "interact_with"
