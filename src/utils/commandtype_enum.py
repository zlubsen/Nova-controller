from enum import Enum

class CommandType(Enum):
    NOVA = 1 # commands that relate to things originating on Nova
    INPUT = 2 # commands that relate to things originating at the controller or web interface
