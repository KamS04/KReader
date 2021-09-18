from source.viewer.sources.online.mangadex.maps import LANGUAGE_MAP
from ..utils.defaulting import DefaultingDict

UNKNOWN = 0
ENGLISH = 1

_LANGUAGE_MAP = {
    UNKNOWN: 'Unknown',
    ENGLISH: 'English'
}

LanguageMap = DefaultingDict('Unknown', _LANGUAGE_MAP)