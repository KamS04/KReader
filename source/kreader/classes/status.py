from ..utils.defaulting import DefaultingDict

UNKNOWN = 0
ONGOING = 1
COMPLETED = 2
HIATUS = 3
ABANDONED = 4

_STATUS_MAP = {
    UNKNOWN: 'UnKnown',
    ONGOING: 'OnGoing',
    COMPLETED: 'Completed',
    HIATUS: 'Hiatus',
    ABANDONED: 'Abandoned'
}

STATUS_MAP = DefaultingDict(UNKNOWN, _STATUS_MAP)
