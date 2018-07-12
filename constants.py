HOST = "localhost"
PORT = 4415
AUTHKEY = "authkey".encode()
QUEUE_NAME = "translation_queue"
TRANSLATE_REQUEST = "https://translation.googleapis.com/language/translate/v2"
DETECT_REQUEST = "{}/detect".format(TRANSLATE_REQUEST)
AvailableTargetLanguages = ["ro", "it", "en", "de"]
