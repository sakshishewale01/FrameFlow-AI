import { useState } from "react";
import { ArrowUpRight, Clapperboard, Clock3, Film, LoaderCircle, Sparkles, WandSparkles } from "lucide-react";

const styles = ["Educational", "Cartoon", "Cinematic", "Story", "Nursery Rhyme"];
const durations = [15, 30, 60];
const aspectRatios = ["16:9", "9:16", "1:1"];
const API_URL = "http://127.0.0.1:8000/api/storyboard";

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

  async function generateStoryboard(event) {
    event.preventDefault();
    if (prompt.trim().length < 8) {
      setError("Add a little more detail so the storyboard has a clear starting point.");
      setStatus("error");
      return;
    }

    setStatus("loading");
    setError("");
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, style, duration, aspect_ratio: aspectRatio }),
      });
      if (!response.ok) {
        throw new Error("The storyboard service returned an error.");
      }
      setStoryboard(await response.json());
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

  return (
    <main className="app-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />
      <nav className="topbar">
        <a className="brand" href="/">
          <span className="brand-mark"><Clapperboard size={18} /></span>
          <span>FrameFlow <em>AI</em></span>
        </a>
        <span className="beta-pill"><span className="pulse-dot" /> storyboard studio</span>
      </nav>

      <section className="hero">
        <div className="eyebrow"><Sparkles size={15} /> Turn a thought into a visual flow</div>
        <h1>Make your next idea<br /><span>move frame by frame.</span></h1>
        <p className="hero-copy">Shape a prompt, choose a creative direction, and get a clear storyboard to build from.</p>
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
              <span className="step-label">02 / storyboard</span>
              <h2>Your visual rhythm</h2>
            </div>
            <div className="preview-badge"><Film size={14} /> planning preview</div>
          </div>
          {status === "empty" && <EmptyState />}
          {status === "loading" && <LoadingState />}
          {status === "success" && storyboard && <div className="scene-list">
            {storyboard.scenes.map((scene) => <article className="scene-card" key={scene.scene_number}>
              <div className="scene-number">{String(scene.scene_number).padStart(2, "0")}</div>
              <div className="scene-content"><div className="scene-topline"><h3>{scene.title}</h3><span><Clock3 size={13} /> {scene.duration}s</span></div><p>{scene.description}</p></div>
            </article>)}
            <div className="notice success"><Sparkles size={15} /> {storyboard.message}</div>
          </div>}
          {status === "error" && <EmptyState isError />}
        </section>
      </section>
      <footer><span>FrameFlow AI</span><span>From first thought to next frame.</span><span>Built for learning · API connected</span></footer>
    </main>
  );
}

function EmptyState({ isError = false }) {
  return <div className="empty-state"><div className="empty-orbit"><Film size={25} /></div><h3>{isError ? "Your canvas is waiting" : "Your storyboard starts here"}</h3><p>{isError ? "Resolve the prompt or connection issue, then generate again." : "Your scenes will appear here as a focused, editable sequence."}</p></div>;
}

function LoadingState() {
  return <div className="empty-state loading-state"><div className="empty-orbit"><LoaderCircle className="spin" size={25} /></div><h3>Finding the flow...</h3><p>Turning your prompt into a sequence of visual beats.</p></div>;
}

export default App;
