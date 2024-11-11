import argparse
from pathlib import Path
from ffmpeg_utils import extract_mp3, chunking
from whisper_utils import get_transcription
from srt_utils import merge_srt
from openai import OpenAI


def main(video_path, api_key=None):
    SRC_MKV = Path(video_path)
    mp3_path = extract_mp3(SRC_MKV)
    chunk_paths = chunking(mp3_path)

    if not api_key:
        with open("./api_key") as fp:
            api_key = fp.read().strip()
    client = OpenAI(api_key=api_key)

    srt_paths = get_transcription(
        client=client, chunk_paths=chunk_paths, output_format="srt"
    )
    merge_srt(srt_paths, SRC_MKV.stem)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract subtitles from a video file.")
    parser.add_argument("video_path", type=str, help="Path to the video file.")
    parser.add_argument("--api_key", type=str, help="API key for OpenAI.", default=None)

    args = parser.parse_args()
    main(args.video_path, args.api_key)
