import ftplib
import os
import re
import datetime
from retrying import retry
from exporters.writers.base_writer import BaseWriter
import uuid


class FtpCreateDirsException(Exception):
    pass


class FTPWriter(BaseWriter):
    """
    Writes items to FTP server.

    Needed parameters:

        - host (str)
            Ftp server ip

        - port (int)
            Ftp port

        - ftp_user (str)
            Ftp user

        - ftp_password (str)
            Ftp password

        - filebase (str)
            Base path to store the items in.
    """
    requirements = {
        'host': {'type': basestring, 'required': True},
        'port': {'type': int, 'required': True},
        'ftp_user': {'type': basestring, 'required': True},
        'ftp_password': {'type': basestring, 'required': True},
        'filebase': {'type': basestring, 'required': True}
    }

    def __init__(self, options, settings):
        super(FTPWriter, self).__init__(options, settings)
        self.ftp_host = self.read_option('host')
        self.ftp_port = self.read_option('port')
        self.ftp_user = self.read_option('ftp_user')
        self.ftp_password = self.read_option('ftp_password')
        self.filebase = self.read_option('filebase').format(datetime.datetime.now())
        self.ftp = ftplib.FTP()
        self.logger.info(
            'FTPWriter has been initiated. host: {}. port: {}. filebase: {}'.format(self.ftp_host, self.ftp_port,
                                                                                    self.filebase))

    # TODO: Refactor recursivity
    def _create_target_dir_if_needed(self, target, depth_limit=20):
        """Creates the directory for the path given, recursively creating
        parent directories when needed"""
        if depth_limit <= 0:
            raise FtpCreateDirsException('Depth limit exceeded')

        target_dir = os.path.dirname(target)
        # target_dir = target
        parent_dir, dir_name = os.path.split(target_dir)

        parent_dir_ls = []
        try:
            parent_dir_ls = self.ftp.nlst(parent_dir)
        except:
            # Possibly a microsoft server
            # They throw exceptions when we try to ls non-existing folders
            pass

        parent_dir_files = [os.path.basename(d) for d in parent_dir_ls]
        if dir_name not in parent_dir_files:
            if parent_dir and target_dir != '/':
                self._create_target_dir_if_needed(target_dir, depth_limit=depth_limit - 1)
                self.logger.info('Will create dir: %s' % target)
                self.ftp.mkd(target)
            else:
                self.logger.info('Will create dir: %s' % target)
                self.ftp.mkd(target)
        else:
            try:
                self.logger.info('Will create dir: %s' % target)
                self.ftp.mkd(target)
            except:
                pass

    @retry(wait_exponential_multiplier=500, wait_exponential_max=10000, stop_max_attempt_number=10)
    def write(self, dump_path, group_key=None):
        if group_key is None:
            group_key = []
        normalized = [re.sub('\W', '_', s) for s in group_key]
        destination_path = os.path.join(self.filebase, os.path.sep.join(normalized))
        self.logger.debug('Uploading predump file')
        self.ftp.connect(self.ftp_host, self.ftp_port)
        self.ftp.login(self.ftp_user, self.ftp_password)
        self._create_target_dir_if_needed(destination_path)
        self.ftp.storbinary('STOR %s' % (destination_path + '/predump_{}.gz'.format(uuid.uuid4())), open(dump_path))
        self.ftp.close()
        self.logger.debug('Flushed {}'.format(dump_path))
