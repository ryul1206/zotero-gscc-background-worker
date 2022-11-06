import requests
import yaml


def _get_headers(webhook_style):
    style_book = {
        'slack' : {'Content-Type': 'application/json'},
        'discord' : {'Content-Type': 'application/json'},
        'jandi' : {
            'Accept': 'application/vnd.tosslab.jandi-v2+json',
            'Content-Type': 'application/json'},
    }
    try:
        return style_book[webhook_style]
    except KeyError:
        raise ValueError(f'Unknown webhook_style: {webhook_style}\nWebhook_style must be one of {list(style_book.keys())}')


def _get_data_key(webhook_style):
    style_book = {
        'slack' : 'text',
        'discord' : 'content',
        'jandi' : 'body',
    }
    try:
        return style_book[webhook_style]
    except KeyError:
        raise ValueError(f'Unknown webhook_style: {webhook_style}\nWebhook_style must be one of {list(style_book.keys())}')


class Webhook:
    def __init__(self, webhook_url, webhook_style):
        self.webhook_url = webhook_url

        style = webhook_style.lower()
        self.headers = _get_headers(style)
        self.data_key = _get_data_key(style)

    def send(self, msg_string):
        # data = {self.data_key: msg_string}
        # requests.post(self.webhook_url, headers=self.headers, json=data)
        print(f"Webhook: {msg_string}")
