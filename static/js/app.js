const API = "/api/v1";

const promptEl       = document.getElementById("prompt");
const generateBtn    = document.getElementById("generate-btn");
const statusEl       = document.getElementById("status");
const playerEl       = document.getElementById("player");
const audioUnavail   = document.getElementById("audio-unavailable");
const midiDownload   = document.getElementById("midi-download");
const scoreContainer = document.getElementById("score-container");
const analysisOut    = document.getElementById("analysis-output");
const explanationOut = document.getElementById("explanation-output");

function setStatus(msg, isError = false) {
  statusEl.textContent = msg;
  statusEl.className = isError ? "error" : "";
}

function b64ToBlob(b64, type) {
  const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  return new Blob([bytes], { type });
}

generateBtn.addEventListener("click", async () => {
  const prompt = promptEl.value.trim();
  if (!prompt) { setStatus("Enter a prompt first.", true); return; }

  generateBtn.disabled = true;
  setStatus("Generating…");
  scoreContainer.textContent = "";
  analysisOut.textContent = "";
  explanationOut.textContent = "";
  playerEl.src = "";
  midiDownload.style.display = "none";
  audioUnavail.style.display = "none";

  try {
    // 1. Generate
    const genRes = await fetch(`${API}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    if (!genRes.ok) throw new Error(`Generate failed: ${genRes.status}`);
    const gen = await genRes.json();

    // Show MusicXML (OSMD will replace this in Issue #3)
    scoreContainer.textContent = gen.musicxml;

    // Audio player — WAV if available, else show unavailable message
    if (gen.wav_b64) {
      const wavBlob = b64ToBlob(gen.wav_b64, "audio/wav");
      playerEl.src = URL.createObjectURL(wavBlob);
      playerEl.style.display = "";
      audioUnavail.style.display = "none";
    } else {
      playerEl.style.display = "none";
      audioUnavail.style.display = "";
    }

    // MIDI download link
    const midiBlob = b64ToBlob(gen.midi_b64, "audio/midi");
    midiDownload.href = URL.createObjectURL(midiBlob);
    midiDownload.download = (gen.piece_json.title || "piece") + ".mid";
    midiDownload.style.display = "";

    setStatus("Analyzing and explaining…");

    // 2. Teach
    const teachRes = await fetch(`${API}/teach`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ piece_json: gen.piece_json }),
    });
    if (!teachRes.ok) throw new Error(`Teach failed: ${teachRes.status}`);
    const teach = await teachRes.json();

    analysisOut.textContent = JSON.stringify(teach.analysis, null, 2);
    explanationOut.textContent = teach.explanation;
    setStatus("Done.");
  } catch (err) {
    setStatus(err.message, true);
  } finally {
    generateBtn.disabled = false;
  }
});
