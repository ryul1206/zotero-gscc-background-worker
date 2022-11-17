from enum import Enum, auto


class MsgStage(Enum):
    """Message stage"""
    EPOCH_START = auto()
    EPOCH_END = auto()
    INTERVAL_SLEEP = auto()
    ITEM_SUCCESS_GSCC_INCREASE = auto()
    ITEM_SUCCESS_GSCC_DECREASE = auto()
    ITEM_SUCCESS_WITHOUT_CHANGE = auto()
    ITEM_NO_MATCH = auto()
    RECAPTCHA_SUCCESS = auto()
    ERROR = auto()


def msgstage_from_str(msg_stage_str: str) -> MsgStage:
    stage = msg_stage_str.upper()
    if stage in MsgStage.__members__:
        return MsgStage.__members__[stage]
    else:
        raise ValueError(f"Unknown message option: {msg_stage_str}")


def msgstage_list() -> list:
    return MsgStage.__members__.values()
