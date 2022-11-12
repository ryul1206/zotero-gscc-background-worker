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

    _from_str = {
        "dnd_start": MsgStage.DND_START,  # Not implemented
        "dnd_end": MsgStage.DND_END,  # Not implemented
        "epoch_start": MsgStage.EPOCH_START,
        "epoch_end": MsgStage.EPOCH_END,
        "item_success_with_change": MsgStage.ITEM_SUCCESS_WITH_CHANGE,
        "item_success_without_change": MsgStage.ITEM_SUCCESS_WITHOUT_CHANGE,
        "item_no_match": MsgStage.ITEM_NO_MATCH,
        "interval_sleep": MsgStage.INTERVAL_SLEEP,
        "error": MsgStage.ERROR,
    }

    @staticmethod
    def from_str(msg_stage_str: str) -> MsgStage:
        return MsgStage._from_str[msg_stage_str.lower()]

    @staticmethod
    def stages() -> list[MsgStage]:
        return list(MsgStage._from_str.values())
