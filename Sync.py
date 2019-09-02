import uuid
from Source import Source
import os
import ImageProcessing
import FileHandler
import subprocess
import datetime
import math


class Sync:

    def __init__(self, source1, source2, frame_path, seek=(0.5, 0.85), force=False, reversed_sync=False):
        self.uid = str(uuid.uuid4())
        if reversed_sync:
            data = FileHandler.load_archive(source1)
            self.sources = [Source(data, load_type='ARCHIVE'), Source(source2)]
            self.reference = None
            self.seek = data["#ref"]["#seek"]
            self.seek_time = data["#ref"]["#seek_time"]
        else:
            self.sources = [Source(source1), Source(source2)]
            self.reference = None
            self.seek = seek
            self.seek_time = None

        self.frame_path = frame_path
        self.rtd = None
        self.delay_ms = None
        self.bulk = None
        self.bulk_reference = None
        self.reversed_sync = reversed_sync
        self.messages = []
        self.errmsg = []
        self.successful = False
        self.merged = False
        self.frame_output = None
        self.force = force
        self.ready = True
        if not force and "MULTi" in source1:
            message = "the source1 is already a multi file and force was disabled"
            print(message)
            self.errmsg.append(message)
            self.ready = False

    def sync(self):
        print("")

        sources = self.sources
        if not sources[0].loaded or not sources[1].loaded:
            message = "there was an error while reading the input sources"
            print(message)
            self.errmsg.append(message)
            return False

        self.rtd = float(sources[0].duration_exact) - \
                   float(sources[1].duration_exact)

        if int(sources[0].container_fps * 100) != int(sources[1].container_fps * 100):
            message = f"inputs {sources[0].container_fps, sources[1].container_fps} don't share the same fps"
            print(message)
            self.errmsg.append(message)
            return False

        print(f"""

{sources[0].file_name} Runtime: {datetime.timedelta(seconds=sources[0].duration_exact)}s FPS: {sources[0].container_fps} 
{sources[1].file_name} Runtime: {datetime.timedelta(seconds=sources[1].duration_exact)}s FPS: {sources[1].container_fps}
RTD: {self.rtd}s
                """)

        delay = []
        index_offset = None

        self.frame_output = FileHandler.create_dir(self.frame_path, self.uid)

        for run in range(2):
            print(f"running {run + 1} lap")

            seek_time = self.seek[run] * sources[0].duration
            vframes = None
            time_offset = None

            if run is 0:
                vframes = self.calc_run_one_vframes(
                    self.rtd, sources[0].container_fps)
                time_offset = seek_time - \
                              int(vframes / 2 / sources[0].container_fps)
            elif run is 1:
                data = self.calc_run_two(
                    index_offset, seek_time, sources[0].container_fps)
                vframes = data["vframes"]
                time_offset = data["time_offset"]
            else:
                return None

            reference = \
                FileHandler.load_frames(
                    ImageProcessing.extract_frames(sources[0].file_path, self.frame_output, seek_time,
                                                   sources[0].container_size,
                                                   1), self.frame_output)[0]
            bulk_reference = \
                FileHandler.load_frames(
                    ImageProcessing.extract_frames(sources[1].file_path, self.frame_output,
                                                   seek_time,
                                                   sources[0].container_size,
                                                   1), self.frame_output)[0]
            bulk = FileHandler.load_frames(
                ImageProcessing.extract_frames(sources[1].file_path, self.frame_output,
                                               time_offset,
                                               sources[0].container_size,
                                               vframes), self.frame_output)

            seek_index = self.null_index(bulk, bulk_reference)

            results = {}
            for image in bulk:
                results[image] = ImageProcessing.compare_image(
                    reference, image)

            result = min(results, key=lambda x: results.get(x))
            delay.append((bulk.index(seek_index) - bulk.index(result)))
            index_offset = bulk.index(result) - bulk.index(seek_index)
            print(
                f"Index: {bulk.index(result)} Null: {bulk.index(seek_index)} Difference: {results.get(result)}")

        message = [f"[Index: {delay[0]} Delay: {delay[0] / sources[0].container_fps * 1000}]",
                   f"[Index: {delay[1]} Delay: {delay[1] / sources[1].container_fps * 1000}]"]
        print(message[0])
        print(message[1])
        self.messages.extend(message)

        delay_ms = self.calc_delay(delay, sources[0].container_fps)
        if delay_ms is not None:
            self.delay_ms = delay_ms
            self.successful = True
            print(self.delay_ms)
            return self.successful

        message = "there was an unexpected error while synchronizing"
        print(message)
        self.errmsg.append(message)
        return False

    def merge(self, delete_source=False, remove_multi_track=False):
        new_file = FileHandler.output_filename(
            self.sources[0].file_name, self.sources[0].file_directory)
        if new_file is None:
            message = "it was not possible to find an unused file name"
            print(message)
            self.errmsg.append(message)
            return None

        index = None
        for stream in self.sources[1].streams:
            if stream.codec_type == "audio":
                index = str(stream.index)
                break

        if index is None:
            message = "no audio stream found"
            print(message)
            self.errmsg.append(message)
            return None

        file_output = os.path.join(
            self.sources[0].file_directory, new_file + ".mkv")

        source1_options = ""
        if remove_multi_track:
            source1_options += " -a !ger"

        try:
            p = subprocess.Popen(
                f"mkvmerge -o \"{file_output}\" {source1_options} \"{self.sources[0].file_path}\" -D -a {index} -S "
                f"--no-chapters -T -y {index}:{self.delay_ms} --language {index}:ger --default-track "
                f"{index}:true \"{self.sources[1].file_path}\" --track-order 0:0,1:{index} -q",
                stdout=subprocess.PIPE, shell=True)

            (output, err) = p.communicate()

            p_status = p.wait()
            exitcode = int(p_status)
        except:
            exitcode = 1

        if exitcode is not 0:
            os.remove(file_output)
            message = "mkvmerge returned with an error"
            print(message)
            self.errmsg.append(message)
            return False

        if delete_source:
            os.remove(self.sources[0].file_path)
            message = f"deleted source file {self.sources[0].file_path} after merge"
            print(message)
            self.messages.append(message)

        self.merged = True
        message = f"successfully synced and merged {self.sources[0].file_name}"
        print(message)
        self.messages.append(message)
        return True

    @staticmethod
    def calc_run_one_vframes(difference, fps):
        frame_diff = int(abs(difference) * fps * 2)
        if frame_diff <= 150:
            if frame_diff + 60 > 150:
                return frame_diff + 60
            return 150
        elif frame_diff > 10000:
            return 150
        else:
            return frame_diff + 60

    @staticmethod
    def calc_run_two(index_offset, seek_time, fps):
        if abs(index_offset) <= 10:
            time_offset = seek_time - round(50 / fps)
            vframes = 100
        else:
            if index_offset < 0:
                time_offset = seek_time - round(abs(index_offset) / fps) - 1
                vframes = abs(index_offset) + math.ceil(fps) * 2
            elif index_offset > 0:
                time_offset = seek_time
                vframes = index_offset + math.ceil(fps)

            if vframes < 100:
                vframes = 100

        return {"time_offset": time_offset, "vframes": vframes}

    def calc_delay(self, delay, fps):
        if -2 <= (delay[0] - delay[1]) <= 2:
            cdelay = [delay[0] / fps * 1000, delay[1] / fps * 1000]
            cdelay.sort(reverse=True)
            return int((cdelay[0] + cdelay[1]) / 2)

        message = f"the provided delay values {delay} are not similar enough"
        print(message)
        self.errmsg.append(message)
        return None

    @staticmethod
    def null_index(bulk, bulk_reference):
        if ImageProcessing.same_image(bulk[0], bulk[1]):
            del bulk[0]
        for i in bulk:
            if ImageProcessing.same_image(i, bulk_reference):
                return i
        return None
