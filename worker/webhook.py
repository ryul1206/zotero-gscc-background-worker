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

    def config_all(self, dnd_cfg: dict):
        if "enabled" in dnd_cfg:
            self._config_enabled(dnd_cfg["enabled"])
        if "start" in dnd_cfg:
            self._config_start(dnd_cfg["start"])
        if "end" in dnd_cfg:
            self._config_end(dnd_cfg["end"])

    def _config_enabled(self, is_enabled: bool):
        self._is_enabled = is_enabled

    def _config_start(self, start: str):
        self._start_h, self._start_m = tuple(map(int, start.split(":")))

    def _config_end(self, end: str):
        self._end_h, self._end_m = tuple(map(int, end.split(":")))

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
        self._balance_warning_enabled = False
        self._balance_warning_threshold = 1.0
        self._msg_enabled = dict.fromkeys(msgstage_list(), False)

    def config_all(self, webhook_cfg: dict):
        if "url" in webhook_cfg:
            self._config_url(webhook_cfg["url"])
        if "style" in webhook_cfg:
            self._config_style(webhook_cfg["style"].lower())
        if "do_not_disturb" in webhook_cfg:
            self._dnd.config_all(webhook_cfg["do_not_disturb"])
        if "2captcha_balance_warning" in webhook_cfg:
            self._config_balance_warning(webhook_cfg["2captcha_balance_warning"])
        if "messages" in webhook_cfg:
            self._config_messages(webhook_cfg["messages"])

    def _config_url(self, url: str):
        self._webhook_url = url

    def _config_style(self, target_style: str):
        target_style = target_style.lower()
        if target_style != self._style:
            self._headers, self._data_key = _get_form(target_style)
            self._style = target_style

    def _config_balance_warning(self, balance_warning_cfg: dict):
        if "enabled" in balance_warning_cfg:
            self._balance_warning_enabled = balance_warning_cfg["enabled"]
        if "threshold" in balance_warning_cfg:
            self._balance_warning_threshold = balance_warning_cfg["threshold"]

    def _config_messages(self, msg_cfg: dict):
        for msg_stage, value in msg_cfg.items():
            if not isinstance(value, bool):
                raise ValueError(f"Message setting must be boolean: {msg_stage}")
            self._msg_enabled[msgstage_from_str(msg_stage)] = value

    def try_send(self, stage: MsgStage, msg_string: str):
        if self._msg_enabled[stage] and self._dnd.okay_to_send(datetime.now()):
            self._send(msg_string)

    def try_balance_warning(self, balance: float):
        if self._balance_warning_enabled and balance < self._balance_warning_threshold:
            _msg = f"🆘 2Captcha balance is low: $ {balance:.2f}\n"
            _msg += "Please refill your balance as soon as possible.\n"
            _msg += "https://2captcha.com/enterpage#finances"
            self._send(_msg)

    def _send(self, msg_string: str):
        data = {self._data_key: msg_string}
        requests.post(self._webhook_url, headers=self._headers, json=data)