from __future__ import annotations

import io
import os
import tempfile
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field


class Note(BaseModel):
    kind: Literal["note"] = "note"
    pitch: int = Field(..., ge=0, le=127)
    duration: float = Field(..., gt=0.0)
    velocity: int = Field(64, ge=0, le=127)
    offset: float = Field(0.0, ge=0.0)
    tied: bool = False


class Chord(BaseModel):
    kind: Literal["chord"] = "chord"
    notes: list[Note] = Field(..., min_length=2)
    duration: float = Field(..., gt=0.0)
    offset: float = Field(0.0, ge=0.0)


Event = Annotated[Union[Note, Chord], Field(discriminator="kind")]


class Measure(BaseModel):
    number: int = Field(..., ge=1)
    time_signature: str = "4/4"
    tempo_bpm: Optional[float] = None
    events: list[Event] = Field(default_factory=list)


class Part(BaseModel):
    name: str = "Piano"
    instrument_midi: int = Field(0, ge=0, le=127)
    measures: list[Measure] = Field(default_factory=list)


class Piece(BaseModel):
    title: str = "Untitled"
    composer: str = ""
    tempo_bpm: float = Field(120.0, gt=0)
    parts: list[Part] = Field(default_factory=list)

    def to_midi(self) -> bytes:
        import mido

        TICKS_PER_BEAT = 480
        mid = mido.MidiFile(type=1, ticks_per_beat=TICKS_PER_BEAT)

        # Track 0: tempo + title
        tempo_track = mido.MidiTrack()
        mid.tracks.append(tempo_track)
        tempo_track.append(
            mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(self.tempo_bpm), time=0)
        )
        tempo_track.append(
            mido.MetaMessage("track_name", name=self.title[:30], time=0)
        )

        for part in self.parts:
            track = mido.MidiTrack()
            mid.tracks.append(track)

            # Build absolute-tick event list.
            # Each entry: (abs_tick, sort_priority, msg_type, pitch, velocity)
            # sort_priority: 0=note_off before 1=note_on at the same tick.
            abs_events: list[tuple[int, int, str, int, int]] = []

            measure_offset_quarters = 0.0
            for measure in part.measures:
                try:
                    num_s, den_s = measure.time_signature.split("/")
                    beats_per_measure = int(num_s) * 4.0 / int(den_s)
                except Exception:
                    beats_per_measure = 4.0

                for event in measure.events:
                    abs_start = measure_offset_quarters + event.offset
                    abs_on = int(abs_start * TICKS_PER_BEAT)

                    if isinstance(event, Note):
                        abs_off = int((abs_start + event.duration) * TICKS_PER_BEAT)
                        abs_events.append((abs_on, 1, "note_on", event.pitch, event.velocity))
                        abs_events.append((abs_off, 0, "note_off", event.pitch, 0))
                    else:  # Chord
                        abs_off = int((abs_start + event.duration) * TICKS_PER_BEAT)
                        for n in event.notes:
                            abs_events.append((abs_on, 1, "note_on", n.pitch, n.velocity))
                            abs_events.append((abs_off, 0, "note_off", n.pitch, 0))

                measure_offset_quarters += beats_per_measure

            # Sort: ascending tick, then note_off (0) before note_on (1)
            abs_events.sort(key=lambda e: (e[0], e[1]))

            # Program change at delta=0 before any notes
            track.append(
                mido.Message("program_change", program=part.instrument_midi, time=0)
            )

            prev_tick = 0
            for abs_tick, _priority, msg_type, pitch, velocity in abs_events:
                delta = abs_tick - prev_tick
                track.append(
                    mido.Message(msg_type, note=pitch, velocity=velocity, time=delta)
                )
                prev_tick = abs_tick

        buf = io.BytesIO()
        mid.save(file=buf)
        return buf.getvalue()

    def to_musicxml(self) -> str:
        from music21 import chord as m21chord
        from music21 import meter
        from music21 import note as m21note
        from music21 import stream
        from music21 import tempo as m21tempo
        from music21.pitch import Pitch

        score = stream.Score()
        score.insert(0, m21tempo.MetronomeMark(number=self.tempo_bpm))

        for part in self.parts:
            m21_part = stream.Part()
            m21_part.id = part.name

            for measure in part.measures:
                m21_measure = stream.Measure(number=measure.number)
                m21_measure.insert(0, meter.TimeSignature(measure.time_signature))

                for event in measure.events:
                    if isinstance(event, Note):
                        n = m21note.Note()
                        n.pitch = Pitch(midi=event.pitch)
                        n.quarterLength = event.duration
                        n.volume.velocity = event.velocity
                        m21_measure.insert(event.offset, n)
                    else:  # Chord
                        pitches = [Pitch(midi=n.pitch) for n in event.notes]
                        c = m21chord.Chord(pitches)
                        c.quarterLength = event.duration
                        m21_measure.insert(event.offset, c)

                m21_part.append(m21_measure)

            score.append(m21_part)

        # Write to TemporaryDirectory so cleanup is guaranteed
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = os.path.join(tmpdir, "score.musicxml")
            actual_path = score.write("musicxml", fp=tmp_path)
            read_path = str(actual_path) if actual_path and os.path.exists(str(actual_path)) else tmp_path
            with open(read_path, "r", encoding="utf-8") as f:
                return f.read()
