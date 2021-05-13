from ....classes import status, languages, map

_STATUS_MAP = {
    'ongoing': status.ONGOING,
    'hiatus': status.HIATUS,
    'completed': status.COMPLETED,
    'abandoned': status.ABANDONED
}

_LANGUAGE_MAP = {
    'en': languages.ENGLISH
}

LANGUAGE_MAP = map.DefaultingMap(_LANGUAGE_MAP, languages.UNKNOWN)

STATUS_MAP = map.DefaultingMap(_STATUS_MAP, status.UNKNOWN)