import subprocess
import json
import os

input_file = "input.mkv"
output_dir = "hls"

# Create output directory if not exists
os.makedirs(output_dir, exist_ok=True)

# Get audio stream info using ffprobe
probe_cmd = [
    "ffprobe",
    "-v", "error",
    "-select_streams", "a",
    "-show_entries", "stream=index:stream_tags=language",
    "-of", "json",
    input_file
]

result = subprocess.run(probe_cmd, capture_output=True, text=True)
data = json.loads(result.stdout)

# Build map and var_stream_map
map_args = ["-map", "0:v:0"]
var_stream_map = "v:0,agroup:audio"

for i, stream in enumerate(data.get("streams", [])):
    lang = stream.get("tags", {}).get("language", "und")
    map_args.extend(["-map", f"0:a:{i}"])
    var_stream_map += f" a:{i},agroup:audio,language:{lang}"

# Build FFmpeg command
ffmpeg_cmd = [
    "ffmpeg",
    "-i", input_file,
    *map_args,
    "-c:v", "libx264",
    "-c:a", "aac",
    "-b:a", "128k",
    "-f", "hls",
    "-hls_time", "6",
    "-hls_playlist_type", "vod",
    "-hls_flags", "independent_segments",
    "-hls_segment_filename", f"{output_dir}/seg_%v_%03d.ts",
    "-master_pl_name", "master.m3u8",
    "-var_stream_map", var_stream_map,
    f"{output_dir}/out_%v.m3u8"
]

# Run FFmpeg
subprocess.run(ffmpeg_cmd)