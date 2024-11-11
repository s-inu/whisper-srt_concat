# Usage

place your open AI api key under in `./api_key` , then run

```bash
python ./main.py xxx.mkv # xxx.mkv is the video you want to transcribe
```



this will generate `./tmp/` subdirectory under the current working directory. The slices of audio and srt subtitle files are stored in it.



# Dependencies

- python package
  - openai
- command cli
  - ffmpeg