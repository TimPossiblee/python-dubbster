import ffmpeg
from Stream import Stream


class Source:
    def __init__(self, file, load_type='FFPROBE'):
        self.streams = []
        self.duration = None
        self.duration_exact = None
        self.file_path = file
        self.container_size = None
        self.container_fps = None

        if load_type is 'FFPROBE':
            self.loaded = self.ffprobe(file)
        elif load_type is 'ARCHIVE':
            self.file_path = file["#aud"]["#path"]
            self.loaded = self.storage_info(file)
        else:
            self.loaded = False

    def storage_info(self, data):
        try:
            self.duration_exact = data["#media_info"]["duration"]
            self.duration = int(self.duration_exact)
            self.container_fps = data["#media_info"]["fps"]
            self.container_size = data["#media_info"]["size"]
            self.streams.append(Stream(0, 'AUDIO', "ger"))
        except Exception as e:
            print(e)
            return False
        return True

    def ffprobe(self, file):
        try:
            data = ffmpeg.probe(file, cmd='ffprobe')
            streams = []

            self.duration = int(float(data["format"]["duration"]))
            self.duration_exact = float(data["format"]["duration"])

            for stream in data["streams"]:
                language = "und"
                if "tags" in stream and "language" in stream["tags"]:
                    language = stream["tags"]["language"]

                obj = Stream(self.file_path, stream["index"], stream["codec_type"], language)

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
        except Exception as e:
            print(e)
            return False
        return True
