import asyncio
import os
import shutil
import tempfile

from app.providers.base import AudioProvider, ProviderUnavailableError


class FluidSynthProvider(AudioProvider):
    """FluidSynth subprocess provider. Constructor always succeeds.
    synthesize() checks for the binary at call time.
    """

    def __init__(self, settings) -> None:
        self._sf2_path = settings.soundfont_path

    async def synthesize(self, midi_bytes: bytes, sf2_path: str = "") -> bytes:
        sf2 = sf2_path or self._sf2_path

        if shutil.which("fluidsynth") is None:
            raise ProviderUnavailableError(
                "fluidsynth binary not found. "
                "Install with: apt-get install fluidsynth  (or brew install fluid-synth)"
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            midi_path = os.path.join(tmpdir, "input.mid")
            wav_path = os.path.join(tmpdir, "output.wav")

            with open(midi_path, "wb") as f:
                f.write(midi_bytes)

            cmd = ["fluidsynth", "-ni", sf2, midi_path, "-F", wav_path, "-r", "44100"]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
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
