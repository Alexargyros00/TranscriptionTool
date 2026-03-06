import argparse
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any
import imageio_ffmpeg
from dotenv import load_dotenv
from openai import OpenAI


WHISPER_MODEL = "whisper-1"
FORMAT_MODEL = "gpt-4.1-mini"
CHUNK_SECONDS = 600


class Segment:
    start: float
    text: str


def parse_args() -> argparse.Namespace:
    # Read the input and output paths from the command line.
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Input .m4a file path")
    parser.add_argument("output_file", help="Output text file path")
    return parser.parse_args()


def chunk_audio(input_path: Path, chunk_dir: Path) -> list[Path]:
    # Split the input audio into fixed-size .m4a chunks before transcription.
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    chunk_pattern = chunk_dir / "chunk_%03d.m4a"
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_path),
        "-f",
        "segment",
        "-segment_time",
        str(CHUNK_SECONDS),
        "-c",
        "copy",
        str(chunk_pattern),
    ]
    subprocess.run(command, check=True)
    chunks = sorted(chunk_dir.glob("chunk_*.m4a"))
    if not chunks:
        raise RuntimeError("No chunks were created.")
    return chunks


def read_field(value: Any, field: str, default: Any = None) -> Any:
    # Read a field from either a dict-like response or an object-like response.
    if isinstance(value, dict):
        return value.get(field, default)
    return getattr(value, field, default)


def transcribe_chunk(client: OpenAI, chunk_path: Path) -> list[Segment]:
    # Send one chunk to Whisper and convert the response into simple Segment objects.
    with chunk_path.open("rb") as audio_file:
        result = client.audio.transcriptions.create(model=WHISPER_MODEL, file=audio_file, response_format="verbose_json")

    raw_segments = read_field(result, "segments", None)
    segments: list[Segment] = []
    if raw_segments:
        for raw in raw_segments:
            text = str(read_field(raw, "text", "")).strip()
            if not text:
                continue
            start = float(read_field(raw, "start", 0.0) or 0.0)
            segment = Segment()
            segment.start = start
            segment.text = text
            segments.append(segment)
        return segments

    text = str(read_field(result, "text", "")).strip()
    if text:
        segment = Segment()
        segment.start = 0.0
        segment.text = text
        return [segment]
    return []


def transcribe_chunks(client: OpenAI, chunks: list[Path]) -> list[Segment]:
    # Transcribe all chunks and shift their timestamps so they match the full file.
    all_segments: list[Segment] = []
    for index, chunk_path in enumerate(chunks):
        print(f"Transcribing chunk {index + 1}/{len(chunks)}: {chunk_path.name}")
        chunk_segments = transcribe_chunk(client, chunk_path)

        # Shift each chunk by its position so timestamps stay global.
        offset = index * CHUNK_SECONDS
        for segment in chunk_segments:
            shifted_segment = Segment()
            shifted_segment.start = segment.start + offset
            shifted_segment.text = segment.text
            all_segments.append(shifted_segment)
    return all_segments


def format_timestamp(seconds: float) -> str:
    # Convert raw seconds into HH:MM:SS format for the final transcript.
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def build_timestamped_text(segments: list[Segment]) -> str:
    # Turn the segment list into plain timestamped lines that GPT can reformat.
    lines = []
    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue
        lines.append(f"[{format_timestamp(segment.start)}] {text}")
    return "\n".join(lines)


def transcript_format(client: OpenAI, timestamped_text: str) -> str:
    # Ask LLM to group the transcript into readable speaker turns.
    prompt = """
        You are given transcript lines with timestamp anchors.
        Task:
        1) Detect speaker turns and infer speaker count automatically.
        2) Output format per line: [HH:MM:SS] Speaker N: text
        3) Keep the original language and wording as much as possible.
        4) Do not summarize or add explanations.
        5) Return only the formatted transcript.
    """

    response = client.responses.create(model=FORMAT_MODEL, input=[{"role": "system", "content": prompt}, {"role": "user", "content": timestamped_text}])
    return response.output_text.strip()


def run() -> None:
    # Orchestrate the full flow: validate input, chunk audio, transcribe, format, and save.
    args = parse_args()
    input_path = Path(args.input_file)
    output_path = Path(args.output_file)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return
    if input_path.suffix.lower() != ".m4a":
        print("Please provide a .m4a file.")
        return

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is missing.")
        return

    client = OpenAI(api_key=api_key)

    with tempfile.TemporaryDirectory(prefix="audio_chunks_") as temp_dir:
        chunk_dir = Path(temp_dir)
        chunks = chunk_audio(input_path, chunk_dir)
        segments = transcribe_chunks(client, chunks)

    if not segments:
        print("No transcript was produced.")
        return

    timestamped_text = build_timestamped_text(segments)
    formatted_text = transcript_format(client, timestamped_text)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(formatted_text, encoding="utf-8")
    print(f"Transcript saved to: {output_path}")


if __name__ == "__main__":
    run()
