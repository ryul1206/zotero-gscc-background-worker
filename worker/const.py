from enum import Enum, auto


class MsgStage(Enum):
    """Message stage"""
    DND_START = auto()
    DND_END = auto()
    EPOCH_START = auto()
    EPOCH_END = auto()
    ITEM_SUCCESS_WITH_CHANGE = auto()
    ITEM_SUCCESS_WITHOUT_CHANGE = auto()
    ITEM_NO_MATCH = auto()
    INTERVAL_SLEEP = auto()
    ERROR = auto()


def msgstage_from_str(msg_stage_str: str) -> MsgStage:
    return MsgStage.__members__[msg_stage_str.upper()]


def msgstage_list() -> list:
    return MsgStage.__members__.values()
