import { useEffect, useRef, useState } from "react";
import {
  ArrowUpRight,
  CheckCircle2,
  Clapperboard,
  Clock3,
  Cpu,
  Download,
  Film,
  Info,
  LoaderCircle,
  Play,
  RotateCcw,
  Sliders,
  Sparkles,
  StopCircle,
  Video,
  Volume2,
  WandSparkles,
} from "lucide-react";

const styles = [
  "Cinematic",
  "Cartoon",
  "Cyberpunk",
  "Educational",
  "Fantasy",
  "Story",
  "Nursery Rhyme",
];

const durationPresets = [15, 30, 60, 120, 300];
const aspectRatios = ["16:9", "9:16", "1:1"];

const engineModes = [
  { id: "auto", label: "Auto (AI Video with Procedural Fallback)" },
  { id: "procedural", label: "Procedural 2D Engine (Offline / Local Fast)" },
  { id: "ai_video", label: "AI Video Generation (Requires API Key)" },
];

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const samplePrompts = [
  "A sleek red sports car zooming down a neon-lit cyberpunk highway in the rain",
  "A majestic eagle soaring over snow-capped mountain peaks at golden sunset",
  "A deep sea submarine exploring bioluminescent underwater coral ruins",
  "A friendly astronaut repairing a solar satellite in deep space with orbiting planets",
];

function App() {
  const [prompt, setPrompt] = useState("");
  const [style, setStyle] = useState("Cinematic");
  const [duration, setDuration] = useState(30);
  const [customDuration, setCustomDuration] = useState(false);
  const [aspectRatio, setAspectRatio] = useState("16:9");
  const [engineMode, setEngineMode] = useState("auto");

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

  async function generateStoryboard(event) {
    if (event) event.preventDefault();
    if (prompt.trim().length < 3) {
      setError("Please describe a character, scene, vehicle, animal, or action.");
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
          ? "Could not connect to FastAPI server at " + API_BASE + ". Please ensure the backend is running."
          : requestError.message,
      );
      setStatus("error");
    }
  }

  async function startRenderVideo() {
    if (!prompt.trim() || prompt.trim().length < 3) {
      setError("Prompt is required to render video.");
      return;
    }

    setVideoStatus("rendering");
    setVideoProgress(3);
    setVideoStage("Queuing video render job...");
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
          setVideoStage(statusData.stage || "Rendering animation...");

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
          // Keep polling on transient network glitch
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
          <span className="beta-pill"><span className="pulse-dot" /> universal text-to-animation</span>
        </div>
      </nav>

      {/* Hero Header */}
      <section className="hero">
        <div className="eyebrow"><Sparkles size={15} /> General-Purpose Text-to-Video Engine</div>
        <h1>Any thought.<br /><span>Rendered frame by frame.</span></h1>
        <p className="hero-copy">
          From sports cars and deep-sea submarines to dragons, astronauts, or nature.
          Support durations up to 5 minutes (300s) with 2D procedural motion, parallax cameras, and synchronized narration.
        </p>

        {/* Quick sample chips */}
        <div className="sample-chips">
          <span className="chip-label">Try an idea:</span>
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className="sample-chip"
              onClick={() => {
                setPrompt(p);
                if (idx === 0) setStyle("Cyberpunk");
                else if (idx === 1) setStyle("Cinematic");
                else if (idx === 2) setStyle("Story");
                else setStyle("Cinematic");
              }}
            >
              {p.slice(0, 36)}...
            </button>
          ))}
        </div>
      </section>

      {/* Main Workspace */}
      <section className="workspace">
        {/* Left Control Panel */}
        <form className="control-panel card" onSubmit={generateStoryboard}>
          <div className="section-heading">
            <div>
              <span className="step-label">01 / prompt & settings</span>
              <h2>Describe your scene</h2>
            </div>
            <WandSparkles className="heading-icon" size={22} />
          </div>

          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            placeholder="Describe characters, objects, vehicles, animals, nature, actions, or environments..."
            maxLength={2000}
            aria-label="Story prompt"
          />
          <div className="textarea-footer">
            <span>Any subject: vehicle, creature, human, space, ocean, or city.</span>
            <span>{prompt.length}/2000</span>
          </div>

          <div className="settings-grid">
            {/* Visual Style */}
            <label>
              <span className="field-label">Visual Style</span>
              <select value={style} onChange={(event) => setStyle(event.target.value)}>
                {styles.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>

            {/* Duration (5s to 300s) */}
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                <span className="field-label" style={{ margin: 0 }}>Duration: {duration}s {duration >= 60 ? `(${(duration / 60).toFixed(1)}m)` : ""}</span>
                <button
                  type="button"
                  className="btn-toggle-custom"
                  onClick={() => setCustomDuration(!customDuration)}
                >
                  <Sliders size={11} /> {customDuration ? "Presets" : "Custom slider"}
                </button>
              </div>

              {!customDuration ? (
                <div className="segmented">
                  {durationPresets.map((option) => (
                    <button
                      type="button"
                      className={duration === option ? "selected" : ""}
                      onClick={() => setDuration(option)}
                      key={option}
                    >
                      {option < 60 ? `${option}s` : `${option / 60}m`}
                    </button>
                  ))}
                </div>
              ) : (
                <div className="slider-wrap">
                  <input
                    type="range"
                    min="5"
                    max="300"
                    step="5"
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                    className="duration-slider"
                  />
                  <div className="slider-markers">
                    <span>5s</span>
                    <span>1m</span>
                    <span>2m</span>
                    <span>3m</span>
                    <span>5m (300s)</span>
                  </div>
                </div>
              )}
            </div>

            {/* Aspect Ratio Canvas */}
            <label>
              <span className="field-label">Canvas Format</span>
              <div className="segmented">
                {aspectRatios.map((option) => (
                  <button
                    type="button"
                    className={aspectRatio === option ? "selected" : ""}
                    onClick={() => setAspectRatio(option)}
                    key={option}
                  >
                    {option === "16:9" ? "16:9 Landscape" : option === "9:16" ? "9:16 Shorts" : "1:1 Square"}
                  </button>
                ))}
              </div>
            </label>

            {/* Engine Mode */}
            <label>
              <span className="field-label">Render Engine Mode</span>
              <select value={engineMode} onChange={(event) => setEngineMode(event.target.value)}>
                {engineModes.map((m) => (
                  <option key={m.id} value={m.id}>{m.label}</option>
                ))}
              </select>
            </label>
          </div>

          {status === "error" && <div className="notice error">{error}</div>}

          <button className="generate-button" type="submit" disabled={status === "loading"}>
            {status === "loading" ? (
              <><LoaderCircle className="spin" size={18} /> Generating prompt scenes...</>
            ) : (
              <>Map Storyboard & Scenes <ArrowUpRight size={18} /></>
            )}
          </button>
        </form>

        {/* Right Panel: Storyboard & Video Player */}
        <section className="storyboard-panel">
          <div className="storyboard-header">
            <div>
              <span className="step-label">02 / visual rhythm & animation</span>
              <h2>Scene Beats & Video Studio</h2>
            </div>
            <div className="preview-badge"><Film size={14} /> universal engine</div>
          </div>

          {status === "empty" && <EmptyState />}
          {status === "loading" && <LoadingState />}

          {status === "success" && storyboard && (
            <div className="scene-list">
              {/* Detected Semantic Entity & Setting Tags */}
              <div className="entity-tag-bar">
                <span className="entity-pill">
                  <strong>Subject:</strong> {storyboard.entity?.subtype?.toUpperCase() || "CUSTOM"} ({storyboard.entity?.category || "general"})
                </span>
                <span className="entity-pill">
                  <strong>Environment:</strong> {storyboard.environment?.name?.toUpperCase() || "ATMOSPHERE"}
                </span>
                <span className="entity-pill">
                  <strong>Duration:</strong> {storyboard.duration}s ({storyboard.scenes?.length} scenes)
                </span>
              </div>

              {/* Storyboard Scene Beats */}
              {storyboard.scenes.map((scene) => (
                <article className="scene-card" key={scene.scene_number}>
                  <div className="scene-number">{String(scene.scene_number).padStart(2, "0")}</div>
                  <div className="scene-content">
                    <div className="scene-topline">
                      <h3>{scene.title}</h3>
                      <span><Clock3 size={13} /> {scene.duration}s</span>
                    </div>

                    {scene.character_action && (
                      <span className="motion-badge">
                        <Play size={10} fill="currentColor" /> {scene.character_action}
                      </span>
                    )}

                    <p>{scene.description}</p>

                    {scene.motion_instruction && (
                      <div className="scene-motion-instruction">
                        <Sparkles size={13} />
                        <span><strong>Camera & Dynamics:</strong> {scene.motion_instruction}</span>
                      </div>
                    )}

                    {scene.narration && (
                      <div className="scene-narration">
                        <Volume2 size={13} />
                        <span>"{scene.narration}"</span>
                      </div>
                    )}
                  </div>
                </article>
              ))}

              {/* Video Generation Trigger Bar */}
              {videoStatus === "idle" && (
                <div className="render-action-bar">
                  <div className="bar-title">
                    <h4><Video size={16} /> Ready to render complete video?</h4>
                    <span className="beta-pill">{duration}s • {aspectRatio} • {storyboard.scenes.length} scenes</span>
                  </div>
                  <p>
                    Renders an actual playable MP4 with dynamic subject sprites, parallax background layers, camera zoom/pan, particle fields, and synchronized narration.
                  </p>
                  <button type="button" className="btn-render-video" onClick={startRenderVideo}>
                    <Play size={16} fill="currentColor" /> Render Full Video (.mp4)
                  </button>
                </div>
              )}

              {/* Rendering Progress Card */}
              {videoStatus === "rendering" && (
                <div className="progress-card">
                  <div className="progress-header">
                    <span>RENDERING MP4 VIDEO</span>
                    <span>{videoProgress}%</span>
                  </div>
                  <div className="progress-bar-bg">
                    <div className="progress-bar-fill" style={{ width: `${videoProgress}%` }} />
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div className="progress-stage">
                      <LoaderCircle className="spin" size={14} /> {videoStage}
                    </div>
                    <button type="button" className="btn-cancel" onClick={cancelRender}>
                      <StopCircle size={14} /> Cancel
                    </button>
                  </div>
                </div>
              )}

              {/* Cancelled State */}
              {videoStatus === "cancelled" && (
                <div className="notice error">
                  Render was cancelled. You can adjust your settings and render again.
                  <button type="button" className="btn-restart" style={{ marginLeft: "auto" }} onClick={startRenderVideo}>
                    Restart
                  </button>
                </div>
              )}

              {/* Video Preview Player & Actions */}
              {videoStatus === "ready" && videoUrl && (
                <div className="video-preview-card">
                  <div className="video-player-wrap">
                    <video key={videoUrl} controls autoPlay playsInline src={videoUrl} />
                  </div>

                  {/* Engine Metadata Badges */}
                  <div className="meta-badges">
                    <span className="badge-engine">
                      <Cpu size={13} /> {providerMeta?.name || "FrameFlow Procedural 2D Engine"}
                    </span>
                    <span className="badge-engine badge-success">
                      <CheckCircle2 size={13} /> {duration}s MP4 Validated
                    </span>
                  </div>

                  {providerMeta?.fallbackReason && (
                    <div className="notice-fallback">
                      <Info size={14} />
                      <span>{providerMeta.fallbackReason}</span>
                    </div>
                  )}

                  <div className="video-toolbar">
                    <a
                      className="btn-download-video"
                      href={videoUrl}
                      download={`frameflow_${style.toLowerCase()}_${duration}s.mp4`}
                    >
                      <Download size={15} /> Download Master MP4
                    </a>
                    <button type="button" className="btn-restart" onClick={startRenderVideo}>
                      <RotateCcw size={13} /> Re-render Video
                    </button>
                  </div>
                </div>
              )}

              {/* Error Notice */}
              {videoStatus === "failed" && (
                <div className="notice error">
                  {videoError}
                  <button type="button" className="btn-restart" style={{ marginLeft: "auto" }} onClick={startRenderVideo}>
                    Try Again
                  </button>
                </div>
              )}

              <div className="notice success"><Sparkles size={15} /> {storyboard.message}</div>
            </div>
          )}

          {status === "error" && <EmptyState isError />}
        </section>
      </section>

      {/* Footer */}
      <footer>
        <span>FrameFlow AI Studio</span>
        <span>Universal Text-to-Animation • Scalable to 300s (5min)</span>
        <span>Built with React + Vite & FastAPI + Python</span>
      </footer>
    </main>
  );
}

function EmptyState({ isError = false }) {
  return (
    <div className="empty-state">
      <div className="empty-orbit"><Film size={25} /></div>
      <h3>{isError ? "Your canvas is waiting" : "Your animation studio starts here"}</h3>
      <p>
        {isError
          ? "Resolve the prompt or server connection issue, then generate again."
          : "Type any prompt describing characters, vehicles, nature, animals, or actions to build a customized storyboard and video."}
      </p>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="empty-state loading-state">
      <div className="empty-orbit"><LoaderCircle className="spin" size={25} /></div>
      <h3>Analyzing prompt entities...</h3>
      <p>Determining subjects, visual environment, motion dynamics, and camera choreography.</p>
    </div>
  );
}

export default App;
