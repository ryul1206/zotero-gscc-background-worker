# Zotero GSCC Background Worker

[![Docker Image Version](https://img.shields.io/docker/v/junghr1206/zotero-gscc-worker?style=flat-square&color=orange)](https://hub.docker.com/repository/docker/junghr1206/zotero-gscc-worker)

Docker container that fetches the number of citations from Google Scholar periodically.

If you want to update the citation count directly, not in the background, I recommend [Justin Ribeiro's Zotero extension](https://github.com/justinribeiro/zotero-google-scholar-citation-count).
This background worker is compatible with his extension in most cases.

## Prerequisite

- [Zotero Library](https://www.zotero.org/): user library or group library
- [2Captcha Account](https://2captcha.com/): A $1 balance is enough for several months.

## Quickstart

1. Prepare `secret_cfg.yml` >> [see here](https://github.com/ryul1206/zotero-gscc-background-worker/blob/main/explain_cfg.md)
3. Get the docker image of GSCC-Worker

    ```sh
    docker pull junghr1206/zotero-gscc-worker
    ```

4. Connect your `secret_cfg.yml` read-only to `/root/secret_cfg.yml` using a docker volume and run the worker container.

    ```sh
    docker run -d -e TZ=Asia/Seoul -v ${PWD}/secret_cfg.yml:/root/secret_cfg.yml:ro --name zotero-gscc-worker zotero-gscc-worker
    ```

## Build from Source

- Build docker image: `docker build -t zotero-gscc-worker:local .`

## References

- [tete1030/zotero-scholar-citations](https://github.com/tete1030/zotero-scholar-citations)
- [justinribeiro/zotero-google-scholar-citation-count](https://github.com/justinribeiro/zotero-google-scholar-citation-count)
