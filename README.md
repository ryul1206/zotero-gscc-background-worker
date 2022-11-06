# zotero-gscc-background-worker

Docker container that fetches the number of citations from Google Scholar periodically.

If you want to update the citation count directly, not in the background, I recommend [Justin Ribeiro's Zotero extension](https://github.com/justinribeiro/zotero-google-scholar-citation-count).
This background worker is compatible with his extension in most cases.

## Quickstart



- userID
  - You can find your personal `userID` [here](https://www.zotero.org/settings/keys), in the text `Your userID for use in API calls <userID>`
- API key
  - You need to create a private key [here](https://www.zotero.org/settings/keys/new).
  - Please, enable `Allow library access` and `Allow write access`.
  - You can manage your keys [here](https://www.zotero.org/settings/keys).



## References

- [tete1030/zotero-scholar-citations](https://github.com/tete1030/zotero-scholar-citations)
- [justinribeiro/zotero-google-scholar-citation-count](https://github.com/justinribeiro/zotero-google-scholar-citation-count)
