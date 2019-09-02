class Stream:
    def __init__(self, index, codec_type, language):
        self.index = index
        self.codec_type = codec_type
        self.language = language
        self.width = None
        self.height = None
        self.fps = None
