from pathlib import Path
from typing import List, Literal

from openai import OpenAI

from time_utils import time_execution


@time_execution
def get_transcription(
    client: OpenAI,
    chunk_paths: List[Path],
    output_format: Literal["srt", "txt"] = "srt",
) -> List[Path]:

    transcription_paths = []
    for chunk_path in chunk_paths:
        with open(chunk_path, "rb") as fp:
            transcription = client.audio.transcriptions.create(
                file=fp, model="whisper-1", response_format=output_format, language="en"
            )

        transcription_path = chunk_path.with_suffix(f".{output_format}")
        transcription_paths.append(transcription_path)

        with open(transcription_path, "w") as fp:
            fp.write(transcription)

        print(f"transcription {output_format} created at: {transcription_path}")

    return transcription_paths
