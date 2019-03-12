# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from pathlib import Path
from uuid import uuid4
from xml.sax.saxutils import escape

import boto3
import yaml

from mutagen.mp3 import MP3


def client(service_name, aws_config):
    region_name = aws_config["region_name"]
    aws_access_key_id = aws_config["aws_access_key_id"]
    aws_secret_access_key = aws_config["aws_secret_access_key"]

    return boto3.client(
        service_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

with open(Path.home() / ".tentacruel" / "config.yaml") as a_stream:
    config = yaml.load(a_stream)

polly = client("polly", config["aws"])
text = "Thank you"
text_name = "ty"
# response = polly.describe_voices()
# voices = [voice["Id"] for voice in response["Voices"] if voice['LanguageCode'].startswith('en')]

voices = ["Ivy"]

target = Path(r"C:\voices")
for voice in voices:
    response = polly.synthesize_speech(
        OutputFormat="mp3",
        VoiceId=voice,
        Text=text
    )

    audio = response["AudioStream"].read()
    try:
        write_to = target / (str(uuid4()) + ".mp3")
        write_to.write_bytes(audio)
        audio_file = MP3(write_to)
        durations = list(map(lambda x: 1.0 + 0.2*x, range(0, 10)))
        for duration in durations:
            initial_pad = duration - audio_file.info.length
            ssml = "<speak>"
            ssml += f"<break time='{initial_pad:.2f}s' />"
            ssml += "<amazon:breath duration='x-long' volume='x-loud' />"
            ssml += text
            ssml += "</speak>"
            print(ssml)

            complete_response = polly.synthesize_speech(
                OutputFormat="mp3",
                VoiceId=voice,
                TextType="ssml",
                Text=ssml
            )
            complete_audio = complete_response["AudioStream"].read()
            filename = f"{voice.lower()}-{text_name}-{duration:.1f}"
            complete_to = target / f"{filename}.mp3"
            complete_to.write_bytes(complete_audio)
            complete_file = MP3(complete_to)
            print(complete_file.info.length)
    finally:
        if write_to.exists():
            write_to.unlink()
