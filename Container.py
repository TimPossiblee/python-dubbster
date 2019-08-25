import os
import ffmpeg
from Stream import Stream


class Container:
    def __init__(self, file):
        self.streams = []
        self.duration = None
        self.duration_exact = None
        self.file_path = file
        self.file_directory = None
        self.file_name = None
        self.file_extension = None
        self.container_size = None
        self.container_fps = None
        self.loaded = self.info(file)

    def info(self, file):
        try:
            data = ffmpeg.probe(file, cmd='ffprobe')
            streams = []

            self.duration = int(float(data["format"]["duration"]))
            self.duration_exact = float(data["format"]["duration"])
            path = data["format"]["filename"]
            self.file_directory, file_name = os.path.split(os.path.abspath(path))
            self.file_name, self.file_extension = os.path.splitext(file_name)

            for stream in data["streams"]:
                language = "und"
                if "tags" in stream and "language" in stream["tags"]:
                    language = stream["tags"]["language"]

                obj = Stream(path, stream["index"], stream["codec_type"], language, stream["start_time"])

                if obj.codec_type == "video":
                    obj.width = stream["width"]
                    obj.height = stream["height"]
                    obj.fps = eval(stream["r_frame_rate"])
                    if self.container_fps is None:
                        self.container_fps = obj.fps
                    if self.container_size is None:
                        self.container_size = f"{obj.width}x{obj.height}"
                streams.append(obj)

            self.streams = streams
            return True
        except:
            return False
