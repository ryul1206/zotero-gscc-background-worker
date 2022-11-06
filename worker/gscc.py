from pyzotero import zotero
import time
import random


def _update_nth_item(z, n):
    items = z.top(start=n, limit=1)
    if items:
        item = items[0]
        print(f"Item: {item['data']['title']}")
        return True
    else:
        print(f"Item {n} not found.")
        return False


def _update_gscc(z):
    # Retrieve all top-level items
    # However, requesting all the items at once is too heavy,
    # so we request them one by one.
    initial_count = z.num_items()
    n = 0
    while n < initial_count:
        update_nth_item(z, n)
        n += 1


class GSCC:
    def __init__(self, user_id, api_key):
        self.z = zotero.Zotero(user_id, 'user', api_key)
        # count items
        # self.item_count = self.z.count_items()
        # print(f'Found {self.item_count} items in Zotero library')
        count = self.z.num_items()
        print(f'Found {count} items in Zotero library')

    def fetch_all(self):
        _update_gscc(self.z)

    # items = z.top(limit=10)

    # for item in items:
    #     print("Item: %s | Key: %s" % (item['data']['title'], item['key']))
