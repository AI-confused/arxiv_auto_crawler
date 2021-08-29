import sys
import os
cur_dir = os.path.abspath(__file__)
sys.path.append(os.path.join('/'.join(cur_dir.split('/')[:-2]), 'src/'))
from arxiv_auto_crawler.daily_crawl import *


if __name__ == '__main__':
    crawl = AutoCrawler('/Users/blacktear/github/arxiv_scrawl/config/crawler_config.yaml')
    crawl.daily_crawler()