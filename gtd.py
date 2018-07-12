#!/usr/local/bin/python3
import sys

import os
import signal
from multiprocessing import Pool

from constants import HOST, PORT, AUTHKEY, QUEUE_NAME
from gcloud_utils.gcloud_api import detect_languages, unpack_translation_arguments
from utils import create_queue

qm = create_queue(HOST, PORT, AUTHKEY, QUEUE_NAME)
queue = qm.translation_queue()


def signal_handler(sig, frame):
    print("Shutting down the queue manager and the google translate daemon.")
    qm.shutdown()
    sys.exit(0)


def reading_file_content(filename: str):
    file_data = []
    with open(filename, "r") as file:
        while True:
            line = file.readline()
            if line and line.strip() != "EOF" and line.strip() != "":
                file_data.append(line.strip())
            else:
                break
    return file_data


def __define_internal_data_to_work_with(filename: str) -> list:
    file_data = reading_file_content(filename)
    languages = detect_languages(file_data)
    data = []
    for i in range(0, len(file_data)):
        data.append({"source_text": file_data[i], "source_language": languages[i]})
    return data


def start_daemon():
    queries_per_second = int(os.environ.get("QUERIES_PER_SEC", 10))

    print("Translation daemon started, throttling at {} queries/second.".format(queries_per_second))
    while True:
        data = queue.get()
        if not data or type(data) != dict:
            queue.put(data)
            continue
        filename = data.get("filename")
        language = data.get("language")
        print("Received the following filename `{}` and target language `{}`. "
              "Starting the translation".format(filename, language))
        internal_data = __define_internal_data_to_work_with(filename)

        pool = Pool(queries_per_second)
        processes_data = []
        for process_data in internal_data:
            processes_data.append((
                process_data.get("source_text"),
                process_data.get("source_language"),
                language
            ))

        results = pool.map_async(unpack_translation_arguments, processes_data)
        pool.close()
        pool.join()
        print("Translation finished successfully. Sending data through the Queue")
        queue.put(results.get())


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    start_daemon()
