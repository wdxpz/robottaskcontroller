import os

class FileUtil(object):
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise OSError('{file_path} not exist'.format(file_path = file_path))
        self.file_path = os.path.abspath(file_path)

    def status(self):
        open_fd_list = self.__get_all_fd()
        open_count = len(open_fd_list)
        is_opened = False
        if open_count > 0:
            is_opened = True

        return {'is_opened': is_opened, 'open_count': open_count}

    def __get_all_pid(self):
        return [ _i for _i in os.listdir('/proc') if _i.isdigit()]

    def __get_all_fd(self):
        all_fd = []
        for pid in self.__get_all_pid():
            _fd_dir = '/proc/{pid}/fd'.format(pid = pid)
            if os.access(_fd_dir, os.R_OK) == False:
                continue

            for fd in os.listdir(_fd_dir):
                fd_path = os.path.join(_fd_dir, fd)
                if os.path.exists(fd_path) and os.readlink(fd_path) == self.file_path:
                    all_fd.append(fd_path)

        return all_fd