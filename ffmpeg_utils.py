import math
import subprocess
from pathlib import Path
from typing import List
from datetime import datetime

from time_utils import time_execution


@time_execution
def extract_mp3(src_path: str | Path, qscale=2) -> Path:
    OUTPUT_DIR = Path.cwd() / "tmp"
    src_path = Path(src_path)

    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = (
        OUTPUT_DIR / f'{src_path.stem}_{datetime.now().strftime("%m%d%y-%H%M%S")}.mp3'
    )

    """
    -y                  # Overwrite the output file without asking for confirmation
    -i                  # Input file
    -map 0:a            # Map the audio stream (a) from the first input file (0)
                        # - 0: Refers to the first input file (if there are multiple inputs, the second would be 1, and so on)
                        # - a: Refers to the audio stream in the input file (you can select other streams too, like video or subtitles)
    -c:a libmp3lame     # Set the codec for the audio stream (a) to libmp3lame, which is an MP3 encoder
    -qscale:a 2         # Set the audio quality scale, where lower values represent better quality (2 is high-quality audio)
    """

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(src_path),
        "-map",
        "0:a",
        "-c:a",
        "libmp3lame",
        "-qscale:a",
        str(qscale),
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Check for errors and handle them
    if result.returncode != 0:
        print(f"Error occurred:\n{result.stderr}")
    else:
        print(f"Extracted mp3 file created at: {output_path}")

    return output_path


@time_execution
def chunking(src_path: str | Path) -> List[Path]:
    if isinstance(src_path, str):
        src_path = Path(src_path)

    # Use ffprobe to get the duration and size of the input file
    """
    -i {src_path}                       # Specifies the input file path (replace {src_path} with the actual file path)
    -show_entries format=duration,size  # Instructs ffprobe to show only specific entries from the file's metadata
    -v quiet                            # Suppresses unnecessary log output
    -of csv="p=0"                       # Output format: CSV (Comma-Separated Values)
                                        # - p=0: Removes the header (prints only the raw values of the selected entries)
    """

    cmd = [
        "ffprobe",
        "-i",
        str(src_path),
        "-show_entries",
        "format=duration,size",
        "-v",
        "quiet",
        "-of",
        "csv=p=0",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    duration, size = result.stdout.split(",")
    duration = float(duration)
    size_MB = int(size) / (1024 * 1024)  # Convert size from bytes to MB

    # Calculate the number of chunks and chunk duration
    number_of_chunks = math.ceil(size_MB / 22)  # Aim for ~25MB per chunk
    duration_chunk = duration / number_of_chunks
    duration_chunk = (
        duration_chunk // 300
    ) * 300  # Round duration to nearest 5 minutes (300 seconds)

    # Generate explicit file names and run FFmpeg for each chunk
    output_paths = []
    duration_covered = 0
    for i in range(number_of_chunks):
        output_file = src_path.parent / f"{src_path.stem}_part{i+1}{src_path.suffix}"
        output_paths.append(output_file)

        """
        -i {src_path}                           # Specifies the input file path (replace {src_path} with the actual file path)
        -ss {start_time}                        # Specify the start time for each segment
        -t {duration_chunk}                     # Defines the duration of each segment in seconds
        -c copy                                 # Copies the streams without re-encoding, making the splitting process faster and preserving original quality
        {output_file}                           # Explicitly defined output file name
        """

        start_time = i * duration_chunk  # Start time for each chunk
        cmd = [
            "ffmpeg",
            "-i",
            str(src_path),
            "-ss",
            str(start_time),
            "-t",
            str(duration_chunk),
            "-c",
            "copy",
            str(output_file),
        ]
        subprocess.run(cmd, shell=True)

        print(f"Chunk {i+1}: {output_file} created.")

    # Ensure covering the entire duration, including the last remaining segment if any
    total_covered_duration = number_of_chunks * duration_chunk
    if total_covered_duration < duration:
        start_time = number_of_chunks * duration_chunk
        remaining_duration = duration - start_time
        output_file = (
            src_path.parent
            / f"{src_path.stem}_part{number_of_chunks+1}{src_path.suffix}"
        )
        cmd = [
            "ffmpeg",
            "-i",
            str(src_path),
            "-ss",
            str(start_time),
            "-t",
            str(remaining_duration),
            "-c",
            "copy",
            str(output_file),
        ]
        subprocess.run(cmd, shell=True)
        output_paths.append(output_file)
        print(f"Final chunk: {output_file} created.")

    return output_paths
