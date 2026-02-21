import shlex
import subprocess
from pathlib import Path

from app.schemas.clip import ClipCandidate


def extract_audio(video_path: Path, audio_path: Path) -> None:
    cmd = f"ffmpeg -y -i {shlex.quote(str(video_path))} -vn -acodec pcm_s16le -ar 16000 -ac 1 {shlex.quote(str(audio_path))}"
    subprocess.run(cmd, shell=True, check=True)


def render_vertical_clip(
    video_path: Path,
    output_path: Path,
    candidate: ClipCandidate,
    subtitle_path: Path,
) -> None:
    duration = max(0.1, candidate.end_time - candidate.start_time)
    vf = (
        "crop='if(gte(iw/ih,9/16),ih*9/16,iw)':'if(gte(iw/ih,9/16),ih,iw*16/9)',"
        "scale=1080:1920:flags=lanczos,"
        f"subtitles={shlex.quote(str(subtitle_path))}:force_style='FontSize=16,Alignment=2',"
        "drawtext=text='HOOK':fontcolor=white:fontsize=54:x=(w-text_w)/2:y=120:"
        "box=1:boxcolor=black@0.5"
    )
    cmd = (
        f"ffmpeg -y -ss {candidate.start_time} -i {shlex.quote(str(video_path))} -t {duration} "
        f"-vf \"{''.join(vf)}\" -c:v libx264 -preset medium -crf 22 -c:a aac -b:a 128k "
        f"-movflags +faststart {shlex.quote(str(output_path))}"
    )
    subprocess.run(cmd, shell=True, check=True)
