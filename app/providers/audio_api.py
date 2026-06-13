from app.providers.base import AudioProvider, ProviderUnavailableError


class APIAudioProvider(AudioProvider):
    """Stub — constructor succeeds; synthesize() raises until Issue #8 is implemented."""

    def __init__(self, settings) -> None:
        self._settings = settings

    async def synthesize(self, midi_bytes: bytes, sf2_path: str = "") -> bytes:
        raise ProviderUnavailableError(
            "API audio provider not implemented in the starting tree. See GitHub Issue #8."
        )
