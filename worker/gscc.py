from pyzotero import zotero
import requests
import re
import pause
import random


class GSCC:
    def __init__(self, user_id, api_key):
        self._z = zotero.Zotero(user_id, 'user', api_key)
        self._max_sleep_sec = 80
        self._min_sleep_sec = 40

    def set_sleep_range(self, min_sec, max_sec):
        if min_sec > max_sec:
            raise ValueError(f'min_sec must be smaller than max_sec')
        self._min_sleep_sec = min_sec
        self._max_sleep_sec = max_sec

    def get_current_num_items(self):
        return self._z.num_items()

    def get_estimated_fetch_time(self):
        initial_count = self._z.num_items()
        estimated_hours = initial_count * (self._max_sleep_sec + self._min_sleep_sec) / 2 / 3600
        return estimated_hours

    def fetch_all(self, webhook):
        """
        Retrieve all top-level items
        However, requesting all the items at once is too heavy,
        so we request them one by one.
        """
        initial_count = self._z.num_items()
        n = 0
        while n < initial_count:
            items = self._z.top(start=n, limit=1)
            if items:
                self._update_item(items[0], webhook)
            n += 1
            # Pause for a random time
            sec =random.randint(self._min_sleep_sec, self._max_sleep_sec)
            print(f'Pausing for {sec} seconds')
            pause.seconds(sec)

    def _update_item(self, item, webhook):
        """
        Update a given item
        """
        # Fetch the query URL
        query_url = self._generate_query_url(item)
        print(f'Updating [{item["data"]["title"]}] with \n\t{query_url}')
        resp = requests.get(query_url)

        # Error handling
        if resp.status_code != 200:
            webhook.send(f"Item: {item['data']['title']}\nError: {resp.status_code}")
            return  # Abnormal response
        if re.search(r'google.com/recaptcha/api.js', resp.text):
            webhook.send(f"Item: {item['data']['title']}\nError: reCaptcha")
            raise Exception('reCaptcha')

        # Extract citation count
        if re.search(r'did not match', resp.text):
            print("No match")
            return  # No search result
        citation_count = re.search(r'Cited by (\d+)', resp.text)
        citation_count = int(citation_count.group(1).replace('Cited by ', '')) if citation_count else 0

        # Check 'GSCC' keyword in extra field (GSCC: 0000003)
        extra = item['data']['extra']
        old_count = re.search(r'GSCC: (\d+)', extra)
        if old_count:
            old_count = int(old_count.group(1).replace('GSCC: ', ''))
            if old_count == citation_count:
                print(f'No change: {old_count}')
                return  # No update
            # Replace the old citation count
            new_extra = re.sub(r'GSCC: (\d+)', f'GSCC: {citation_count:07d}', extra)
        else:
            # Append the citation count
            new_extra = f'GSCC: {citation_count:07d}\n{extra}'

        # Update item
        # print(f"Item: {item['data']['title']}\nOld: {extra}\nNew: {new_extra}")
        item['data']['extra'] = new_extra
        try:
            self._z.update_item(item)
            print(f'Updated successfully.')
        except Exception as e:
            webhook.send(f"Error while updating [{item['data']['title']}]\n{e}")
            if re.search(r'undergoing scheduled maintenance', str(e)):
                # Waiting for scheduled maintenance
                hours = 0.5
                webhook.send(f"Waiting for scheduled maintenance for {hours} hours")
                pause.hours(hours)
            return

    def _generate_query_url(self, item):
        """
        Generate a query URL for a given item
        """
        title = item['data']['title']
        query = title.replace(' ', '+')
        url = f'https://scholar.google.com/scholar?hl=en&as_q={query}&as_occt=title&num=1'
        # Filter by author
        creators = item['data']['creators']
        if creators:
            creator = creators[0]
            query = (creator['lastName'] if 'lastName' in creator else creator['name']).replace(' ', '+')
            url += f'&as_sauthors={query}'
        # Filter by year
        year = re.search(r'\d{4}', item['data']['date'])  # Extract year from date
        if year:
            # url += f'&as_ylo={year.group(0)}&as_yhi={year.group(0)}'
            url += f'&as_yhi={year.group(0)}'
        return url
