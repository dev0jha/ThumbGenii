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
              <span className="font-bold" style={{ color: "#3ecf8e" }}>
                Thumb
              </span>
              Genii
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
          </div>
        </section>

        {/* Generator */}
        <section className="pb-24 px-6">
          <div className="max-w-xl mx-auto">
            <div className="relative p-[1px] rounded-xl shadow-2xl overflow-hidden group">
              {/* Diagonal Hashed Border layer */}
              <div 
                className="absolute inset-0 pointer-events-none opacity-40 transition-opacity duration-500 group-hover:opacity-80"
                style={{
                  background: "repeating-linear-gradient(45deg, #4ade80, #4ade80 2px, transparent 2px, transparent 6px)"
                }}
              />
              <div className="bg-[#1c1c1c] rounded-xl p-5 relative z-10 w-full h-full">
                <label
                  htmlFor="prompt"
                  className="block text-sm font-bold text-gray-100 mb-3"
                >
                  Prompt
                </label>
                <textarea
                  id="prompt"
                  rows={3}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="A cinematic shot of a cyberpunk city at night, neon lights reflecting on wet streets..."
                  className="block w-full text-[15px] leading-relaxed resize-none font-sans bg-transparent text-gray-300 placeholder-gray-600 border-none outline-none focus:ring-0 p-0"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      generate();
                    }
                  }}
                />
                <div className="h-[1px] w-full bg-[#2e2e2e] my-4" />
                <div className="flex items-center justify-between mt-1">
                  <span className="text-xs text-gray-500 font-medium">
                    Enter to generate &middot; Shift+Enter for new line
                  </span>
                  <button
                    onClick={generate}
                    disabled={loading || !prompt.trim()}
                    className="px-5 py-2 rounded-lg text-sm font-medium bg-[#1e3a2b] text-[#4ade80] hover:bg-[#254734] transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
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
                    className="text-sm truncate mr-4 bg-transparent border border-[#3ecf8e]/30 px-3 py-1.5 rounded-md"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    {prompt}
                  </span>
                  <a
                    href={imageUrl}
                    download={`thumbnail-${Date.now()}.png`}
                    className="px-4 py-2 rounded-lg text-sm font-medium bg-[#3ecf8e] text-[#121212] hover:bg-[#2eab73] transition-colors whitespace-nowrap"
                  >
                    Download
                  </a>
                </div>
              </div>
            )}

            {!imageUrl && !error && (
              <p
                className="flex justify-center text-sm leading-relaxed"
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
