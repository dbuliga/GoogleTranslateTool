#!/usr/local/bin/python3
import argparse
from queue import Empty

from constants import HOST, PORT, AUTHKEY, QUEUE_NAME
from utils import connect_queue, validate_language


def __get_the_actual_queue():
    try:
        qm = connect_queue(HOST, PORT, AUTHKEY, QUEUE_NAME)
        translation_queue = qm.translation_queue()
    except ConnectionRefusedError as e:
        raise ConnectionRefusedError("Connection refused to the following address ({}, {}). "
                                     "Actual exception was {}".format(HOST, PORT, e))
    return translation_queue


def send_data_to_daemon(translation_queue, filename: str, language: str):
    translation_queue.put({"filename": filename, "language": language})


def get_data_from_daemon(translation_queue):
    print("Translating, please wait…")
    while True:
        try:
            data = translation_queue.get(block=False)
        except Empty:
            continue
        except EOFError:
            continue

        for item in data:
            print(item)
        break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="gtanslate 1.0: command line utility for translating text",
                                     usage="gtranslate -f <filename> -l <lang>")
    parser.add_argument("-f", dest="filename", help="<filename>: path to input filename to be translated",
                        required=True, type=str)
    parser.add_argument("-lang", dest="lang", help="<lang>: output language, can be one of \"en\", \"it\" or \"de\"",
                        required=True, type=validate_language)
    args = parser.parse_args()
    queue = __get_the_actual_queue()
    send_data_to_daemon(queue, args.filename, args.lang)
    get_data_from_daemon(queue)
