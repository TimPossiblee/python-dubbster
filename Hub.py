import FileHandler
from Logger import Logger
from Sync import Sync


class Hub:
    def __init__(self):
        self.logger = Logger()

    def cli_sync(self, sources=None, file=None, tv=None, do_merge=True, delete_source=True, force=False, clean_merge=False):
        array = []

        if sources is not None:
            array.append(sources)
        elif file is not None:
            array.extend(FileHandler.read_sources_file(file))
        elif tv is not None:
            array.extend(FileHandler.load_tv(tv[0], tv[1]))
        else:
            print("no sources specified")
            return None

        left_array = array[:]

        for entry in array:
            FileHandler.write_batch_file(self.logger.backup_file, left_array)
            self.synchronize(
                entry[0], entry[1], do_merge=do_merge, delete_source=delete_source, force=force, clean_merge=clean_merge)
            del left_array[0]

        FileHandler.write_batch_file(self.logger.backup_file, left_array)
        self.logger.print_overview()

    def synchronize(self, source1, source2, do_merge=True, delete_source=True, force=False, clean_merge=False):
        sync = Sync(source1, source2, self.logger.frame_path, force=force)

        if sync.ready and sync.sync():
            if do_merge:
                print("merging...")
                sync.merge(delete_source=delete_source,
                           remove_multi_track=clean_merge)

        self.logger.log_sync(sync)

    def cli_batch(self):
        array = []

        while True:
            tmp = [None, None]
            for i in range(2):
                entry = input(f"enter {i + 1} value \n")
                if entry != "":
                    tmp[i] = entry.replace("\"", "")

            if None not in tmp:
                entry = input("store inputs? Y/N \n")
                if entry.lower() == "y":
                    array.append(tmp)

            entry = input("add an other entry? Y/N \n")
            if entry.lower() != "y":
                break

        FileHandler.write_batch_file(self.logger.batch_file, array)

        print(self.logger.batch_file)
