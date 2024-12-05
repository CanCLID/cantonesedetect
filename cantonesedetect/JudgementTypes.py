from enum import Enum

class JudgementType(str, Enum):
    CANTONESE = "cantonese"
    SWC = "swc"
    NEUTRAL = "neutral"
    MIXED = "mixed"
    CANTONESE_QUOTES_IN_SWC = "cantonese_quotes_in_swc"
    MIXED_QUOTES_IN_SWC = "mixed_quotes_in_swc"

    def __str__(self) -> str:
        return self.value