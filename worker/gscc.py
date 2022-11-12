from pyzotero import zotero
import requests
import re
import pause
import random
from datetime import datetime, timedelta
from croniter import croniter
from const import MsgStage


def _generate_query_url(item: dict) -> str:
    """
    Generate a query URL for a given item
    """
    title = item['data']['title']
    info = f"Item: {title}\n"
    query = title.replace(' ', '+')
    url = f'https://scholar.google.com/scholar?hl=en&as_q={query}&as_occt=title&num=1'
    # Filter by author
    if 'creators' in item['data']:
        creators = item['data']['creators']
        if creators:
            creator = creators[0]
            creator_name = creator['lastName'] if 'lastName' in creator else creator['name']
            info += f"Autor: {creator_name}\n"
            query = creator_name.replace(' ', '+')
            url += f'&as_sauthors={query}'
    # Filter by year
    year = re.search(r'\d{4}', item['data']['date'])  # Extract year from date
    if year:
        # url += f'&as_ylo={year.group(0)}&as_yhi={year.group(0)}'
        info += f"Search range: Since {year.group(0)}\n"
        url += f'&as_yhi={year.group(0)}'
    return url, info


class GSCC:
    def __init__(self, zotero_cfg: dict, update_cfg: dict, recaptcha: ReCaptcha, webhook: Webhook):
        # Zotero
        self._z = zotero.Zotero(
            zotero_cfg["library_id"],
            zotero_cfg["library_type"],
            zotero_cfg["api_key"],
        )
        # 2Captcha
        self._recaptcha = recaptcha
        # Update schedule
        self._epoch_cron_format = update_cfg["epoch_cycle"]
        self._item_interval_sec = (
            update_cfg["item_interval_seconds"]["min"],
            update_cfg["item_interval_seconds"]["max"],
        )
        if self._item_interval_sec[0] > self._item_interval_sec[1]:
            raise ValueError("min_sec must be smaller than max_sec")
        # Webhook
        self._webhook = webhook

    @property
    def num_items(self):
        return self._z.num_items()

    @property
    def estimated_fetch_hours(self) -> float:
        sec = self.num_items * (self._item_interval_sec[0] + self._item_interval_sec[1]) / 2.0
        return sec / 3600.0

    def run(self):
        while True:
            # Start message
            estimated_hours = self.estimated_fetch_hours
            estimated_date = datetime.now() + timedelta(hours=estimated_hours)
            info = f"🚀 Starting GSCC worker.\n"
            info += f"📚 {self.num_items} items to fetch. ({estimated_hours:0.1f} hours estimated)\n"
            info += f"🕒 Estimated completion time: {estimated_date.strftime('%Y-%m-%d %H:%M')}"
            self._webhook.send(MsgStage.EPOCH_START, info)

            # Fetch all GSCC
            log = {
                "success": {
                    "updated": 0,
                    "unchanged": 0,
                    "no_match": 0,
                },
                "captcha": {
                    "solved": 0,
                    "failed": 0,
                },
                "error": 0,  # Exclued Zotero server maintenance alerts
            }
            self.fetch_all(log)

            # Finish message
            summary_msg = f"🎉 Finished GSCC worker.\n"

            num_updated = log["success"]["updated"]
            num_unchanged = log["success"]["unchanged"]
            num_no_match = log["success"]["no_match"]
            num_captcha_solved = log["captcha"]["solved"]
            num_captcha_failed = log["captcha"]["failed"]
            num_error = log["error"]
            summary_msg += f"📚 {self.num_items} items processed. (Updated: {num_updated}, Unchanged: {num_unchanged}, No match: {num_no_match})\n"
            summary_msg += f"🔐 {num_captcha_solved} CAPTCHAs solved. ({num_captcha_failed} failed)\n"
            summary_msg += f"⚠️ {num_error} errors."

            now_dt = datetime.now()
            cron = croniter(self._epoch_cron_format, now_dt)
            next_dt = cron.get_next(datetime)
            summary_msg += f"🕒 Next update will be at {next_dt.strftime('%Y-%m-%d %H:%M')}."

            # Pause until next update
            self._webhook.send(MsgStage.EPOCH_END, summary_msg)
            pause.until(time=next_dt)

    def fetch_all(self, log: dict):
        """
        Retrieve all top-level items in small batch sizes
        Large batch sizes are too heavy for the Zotero API.
        """
        batch_size = 10
        start = 0
        count = 0
        while True:
            items = self._z.top(start=start, limit=batch_size)
            if not items:
                break
            for item in items:
                self.fetch_item(item, log)
                # Interval sleep
                sleep_sec = random.uniform(*self._item_interval_sec)
                count += 1
                self._webhook.send(MsgStage.INTERVAL_SLEEP, f"💤 Sleeping for {sleep_sec:0.1f} seconds after {count} items.")
                pause.seconds(sleep_sec)
            start += batch_size

    def fetch_item(self, item: dict, log: dict):
        """
        Fetch GSCC for a given item
        """
        # Get the query URL
        query_url, query_info = _generate_query_url(item)
        # Fetch the query URL
        response = requests.get(query_url)

        # Abnormal response
        if response.status_code != 200:
            log["error"] += 1
            self._webhook.send(MsgStage.ERROR, f"🚨 Error:{response.text}\nQuery:\n{query_info}")
            return

        # Check if the response is a captcha
        if re.search(r'g-recaptcha', response.text):
            # Solve the captcha
            try:
                is_solved = self._recaptcha.solve(response, query_url)
            except Exception as e:
                log["error"] += 1
                self._webhook.send(MsgStage.ERROR, f"🚨 Error: {e}\nQuery:\n{query_info}")
                return
            # Fetch the query URL again
            if is_solved:
                log["captcha"]["solved"] += 1
                response = requests.get(query_url)
            else:
                log["captcha"]["failed"] += 1
                log["error"] += 1
                self._webhook.send(MsgStage.ERROR, f"🤖 Failed to solve captcha for {item['data']['title']}")
                return

        # If no match, skip
        if re.search(r'did not match', response.text):
            log["success"]["no_match"] += 1
            self._webhook.send(MsgStage.ITEM_NO_MATCH, f"💭 No match for\n{query_info}")
            return

        # Extract the GSCC
        citation_count = re.search(r'Cited by (\d+)', response.text)
        citation_count = int(citation_count.group(1).replace('Cited by ', '')) if citation_count else 0

        # Check 'GSCC' keyword in extra field (GSCC: 0000003)
        extra = item['data']['extra']
        old_count_re = re.search(r'GSCC: (\d+)', extra)
        old_count = 0
        if old_count_re:
            old_count = int(old_count_re.group(1).replace('GSCC: ', ''))
            if old_count == citation_count:
                log["success"]["unchanged"] += 1
                self._webhook.send(MsgStage.ITEM_SUCCESS_WITHOUT_CHANGE, f"✅ Unchanged for\n{query_info}")
                return
            # Update the citation count
            new_extra = re.sub(r'GSCC: (\d+)', f'GSCC: {citation_count:07d}', extra)
        else:
            # Add the citation count
            new_extra = f'GSCC: {citation_count:07d}\n{extra}'

        # Update the item
        item['data']['extra'] = new_extra
        is_updated = False
        while not is_updated:
            try:
                is_updated = self._z.update_item(item)
            except Exception as e:
                if re.search(r'undergoing scheduled maintenance', str(e)):
                    hours = 1.0
                    self._webhook.send(MsgStage.ERROR, f"⏳ Zotero API is undergoing scheduled maintenance. Try after {hours:0.1f} hours.")
                    pause.hours(hours)
                else:
                    log["error"] += 1
                    self._webhook.send(MsgStage.ERROR, f"🚨 Failed to update Zotero. Error: {e=}\n{query_info}")
                    return
            if is_updated:
                log["success"]["updated"] += 1
                self._webhook.send(MsgStage.ITEM_SUCCESS_WITH_CHANGE, f"✅ (GSCC: {old_count:07d} → {citation_count:07d}) updated.\n{query_info}")
