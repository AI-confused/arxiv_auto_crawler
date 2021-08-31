import datetime
import urllib.request as libreq
import time
import feedparser
import json
import logging
import yaml
from tqdm import tqdm
import urllib.request
import os


class AutoCrawler(object):
    def __init__(self, task_config_path) -> None:
        self.__update_by_dict(task_config_path)
        self.__set_basic_log_config()
        self.__set_default_attributes()


    def __update_by_dict(self, task_config_path: str):
        """Update class attributes by dict.
        
        @task_config_path: configuration path
        """
        with open(task_config_path, 'r', encoding='utf-8') as f:
            self.task_configuration = yaml.load(f.read(), Loader=yaml.FullLoader)
        for key, val in self.task_configuration.items():
            setattr(self, key, val)


    def __set_default_attributes(self):
        self.metadatas = []
        self.total_counts = 0
        self.newly_update_date = ''
        self.pdf_flag = 0
        self.daily_pdfs = 0


    def __set_basic_log_config(self):
        """Set basic logger configuration.

        Private class function.
        """
        # get now time
        self.now_time = datetime.datetime.now().strftime("%Y-%m-%d|%H:%M:%S")

        # set logging format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s', 
                                        datefmt='%Y-%m-%d | %H:%M:%S')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # output to log file handler
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)
        file_handler = logging.FileHandler(os.path.join(self.log_dir, 'log-{}.log'.format(self.log_date)))
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # output to cmd
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)

        # add handler
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)


    def is_time_equal(self, now, sched) -> bool:
        """
        """
        if not str(now).split(' ')[0] == str(sched).split(' ')[0]:
            return False
        if not str(now).split(' ')[1].split('.')[0] == str(sched).split(' ')[1].split('.')[0]:
            return False
        return True


    def get_paper_pdf(self, url: str, file_path: str, time_gap: int) -> None:
        """

        @url: for example, 'http://arxiv.org/pdf/1907.00126v1'
        @path: 
        @time_gap:
        """
        urllib.request.urlretrieve(url, file_path)
        self.logger.info('{} downloaded'.format(file_path.split('/')[-1]))
        self.logger.info('sleeping for {}s...'.format(time_gap))
        time.sleep(time_gap)


    def daily_crawler(self) -> None:
        """
        """
        self.sched_time = datetime.datetime.now() + datetime.timedelta(seconds=10)
        while True:
            now = datetime.datetime.now()
            flag = 0

            if self.is_time_equal(now, self.sched_time):
                self.logger.info('now time: {}'.format(str(now)))

                query = 'search_query=%s&sortBy=%s&sortOrder=%s&start=%i&max_results=%i' % (self.search_query,
                                                                                            self.sortBy, self.sortOrder, 0,
                                                                                            1)
                with libreq.urlopen(self.base_url + query) as url:
                    response = url.read()
                feed = feedparser.parse(response)
                self.newly_update_date = feed.entries[0].published.split('T')[0]
                self.logger.info('last_update_date: ' + str(self.last_update_date))
                self.logger.info('newly_update_date: ' + str(self.newly_update_date))

                if self.last_update_date == self.newly_update_date:
                    # no new pdf update
                    flag = 0  
                else:
                    # new pdf update
                    flag = 1 

                if flag:
                    start = 0
                    daily_counts = 0
                    inner_flag = 0
                    item = {}
                    self.logger.info('check date: ' + self.newly_update_date + '\n')

                    # download pdf links
                    self.logger.info('download pdf links...')
                    for _ in tqdm(range(self.total_results), desc='download link progress'):
                        query = 'search_query=%s&sortBy=%s&sortOrder=%s&start=%i&max_results=%i' % (self.search_query,
                                                                                            self.sortBy, self.sortOrder, start,
                                                                                                    5)
                        with libreq.urlopen(self.base_url + query) as url:
                            response = url.read()
                        feed = feedparser.parse(response)
                        
                        for entry in feed.entries:
                            if self.last_update_date in entry.published:
                                inner_flag = 1
                            if inner_flag:
                                break

                            daily_counts += 1
                            item['id'] = entry.id.split('/abs/')[-1]
                            title_list = entry.title.split()
                            entry.title = ' '.join(title_list)
                            item['title'] = entry.title
                            item['published'] = entry.published[:10]
                            item['authors'] = []
                            for author in entry.authors:
                                item['authors'].append(author.name)
                            summary_list = entry.summary.split()
                            entry.summary = ' '.join(summary_list)
                            item['summary'] = entry.summary

                            for link in entry.links:
                                if link.rel == 'related':
                                    item['paper_link'] = link.href
                            if not os.path.exists(self.link_dir):
                                os.mkdir(self.link_dir)
                            self.link_file = os.path.join(self.link_dir, self.newly_update_date + '.txt')
                            if daily_counts == 1:
                                with open(self.link_file, 'w') as f:
                                    f.write(link.href + ' ' + item['title'] + '\n')
                            else:
                                with open(self.link_file, 'a') as f:
                                    f.write(link.href + ' ' + item['title'] + '\n')
                            self.metadatas.append(item)
                            item = {}
                        # update start index
                        start += 5
                        # stop get data
                        if inner_flag:  
                            break
                        time.sleep(self.wait_time)
                    self.pdf_flag = 1
                    self.daily_pdfs = daily_counts
                    if not os.path.exists(self.metadata_dir):
                        os.mkdir(self.metadata_dir)
                    self.meta_file = os.path.join(self.metadata_dir, self.newly_update_date + '.json')
                    with open(self.meta_file, 'w') as f:
                        json.dump(self.metadatas, f)
                    self.metadatas = []
                    self.logger.info('today_items: %i' % daily_counts + '\n')
                    self.total_counts += daily_counts
                    daily_counts = 0
                    self.logger.info('total_items: %i' % self.total_counts)
                    self.logger.info('check finished\n')
                    self.last_update_date = self.newly_update_date
                else:
                    self.logger.info('today not updated\n')
                self.sched_time += datetime.timedelta(days=1)
                self.logger.info('last_update_date: ' + str(self.last_update_date) + '\n')
                self.logger.info('next check time: ' + str(self.sched_time) + '\n')

            if self.pdf_flag:
                # start download pdf
                self.logger.info('start download pdfs...')
                time.sleep(10)
                if not hasattr(self, 'time_gap'):
                    self.time_gap = (23 * 60 * 60) // self.daily_pdfs
                self.logger.info('time gap: {}s'.format(self.time_gap))
                with open(self.link_file) as f:
                    pdf_path = os.path.join(self.pdf_dir, self.newly_update_date)
                    if not os.path.exists(pdf_path):
                        os.makedirs(pdf_path)
                    for line in tqdm(f.readlines(), desc='download pdf progress'):
                        if line:
                            url = line.split(' ')[0]
                            paper_title = ' '.join(line.split(' ')[1:]).strip()
                            pdf_name = url.split('/')[4]
                            pdf_file_path = pdf_path + '/' + pdf_name + '-' + paper_title + '.pdf'
                            self.get_paper_pdf(url, pdf_file_path, self.time_gap)
                self.logger.info('download finished')
                self.pdf_flag = 0
