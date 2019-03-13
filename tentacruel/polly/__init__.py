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
# response = polly.describe_voices()
# voices = [voice["Id"] for voice in response["Voices"] if voice['LanguageCode'].startswith('en')]

clips = [
    ("thank-you", "Thank You"),
    ("bedroom-on", "Would you please turn on the leftmost light switch in the bedroom?"),
    ("hallway-on", "Excuse me.  Would you please toggle the lights in the stairwell?"),
    ("downstairs-on", "Excuse me.  Would you please pull the chain "
                      "on the light at the bottom of the stairs?")
]

target = Path(r"E:\voices")
def speak(text_name, text, voice="Ivy"):
    ssml = "<speak>"
    ssml += f"<break time='0.9s' />"
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
    filename = f"{voice.lower()}-{text_name}"
    complete_to = target / f"{filename}.mp3"
    complete_to.write_bytes(complete_audio)
    complete_file = MP3(complete_to)
    print(complete_file.info.length)

for clip in clips:
    speak(*clip)
