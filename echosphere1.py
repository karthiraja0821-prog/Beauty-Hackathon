# app6.py  (SINGLE FILE — same program, only language-gating fix added)
import os, uuid, base64, binascii
import librosa, numpy as np, whisper

from fastapi import FastAPI, UploadFile, File, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi import Request, UploadFile, File, Header
from fastapi import FastAPI, Request
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import Header



# =========================================================
# CONFIG
# =========================================================
UPLOAD_DIR = "uploads"
STATIC_DIR = "static"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

API_KEY = "sk_test_123456789"


SUPPORTED_LANG_MAP = {
    "ta": "Tamil",
    "en": "English",
    "hi": "Hindi",
    "ml": "Malayalam",
    "te": "Telugu",
}
ALLOWED_LANGUAGES = set(SUPPORTED_LANG_MAP.values())

# =========================================================
# APP INIT
# =========================================================
app = FastAPI(title="ECHO SPHERE")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")




@app.post("/github-webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    print(payload)
    return {"status": "received"}

@app.post("/debug/headers")
async def debug_headers(request: Request):
    return {
        "received_headers": dict(request.headers),
        "received_body": (await request.body()).decode("utf-8", errors="ignore")
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🔍 Loading Whisper model…")
whisper_model = whisper.load_model("base")

# =========================================================
# HELPERS
# =========================================================
def detect_language_from_audio(path: str) -> str:
    """
    STRICT supported-language detector (ONLY 5):
    - Returns ONLY: Tamil/English/Hindi/Malayalam/Telugu or "Unknown"
    - Any other language => "Unknown"
    - More stable than a single 30s window: averages language-probabilities over multiple segments
    - Kannada-specific hard-gate to stop Kannada→Tamil confusion
    - Tamil↔Malayalam fix: script-vote tie-break even when probs are "confident"
    """
    audio = whisper.load_audio(path)  # 16k mono float32

    # Limit to 60s
    max_len = 60 * 16000
    if len(audio) > max_len:
        audio = audio[:max_len]

    def _probs_for_offset(offset: int):
        seg = audio[offset: offset + 30 * 16000]
        if len(seg) < 1 * 16000:
            return None
        seg = whisper.pad_or_trim(seg)
        mel = whisper.log_mel_spectrogram(seg).to(whisper_model.device)
        _, probs = whisper_model.detect_language(mel)
        return probs

    # Windows: start / middle / end
    offsets = [0]
    if len(audio) > 35 * 16000:
        offsets.append(max(0, (len(audio) // 2) - 15 * 16000))
    if len(audio) > 50 * 16000:
        offsets.append(max(0, len(audio) - 30 * 16000))

    probs_list = []
    for off in offsets:
        p = _probs_for_offset(off)
        if p:
            probs_list.append(p)

    if not probs_list:
        return "Unknown"

    # Average probabilities across windows
    avg_probs = {}
    for p in probs_list:
        for k, v in p.items():
            avg_probs[k] = avg_probs.get(k, 0.0) + float(v)
    for k in list(avg_probs.keys()):
        avg_probs[k] /= float(len(probs_list))

    # Kannada hard-gate
    top = sorted(avg_probs.items(), key=lambda x: x[1], reverse=True)[:3]
    top_code, top_p = top[0]
    second_code, second_p = (top[1] if len(top) > 1 else ("", 0.0))

    kn_p = float(avg_probs.get("kn", 0.0) or 0.0)
    if kn_p >= 0.08:
        return "Unknown"
    if second_code == "kn" and (top_p - second_p) < 0.20:
        return "Unknown"

    # Helper: unicode script vote from short transcription
    def _script_vote(text: str):
        if not text:
            return None

        counts = {
            "Tamil": 0,      # U+0B80–U+0BFF
            "Malayalam": 0,  # U+0D00–U+0D7F
            "Telugu": 0,     # U+0C00–U+0C7F (note: exclude Kannada block separately)
            "Hindi": 0,      # U+0900–U+097F
            "English": 0,    # basic latin letters
            "Kannada": 0,    # U+0C80–U+0CFF
        }

        for ch in text:
            o = ord(ch)
            if 0x0B80 <= o <= 0x0BFF:
                counts["Tamil"] += 1
            elif 0x0D00 <= o <= 0x0D7F:
                counts["Malayalam"] += 1
            elif 0x0C00 <= o <= 0x0C7F:
                counts["Telugu"] += 1
            elif 0x0C80 <= o <= 0x0CFF:
                counts["Kannada"] += 1
            elif 0x0900 <= o <= 0x097F:
                counts["Hindi"] += 1
            elif ("A" <= ch <= "Z") or ("a" <= ch <= "z"):
                counts["English"] += 1

        # If Kannada letters appear, force Unknown (per your rules)
        if counts["Kannada"] >= 3:
            return "Unknown"

        # Pick dominant script if strong enough
        best_lang = max(
            ["Tamil", "Malayalam", "Telugu", "Hindi", "English"],
            key=lambda k: counts[k]
        )
        if counts[best_lang] >= 6:
            return best_lang

        return None

    # Transcribe a short stable slice for script vote (fast + fixes Tamil↔Malayalam)
    def _short_transcribe_script_vote():
        try:
            seg = audio[: min(len(audio), 25 * 16000)]
            res = whisper_model.transcribe(
                seg,
                task="transcribe",
                fp16=False,
                temperature=0,
                condition_on_previous_text=False
            )
            text = (res.get("text") or "").strip()
            voted = _script_vote(text)
            if voted in ALLOWED_LANGUAGES:
                return voted

            # fallback to whisper's own language only if it's one of your supported ones
            lang2 = res.get("language")
            if isinstance(lang2, str) and lang2 in SUPPORTED_LANG_MAP:
                return SUPPORTED_LANG_MAP[lang2]
        except Exception:
            pass
        return None

    # If top language is NOT one of your 5 => Unknown
    if top_code not in SUPPORTED_LANG_MAP:
        # still allow script vote to rescue supported languages
        voted = _short_transcribe_script_vote()
        return voted if voted else "Unknown"

    # ✅ Main fix:
    # Always run tie-break when Tamil/Malayalam are close OR when top is Malayalam (common failure)
    ta_p = float(avg_probs.get("ta", 0.0) or 0.0)
    ml_p = float(avg_probs.get("ml", 0.0) or 0.0)

    # If Malayalam wins but Tamil is not far behind, use script vote
    if top_code == "ml" and (ml_p - ta_p) < 0.30:
        voted = _short_transcribe_script_vote()
        if voted:
            return voted

    # If Tamil wins but Malayalam is close, use script vote (symmetry)
    if top_code == "ta" and (ta_p - ml_p) < 0.30:
        voted = _short_transcribe_script_vote()
        if voted:
            return voted

    # Original ambiguity check (keep it)
    if top_p < 0.62 or (top_p - second_p) < 0.16:
        voted = _short_transcribe_script_vote()
        if voted:
            return voted
        return "Unknown"

    return SUPPORTED_LANG_MAP.get(top_code, "Unknown")


# =========================================================
# ✅ FEATURE EXTRACTION (UNCHANGED)
# =========================================================
def extract_features(path: str) -> dict:
    y, sr = librosa.load(path, sr=None, mono=True)

    if y is None or sr is None or len(y) < int(sr * 0.6):
        return {
            "pitch_variance": 9999.0,
            "pitch_cv": 9999.0,
            "pitch_diff_std": 9999.0,
            "energy": 0.0,
            "rms_std": 0.0,
            "zcr": 0.0,
            "zcr_std": 0.0,
            "spectral_flatness": 0.0,
            "spectral_flux": 0.0,
            "centroid_std": 0.0,
            "rolloff_std": 0.0,
            "mfcc_delta_std": 9999.0,
            "spec_contrast_std": 9999.0,
            "harmonic_ratio": 0.0,
            "voiced_ratio": 0.0,
        }

    pitch = librosa.yin(y, fmin=50, fmax=400, sr=sr)
    voiced_mask = np.isfinite(pitch)
    voiced_ratio = float(np.mean(voiced_mask)) if pitch.size else 0.0
    pitch_voiced = pitch[voiced_mask]

    if pitch_voiced.size < 12:
        pitch_variance = 9999.0
        pitch_std = 9999.0
        pitch_cv = 9999.0
        pitch_diff_std = 9999.0
    else:
        pitch_mean = float(np.mean(pitch_voiced))
        pitch_variance = float(np.var(pitch_voiced))
        pitch_std = float(np.std(pitch_voiced))
        pitch_cv = float(pitch_std / (pitch_mean + 1e-6))
        pitch_diff_std = float(np.std(np.diff(pitch_voiced))) if pitch_voiced.size > 2 else 9999.0

    rms = librosa.feature.rms(y=y)[0]
    energy = float(np.mean(rms))
    rms_std = float(np.std(rms))

    zcr = librosa.feature.zero_crossing_rate(y)[0]
    zcr_mean = float(np.mean(zcr))
    zcr_std = float(np.std(zcr))

    flatness = librosa.feature.spectral_flatness(y=y)[0]
    spectral_flatness = float(np.mean(flatness))

    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    centroid_std = float(np.std(centroid))

    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85)[0]
    rolloff_std = float(np.std(rolloff))

    S = np.abs(librosa.stft(y, n_fft=1024, hop_length=256))
    if S.shape[1] > 2:
        S_sum = np.sum(S, axis=0, keepdims=True) + 1e-9
        S_norm = S / S_sum
        flux = np.sqrt(np.sum((np.diff(S_norm, axis=1)) ** 2, axis=0))
        spectral_flux = float(np.mean(flux))
    else:
        spectral_flux = 0.0

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_delta = librosa.feature.delta(mfcc, order=1)
    mfcc_delta_std = float(np.mean(np.std(mfcc_delta, axis=1)))

    sc = librosa.feature.spectral_contrast(y=y, sr=sr)
    spec_contrast_std = float(np.mean(np.std(sc, axis=1)))

    y_harm, y_perc = librosa.effects.hpss(y)
    harm_energy = float(np.mean(np.abs(y_harm)))
    perc_energy = float(np.mean(np.abs(y_perc))) + 1e-9
    harmonic_ratio = float(harm_energy / perc_energy)

    return {
        "pitch_variance": pitch_variance,
        "pitch_cv": pitch_cv,
        "pitch_diff_std": pitch_diff_std,
        "energy": energy,
        "rms_std": rms_std,
        "zcr": zcr_mean,
        "zcr_std": zcr_std,
        "spectral_flatness": spectral_flatness,
        "spectral_flux": spectral_flux,
        "centroid_std": centroid_std,
        "rolloff_std": rolloff_std,
        "mfcc_delta_std": mfcc_delta_std,
        "spec_contrast_std": spec_contrast_std,
        "harmonic_ratio": harmonic_ratio,
        "voiced_ratio": voiced_ratio,
    }


# =========================================================
# ✅ CLASSIFIER (UNCHANGED)
# =========================================================
def classify_voice(f: dict):
    import math

    ai_points = 0.0
    max_points = 15.0
    triggers = []

    pv  = float(f.get("pitch_variance", 9999.0))
    pcv = float(f.get("pitch_cv", 9999.0))
    pds = float(f.get("pitch_diff_std", 9999.0))

    e  = float(f.get("energy", 0.0))
    es = float(f.get("rms_std", 0.0))

    z  = float(f.get("zcr", 0.0))
    zs = float(f.get("zcr_std", 0.0))

    sf = float(f.get("spectral_flatness", 0.0))
    fl = float(f.get("spectral_flux", 0.0))
    cs = float(f.get("centroid_std", 0.0))
    rs = float(f.get("rolloff_std", 0.0))

    md  = float(f.get("mfcc_delta_std", 0.0))
    scs = float(f.get("spec_contrast_std", 0.0))

    hr = float(f.get("harmonic_ratio", 0.0))
    vr = float(f.get("voiced_ratio", 0.0))

    # ---------------- AI cues (same cues you already use) ----------------
    if pcv < 0.10:
        ai_points += 1; triggers.append("unnatural pitch steadiness")
    if pds < 2.4:
        ai_points += 1; triggers.append("over-smooth pitch motion")
    if pv < 80:
        ai_points += 1; triggers.append("low pitch variability")

    if es < 0.011:
        ai_points += 1; triggers.append("over-consistent loudness")
    if e < 0.018:
        ai_points += 1; triggers.append("unnaturally low energy")
    if e > 0.140:
        ai_points += 1; triggers.append("over-processed energy level")

    if zs < 0.010:
        ai_points += 1; triggers.append("stable voicing/noise profile")
    if z < 0.032 or z > 0.190:
        ai_points += 1; triggers.append("abnormal fine-grain noise pattern")

    if fl < 0.085:
        ai_points += 1; triggers.append("over-smooth spectral transitions")
    if cs < 260:
        ai_points += 1; triggers.append("uniform articulation dynamics")
    if rs < 900:
        ai_points += 1; triggers.append("stable spectral rolloff")

    if md < 7.5:
        ai_points += 1; triggers.append("over-smooth MFCC dynamics")
    if scs < 6.0:
        ai_points += 1; triggers.append("limited timbre contrast variation")

    if sf < 0.010 or sf > 0.200:
        ai_points += 1; triggers.append("spectral flatness anomaly")

    if hr > 4.0 or hr < 0.7:
        ai_points += 1; triggers.append("harmonic balance anomaly")

    # ---------------- scoring + calibration (key upgrade) ----------------
    raw_ai = ai_points / max_points  # keep your original meaning

    # Count "key" AI cues that are especially strong for synthetic speech
    key_ai_cues = 0
    if fl < 0.085: key_ai_cues += 1
    if md < 7.5:   key_ai_cues += 1
    if scs < 6.0:  key_ai_cues += 1
    if es < 0.011: key_ai_cues += 1
    if pcv < 0.10: key_ai_cues += 1

    # Logistic calibration: improves separation for high-quality TTS/voice-clones
    # (still outputs 0..1; cheap; no training required)
    calibrated_ai = 1.0 / (1.0 + math.exp(-7.0 * (raw_ai - 0.42)))

    # Consistency enforcement:
    # If multiple key cues fire, don't allow a tiny aiScore (prevents your contradiction case)
    if key_ai_cues >= 3:
        calibrated_ai = max(calibrated_ai, 0.60)
    elif key_ai_cues == 2:
        calibrated_ai = max(calibrated_ai, 0.48)

    # Decision with a "grey zone" to avoid confident mistakes
    if calibrated_ai >= 0.55:
        classification = "AI_GENERATED"
        confidence = calibrated_ai
    elif calibrated_ai <= 0.45:
        classification = "HUMAN"
        confidence = 1.0 - calibrated_ai
    else:
        # borderline case: choose a side but keep confidence conservative
        classification = "AI_GENERATED" if calibrated_ai >= 0.50 else "HUMAN"
        confidence = 0.60

    confidence = float(np.clip(confidence, 0.50, 0.99))
    confidence = round(confidence, 2)

    # ---------------- explanation (bug fix + no contradictions) ----------------
    if classification == "AI_GENERATED":
        # show AI reasons, not human reasons
        explanation = ", ".join(triggers[:2]) if triggers else "AI-like speech artifacts detected"
    else:
        # If AI triggers exist but we still say HUMAN, be honest and keep confidence modest (already done)
        human_cues = []
        if pcv >= 0.10: human_cues.append("natural pitch variation")
        if es >= 0.011: human_cues.append("natural loudness variation")
        if fl >= 0.085: human_cues.append("natural spectral dynamics")

        if len(triggers) >= 3:
            # avoids “HUMAN 0.8” + “AI triggers” contradiction
            explanation = "mixed signals: " + ", ".join(triggers[:2])
        else:
            explanation = ", ".join(human_cues[:2]) if human_cues else "Natural human speech variation detected"
            
        print(f"[DEBUG] aiScore={calibrated_ai:.3f}, triggers={triggers}")
        
    #   Return format unchanged: (classification, confidence, explanation, ai_score, triggers)
    #   ai_score should reflect the calibrated score (better for evaluation + consistency)
    return classification, float(confidence), explanation, float(round(calibrated_ai, 3)), triggers


# =========================================================
# DASHBOARD (PROFESSIONAL DARK)  [UNCHANGED]
# =========================================================
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Echosphere</title>
  <link rel="icon" href="/static/voice.png" type="image/png">
  <style>
    body{background:#0b1116;color:#e6f1f5;font-family:Segoe UI,Arial;margin:0}
    .container{max-width:1200px;margin:auto;padding:28px}
    h1{text-align:center;color:#00f7d2;margin:8px 0 18px}
    h4{
    text-align:center;
    color:#86a8ad;
    margin:-10px 0 22px;
    font-weight:500;
    letter-spacing:0.6px;
    }
    .panel{background:#111923;border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:16px;margin:12px 0}
    label{display:block;color:#86a8ad;font-size:13px;margin-bottom:8px}
    input,button{width:100%;padding:12px;border-radius:10px;border:1px solid rgba(255,255,255,.10);background:#0b1116;color:#e6f1f5}
    button{border:0;background:linear-gradient(90deg,#00f7d2,#00c6ff);font-weight:800;color:#001b18;cursor:pointer}
    button:disabled{opacity:.6;cursor:not-allowed}
    pre{background:#0b1116;padding:14px;border-radius:10px;border:1px solid rgba(255,255,255,.08);overflow:auto;max-height:340px}
    .grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
    @media(max-width:900px){.grid{grid-template-columns:1fr}}
    .muted{color:#86a8ad;font-size:12px;line-height:1.5}
  </style>
</head>
<body>
<div class="container">
  <h1>ECHOSPHERE</h1>
    <h4>Decoding Human and AI Speech</h4>
  <div class="panel">
    <label>API Key (x-api-key)</label>
    <input id="key" type="password" value="sk_test_123456789">
    <div class="muted">This is only for testing. Evaluation system will send this header automatically.</div>
  </div>

  <div class="panel">
    <label>Upload MP3 (will be sent as Base64 JSON)</label>
    <input id="file" type="file" accept=".mp3,audio/mpeg">
    <div class="muted">Language is auto-detected by server (no dropdown).</div>
  </div>

  <button id="btn" onclick="run()" disabled>Analyze via Base64 API</button>

  <div class="grid">
    <div class="panel">
      <h3 style="margin:0 0 10px;color:#00f7d2;">Request JSON (preview)</h3>
      <pre id="req">{ "language":"auto-detect", "audioFormat":"mp3", "audioBase64":"(from mp3)" }</pre>
    </div>
    <div class="panel">
      <h3 style="margin:0 0 10px;color:#00f7d2;">Response JSON</h3>
      <pre id="res">Waiting…</pre>
    </div>
  </div>

  <div class="panel">
    <h3 style="margin:0 0 10px;color:#00f7d2;">cURL (copy)</h3>
    <pre id="curl">Select an MP3 file…</pre>
  </div>
</div>

<script>
const fileEl=document.getElementById("file");
const btn=document.getElementById("btn");
const reqEl=document.getElementById("req");
const resEl=document.getElementById("res");
const curlEl=document.getElementById("curl");

fileEl.addEventListener("change", ()=>{
  btn.disabled = !(fileEl.files && fileEl.files.length);
  resEl.textContent="Waiting…";
  reqEl.textContent=JSON.stringify({
    language:"auto-detect",
    audioFormat:"mp3",
    audioBase64:"(from mp3)"
  }, null, 2);
  curlEl.textContent="Ready. Click Analyze…";
});

function toB64(f){
  return new Promise((resolve,reject)=>{
    const rd=new FileReader();
    rd.onload=()=>resolve(String(rd.result).split("base64,")[1]);
    rd.onerror=reject;
    rd.readAsDataURL(f);
  });
}

async function run(){
  const f=fileEl.files[0];
  const k=document.getElementById("key").value.trim();
  if(!f){alert("Select MP3");return;}
  if(!k){alert("Enter API key");return;}

  btn.disabled=true;
  btn.textContent="Analyzing…";
  resEl.textContent="Converting MP3 → Base64…";

  const b64=await toB64(f);

  const payload={
    language:"auto",
    audioFormat:"mp3",
    audioBase64:b64
  };

  reqEl.textContent=JSON.stringify({
    language:"auto-detect",
    audioFormat:"mp3",
    audioBase64:"(base64 from selected mp3)"
  }, null, 2);

  const r=await fetch("/api/voice-detection",{
    method:"POST",
    headers:{"Content-Type":"application/json","x-api-key":k},
    body:JSON.stringify(payload)
  });

  const d=await r.json();
  resEl.textContent=JSON.stringify(d,null,2);

  const shortB64 = b64.slice(0, 80) + "..." + b64.slice(-20);
  curlEl.textContent =
`curl -X POST http://127.0.0.1:8090/api/voice-detection \\
  -H "Content-Type: application/json" \\
  -H "x-api-key: ${k}" \\
  -d '{
    "language": "${(d && d.language) ? d.language : "Tamil"}",
    "audioFormat": "mp3",
    "audioBase64": "${shortB64}"
  }'`;

  btn.disabled=false;
  btn.textContent="Analyze via Base64 API";
}
</script>
</body>
</html>"""


# =========================================================
# FAVICON (prevents Content-Length errors)
# =========================================================
@app.get("/favicon.ico")
def favicon():
    favicon_path = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return Response(status_code=204)


# =========================================================
# ✅ HEALTH CHECK ENDPOINT
# =========================================================
@app.get("/api/health")
def api_health():
    return {"status": "ok", "service": "ai-voice-detection", "version": "1.0"}

@app.post("/api/voice-detection-file")
async def voice_detection_file(
    file: UploadFile = File(...),
    x_api_key: str = Header(None, alias="x-api-key")
):
    # ---------- AUTH ----------
    if (x_api_key or "").strip() != (API_KEY or "").strip():
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid API key or malformed request"}
        )

    # ---------- FILE VALIDATION ----------
    if not file or not file.filename:
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": "Field required: file"}
        )

    ext = os.path.splitext(file.filename.lower())[1]
    if ext not in [".mp3", ".wav", ".m4a", ".aac", ".ogg"]:
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": "Unsupported audio type"}
        )

    # ---------- SAVE ----------
    path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{ext}")
    data = await file.read()
    if not data or len(data) < 2000:
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": "Audio file too small or empty"}
        )

    with open(path, "wb") as f:
        f.write(data)

    # ---------- ANALYZE ----------
    try:
        detected_lang = detect_language_from_audio(path)
        feats = extract_features(path)
        classification, confidence, explanation, _, _ = classify_voice(feats)

        # STRICT format (same as evaluator)
        return {
            "status": "success",
            "language": detected_lang if detected_lang in ALLOWED_LANGUAGES else "Unknown",
            "classification": classification,
            "confidenceScore": float(confidence),
            "explanation": explanation,
        }
    except Exception:
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": "Invalid or unsupported audio"}
        )


# =========================================================
# ✅ EVALUATION API (BASE64 + API KEY)  — SINGLE SOURCE OF TRUTH
# =========================================================
@app.post("/api/voice-detection")
async def voice_detection(
    payload: dict,
    x_api_key: str = Header(None, alias="x-api-key")
):
          # ---------- AUTH ----------
    sent = (x_api_key or "").strip()
    expected = (API_KEY or "").strip()
    if sent != expected:
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid API key or malformed request"}
        )

    # ---------- REQUIRED FIELDS ----------
    # ---------- REQUIRED FIELDS ----------
    language_in = (payload.get("language") or "").strip()
    audio_format = (payload.get("audioFormat") or "").strip().lower()
    audio_b64 = payload.get("audioBase64")
    
# ✅ PATCH: allow missing/empty/auto language
    if (not language_in) or (language_in.lower() in ["auto", "auto-detect", "autodetect"]):
       language_in = "auto"
       
    if not language_in or not audio_format or not audio_b64:
       return JSONResponse(
         status_code=400,
         content={"status": "error", "message": "Missing required fields"}
       )

    if audio_format != "mp3":
       return JSONResponse(
          status_code=400,
          content={"status": "error", "message": "audioFormat must be mp3"}
       )

# ---------- BASE64 → FILE ----------
    try:
      mp3_bytes = base64.b64decode(audio_b64, validate=True)
    except (binascii.Error, ValueError):
      return JSONResponse(
         status_code=422,
         content={"status": "error", "message": "Invalid audioBase64"}
      )

    path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.mp3")
    with open(path, "wb") as f:
         f.write(mp3_bytes)

# ---------- ANALYSIS ----------
    try:
        detected_lang = detect_language_from_audio(path)
        feats = extract_features(path)
        classification, confidence, explanation, _, _ = classify_voice(feats)

        return {
           "status": "success",
           "language": detected_lang if detected_lang in ALLOWED_LANGUAGES else "Unknown",
           "classification": classification,
            "confidenceScore": float(confidence),
            "explanation": explanation,
        }
    except Exception:
        return JSONResponse(
           status_code=422,
           content={"status": "error", "message": "Invalid or unsupported mp3 audio"}
       )
    
# =========================================================
# RUN
# =========================================================
#if __name__ == "__main__":
#    import uvicorn
#    import webbrowser
#    import threading
#    import time

#    HOST = "127.0.0.1"
#    PORT = 8090
#    uvicorn.run(app, host=HOST, port=PORT)

#    def open_browser():
#        time.sleep(1.5)  # wait for server to start
#        webbrowser.open(URL)

#    threading.Thread(target=open_browser, daemon=True).start()

#    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
