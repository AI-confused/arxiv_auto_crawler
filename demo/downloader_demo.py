import sys
import os
cur_dir = os.path.abspath(__file__)
sys.path.append(os.path.join('/'.join(cur_dir.split('/')[:-2]), 'src/'))
from arxiv_auto_crawler.download_file import *


if __name__ == '__main__':
    downloader = PaperDownloader(task_config_path='/Users/tal/github/arxiv_scrawl/config/downloader_config.yaml')
    downloader.paper_download()