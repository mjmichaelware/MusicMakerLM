const API = "/api/v1";

const promptEl       = document.getElementById("prompt");
const generateBtn    = document.getElementById("generate-btn");
const statusEl       = document.getElementById("status");
const resultsEl      = document.getElementById("results");
const scoreEl        = document.getElementById("score-container");
const playerEl       = document.getElementById("player");
const audioUnavailEl = document.getElementById("audio-unavailable");
const midiDlEl       = document.getElementById("midi-download");
const analysisEl     = document.getElementById("analysis-output");
const explanationEl  = document.getElementById("explanation-output");

function setStatus(msg, show = true) {
  statusEl.textContent = msg;
  statusEl.classList.toggle("hidden", !show);
}

function b64ToBlob(b64, mimeType) {
  const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  return new Blob([bytes], { type: mimeType });
}

generateBtn.addEventListener("click", async () => {
  const prompt = promptEl.value.trim();
  if (!prompt) return;

  generateBtn.disabled = true;
  setStatus("Generating...");
  resultsEl.classList.add("hidden");

  try {
    // --- Generate ---
    const genRes = await fetch(`${API}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    if (!genRes.ok) throw new Error(`Generate failed: ${genRes.status}`);
    const gen = await genRes.json();

    // MusicXML display (OSMD deferred — Issue #3)
    scoreEl.textContent = gen.musicxml;

    // MIDI download link (MIDI is for download; browsers don't play .mid natively)
    const midBlob = b64ToBlob(gen.midi_b64, "audio/midi");
    midiDlEl.href = URL.createObjectURL(midBlob);
    midiDlEl.classList.remove("hidden");

    // WAV audio player — only when FluidSynth was available
    if (gen.wav_b64) {
      const wavBlob = b64ToBlob(gen.wav_b64, "audio/wav");
      playerEl.src = URL.createObjectURL(wavBlob);
      playerEl.classList.remove("hidden");
      audioUnavailEl.classList.add("hidden");
    } else {
      playerEl.classList.add("hidden");
      audioUnavailEl.classList.remove("hidden");
    }

    setStatus("Analyzing...");

    // --- Teach (analysis + explanation in one call) ---
    const teachRes = await fetch(`${API}/teach`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ piece_json: gen.piece_json }),
    });
    if (!teachRes.ok) throw new Error(`Teach failed: ${teachRes.status}`);
    const teach = await teachRes.json();

    analysisEl.textContent = JSON.stringify(teach.analysis, null, 2);
    explanationEl.textContent = teach.explanation;

    resultsEl.classList.remove("hidden");
    setStatus("", false);
  } catch (err) {
    setStatus(`Error: ${err.message}`);
  } finally {
    generateBtn.disabled = false;
  }
});
