import { useEffect, useRef, useState } from "react";
import {
  ArrowUpRight,
  CheckCircle2,
  Clapperboard,
  Clock3,
  Cpu,
  Download,
  Film,
  Globe,
  Info,
  Languages,
  LoaderCircle,
  Mic,
  MicOff,
  Play,
  RotateCcw,
  Sliders,
  Sparkles,
  StopCircle,
  Subtitles,
  Video,
  Volume2,
  WandSparkles,
} from "lucide-react";

const languages = [
  { id: "mr", label: "मराठी (Marathi)", icon: "🚩", flag: "MR" },
  { id: "hi", label: "हिंदी (Hindi)", icon: "🇮🇳", flag: "HI" },
  { id: "en", label: "English", icon: "🌐", flag: "EN" },
];

const styles = [
  "Cinematic",
  "Cartoon",
  "Cyberpunk",
  "Educational",
  "Fantasy",
  "Story",
  "Nursery Rhyme",
];

const durationPresets = [15, 30, 60, 90, 120, 180, 300];

const aspectRatios = [
  { id: "9:16", label: "9:16", desc: "Shorts & Reels", tag: "Recommended" },
  { id: "16:9", label: "16:9", desc: "YouTube Landscape", tag: "Widescreen" },
  { id: "1:1", label: "1:1", desc: "Square Post", tag: "Instagram" },
];

const engineModes = [
  { id: "auto", label: "Auto (AI Video with Procedural Fallback)" },
  { id: "procedural", label: "Procedural 2D Engine (100% Free / Local Fast)" },
  { id: "ai_video", label: "AI Video Generation (Requires API Key)" },
];

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const samplePromptsByLang = {
  mr: [
    { text: "एका छोट्या मांजरीने गावातल्या सगळ्यांना हसवलं.", style: "Cartoon", note: "मांजर व गाव" },
    { text: "एका हुशार मुलीने आपल्या गावाला पाण्याच्या समस्येतून वाचवलं.", style: "Story", note: "हुशार मुलगी" },
    { text: "एक गरीब मुलगा मेहनत करून मोठं यश मिळवतो.", style: "Story", note: "कष्टाळू मुलगा" },
    { text: "एका जादुई तळ्यात एक सुंदर गुलाबी कमळ नाचतं.", style: "Cinematic", note: "गुलाबी कमळ" },
  ],
  hi: [
    { text: "एक छोटा हाथी जंगल में अपना खोया हुआ दोस्त ढूँढता है।", style: "Story", note: "छोटा हाथी" },
    { text: "एक गरीब लड़का मेहनत करके बड़ा अफसर बनता है।", style: "Story", note: "मेहनती लड़का" },
    { text: "जादुई तालाब पर एक गुलाबी कमल खिलकर नाचता है।", style: "Cinematic", note: "गुलाबी कमल" },
    { text: "एक नन्हा डायनासोर जंगल का सबसे मशहूर डांसर बनता है।", style: "Cartoon", note: "डायनासोर" },
  ],
  en: [
    { text: "A tiny pink lotus dances on a magical pond.", style: "Cinematic", note: "Lotus & Water" },
    { text: "A funny baby dinosaur tries to become a famous dancer.", style: "Cartoon", note: "Dancing Dino" },
    { text: "A sleek red sports car zooming down a neon cyberpunk highway in the rain.", style: "Cyberpunk", note: "Sports Car" },
    { text: "A friendly astronaut repairing a solar satellite in deep space.", style: "Cinematic", note: "Astronaut" },
  ],
};

function App() {
  const [language, setLanguage] = useState("mr");
  const [prompt, setPrompt] = useState("एका छोट्या मांजरीने गावातल्या सगळ्यांना हसवलं.");
  const [style, setStyle] = useState("Cartoon");
  const [duration, setDuration] = useState(15);
  const [customDuration, setCustomDuration] = useState(false);
  const [aspectRatio, setAspectRatio] = useState("9:16");
  const [engineMode, setEngineMode] = useState("auto");

  // Narration and Subtitle controls
  const [narrationEnabled, setNarrationEnabled] = useState(true);
  const [voiceGender, setVoiceGender] = useState("female");
  const [showSubtitles, setShowSubtitles] = useState(true);

  const [storyboard, setStoryboard] = useState(null);
  const [status, setStatus] = useState("empty");
  const [error, setError] = useState("");

  // Video generation state
  const [currentJobId, setCurrentJobId] = useState(null);
  const [videoStatus, setVideoStatus] = useState("idle"); // idle | rendering | ready | failed | cancelled
  const [videoProgress, setVideoProgress] = useState(0);
  const [videoStage, setVideoStage] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const [videoError, setVideoError] = useState("");
  const [providerMeta, setProviderMeta] = useState(null);

  const pollIntervalRef = useRef(null);

  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, []);

  function handleLanguageChange(newLang) {
    setLanguage(newLang);
    const defaultSample = samplePromptsByLang[newLang]?.[0];
    if (defaultSample) {
      setPrompt(defaultSample.text);
      setStyle(defaultSample.style);
    }
  }

  async function generateStoryboard(event) {
    if (event) event.preventDefault();
    if (prompt.trim().length < 3) {
      setError("Please describe a character, story, action, or scene.");
      setStatus("error");
      return;
    }

    setStatus("loading");
    setError("");
    setVideoStatus("idle");
    setVideoUrl("");
    setProviderMeta(null);
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);

    try {
      const response = await fetch(`${API_BASE}/api/storyboard`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt.trim(),
          style,
          duration,
          aspect_ratio: aspectRatio,
          language,
          engine_mode: engineMode,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail?.[0]?.msg || errorData?.detail || "Storyboard generation failed.");
      }

      const data = await response.json();
      setStoryboard(data);
      setStatus("success");
    } catch (requestError) {
      setError(
        requestError.message.includes("fetch")
          ? "Could not connect to FastAPI server at " + API_BASE + ". Please ensure the backend is running (uvicorn backend.main:app)."
          : requestError.message,
      );
      setStatus("error");
    }
  }

  async function startRenderVideo() {
    if (!prompt.trim() || prompt.trim().length < 3) {
      setError("Prompt is required to render animated video.");
      return;
    }

    setVideoStatus("rendering");
    setVideoProgress(3);
    setVideoStage("Queuing animation render pipeline...");
    setVideoError("");
    setProviderMeta(null);

    try {
      const response = await fetch(`${API_BASE}/api/render-video`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt.trim(),
          style,
          duration,
          aspect_ratio: aspectRatio,
          language,
          narration_enabled: narrationEnabled,
          voice_gender: voiceGender,
          show_subtitles: showSubtitles,
          engine_mode: engineMode,
          scenes: storyboard?.scenes || null,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to start video rendering job.");
      }

      const { job_id } = await response.json();
      setCurrentJobId(job_id);

      // Poll video rendering status
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = setInterval(async () => {
        try {
          const statusRes = await fetch(`${API_BASE}/api/video-status/${job_id}`);
          if (!statusRes.ok) return;
          const statusData = await statusRes.json();

          setVideoProgress(statusData.progress || 0);
          setVideoStage(statusData.stage || "Rendering frames...");

          if (statusData.status === "completed") {
            clearInterval(pollIntervalRef.current);
            setVideoUrl(`${API_BASE}${statusData.video_url}`);
            setProviderMeta({
              used: statusData.provider_used,
              name: statusData.provider_name,
              fallbackReason: statusData.fallback_reason,
            });
            setVideoStatus("ready");
          } else if (statusData.status === "failed") {
            clearInterval(pollIntervalRef.current);
            setVideoStatus("failed");
            setVideoError(statusData.error || "Video rendering failed. Please try again.");
          } else if (statusData.status === "cancelled") {
            clearInterval(pollIntervalRef.current);
            setVideoStatus("cancelled");
            setVideoStage("Rendering cancelled by user.");
          }
        } catch {
          // Keep polling on transient network delay
        }
      }, 1000);
    } catch (err) {
      setVideoStatus("failed");
      setVideoError(err.message || "Could not start video generation.");
    }
  }

  async function cancelRender() {
    if (!currentJobId) return;
    try {
      await fetch(`${API_BASE}/api/cancel-job/${currentJobId}`, { method: "POST" });
      setVideoStage("Cancellation requested...");
    } catch (e) {
      console.error("Cancel failed:", e);
    }
  }

  const currentSamplePrompts = samplePromptsByLang[language] || samplePromptsByLang.en;

  return (
    <main className="app-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      {/* Top Navbar */}
      <nav className="topbar">
        <a className="brand" href="/">
          <span className="brand-mark"><Clapperboard size={18} /></span>
          <span>FrameFlow <em>AI</em></span>
        </a>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <span className="beta-pill"><span className="pulse-dot" /> Hindi & Marathi Animation Studio</span>
        </div>
      </nav>

      {/* Hero Header */}
      <section className="hero">
        <div className="eyebrow"><Sparkles size={15} /> Real AI & Procedural 2D Animation Studio</div>
        <h1>Any story.<br /><span>Rendered frame by frame.</span></h1>
        <p className="hero-copy">
          Create engaging Hindi, Marathi, and English animated videos for YouTube Shorts and Instagram Reels.
          Features procedural 2D characters, dynamic parallax environments, virtual cameras, neural voiceovers, and native Devanagari subtitles.
        </p>

        {/* Language Tabs */}
        <div className="language-selector" style={{ marginTop: "24px" }}>
          {languages.map((l) => (
            <button
              key={l.id}
              type="button"
              className={`lang-btn ${language === l.id ? "active" : ""}`}
              onClick={() => handleLanguageChange(l.id)}
            >
              <span>{l.icon}</span>
              <span>{l.label}</span>
            </button>
          ))}
        </div>

        {/* Sample prompt chips */}
        <div className="sample-chips">
          <span className="chip-label">Sample Prompts:</span>
          {currentSamplePrompts.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className="sample-chip"
              onClick={() => {
                setPrompt(p.text);
                setStyle(p.style);
              }}
            >
              <strong>{p.note}:</strong> {p.text.slice(0, 38)}...
            </button>
          ))}
        </div>
      </section>

      {/* Main Studio Workspace */}
      <section className="workspace">
        {/* Left Control Panel */}
        <div className="card control-panel">
          <div className="section-heading">
            <div>
              <span className="step-label">Creative Controls</span>
              <h2>Prompt & Settings</h2>
            </div>
            <Sliders className="heading-icon" size={20} />
          </div>

          <form onSubmit={generateStoryboard}>
            {/* Prompt Input */}
            <label className="field-label" htmlFor="prompt-input">
              Story Prompt (मराठी, हिंदी, English)
            </label>
            <textarea
              id="prompt-input"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe your character, actions, setting, or narrative..."
            />
            <div className="textarea-footer">
              <span>{prompt.length} / 2000 characters</span>
              <span>Supports Devanagari Unicode</span>
            </div>

            <div className="settings-grid">
              {/* Aspect Ratio Selector with Shorts / Reels badge */}
              <div>
                <label className="field-label">Aspect Ratio</label>
                <div className="aspect-grid">
                  {aspectRatios.map((ar) => (
                    <button
                      key={ar.id}
                      type="button"
                      className={`aspect-btn ${aspectRatio === ar.id ? "selected" : ""}`}
                      onClick={() => setAspectRatio(ar.id)}
                    >
                      <strong style={{ fontSize: "14px" }}>{ar.label}</strong>
                      <span style={{ fontSize: "10px", color: "#9ca3af" }}>{ar.desc}</span>
                      <span className="aspect-subtag">{ar.tag}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Duration Presets (15s Default for Shorts) */}
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <label className="field-label" style={{ margin: 0 }}>
                    Duration: <strong style={{ color: "#f472b6" }}>{duration}s</strong> {duration === 15 && "(Shorts/Reels)"}
                  </label>
                  <button
                    type="button"
                    className="btn-toggle-custom"
                    onClick={() => setCustomDuration(!customDuration)}
                  >
                    {customDuration ? "Preset list" : "Custom slider"}
                  </button>
                </div>

                {customDuration ? (
                  <div className="slider-wrap">
                    <input
                      type="range"
                      className="duration-slider"
                      min={5}
                      max={300}
                      step={5}
                      value={duration}
                      onChange={(e) => setDuration(Number(e.target.value))}
                    />
                    <div className="slider-markers">
                      <span>5s</span>
                      <span>15s (Shorts)</span>
                      <span>60s (1m)</span>
                      <span>180s (3m)</span>
                      <span>300s (5m)</span>
                    </div>
                  </div>
                ) : (
                  <div className="duration-pills">
                    {durationPresets.map((d) => (
                      <button
                        key={d}
                        type="button"
                        className={`dur-pill ${duration === d ? "selected" : ""}`}
                        onClick={() => setDuration(d)}
                      >
                        {d}s {d === 15 ? "🔥" : d >= 60 ? `(${d / 60}m)` : ""}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Style Presets */}
              <div>
                <label className="field-label" htmlFor="style-select">Art & Narrative Style</label>
                <select
                  id="style-select"
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                >
                  {styles.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              {/* Audio & Narration Controls */}
              <div>
                <label className="field-label">Audio & Subtitle Settings</label>
                <div className="audio-controls-card">
                  {/* Voiceover Toggle */}
                  <div className="toggle-item">
                    <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      {narrationEnabled ? <Mic size={14} color="#34d399" /> : <MicOff size={14} color="#9ca3af" />}
                      <span>Neural Voiceover</span>
                    </span>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={narrationEnabled}
                        onChange={(e) => setNarrationEnabled(e.target.checked)}
                      />
                      <span className="toggle-slider" />
                    </label>
                  </div>

                  {/* Subtitles Toggle */}
                  <div className="toggle-item">
                    <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <Subtitles size={14} color="#60a5fa" />
                      <span>On-Screen Subtitles</span>
                    </span>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={showSubtitles}
                        onChange={(e) => setShowSubtitles(e.target.checked)}
                      />
                      <span className="toggle-slider" />
                    </label>
                  </div>

                  {/* Voice Gender */}
                  {narrationEnabled && (
                    <div style={{ gridColumn: "1 / -1", display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: "6px", borderTop: "1px solid #1a1e46" }}>
                      <span style={{ fontSize: "11px", color: "#a5b4fc" }}>Voice Gender:</span>
                      <div className="segmented" style={{ width: "160px", height: "32px" }}>
                        <button
                          type="button"
                          className={voiceGender === "female" ? "selected" : ""}
                          onClick={() => setVoiceGender("female")}
                        >
                          Female
                        </button>
                        <button
                          type="button"
                          className={voiceGender === "male" ? "selected" : ""}
                          onClick={() => setVoiceGender("male")}
                        >
                          Male
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Rendering Engine Mode */}
              <div>
                <label className="field-label" htmlFor="engine-select">Rendering Engine</label>
                <select
                  id="engine-select"
                  value={engineMode}
                  onChange={(e) => setEngineMode(e.target.value)}
                >
                  {engineModes.map((em) => (
                    <option key={em.id} value={em.id}>{em.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Action Button: Create Storyboard */}
            <button
              type="submit"
              className="generate-button"
              disabled={status === "loading" || videoStatus === "rendering"}
            >
              {status === "loading" ? (
                <>
                  <LoaderCircle className="spin" size={18} />
                  <span>Analyzing Prompt & Mapping Scenes...</span>
                </>
              ) : (
                <>
                  <WandSparkles size={18} />
                  <span>Generate Storyboard ({duration}s)</span>
                </>
              )}
            </button>
          </form>

          {/* Error notice */}
          {error && <div className="notice error">{error}</div>}
        </div>

        {/* Right Storyboard & Video Panel */}
        <div className="card storyboard-panel">
          <div className="storyboard-header">
            <div>
              <span className="step-label">Live Preview</span>
              <h2>Storyboard & Animation</h2>
            </div>
            {storyboard && (
              <span className="preview-badge">
                <CheckCircle2 size={13} /> {storyboard.scenes.length} Scenes ({storyboard.language.toUpperCase()})
              </span>
            )}
          </div>

          {/* Render Active Video Progress Card */}
          {videoStatus === "rendering" && (
            <div className="progress-card">
              <div className="progress-header">
                <span>Rendering Animation...</span>
                <span style={{ fontWeight: 700, color: "#38bdf8" }}>{videoProgress}%</span>
              </div>
              <div className="progress-bar-bg">
                <div className="progress-bar-fill" style={{ width: `${videoProgress}%` }} />
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className="progress-stage">
                  <LoaderCircle className="spin" size={13} color="#818cf8" />
                  <span>{videoStage}</span>
                </span>
                <button type="button" className="btn-cancel" onClick={cancelRender}>
                  <StopCircle size={13} /> Cancel
                </button>
              </div>
            </div>
          )}

          {/* Render Completed Video Preview */}
          {videoStatus === "ready" && videoUrl && (
            <div className="video-preview-card">
              <div className="video-player-wrap">
                <video src={videoUrl} controls autoPlay loop playsInline />
              </div>

              <div className="video-toolbar">
                <a
                  href={videoUrl}
                  download={`frameflow_${language}_${aspectRatio.replace(":", "x")}.mp4`}
                  className="btn-download-video"
                >
                  <Download size={15} /> Download MP4 Video
                </a>

                <button
                  type="button"
                  className="btn-restart"
                  onClick={startRenderVideo}
                >
                  <RotateCcw size={13} /> Re-render Animation
                </button>
              </div>

              {providerMeta && (
                <div className="meta-badges">
                  <span className="badge-engine badge-success">
                    <CheckCircle2 size={12} /> {providerMeta.name}
                  </span>
                  <span className="badge-engine">
                    Aspect Ratio: {aspectRatio}
                  </span>
                  <span className="badge-engine">
                    Language: {language.toUpperCase()}
                  </span>
                  {providerMeta.fallbackReason && (
                    <div className="notice-fallback">
                      <Info size={14} />
                      <span>{providerMeta.fallbackReason}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Video Failure notice */}
          {videoStatus === "failed" && (
            <div className="notice error" style={{ marginTop: "14px" }}>
              {videoError}
            </div>
          )}

          {/* Storyboard Rendering Call-to-Action Bar */}
          {storyboard && videoStatus !== "rendering" && (
            <div className="render-action-bar">
              <div className="bar-title">
                <div>
                  <h4><Film size={16} color="#ec4899" /> Ready to Render Animation</h4>
                  <p>
                    Universal procedural engine will compile {storyboard.scenes.length} choreographed scenes into an MP4 video with {language.toUpperCase()} audio and subtitles.
                  </p>
                </div>
              </div>

              <button
                type="button"
                className="btn-render-video"
                onClick={startRenderVideo}
                disabled={videoStatus === "rendering"}
              >
                <Play size={16} fill="#fff" />
                <span>Render Animated Video ({duration}s • {aspectRatio})</span>
              </button>
            </div>
          )}

          {/* Detected Subject Entity & Environment Summary */}
          {storyboard && (
            <div style={{ marginTop: "16px", marginBottom: "8px" }}>
              <div className="entity-tag-bar">
                <span className="entity-pill">
                  Subject: <strong>{storyboard.entity.display_name || storyboard.entity.subtype}</strong> ({storyboard.entity.category})
                </span>
                <span className="entity-pill">
                  Environment: <strong>{storyboard.environment.name}</strong>
                </span>
                <span className="entity-pill">
                  Format: <strong>{storyboard.aspect_ratio}</strong>
                </span>
                <span className="entity-pill">
                  Language: <strong>{storyboard.language.toUpperCase()}</strong>
                </span>
              </div>
            </div>
          )}

          {/* Storyboard Scene List */}
          {storyboard && (
            <div className="scene-list" style={{ marginTop: "12px" }}>
              {storyboard.scenes.map((scene) => (
                <div key={scene.scene_number} className="scene-card">
                  <div className="scene-number">{String(scene.scene_number).padStart(2, "0")}</div>
                  <div className="scene-content">
                    <div className="scene-topline">
                      <h3>{scene.title}</h3>
                      <span><Clock3 size={11} /> {scene.duration}s</span>
                    </div>

                    <p>{scene.description}</p>

                    {scene.narration && (
                      <div className="scene-narration">
                        <Volume2 size={13} />
                        <span>"{scene.narration}"</span>
                      </div>
                    )}

                    <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginTop: "6px" }}>
                      <span className="motion-badge">
                        Choreography: {scene.motion_type.replace(/_/g, " ")}
                      </span>
                      <span className="motion-badge" style={{ color: "#38bdf8", borderColor: "#0369a1", background: "#0c4a6e33" }}>
                        Camera: {scene.camera_motion.replace(/_/g, " ")}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Empty State */}
          {!storyboard && (
            <div className="empty-state">
              <div className="empty-orbit">
                <Clapperboard size={26} />
              </div>
              <h3>Studio Awaiting Your Idea</h3>
              <p>
                Select Marathi, Hindi, or English, pick a prompt or write your own, and click <strong>Generate Storyboard</strong> to map out scenes and render your video.
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer>
        <span>FrameFlow AI Studio &bull; Marathi, Hindi & English Animation Engine</span>
        <span>Runs locally on standard Windows hardware &bull; Free & Open-Source Pipeline</span>
      </footer>
    </main>
  );
}

export default App;
