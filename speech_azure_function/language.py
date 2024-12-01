import logging
import os

import azure.cognitiveservices.speech as speechsdk

# Get the necessary values for the azure speech key and region for Speech Language
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")
# AZURE_SPEECH_ENDPOINT = os.getenv("AZURE_SPEECH_ENDPOINT")


def speech_language_detection_once_from_file(filepath):
    """
    Perform one-shot speech language detection with input from an audio file.

    Parameters:
    filepath (os.PathLike): The path to the audio file to be used for language detection.

    Returns:
    str: The detected language code if speech is recognized, otherwise None.

    Notes:
    - The function creates an `AutoDetectSourceLanguageConfig` with a list of possible spoken languages.
    - A `SpeechConfig` is created using the Azure Speech key and endpoint.
    - An `AudioConfig` is created from the provided WAV file.
    - A `SourceLanguageRecognizer` is initialized with the speech, auto-detect language, and audio configurations.
    - The recognizer performs language detection with the `recognize_once` method.
    - If speech is detected, the function logs the detected language and returns the language code.
    - If no speech is recognized or the process is canceled, the function logs the corresponding information and returns None.

    Example:
    >>> detected_language = speech_language_detection_once_from_file("path/to/audio.wav")
    >>> print(detected_language)
    "en-US"
    """

    # Creates an AutoDetectSourceLanguageConfig, which defines a number of possible spoken languages
    auto_detect_source_language_config = (
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
            languages=[
                "en-US",
                "el-GR",
            ]
        )
    )

    # Creates a SpeechConfig from your speech key and region
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION,
        # endpoint=AZURE_SPEECH_ENDPOINT,
    )

    # Creates an AudioConfig from a given WAV file
    audio_config = speechsdk.audio.AudioConfig(filename=filepath)

    # Creates a source language recognizer using a file as audio input, also specify the speech language
    source_language_recognizer = speechsdk.SourceLanguageRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_source_language_config,
        audio_config=audio_config,
    )

    result = source_language_recognizer.recognize_once()

    # Check the result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        detected_src_lang = result.properties[
            speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
        ]
        logging.info("Speech detected!")
    elif result.reason == speechsdk.ResultReason.NoMatch:
        logging.info(
            "No speech could be recognized: {}".format(result.no_match_details)
        )
        detected_src_lang = None
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        logging.error(
            "Speech Language Detection canceled: {} with error {}".format(
                cancellation_details.reason, cancellation_details.error_details
            )
        )
        # detected_src_lang = "el-GR"
        raise "Speech Language Detection canceled"
    return detected_src_lang
