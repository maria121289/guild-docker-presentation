import logging
import os
import tempfile
import uuid

import azure.functions as func
from azure_speech import AzureSpeechServiceTranscription
from language import speech_language_detection_once_from_file
from utils import convert_mp3_to_wav_subprocess

app = func.FunctionApp()


@app.function_name(name="call-center-transcription")
@app.blob_trigger(
    arg_name="myblob",
    path="recordings/{name}.mp3",
    connection="BLOB_CONNECTION_STRING",
)
def blob_trigger(myblob: func.InputStream):
    # Get the file path
    filepath = myblob.name

    # ========================== Extract File Information ==========================

    fullname = filepath.split("/")[-1]
    # Get only the actual filename without the extension
    filename = fullname.split(".")[0]
    logging.info(f"Processing file: {fullname}")

    # ========================== Preprocess Audio Call ==========================

    # Store a file locally
    tempFilePath = tempfile.gettempdir()
    random_id = uuid.uuid4().hex
    temp_audio_path = f"{tempFilePath}/{random_id}_{fullname}"
    with open(temp_audio_path, "wb") as f:
        f.write(myblob.read())
        f.close()

    # Convert the file to WAV format if needed
    filepath_wav = convert_mp3_to_wav_subprocess(
        temp_audio_path, timeout_threshold_seconds=120
    )

    # ========================== Extract Transcription ==========================

    service = AzureSpeechServiceTranscription(
        speech_key=os.getenv("AZURE_SPEECH_KEY"),
        speech_region=os.getenv("AZURE_SPEECH_REGION"),
        continuous_LID=False,
    )

    # Detect the language of the audio file
    detected_language = speech_language_detection_once_from_file(filepath_wav)
    logging.info(f"Detected language: {detected_language}")

    logging.info("Going to transcribe with Speech Service with continous LID")
    transcript = service.transcribe(filepath_wav, language=detected_language)
    logging.info(f"Transcription: {transcript}")
