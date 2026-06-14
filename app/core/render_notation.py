from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

from app.core.data_model import Piece


def render_to_musicxml(piece: Piece) -> str:
    return piece.to_musicxml()


def render_to_svg(piece: Piece) -> str:
    """
    Returns an SVG string if the Verovio CLI is installed.
    Falls back to a plain string (MusicXML with a comment header) otherwise.
    Tests should only assert non-empty fallback, not SVG validity.
    """
    xml = render_to_musicxml(piece)

    if shutil.which("verovio") is None:
        return f"<!-- verovio not installed; MusicXML follows -->\n{xml}"

    with tempfile.TemporaryDirectory() as d:
        in_path = os.path.join(d, "score.musicxml")
        out_path = os.path.join(d, "score.svg")
        with open(in_path, "w", encoding="utf-8") as f:
            f.write(xml)
        try:
            subprocess.run(
                ["verovio", "-f", "musicxml", "-t", "svg", "-o", out_path, in_path],
                check=True,
                capture_output=True,
            )
            with open(out_path, encoding="utf-8") as f:
                return f.read()
        except subprocess.CalledProcessError as e:
            return f"<!-- verovio failed: {e.stderr.decode()[:200]} -->\n{xml}"
