
<!-- TODO: readthedocs.org -->

Example `secret_cfg.yml`:

```yaml
# Zotero API
zotero:
  library_type: YOUR_ZOTERO_LIB_TYPE  # "user" or "group"
  library_id: YOUR_ZOTERO_LIB_ID
  api_key: YOUR_ZOTERO_API_KEY

# 2Captcha (https://github.com/2captcha/2captcha-python)
captcha:
  server: "2captcha.com"
  apiKey: YOUR_2CAPTCHA_API_KEY
  recaptchaTimeout: 600
  pollingInterval: 10

# Update Config
update:
  epoch_cycle: "0 0 1 * *"  # Cron expression of “At 00:00 on day-of-month 1.”
  item_interval_seconds:
    min: 30
    max: 80

# =============== OPTIONAL ===============
# You can comment out the following section if you don't want to use it.
# The default settings are 'false' for all the following settings.

webhook:
  style: YOUR_WEBHOOK_TARGET  # "discord", "slack", "jandi"
  url: YOUR_WEBHOOK_URL
  do_not_disturb:
    enabled: false
    start: "23:00"  # 24-hour format
    end: "08:00"  # 24-hour format
  messages:
    dnd_start: false
    dnd_end: false
    epoch_start: false
    epoch_end: false
    interval_sleep: false
    item_success_with_change: false
    item_success_without_change: false
    item_no_match: false
    error: false
```

- userID
  - You can find your personal `userID` [here](https://www.zotero.org/settings/keys), in the text `Your userID for use in API calls <userID>`
- API key
  - You need to create a private key [here](https://www.zotero.org/settings/keys/new).
  - Please, enable `Allow library access` and `Allow write access`.
  - You can manage your keys [here](https://www.zotero.org/settings/keys).
- Webhook URL
- Webhook Style
  - Currently, supported styles are [Discord](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks), [Slack](https://api.slack.com/messaging/webhooks), and [Jandi](https://support.jandi.com/en/articles/6352697-receiving-incoming-webhooks-in-jandi).
- `min_sleep_sec` and `max_sleep_sec`
  - GSCC-Worker will sleep for a random number of seconds between `min_sleep_sec` and `max_sleep_sec` before requesting the next query to Google Scholar.
  - To avoid getting blocked, set `min_sleep_sec` to a high value.
- `day_cycle`
  - You can specify how frequently GSCC-Worker should fetch items. For example, if your `day_cycle` is 7, the worker will refresh your Zotero once a week.
  - If certain jobs are left until the next cycle begins, the following procedure starts immediately after the current cycle. And the worker updates the cycle's reference time to the new start time.

- `dnd_end`: It will send a summary of the events that occurred during DND mode.

- `update`
  - `epoch_cycle`
    - [cron expression](https://en.wikipedia.org/wiki/Cron)을 사용.
    - [https://crontab.guru/](https://crontab.guru/) 추천