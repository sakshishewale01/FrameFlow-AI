import { useEffect, useRef, useState } from "react";
import {
  ArrowUpRight,
  Clapperboard,
  Clock3,
  Download,
  Film,
  LoaderCircle,
  Play,
  RotateCcw,
  Sparkles,
  Video,
  Volume2,
  WandSparkles,
} from "lucide-react";

const styles = ["Educational", "Cartoon", "Cinematic", "Story", "Nursery Rhyme"];
const durations = [15, 30, 60];
const aspectRatios = ["16:9", "9:16", "1:1"];

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const initialPrompt =
  "A tiny lighthouse keeper discovers a constellation hidden in the ocean and follows its light home.";

function App() {
  const [prompt, setPrompt] = useState("");
  const [style, setStyle] = useState("Cinematic");
  const [duration, setDuration] = useState(30);
  const [aspectRatio, setAspectRatio] = useState("16:9");
  const [storyboard, setStoryboard] = useState(null);
  const [status, setStatus] = useState("empty");
  const [error, setError] = useState("");

  // Video generation state
  const [videoStatus, setVideoStatus] = useState("idle"); // idle | rendering | ready | failed
  const [videoProgress, setVideoProgress] = useState(0);
  const [videoStage, setVideoStage] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const [videoError, setVideoError] = useState("");
  const pollIntervalRef = useRef(null);

  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, []);

  async function generateStoryboard(event) {
    event.preventDefault();
    if (prompt.trim().length < 8) {
      setError("Add a little more detail so the storyboard has a clear starting point.");
      setStatus("error");
      return;
    }

    setStatus("loading");
    setError("");
    setVideoStatus("idle");
    setVideoUrl("");
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);

    try {
      const response = await fetch(`${API_BASE}/api/storyboard`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, style, duration, aspect_ratio: aspectRatio }),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail?.[0]?.msg || "The storyboard service returned an error.");
      }
      const data = await response.json();
      setStoryboard(data);
      setStatus("success");
    } catch (requestError) {
      setError(
        requestError.message.includes("fetch")
          ? "Could not reach FastAPI. Start the backend and try again."
          : requestError.message,
      );
      setStatus("error");
    }
  }

  async function startRenderVideo() {
    if (!prompt.trim() || prompt.trim().length < 8) {
      setError("Prompt is required to render video.");
      return;
    }

    setVideoStatus("rendering");
    setVideoProgress(5);
    setVideoStage("Queuing video render job...");
    setVideoError("");

    try {
      const response = await fetch(`${API_BASE}/api/render-video`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          style,
          duration,
          aspect_ratio: aspectRatio,
          scenes: storyboard?.scenes || null,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to start video rendering job.");
      }

      const { job_id } = await response.json();

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
            setVideoStatus("ready");
          } else if (statusData.status === "failed") {
            clearInterval(pollIntervalRef.current);
            setVideoStatus("failed");
            setVideoError(statusData.error || "Video rendering failed. Please try again.");
          }
        } catch {
          // Keep polling on transient network hiccup
        }
      }, 1000);
    } catch (err) {
      setVideoStatus("failed");
      setVideoError(err.message || "Could not start video generation.");
    }
  }

  return (
    <main className="app-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />
      <nav className="topbar">
        <a className="brand" href="/">
          <span className="brand-mark"><Clapperboard size={18} /></span>
          <span>FrameFlow <em>AI</em></span>
        </a>
        <span className="beta-pill"><span className="pulse-dot" /> text-to-video studio</span>
      </nav>

      <section className="hero">
        <div className="eyebrow"><Sparkles size={15} /> Turn a thought into a visual flow</div>
        <h1>Make your next idea<br /><span>move frame by frame.</span></h1>
        <p className="hero-copy">Shape a prompt, choose a creative direction, generate an intelligent storyboard, and render the final narrated MP4 video.</p>
      </section>

      <section className="workspace">
        <form className="control-panel card" onSubmit={generateStoryboard}>
          <div className="section-heading">
            <div>
              <span className="step-label">01 / prompt</span>
              <h2>What should we create?</h2>
            </div>
            <WandSparkles className="heading-icon" size={22} />
          </div>
          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            placeholder={initialPrompt}
            maxLength={1000}
            aria-label="Story prompt"
          />
          <div className="textarea-footer"><span>Be specific about the subject, mood, or action.</span><span>{prompt.length}/1000</span></div>

          <div className="settings-grid">
            <label>
              <span className="field-label">Creative style</span>
              <select value={style} onChange={(event) => setStyle(event.target.value)}>
                {styles.map((option) => <option key={option}>{option}</option>)}
              </select>
            </label>
            <label>
              <span className="field-label">Duration</span>
              <div className="segmented">{durations.map((option) => <button type="button" className={duration === option ? "selected" : ""} onClick={() => setDuration(option)} key={option}>{option}s</button>)}</div>
            </label>
            <label>
              <span className="field-label">Canvas</span>
              <div className="segmented">{aspectRatios.map((option) => <button type="button" className={aspectRatio === option ? "selected" : ""} onClick={() => setAspectRatio(option)} key={option}>{option}</button>)}</div>
            </label>
          </div>
          {status === "error" && <div className="notice error">{error}</div>}
          <button className="generate-button" type="submit" disabled={status === "loading"}>
            {status === "loading" ? <><LoaderCircle className="spin" size={18} /> Mapping your scenes...</> : <>Generate storyboard <ArrowUpRight size={18} /></>}
          </button>
        </form>

        <section className="storyboard-panel">
          <div className="storyboard-header">
            <div>
              <span className="step-label">02 / storyboard & render</span>
              <h2>Your visual rhythm</h2>
            </div>
            <div className="preview-badge"><Film size={14} /> creative preview</div>
          </div>
          {status === "empty" && <EmptyState />}
          {status === "loading" && <LoadingState />}
          {status === "success" && storyboard && (
            <div className="scene-list">
              {storyboard.scenes.map((scene) => (
                <article className="scene-card" key={scene.scene_number}>
                  <div className="scene-number">{String(scene.scene_number).padStart(2, "0")}</div>
                  <div className="scene-content">
                    <div className="scene-topline">
                      <h3>{scene.title}</h3>
                      <span><Clock3 size={13} /> {scene.duration}s</span>
                    </div>
                    <p>{scene.description}</p>
                    {scene.narration && (
                      <div className="scene-narration">
                        <Volume2 size={13} />
                        <span>"{scene.narration}"</span>
                      </div>
                    )}
                  </div>
                </article>
              ))}

              {/* Video Generation Control & Live Progress */}
              {videoStatus === "idle" && (
                <div className="render-action-bar">
                  <div className="bar-title">
                    <h4><Video size={16} /> Ready to render video?</h4>
                    <span className="beta-pill">{duration}s • {aspectRatio}</span>
                  </div>
                  <p>Compile these scenes into an MP4 video with custom visual motion cards and synchronized voiceover narration.</p>
                  <button type="button" className="btn-render-video" onClick={startRenderVideo}>
                    <Play size={16} fill="currentColor" /> Render Narrated Video (.mp4)
                  </button>
                </div>
              )}

              {videoStatus === "rendering" && (
                <div className="progress-card">
                  <div className="progress-header">
                    <span>RENDERING VIDEO</span>
                    <span>{videoProgress}%</span>
                  </div>
                  <div className="progress-bar-bg">
                    <div className="progress-bar-fill" style={{ width: `${videoProgress}%` }} />
                  </div>
                  <div className="progress-stage">
                    <LoaderCircle className="spin" size={14} /> {videoStage}
                  </div>
                </div>
              )}

              {videoStatus === "ready" && videoUrl && (
                <div className="video-preview-card">
                  <div className="video-player-wrap">
                    <video key={videoUrl} controls autoPlay playsInline src={videoUrl} />
                  </div>
                  <div className="video-toolbar">
                    <a className="btn-download-video" href={videoUrl} download={`frameflow_${style.toLowerCase()}_${duration}s.mp4`}>
                      <Download size={15} /> Download MP4 Video
                    </a>
                    <button type="button" className="btn-restart" onClick={startRenderVideo}>
                      <RotateCcw size={13} /> Re-render
                    </button>
                  </div>
                </div>
              )}

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
      <footer><span>FrameFlow AI</span><span>From first thought to next frame.</span><span>Built for learning · Full Text-to-Video Engine</span></footer>
    </main>
  );
}

function EmptyState({ isError = false }) {
  return (
    <div className="empty-state">
      <div className="empty-orbit"><Film size={25} /></div>
      <h3>{isError ? "Your canvas is waiting" : "Your storyboard starts here"}</h3>
      <p>{isError ? "Resolve the prompt or connection issue, then generate again." : "Enter a prompt and choose your settings to generate an intelligent storyboard and video."}</p>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="empty-state loading-state">
      <div className="empty-orbit"><LoaderCircle className="spin" size={25} /></div>
      <h3>Finding the flow...</h3>
      <p>Turning your prompt into a sequence of visual beats and narration.</p>
    </div>
  );
}

export default App;
