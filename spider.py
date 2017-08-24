from urllib.request import urlopen
from domain import *
from general import *
from bs4 import BeautifulSoup
import requests
from link_finder import internals, externals

class Spider:

    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    data_file = ''
    crawled_file = ''
    crawl_type = ''
    queue = set()
    crawled = set()
    external = set()
    data = ''

    def __init__(self, project_name, base_url, domain_name,spider_type,queue_file):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.type = spider_type
        Spider.queue_file = queue_file
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        Spider.data_file = Spider.project_name + '/data.csv'
        Spider.custom_file = Spider.project_name + '/custom.csv'
        Spider.external_file = Spider.project_name + '/external.txt'
        self.boot()
        if Spider.type == 'crawl':
            self.crawl_page('First spider', Spider.base_url)

    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url,Spider.type)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)
        Spider.external = file_to_set(Spider.external_file)

    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' now crawling ' + page_url)
            print('Queue ' + str(len(Spider.queue)) + ' | Crawled  ' + str(len(Spider.crawled)))
            try:
                response = requests.get(page_url,timeout=5)
                status = requests.get(page_url).status_code
                html = response.text
                data_file = Spider.data_file
                response_header = response.headers['Content-Type']
                base = ''
                if Spider.type == 'crawl':
                    Spider.add_links_to_queue(Spider.gather_links(page_url, html, status, data_file, response_header))
                    Spider.add_links_to_external(Spider.gather_externals(page_url, html, status, data_file, response_header))
                Spider.gather_meta(page_url, html,base, status,data_file,response_header)
                Spider.queue.remove(page_url)
                Spider.crawled.add(page_url)
                Spider.update_files()
            except:
                pass

    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_meta(page_url,html,base,status,data_file, response_header):
        try:
            base = Spider.base_url
            finder = internals(html, base,status,page_url,data_file,response_header)
        except Exception as e:
            print(str(e))
            return set()
        data = finder.meta_data(html,base,status,page_url,data_file,response_header)
        #print(data)
        #return finder.page_links()

    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(page_url,html,status,data_file,response_header):
        try:
            #response = requests.get(page_url)
            #status = requests.get(page_url).status_code
            #html = response.text
            #print(soup)
            base = Spider.base_url
            finder = internals(html,base,status,page_url,data_file,response_header)
        except Exception as e:
            print(str(e))
            return set()
        #print(finder.page_links())
        return finder.page_links()

    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_externals(page_url, html, status, data_file, response_header):
        try:
            base = Spider.base_url
            finder = externals(html, base, status, page_url, data_file, response_header)
        except Exception as e:
            print(str(e))
            return set()
        #print(finder.page_outlinks())
        return finder.page_outlinks()

    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            if Spider.domain_name != get_domain_name(url):
                continue
            Spider.queue.add(url)

    # Saves externals into separate project files
    @staticmethod
    def add_links_to_external(links):
        for url in links:
            Spider.external.add(url)

    @staticmethod
    def update_files():
        if Spider.type == 'crawl':
            set_to_file(Spider.queue, Spider.queue_file)
            set_to_file(Spider.crawled, Spider.crawled_file)
            set_to_file(Spider.external, Spider.external_file)
        else:
            set_to_file(Spider.crawled, Spider.crawled_file)
            set_to_file(Spider.queue, Spider.queue_file)

