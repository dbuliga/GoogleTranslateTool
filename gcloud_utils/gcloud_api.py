import json
import requests
import subprocess

from constants import TRANSLATE_REQUEST, DETECT_REQUEST


def get_authorization_bearer():
    process = subprocess.Popen(["gcloud", "auth", "application-default", "print-access-token"], stdout=subprocess.PIPE)
    out, err = process.communicate(timeout=15)
    auth = out.decode().strip()
    return auth


def __format_headers():
    return {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "Bearer {}".format(get_authorization_bearer())
    }


def __format_data_for_detection(file_data: list) -> str:
    formatted_data = []
    for line in file_data:
        formatted_data.append("'q': '{}'".format(line))
    data = ",".join(formatted_data)
    return "{{{}}}".format(data)


# Seems the response comes as list of lists.
# Example:
# "detections": [
#       [
#         {
#           "confidence": 1,
#           "isReliable": false,
#           "language": "en"
#         }
#       ],
#       [
#         {
#           "confidence": 1,
#           "isReliable": false,
#           "language": "zh-TW"
#         }
#       ]
#     ]
def __parsing_detection_response(response_data: dict) -> list:
    languages = []
    for language in response_data.get("data", {}).get("detections", []):
        languages.append(language[0].get("language"))
    return languages


def detect_languages(file_data: list) -> list:
    response = requests.post(DETECT_REQUEST, headers=__format_headers(), data=__format_data_for_detection(file_data))

    if response.status_code == 200:
        response_data = json.loads(response.text)
        return __parsing_detection_response(response_data)
    raise Exception("Unable to detect languages from the provided file_data. "
                    "Response content was: {}".format(response.text))


def __format_data_for_translation(text: str, source_language: str, target_language: str) -> str:
    return "{}".format({"q": text, "source": source_language, "format": "text", "target": target_language})


# Seems the translation response comes in a list
# "translations": [
#       {
#         "translatedText": "La Gran Pirámide de Giza (también conocida como la
#          Pirámide de Khufu o la Pirámide de Keops) es la más antigua y más
#          grande de las tres pirámides en el complejo de la pirámide de Giza."
#       }
#     ]
def __parsing_translation_response(response_data: dict) -> str:
    return response_data.get("data", {}).get("translations", [{"translatedText": ""}])[0].get("translatedText")


def perform_translation(text: str, source_language: str, target_language: str) -> str:
    if source_language == target_language:
        # Since target language is the same as source language, return the given text.
        return text

    data = __format_data_for_translation(text, source_language, target_language)
    response = requests.post(TRANSLATE_REQUEST, headers=__format_headers(), data=data)

    if response.status_code == 200:
        response_data = json.loads(response.text)
        return __parsing_translation_response(response_data)
    raise Exception("Unable to translate lines from the provided file_data. "
                    "Response content was: {}".format(response.text))


def unpack_translation_arguments(args):
    return perform_translation(*args)
