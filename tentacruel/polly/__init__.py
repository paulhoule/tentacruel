# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from pathlib import Path
import boto3
import yaml


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
text = "Thank you very much"
text_name = "tyvm"
response = polly.describe_voices()
voices = [voice["Id"] for voice in response["Voices"] if voice['LanguageCode'].startswith('en')]

target = Path(r"C:\voices")
for voice in voices:
    response = polly.synthesize_speech(
        OutputFormat="mp3",
        VoiceId=voice,
        Text=text
    )
    audio = response["AudioStream"].read()
    write_to = target / (voice.lower() +"-" +text_name + ".mp3")
    write_to.write_bytes(audio)
