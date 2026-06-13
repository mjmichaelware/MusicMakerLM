import logging
import os
import shutil
import subprocess
import tempfile

from app.core.data_model import Piece

logger = logging.getLogger(__name__)


def render_to_musicxml(piece: Piece) -> str:
    return piece.to_musicxml()


def render_to_svg(piece: Piece) -> str:
    """Try Verovio CLI. If absent or it fails, return a fallback string (not real SVG)."""
    musicxml = render_to_musicxml(piece)

    if shutil.which("verovio") is None:
        return (
            "<!-- verovio not installed; returning MusicXML fallback, not SVG -->\n"
            + musicxml
        )

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            in_path = os.path.join(tmpdir, "score.musicxml")
            out_path = os.path.join(tmpdir, "score.svg")
            with open(in_path, "w", encoding="utf-8") as f:
                f.write(musicxml)
            subprocess.run(
                ["verovio", "-f", "musicxml", "-t", "svg", "-o", out_path, in_path],
                check=True,
                capture_output=True,
            )
            with open(out_path, encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        logger.warning("Verovio failed (%s) — returning MusicXML fallback", e)
        return (
            f"<!-- verovio failed ({e}); returning MusicXML fallback, not SVG -->\n"
            + musicxml
        )
