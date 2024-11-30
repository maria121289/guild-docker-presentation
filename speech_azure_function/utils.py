import logging
import os
import subprocess
from datetime import datetime

from pydub import AudioSegment

EMPTY_STRING = ""


def convert_file_to_wav_if_needed(filepath: os.PathLike, sample_rate: int = 16000):
    _, file_extension = os.path.splitext(filepath)
    # get also the file name
    file_name = os.path.basename(filepath)
    if file_extension != ".wav":
        logging.info(
            f"The file extension is {file_extension}, converting to WAV format..."
        )
        # Convert the audio file to WAV format
        audio = AudioSegment.from_file(filepath)
        # Set the frame rate to 16kHz as the speech service requires in this format
        audio = audio.set_frame_rate(sample_rate)
        filepath = f"{os.path.splitext(filepath)[0]}.wav"
        audio.export(filepath, format="wav")
        logging.info(f"File {file_name} converted to WAV format!")
    return filepath, file_extension


def convert_mp3_to_wav_subprocess(
    abs_filepath: os.PathLike,
    sample_rate: str = "16000",
    timeout_threshold_seconds: int = 60,
):
    """
    Convert an MP3 file to WAV format using FFmpeg.

    Parameters:
    abs_filepath (os.PathLike): The absolute file path of the MP3 file to be converted.
    sample_rate (str): The sample rate for the output WAV file (default is "16000").
    timeout_threshold_seconds (int): The timeout threshold in seconds for the conversion process (default is 60).

    Returns:
    os.PathLike: The absolute file path of the converted WAV file if successful;
                 otherwise, returns None if there was an error during conversion.
    """
    _, file_extension = os.path.splitext(abs_filepath)
    if file_extension != ".wav":
        processed_path = abs_filepath.replace(".mp3", ".wav")
        try:
            # convert the file to wav
            subprocess.check_output(
                [
                    "ffmpeg",
                    "-i",
                    abs_filepath,
                    "-f",
                    "wav",
                    "-ar",
                    sample_rate,
                    processed_path,
                ],
                timeout=timeout_threshold_seconds,
            )
            logging.info("Successfully converted to WAV format!")
            return processed_path
        except Exception as e:
            logging.warning(f"Error converting to WAV file {abs_filepath}")
            return None
    return abs_filepath


def bcp47_to_iso6391(locale):
    """
    Convert a BCP-47 locale tag to an ISO 639-1 language code.

    Parameters:
    locale (str): The BCP-47 locale tag (e.g., 'en-US', 'fr-CA').

    Returns:
    str: The ISO 639-1 language code (e.g., 'en', 'fr').
    """
    # Split the BCP-47 tag by hyphen and take the first part
    try:
        iso6391 = locale.split("-")[0]
    except Exception as e:
        iso6391 = "el"
    return iso6391


def extract_filename_info(file_name):
    """
    Extract information from a filename based on a predefined structure.

    Parameters:
    file_name (str): The name of the file to extract information from.

    Returns:
    dict: A dictionary containing the extracted information, including:
        - type (str): The type of call ('inbound' or 'outbound').
        - datetime (str): The datetime of the call in the format "YYYY-MM-DDTHH:MM:SS".
        - phone (str): The phone number.
        - campaign_code (str): The campaign code.
        - campaign_inbound_group (str): The campaign inbound group (if applicable).
        - agent_id (str): The agent ID.
        - unique_recording_id (str): The unique recording ID.
    """
    try:
        # Split the file name by underscore
        parts = file_name.split("_")

        # Datetime of the call and phone number are always the first 2 parts
        date_time = datetime.strptime(parts[0], "%Y%m%d-%H%M%S")
        #  make the datetime to this format "2024-06-30T16:40:00"
        date_time_string = date_time.strftime("%Y-%m-%dT%H:%M:%S")

        date_time = parts[0]
        phone = parts[1]
        # Also campaign code is the thrid element
        campaign_code = parts[2]

        # Determine the type of call based on the number of parts and presence of the unique recording id
        if len(parts) == 5:
            # In this case we are in the old version and have an outbound call
            if parts[3] == "":
                type = "outbound"
                campaign_inbound_group = EMPTY_STRING
                agent_id = parts[4].split("-")[0]
                unique_recording_id = f"{parts[0]}_{phone}_{agent_id}"
            elif len(parts[4]) < 10:
                # in this case we are in the old inbound version
                type = "inbound"
                campaign_inbound_group = parts[3]
                agent_id = parts[4].split("-")[0]
                unique_recording_id = f"{parts[0]}_{phone}_{agent_id}"
            else:
                # In this case we are in the new version and have an outbound call
                type = "outbound"
                campaign_inbound_group = EMPTY_STRING
                agent_id = parts[3]
                unique_recording_id = parts[4].rstrip("-all")

        elif len(parts) == 6:
            # Call that has 6 fields is 100% inbound as described in the docs
            type = "inbound"
            campaign_inbound_group = parts[3]
            agent_id = parts[4]
            unique_recording_id = parts[5].rstrip("-all")
        elif len(parts) == 4:
            # Call that has 6 fields is 100% inbound as described in the docs
            type = "outbound"
            campaign_inbound_group = EMPTY_STRING
            agent_id = parts[3].split("-")[0]
            unique_recording_id = f"{parts[0]}_{phone}_{agent_id}"

        return {
            "type": type,
            "datetime": date_time_string,
            "phone": phone,
            "campaign_code": campaign_code,
            "campaign_inbound_group": campaign_inbound_group,
            "agent_id": agent_id,
            "unique_recording_id": unique_recording_id,
        }
    except Exception as e:
        logging.warning(f"Error extracting info for file {file_name}")
        logging.warning(f"The error is: {e}")
        return {
            "type": EMPTY_STRING,
            "datetime": EMPTY_STRING,
            "phone": EMPTY_STRING,
            "campaign_code": EMPTY_STRING,
            "campaign_inbound_group": EMPTY_STRING,
            "agent_id": EMPTY_STRING,
            "unique_recording_id": EMPTY_STRING,
        }
