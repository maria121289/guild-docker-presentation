import logging
import os
import time
from typing import Optional

import azure.cognitiveservices.speech as speech_sdk


class AzureSpeechServiceTranscription:
    """
    A class for performing speech transcription using the Azure Speech Service.

    Attributes:
    speech_key (str): Subscription key for the Azure Speech service.
    speech_region (str): Region for the Azure Speech service.
    speech_endpoint (str): Custom endpoint for the Azure Speech service (default is None).
    continuous_LID (bool): Flag to enable continuous Language Identification (default is False).
    possible_languages (list[str]): List of possible languages for language identification (default is ["en-US", "el-Gr"]).
    speech_config (SpeechConfig): Configuration object for the Azure Speech service.
    transcription (list): List to store the transcribed text segments.

    Methods:
    __init__(self, speech_key, speech_region, speech_endpoint=None, continuous_LID=False, possible_languages=["en-US", "el-Gr"]):
        Initializes the AzureSpeechServiceTranscription object with the provided parameters.

    transcribe(self, filepath, language="el-Gr") -> TranscriptionResponse:
        Performs transcription on the specified audio file and returns the transcription result.

    stop_cb(self, evt):
        Callback function to stop the speech recognizer.

    transcribe_sound(self, evt):
        Callback function to handle recognized speech events and store the transcribed text.
    """

    def __init__(
        self,
        speech_key: str,
        speech_region: str,
        speech_endpoint: str = None,
        continuous_LID: bool = False,
        possible_languages: Optional[list[str]] = ["en-US", "el-GR"],
    ):
        self.continuous_LID = continuous_LID
        self.possible_languages = possible_languages
        # # Enable profanity
        # self.speech_config.set_property(
        #     property_id=speech_sdk.PropertyId.SpeechServiceResponse_RequestProfanityFilterTrueFalse,
        #     value="True",
        # )
        if self.continuous_LID:
            if speech_endpoint:
                endpoint_string = speech_endpoint
            else:
                endpoint_string = f"wss://{speech_region}.cognitiveservices.azure.com/speech/universal/v2"
            self.speech_config = speech_sdk.SpeechConfig(
                subscription=speech_key, endpoint=endpoint_string
            )
        else:
            if speech_endpoint:
                self.speech_config = speech_sdk.SpeechConfig(
                    subscription=speech_key, endpoint=speech_endpoint
                )
            else:
                self.speech_config = speech_sdk.SpeechConfig(
                    subscription=speech_key, region=speech_region
                )
        # Set the profanity option
        self.speech_config.set_property(
            property_id=speech_sdk.PropertyId.SpeechServiceResponse_ProfanityOption,
            value="masked",
        )
        self.transcription = []

    def transcribe(self, filepath: os.PathLike, language: Optional[str] = "el-GR"):
        print(f"Transcribing the audio file with SPEECH: {filepath}")
        if self.continuous_LID:
            # Set the LanguageIdMode (Optional; Either Continuous or AtStart are accepted; Default AtStart)
            self.speech_config.set_property(
                property_id=speech_sdk.PropertyId.SpeechServiceConnection_LanguageIdMode,
                value="Continuous",
            )
            auto_detect_source_language_config = (
                speech_sdk.languageconfig.AutoDetectSourceLanguageConfig(
                    languages=self.possible_languages
                )
            )
        else:
            # Set the found language
            self.speech_config.speech_recognition_language = language

        # Initialize audio config
        audio_config = speech_sdk.audio.AudioConfig(
            use_default_microphone=False, filename=filepath
        )

        # Initialize speech recognizer
        # If there is continuous Language Identification add the auto_detect_source_language_config
        self.speech_recognizer = speech_sdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config,
            auto_detect_source_language_config=auto_detect_source_language_config
            if self.continuous_LID
            else None,
        )

        # Set the callbacks
        self.speech_recognizer.recognized.connect(self.transcribe_sound)
        self.speech_recognizer.session_started.connect(
            lambda evt: print("Session Started.")
        )
        self.speech_recognizer.session_stopped.connect(
            lambda evt: print("Session Stopped.")
        )
        self.speech_recognizer.canceled.connect(self.stop_cb)

        self.speech_recognizer.start_continuous_recognition()
        global done
        done = False
        while not done:
            time.sleep(0.5)

        transcription = " ".join(self.transcription)
        return transcription

    def stop_cb(self, evt):
        print("Terminating the speech recognizer...")
        self.speech_recognizer.stop_continuous_recognition()
        global done
        done = True

    def transcribe_sound(self, evt):
        print("SOUND")
        if evt.result.reason == speech_sdk.ResultReason.RecognizedSpeech:
            print("Recognized Text")
            # Append the transcription
            self.transcription.append(evt.result.text)
            self.segments.append(
                {
                    "speaker": evt.result.speaker_id,
                    "start": evt.result.offset,
                    "duration": evt.result.duration,
                }
            )
