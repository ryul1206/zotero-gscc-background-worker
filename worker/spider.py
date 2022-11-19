import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_splash import SplashRequest, SplashFormRequest  # Enable JavaScript
from multiprocessing import Process, Queue


def get_spider(_url, _fname):

    class ScholarSpider(scrapy.Spider):
        name = "scholar_spider"
        allowed_domains = ["scholar.google.com"]
        start_urls = [_url]
        fname = _fname

        def start_requests(self):
            splash_args = {
                'wait': 1.5,
                'html': 1,
                'png': 0,
                'width': 828,
                'height': 612,
                'render_all': 1,
            }
            for url in self.start_urls:
                yield SplashRequest(url, callback=self.parse, args=splash_args)

        def parse(self, response):
            html = response.body
            # Save the HTML
            with open(self.fname, 'wb') as f:
                f.write(html)

    return ScholarSpider


# the wrapper to make it run more times
# https://stackoverflow.com/questions/41495052/scrapy-reactor-not-restartable
def f(q, x_url, x_fname):
    try:
        process = CrawlerProcess()
        process.crawl(get_spider(x_url, x_fname))
        process.start()
        q.put(None)
    except Exception as e:
        q.put(e)


def run_spider(x_url, x_fname):
    q = Queue()
    p = Process(target=f, args=(q, x_url, x_fname))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result


if __name__ == "__main__":
    url1 = 'https://scholar.google.com/scholar?cluster=15154755818357511167&hl=en&as_sdt=2005&sciodt=0,5'
    url2 = 'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=cnn&btnG='

    run_spider(url1, 'scholar1.html')
    run_spider(url2, 'scholar2.html')


# With 2captcha
# https://docs.scrapy.org/en/latest/topics/request-response.html#using-formrequest-from-response-to-simulate-a-user-login
# SplashFormRequest.from_response(response)