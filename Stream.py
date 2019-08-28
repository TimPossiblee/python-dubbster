class Stream:
    def __init__(self, container_path, index, codec_type, language):
        self.container_path = container_path
        self.index = index
        self.codec_type = codec_type
        self.language = language
        self.width = None
        self.height = None
        self.fps = None
