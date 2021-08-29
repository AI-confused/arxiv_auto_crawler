import pysftp
import paramiko
import datetime
import time
import os
import argparse


cnopts = pysftp.CnOpts()
cnopts.hostkeys = None
now = datetime.datetime.now()
sched_time = now + datetime.timedelta(seconds=5)


def check_files_exist(sftp, file_path):
    sftp.cwd(file_path)
    directory_structure = sftp.listdir(file_path)
    # print(directory_structure)
    return directory_structure
    
def download_files_from_server(sftp, remoteFilePath, localFilePath):
    sftp.get(remoteFilePath, localFilePath)
    time.sleep(10)
    
def delete_files_from_server(sftp, file_path=None, file_directory=None):
    if file_path:
        sftp.remove(file_path)
    if file_directory:
        sftp.rmdir(file_directory)
        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='download from remote')
    parser.add_argument('-hostname', type=str, default=None, required=True, help='set remote hostname')
    parser.add_argument('-username', type=str, default=None, required=True, help='set remote user name')
    parser.add_argument('-password', type=str, default=None, required=True, help='set remote password')
    args = parser.parse_args()
    while True:
        now = datetime.datetime.now()
        if now == sched_time:
            with open('log_download.txt', 'a') as f:
                f.write('*******************\n')
                f.write('now_time :' + str(now) + '\n')
            #print('download time: ' + str(now))
            daily_count = 0
            remote_path = '/home/arxiv_crawl/pdf/'
            local_path = '/home/blackteat/PycharmProjects/arxiv_crawl/pdf/'
            with pysftp.Connection(host=args.hostname, username=args.username, password=args.password, cnopts=cnopts) as sftp:
                #print('connection successful....')
                directory_list = check_files_exist(sftp, remote_path)
                if len(directory_list) > 1:
                    with open('log_download.txt', 'a') as f:
                        f.write('strat download pdf\n')
                    #print(directory_list)
                    remote_file_directory = remote_path + directory_list[0] + '/'
                    # print(remote_file_directory)
                    file_list = check_files_exist(sftp, remote_file_directory)
                    if len(file_list):
                        # print(file_list)
                        local_path = local_path + directory_list[0] + '/'
                        if not os.path.exists(local_path):
                            os.mkdir(local_path)
                        # print(local_path)
                        for file in file_list:
                            daily_count += 1
                            remote_file_path = remote_file_directory + file
                            local_file_path = local_path + file + '.pdf'
                            # print(remote_file_path)
                            # print(local_file_path)
                            download_files_from_server(sftp, remote_file_path, local_file_path)
                        #print(daily_count)
                        with open('log_download.txt', 'a') as f:
                            f.write('today count:' + str(daily_count) + '\n')
                        #print('transfer finished')
                        time.sleep(20)
                        for file in file_list:
                            # print(file)
                            remote_file_path = remote_file_directory + file
                            delete_files_from_server(sftp, file_path=remote_file_path)
                        delete_files_from_server(sftp, file_path=None, file_directory=remote_file_directory)
                        #print('delete finished')
                        with open('log_download.txt', 'a') as f:
                            f.write('delete finished\n')
                else:
                    #print('not update pdfs'):q!
                    with open('log_download.txt', 'a') as f:
                        f.write('not update pdfs\n')
            sched_time = sched_time + datetime.timedelta(days=1)
            with open('log_download.txt', 'a') as f:
                f.write('next download time: ' + str(sched_time) + '\n')
                
                
