from enum import StrEnum, auto


class JudgementType(StrEnum):
    CANTONESE = auto()
    SWC = auto()
    NEUTRAL = auto()
    MIXED = auto()
    CANTONESE_QUOTES_IN_SWC = auto()
    MIXED_QUOTES_IN_SWC = auto()
