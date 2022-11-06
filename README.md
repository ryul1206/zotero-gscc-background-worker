# Zotero GSCC Background Worker

![Docker Image Version](https://img.shields.io/docker/v/junghr1206/zotero-gscc-worker?style=flat-square&color=orange)

Docker container that fetches the number of citations from Google Scholar periodically.

If you want to update the citation count directly, not in the background, I recommend [Justin Ribeiro's Zotero extension](https://github.com/justinribeiro/zotero-google-scholar-citation-count).
This background worker is compatible with his extension in most cases.

## Quickstart

### 1. Prepare `secret_cfg.yml`

Example `secret_cfg.yml`:

```yaml
user_id: '1234567'
api_key: QWERTYUIOP1234567890asdf
webhook_url: https://discord.com/api/webhooks/1234123412341234123/asdfasdfasdfasdfasdf
webhook_style: 'discord'
min_sleep_sec: 40
max_sleep_sec: 80
day_cycle: 3
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

### 2. Get the docker image of GSCC-Worker

```sh
docker pull junghr1206/zotero-gscc-worker
```

### 3. Run a worker

```sh
docker run -v ${PWD}/secret_cfg.yml:/root/secret_cfg.yml:ro --name zotero-gscc-worker zotero-gscc-worker
```

## Build from Source

- Build docker image: `docker build -t zotero-gscc-worker:local .`

## References

- [tete1030/zotero-scholar-citations](https://github.com/tete1030/zotero-scholar-citations)
- [justinribeiro/zotero-google-scholar-citation-count](https://github.com/justinribeiro/zotero-google-scholar-citation-count)
