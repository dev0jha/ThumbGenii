import { useState, useEffect, useCallback } from "react";
import RadialGradientButton from "@/components/pixel-perfect/radial-gradient-button";


export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem("thumbai-theme") || "dark";
    } catch {
      return "dark";
    }
  });
  const [cookiesAccepted, setCookiesAccepted] = useState(() => {
    try {
      return localStorage.getItem("thumbai-cookies") === "true";
    } catch {
      return false;
    }
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("thumbai-theme", theme);
    } catch {}
  }, [theme]);



  const acceptCookies = useCallback(() => {
    setCookiesAccepted(true);
    try {
      localStorage.setItem("thumbai-cookies", "true");
    } catch {}
  }, []);

  const declineCookies = useCallback(() => {
    setCookiesAccepted(true);
    try {
      localStorage.setItem("thumbai-cookies", "false");
    } catch {}
  }, []);

  const generate = async () => {
    const p = prompt.trim();
    if (!p) return;
    setLoading(true);
    setError(null);
    setImageUrl(null);
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: p }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Generation failed");
      }
      const blob = await res.blob();
      setImageUrl(URL.createObjectURL(blob));
    } catch (e) {
      setError(e.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ backgroundColor: "var(--bg)" }}
    >
      {/* Navigation */}
      <header>
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <img src="/thumbAi.png" alt="ThumbAI Logo" className="h-15 w-auto" />
            <span
              className="text-base font-medium hidden sm:inline"
              style={{ color: "var(--text-primary)" }}
            >
              <span className="font-medium" style={{ color: "#3ecf8e" }}>
                Thumb
              </span>
              AI
            </span>
          </div>
          
          <div className="flex items-center">
            <a href="https://github.com/dev0jha/ThumbGenii">
            <RadialGradientButton className="h-8 px-4 py-1 text-xs min-w-20">
              Github
            </RadialGradientButton>
            </a>
          </div>
        </div>
      </header>
      

      {/* Main */}
      <main className="flex-1">
        {/* Hero */}
        <section className="pt-28 pb-20 px-6 text-center">
          <div className="max-w-3xl mx-auto">
            <span
              className="text-xs font-medium tracking-widest uppercase"
              style={{ color: "var(--text-muted)" }}
            >
              AI-Powered Image Generation
            </span>
            <h1 className="text-4xl md:text-5xl leading-tight tracking-tight mt-6 font-medium">
              Generate thumbnails with <br />
              <span className="gradient-text">AI in seconds.</span>
            </h1>
            <p
              className="text-base mt-5 max-w-lg mx-auto leading-relaxed"
              style={{ color: "var(--text-secondary)" }}
            >
              Describe your vision and let AI create the perfect image for your
              content. No design skills needed.
            </p>
            <div className="flex items-center justify-center gap-3 mt-8">
              <button className="btn-primary">Start Generating</button>
              <button className="btn-secondary">Learn More</button>
            </div>
          </div>
        </section>

        {/* Generator */}
        <section className="pb-24 px-6">
          <div className="max-w-xl mx-auto">
            <div
              className="p-6 md:p-8 rounded-xl"
              style={{
                backgroundColor: "var(--surface)",
                border: "1px solid var(--border)",
              }}
            >
              <label
                htmlFor="prompt"
                className="text-sm font-medium"
                style={{ color: "var(--text-surface)" }}
              >
                Prompt
              </label>
              <textarea
                id="prompt"
                rows={3}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="A cinematic shot of a cyberpunk city at night, neon lights reflecting on wet streets..."
                className="block w-full mt-2 px-0 text-base leading-relaxed resize-none font-sans transition"
                style={{
                  color: "var(--text-surface)",
                  backgroundColor: "transparent",
                  border: "none",
                  borderBottom: "1px solid",
                  borderColor: error ? "rgba(239,68,68,0.4)" : "var(--border)",
                  outline: "none",
                  borderRadius: 0,
                  fontWeight: 400,
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = "#3ecf8e";
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = error
                    ? "rgba(239,68,68,0.4)"
                    : "var(--border)";
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    generate();
                  }
                }}
              />
              <div className="flex items-center justify-between mt-5">
                <span
                  className="text-xs"
                  style={{ color: "rgba(250,250,250,0.4)" }}
                >
                  Enter to generate &middot; Shift+Enter for new line
                </span>
                <button
                  onClick={generate}
                  disabled={loading || !prompt.trim()}
                  className="btn-primary"
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <svg
                        className="animate-spin h-3.5 w-3.5"
                        viewBox="0 0 24 24"
                        fill="none"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                        />
                      </svg>
                      Generating
                    </span>
                  ) : (
                    "Generate"
                  )}
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Result */}
        <section className="pb-24 px-6">
          <div className="max-w-xl mx-auto">
            {error && (
              <p
                className="text-sm leading-relaxed"
                style={{ color: "rgba(239,68,68,0.8)" }}
              >
                {error}
              </p>
            )}

            {imageUrl && (
              <div>
                <div
                  className="rounded-lg overflow-hidden"
                  style={{ border: "1px solid var(--border)" }}
                >
                  <img
                    src={imageUrl}
                    alt={prompt}
                    className="w-full h-auto block"
                  />
                </div>
                <div className="flex items-center justify-between pt-4">
                  <span
                    className="text-sm truncate mr-4"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    {prompt}
                  </span>
                  <a
                    href={imageUrl}
                    download={`thumbnail-${Date.now()}.png`}
                    className="text-sm font-medium transition whitespace-nowrap"
                    style={{ color: "var(--text-secondary)" }}
                    onMouseEnter={(e) => (e.target.style.color = "#3ecf8e")}
                    onMouseLeave={(e) =>
                      (e.target.style.color = "var(--text-secondary)")
                    }
                  >
                    Download
                  </a>
                </div>
              </div>
            )}

            {!imageUrl && !error && (
              <p
                className="text-sm leading-relaxed"
                style={{ color: "var(--text-muted)" }}
              >
                Your generated image will appear here.
              </p>
            )}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer style={{ borderTop: "1px solid var(--border)" }}>
        <div
          className="max-w-5xl mx-auto px-6 py-6 flex items-center justify-between text-xs"
          style={{ color: "var(--text-muted)" }}
        >
          <span>&copy; {new Date().getFullYear()} ThumbAI</span>
          <span>Powered by Stable Diffusion &amp; Hugging Face</span>
        </div>
      </footer>

      {/* Cookie Banner */}
      {!cookiesAccepted && (
        <div
          className="fixed bottom-6 right-6 max-w-sm p-5 rounded-lg z-50"
          style={{
            backgroundColor: "var(--surface)",
            border: "1px solid var(--border)",
          }}
        >
          <p
            className="text-sm leading-relaxed mb-4"
            style={{ color: "var(--text-secondary)" }}
          >
            This site uses cookies to improve your experience. By continuing,
            you agree to our use of cookies.
          </p>
          <div className="flex items-center gap-3">
            <button
              onClick={acceptCookies}
              className="btn-primary"
              style={{ padding: "8px 18px", fontSize: "13px" }}
            >
              Accept
            </button>
            <button
              onClick={declineCookies}
              className="text-sm font-medium transition"
              style={{ color: "var(--text-muted)" }}
              onMouseEnter={(e) =>
                (e.target.style.color = "var(--text-primary)")
              }
              onMouseLeave={(e) => (e.target.style.color = "var(--text-muted)")}
            >
              Decline
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
