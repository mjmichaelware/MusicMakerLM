from __future__ import annotations

import asyncio
import os
import shutil
import tempfile
from typing import TYPE_CHECKING

from app.providers.base import AudioProvider, ProviderUnavailableError

if TYPE_CHECKING:
    from app.config import Settings


class FluidSynthProvider(AudioProvider):
    """Synthesize WAV from MIDI using the system FluidSynth binary."""

    def __init__(self, settings: "Settings") -> None:
        self._default_sf2 = settings.soundfont_path

    async def synthesize(self, midi_bytes: bytes, sf2_path: str = "") -> bytes:
        if shutil.which("fluidsynth") is None:
            raise ProviderUnavailableError(
                "fluidsynth binary not found. "
                "Install with: apt-get install fluidsynth  (or brew install fluid-synth)"
            )
        sf2 = sf2_path or self._default_sf2
        if not os.path.exists(sf2):
            raise ProviderUnavailableError(
                f"SoundFont not found at {sf2!r}. "
                "Run scripts/download_soundfonts.sh to fetch a free SoundFont."
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            midi_path = os.path.join(tmpdir, "input.mid")
            wav_path = os.path.join(tmpdir, "output.wav")
            with open(midi_path, "wb") as f:
                f.write(midi_bytes)

            proc = await asyncio.create_subprocess_exec(
                "fluidsynth", "-ni", sf2, midi_path, "-F", wav_path, "-r", "44100",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                raise ProviderUnavailableError(
                    f"fluidsynth failed (exit {proc.returncode}): {stderr.decode()}"
                )
            with open(wav_path, "rb") as f:
                return f.read()
