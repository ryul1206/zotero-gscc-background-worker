import requests
from datetime import datetime
from const import MsgStage, msgstage_from_str, msgstage_list


def _get_form(webhook_style: str) -> tuple:
    # headers & data_key
    style_book = {
        "slack": ({"Content-Type": "application/json"}, "text"),
        "discord": ({"Content-Type": "application/json"}, "content"),
        "jandi": (
            {
                "Accept": "application/vnd.tosslab.jandi-v2+json",
                "Content-Type": "application/json",
            },
            "body",
        ),
    }
    if webhook_style not in style_book:
        raise ValueError(
            f"Unknown webhook_style: {webhook_style}\nWebhook_style must be one of {list(style_book.keys())}"
        )
    return style_book[webhook_style]


# DND: Do Not Disturb
class _DND:
    def __init__(self):
        self._is_enabled = False
        # 24-hour time
        self._start_h = 23
        self._start_m = 0
        self._end_h = 8
        self._end_m = 0

    def config_dnd_enabled(self, is_enabled: bool):
        self._is_enabled = is_enabled

    def config_dnd_start(self, start_h: int, start_m: int):
        self._start_h = start_h
        self._start_m = start_m

    def config_dnd_end(self, end_h: int, end_m: int):
        self._end_h = end_h
        self._end_m = end_m

    def okay_to_send(self, now: datetime) -> bool:
        # True if DND is disabled
        if not self._is_enabled:
            return True
        start = datetime(now.year, now.month, now.day, self._start_h, self._start_m)
        end = datetime(now.year, now.month, now.day, self._end_h, self._end_m)
        if end < start:
            return end <= now < start
        else:
            return (now < start) or (end <= now)


class Webhook:
    def __init__(self):
        self._webhook_url = None
        self._style = "discord"
        self._headers, self._data_key = _get_form(self._style)
        self._dnd = _DND()
        self._msg_enabled = dict.fromkeys(msgstage_list(), False)

    def config_all(self, webhook_cfg: dict):
        if "url" in webhook_cfg:
            self.config_url(webhook_cfg["url"])
        if "style" in webhook_cfg:
            self.config_style(webhook_cfg["style"].lower())
        if "do_not_disturb" in webhook_cfg:
            dnd_cfg = webhook_cfg["do_not_disturb"]
            if "enabled" in dnd_cfg:
                self.config_dnd_enabled(dnd_cfg["enabled"])
            if "start" in dnd_cfg:
                self.config_dnd_start(dnd_cfg["start"])
            if "end" in dnd_cfg:
                self.config_dnd_end(dnd_cfg["end"])
        if "messages" in webhook_cfg:
            self.config_messages(webhook_cfg["messages"])

    def config_url(self, url: str):
        self._webhook_url = url

    def config_style(self, target_style: str):
        target_style = target_style.lower()
        if target_style != self._style:
            self._headers, self._data_key = _get_form(target_style)
            self._style = target_style

    def config_dnd_enabled(self, enabled: bool):
        self._dnd.config_dnd_enabled(enabled)

    def config_dnd_start(self, start: str):
        self._dnd.config_dnd_start(*tuple(map(int, start.split(":"))))

    def config_dnd_end(self, end: str):
        self._dnd.config_dnd_end(*tuple(map(int, end.split(":"))))

    def config_messages(self, msg_cfg: dict):
        for msg_stage, value in msg_cfg.items():
            stage = msgstage_from_str(msg_stage)
            if stage not in self._msg_enabled:
                raise ValueError(f"Unknown message setting: {msg_stage}")
            if not isinstance(value, bool):
                raise ValueError(f"Message setting must be boolean: {msg_stage}")
            self._msg_enabled[stage] = value

    def send(self, stage: MsgStage, msg_string: str):
        if self._msg_enabled[stage] and self._dnd.okay_to_send(datetime.now()):
            data = {self._data_key: msg_string}
            requests.post(self._webhook_url, headers=self._headers, json=data)
