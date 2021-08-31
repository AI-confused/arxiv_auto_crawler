import pysftp
import datetime
import time
import os
from tqdm import tqdm
import yaml
import logging


class PaperDownloader(object):
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
        self.cnopts = pysftp.CnOpts()
        self.cnopts.hostkeys = None


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
            os.makedirs(self.log_dir)
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
        

    def check_files_exist(self, sftp, file_path):
        sftp.cwd(file_path)
        directory_structure = sftp.listdir(file_path)
        return directory_structure

    
    def download_files_from_server(self, sftp, remoteFilePath, localFilePath):
        sftp.get(remoteFilePath, localFilePath)
        time.sleep(10)
        
    
    def delete_files_from_server(self, sftp, file_path=None, file_directory=None):
        if file_path:
            sftp.remove(file_path)
        if file_directory:
            sftp.rmdir(file_directory)
        
        
    def paper_download(self):
        sched_time = datetime.datetime.now() + datetime.timedelta(seconds=10)
        while True:
            now = datetime.datetime.now()
            if self.is_time_equal(now, sched_time):
                self.logger.info('download time: ' + str(now))
                daily_count = 0

                with pysftp.Connection(host=self.hostname, port=self.port, username=self.username, password=self.password, cnopts=self.cnopts) as sftp:
                    self.logger.info('connection successful')
                    directory_list = self.check_files_exist(sftp, self.remote_path)
                    if len(directory_list) > 0:
                        self.logger.info('start download pdf from remote server...')

                        remote_file_directory = self.remote_path + directory_list[0] + '/'

                        file_list = self.check_files_exist(sftp, remote_file_directory)
                        if len(file_list):

                            self.local_path = self.local_path + directory_list[0] + '/'
                            if not os.path.exists(self.local_path):
                                os.makedirs(self.local_path)

                            for file in tqdm(file_list, desc='download progress'):
                                daily_count += 1
                                remote_file_path = remote_file_directory + file
                                local_file_path = self.local_path + file

                                self.download_files_from_server(sftp, remote_file_path, local_file_path)
                            self.logger.info('daily_count: {}'.format(daily_count))
                            self.logger.info('today count:' + str(daily_count))
                            self.logger.info('transfer finished')
                            time.sleep(20)
                            for file in tqdm(file_list, desc='delete remote server progress'):
                                remote_file_path = remote_file_directory + file
                                self.delete_files_from_server(sftp, file_path=remote_file_path)
                            # delete remote_file_directory
                            self.delete_files_from_server(sftp, file_path=None, file_directory=remote_file_directory)
                            self.logger.info('delete finished')
                    else:
                        self.logger.info('no update pdf on remote server')
                sched_time = datetime.datetime.now() + datetime.timedelta(days=1)
                self.logger.info('next check time: ' + str(sched_time))
                
                
