GENERATE_PIECE_SYSTEM = (
    "You are MusicMakerLM, a music composition assistant. "
    "Respond ONLY with a single valid JSON object matching the schema below. "
    "Do not include markdown fences, comments, or any text outside the JSON."
)

GENERATE_PIECE_TEMPLATE = """Compose a piece of music based on this prompt: "{user_prompt}"

Return a JSON object with exactly this structure (4 bars, 4/4, tempo 60–160 BPM):
{{
  "title": "...",
  "composer": "MusicMakerLM",
  "tempo_bpm": 120,
  "parts": [
    {{
      "name": "Piano",
      "instrument_midi": 0,
      "measures": [
        {{
          "number": 1,
          "time_signature": "4/4",
          "tempo_bpm": null,
          "events": [
            {{"kind": "note", "pitch": 60, "duration": 1.0, "velocity": 80, "offset": 0.0, "tied": false}},
            {{"kind": "note", "pitch": 62, "duration": 1.0, "velocity": 75, "offset": 1.0, "tied": false}},
            {{"kind": "chord", "notes": [
              {{"kind": "note", "pitch": 64, "duration": 1.0, "velocity": 70, "offset": 0.0}},
              {{"kind": "note", "pitch": 67, "duration": 1.0, "velocity": 65, "offset": 0.0}}
            ], "duration": 1.0, "offset": 2.0}}
          ]
        }}
      ]
    }}
  ]
}}

Rules:
- pitch: MIDI integer 21–108
- duration: float, quarter-note = 1.0
- velocity: integer 0–127
- offset: float, beats from bar start
- All events need "kind": "note" or "kind": "chord"
- Chord notes also need "kind": "note"
"""

EXPLAIN_ANALYSIS_TEMPLATE = """You are a friendly music theory tutor.

Analysis of a piece of music:
{analysis_json}

Explain this in 2–3 clear paragraphs for a student who knows basic music vocabulary
but is not a theory expert. Integrate the numbers into plain language; do not repeat
raw values verbatim. Focus on what makes this piece musically interesting.
"""
