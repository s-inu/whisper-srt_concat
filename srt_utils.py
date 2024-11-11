import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from time_utils import time_execution

TS_SEPERATOR = " --> "


def ts_parse(ts: str) -> datetime:
    return datetime.strptime(ts, "%H:%M:%S,%f")


def ts_format(ts: datetime) -> str:
    return datetime.strftime(ts, "%H:%M:%S,%f")[:-3]


def timedelta_from_ts(ts: str) -> timedelta:
    h, m, s, ms = map(int, re.split("[:,]", ts))
    return timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms)


def is_ts_line(line: str) -> bool:
    return TS_SEPERATOR in line


def is_block_number_line(line: str) -> bool:
    return bool(re.match("\d+$", line))


@time_execution
def merge_srt(srt_paths: List[str | Path], output_stem: str) -> None:
    srt_paths = [Path(srt_path) for srt_path in srt_paths]

    output = []
    carryover_time = timedelta()
    last_block_number = 0

    for path in srt_paths:
        with open(path) as fp:
            lines = fp.readlines()

        last_end_ts: str = "00:00:00,000"
        for idx, line in enumerate(lines):
            if is_ts_line(line):
                start_ts, end_ts = line.split(TS_SEPERATOR)

                start_ts = ts_parse(start_ts.strip()) + carryover_time
                end_ts = ts_parse(end_ts.strip()) + carryover_time

                start_ts = ts_format(start_ts)
                end_ts = ts_format(end_ts)

                last_end_ts = end_ts
                lines[idx] = f"{start_ts}{TS_SEPERATOR}{end_ts}\n"

            if is_block_number_line(line):
                last_block_number += 1
                lines[idx] = f"{last_block_number}\n"

        carryover_time = timedelta_from_ts(last_end_ts)
        output.extend(lines)

    merged_output_path = f"{output_stem}.srt"

    with open(merged_output_path, "w", encoding="utf-8") as merged_file:
        merged_file.writelines(output)

    print(f"Merged srt file created at: {merged_output_path}")


@time_execution
def merge_txt(txt_paths: List[str | Path], output_stem: str) -> None:
    txt_paths = [Path(p) for p in txt_paths]

    output_path = txt_paths[0].parent / f"{output_stem}.txt"

    with open(output_path, "w", encoding="utf-8") as outfile:
        for txt_path in txt_paths:
            with open(txt_path, "r", encoding="utf-8") as infile:
                outfile.write(infile.read() + "\n")

    print(f"Merged txt file created at: {output_path}")
