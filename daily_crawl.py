import datetime
import urllib.request as libreq
import time
import feedparser
import json
import urllib.request
import os
import argparse

# d = 0
now = datetime.datetime.now()
sched_time = now + datetime.timedelta(seconds=5)

# Base api query url
base_url = 'http://export.arxiv.org/api/query?'

# Search parameters
#search_query = 'cat:cs.LG'  # search for electron in all fields
total_results = 100  # want 500 total results
wait_time = 3  # number of seconds to wait beetween calls
sortBy = 'submittedDate'
sortOrder = 'descending'
metadatas = []
item = {}
total_counts = 0
newly_update_date = ''
#last_update_date = '2019-10-03'
pdf_flag = 0
daily_pdfs = 0

def pdf_scrawl(url, path, time_gap):
    # url = 'http://arxiv.org/pdf/1907.00126v1'
    urllib.request.urlretrieve(url, path)
    print('sleeping...')
    time.sleep(time_gap)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='arxiv crawl')
    parser.add_argument('-last_update_date', type=str, default=None, required=True, help='init crawl time start point')
    parser.add_argument('-search_query', type=str, default='cat:cs.LG', help='define search fields')
    args = parser.parse_args()
    while True:
        now = datetime.datetime.now()
        flag = 0

        if now == sched_time:
            with open('../log_file.txt', 'a') as f:
                f.write('*****************************\n')
                f.write('now_time: ' + str(now) + '\n')

            query = 'search_query=%s&sortBy=%s&sortOrder=%s&start=%i&max_results=%i' % (args.search_query,
                                                                                        sortBy, sortOrder, 0,
                                                                                        1)
            with libreq.urlopen(base_url + query) as url:
                response = url.read()
            feed = feedparser.parse(response)
            newly_update_date = feed.entries[0].published.split('T')[0]
            print('newly_update_date: ' + str(newly_update_date))

            if args.last_update_date == newly_update_date:
                flag = 0  #no new pdf update
            else:
                flag = 1 #new pdf update

            if flag:
                start = 0
                daily_counts = 0
                inner_flag = 0
                with open('../log_file.txt', 'a') as f:
                    f.write('log_date: ' + newly_update_date + '\n')

                for _ in range(100):
                    query = 'search_query=%s&sortBy=%s&sortOrder=%s&start=%i&max_results=%i' % (args.search_query,
                                                                                                sortBy, sortOrder, start,
                                                                                                5)
                    with libreq.urlopen(base_url + query) as url:
                        response = url.read()
                    feed = feedparser.parse(response)
                    start += 5
                    for entry in feed.entries:
                        if args.last_update_date in entry.published:
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
                        link_file = '../link/links:' + newly_update_date + '.txt'
                        with open(link_file, 'a') as f:
                            f.write(link.href + '\n')
                        metadatas.append(item)
                        item = {}
                    # print('finish ' + str(start))


                    if inner_flag:  # stop get data
                        break
                    time.sleep(wait_time)
                pdf_flag = 1
                daily_pdfs = daily_counts
                file_name = '../metadata/metadatas:' + newly_update_date + '.json'
                with open(file_name, 'w') as f:
                    json.dump(metadatas, f)
                metadatas = []
                with open('../log_file.txt', 'a') as f:
                    f.write('today_items: %i' % daily_counts + '\n')
                print('today_items: %i' % daily_counts)
                total_counts += daily_counts
                daily_counts = 0
                with open('../log_file.txt', 'a') as f:
                    f.write('total_items: %i' % total_counts + '\n')
                print('total_items: %i' % total_counts)

                with open('../log_file.txt', 'a') as f:
                    f.write('log finished\n')
                    # f.write('********分界线*********\n')
                args.last_update_date = newly_update_date
                print('log finish')
            else:
                with open('../log_file.txt', 'a') as f:
                    f.write('today not updated\n')
                print('not updated')
            sched_time += datetime.timedelta(days=1)
            with open('../log_file.txt', 'a') as f:
                f.write('args.last_update_date: ' + str(args.last_update_date) + '\n')
                f.write('next log time: ' + str(sched_time) + '\n')

        if pdf_flag:
            print('start download pdfs')
            time.sleep(120)
            time_gap = int((23 * 60 * 60) / daily_pdfs)
            print(time_gap)
            with open('../link/links:' + newly_update_date + '.txt') as f:
                pdf_path = '../pdf/' + newly_update_date
                if not os.path.exists(pdf_path):
                    os.mkdir(pdf_path)
                for line in f:
                    if line:
                        url = ''.join(line.split())
                        print(url)
                        pdf_name = url.split('/')[4]
                        pdf_file_path = pdf_path + '/' + pdf_name
                        print(pdf_file_path)
                        pdf_scrawl(url, pdf_file_path, time_gap)
            print('download finished')
            pdf_flag = 0
