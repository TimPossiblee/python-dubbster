class Stream:
    def __init__(self, container_path, index, codec_type, language, delay):
        self.container_path = container_path
        self.index = index
        self.codec_type = codec_type
        self.language = language
        self.delay = delay
        self.width = None
        self.height = None
        self.fps = None
