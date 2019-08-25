import datetime
import Sync
import FileHandler
import os


class Logger:
    def __init__(self):
        self.log_file = os.path.join(FileHandler.create_dir(os.path.dirname(__file__), "logs"),
                                     datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f") + '.txt')
        self.frame_path = FileHandler.create_dir(os.path.dirname(__file__), "tmp")
        self.backup_file = os.path.join(FileHandler.create_dir(os.path.dirname(__file__), "backup"),
                                        datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f") + '.txt')
        self.batch_file = os.path.join(FileHandler.create_dir(os.path.dirname(__file__), "batch"),
                                       datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f") + '.txt')
        self.syncs = []
        self.splitter = "#"

    def log_sync(self, sync: Sync):
        self.syncs.append(sync)
        log_file = self.log_file

        if not os.path.exists(log_file):
            FileHandler.create_file(log_file)

        f = open(log_file, "r")
        contents = f.readlines()
        f.close()

        contents
        insert_index = None
        for index, val in enumerate(contents):
            if self.splitter in val:
                insert_index = index - 1
        if len(contents) is 0:
            contents.append("#")
            insert_index = 0

        if insert_index is not None:
            overview = f"""
uid: {sync.uid}
source1: {sync.sources[0].file_name}
source1: {sync.sources[1].file_name}
status: {sync.successful}
            """
            contents.insert(insert_index, overview)
            log = f"""
uid: {sync.uid}
source1: {sync.sources[0].file_name}
path: {sync.sources[0].file_path}
source1: {sync.sources[1].file_name}
path: {sync.sources[1].file_path}
successful: {sync.successful}
merged: {sync.merged}

            """

            contents.append(log)
            contents.extend(sync.messages)
            contents.extend(sync.errmsg)
            contents.append("-----------------------------")

        f = open(log_file, "w")
        f.writelines(contents)
        f.close()

    def print_overview(self):
        for i in self.syncs:
            print(f"""
#
uid: {i.uid}
name: {i.sources[0].file_name}
successful: {i.successful}
merged: {i.merged}
           """)
