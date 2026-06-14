from __future__ import annotations

import io
import os
import tempfile
from typing import Annotated, Literal, Optional, Union

import mido
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

TICKS_PER_BEAT = 480


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
        mid = mido.MidiFile(type=1, ticks_per_beat=TICKS_PER_BEAT)

        for part in self.parts:
            track = mido.MidiTrack()
            mid.tracks.append(track)

            tempo_bpm = self.tempo_bpm
            track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(tempo_bpm), time=0))
            track.append(mido.Message("program_change", program=part.instrument_midi, time=0))

            # Build absolute-tick event list
            abs_events: list[tuple[int, str, int, int]] = []
            beats_per_measure = 4.0

            for measure in part.measures:
                bar_offset_beats = (measure.number - 1) * beats_per_measure
                measure_bpm = measure.tempo_bpm or tempo_bpm

                def beats_to_ticks(b: float) -> int:
                    return int(b * TICKS_PER_BEAT)

                for event in measure.events:
                    if isinstance(event, Note):
                        abs_on = beats_to_ticks(bar_offset_beats + event.offset)
                        abs_off = beats_to_ticks(bar_offset_beats + event.offset + event.duration)
                        abs_events.append((abs_on, "note_on", event.pitch, event.velocity))
                        abs_events.append((abs_off, "note_off", event.pitch, 0))
                    elif isinstance(event, Chord):
                        abs_on = beats_to_ticks(bar_offset_beats + event.offset)
                        abs_off = beats_to_ticks(bar_offset_beats + event.offset + event.duration)
                        for n in event.notes:
                            abs_events.append((abs_on, "note_on", n.pitch, n.velocity))
                            abs_events.append((abs_off, "note_off", n.pitch, 0))

            # Sort by absolute tick, then note_off before note_on at same tick
            abs_events.sort(key=lambda e: (e[0], 0 if e[1] == "note_off" else 1))

            # Convert to delta ticks
            prev_tick = 0
            for abs_tick, msg_type, pitch, vel in abs_events:
                delta = abs_tick - prev_tick
                track.append(mido.Message(msg_type, note=pitch, velocity=vel, time=delta))
                prev_tick = abs_tick

            track.append(mido.MetaMessage("end_of_track", time=0))

        buf = io.BytesIO()
        mid.save(file=buf)
        return buf.getvalue()

    def to_musicxml(self) -> str:
        from music21 import chord as m21chord
        from music21 import meter, note as m21note
        from music21 import stream, tempo as m21tempo
        from music21.pitch import Pitch

        score = stream.Score()
        score.insert(0, m21tempo.MetronomeMark(number=self.tempo_bpm))

        for part in self.parts:
            m21_part = stream.Part(id=part.name)
            m21_part.partName = part.name

            for measure in part.measures:
                m21_measure = stream.Measure(number=measure.number)
                m21_measure.append(meter.TimeSignature(measure.time_signature))

                for event in measure.events:
                    if isinstance(event, Note):
                        if event.pitch == 0:
                            n = m21note.Rest(quarterLength=event.duration)
                        else:
                            n = m21note.Note(quarterLength=event.duration)
                            n.pitch = Pitch(midi=event.pitch)
                        n.volume.velocity = event.velocity
                        n.offset = event.offset
                        m21_measure.insert(event.offset, n)
                    elif isinstance(event, Chord):
                        pitches = [Pitch(midi=n.pitch) for n in event.notes]
                        c = m21chord.Chord(pitches, quarterLength=event.duration)
                        m21_measure.insert(event.offset, c)

                m21_part.append(m21_measure)

            score.insert(0, m21_part)

        with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False, mode="w") as f:
            tmp_path = f.name
        try:
            score.write("musicxml", fp=tmp_path)
            with open(tmp_path, encoding="utf-8") as f:
                return f.read()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
