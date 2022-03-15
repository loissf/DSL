from enum import Enum
from dataclasses import dataclass

class EventType(Enum):

    MESSAGE         = 0
    LOGIN           = 1
    SCHEDULE        = 2

@dataclass
class Event():
    type: EventType
    value: any = None
    # other event related info

    def __repr__(self):
        return f'{self.type.name} EVENT'
