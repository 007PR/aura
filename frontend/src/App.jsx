import { useState, useEffect, useRef } from "react";
import { apiPost } from "./api";

const Z = {
  aries: { s: "♈", el: "Fire", e: "🔥", c: "#FF6B6B", c2: "#FF8A80", d: "Mar 21 – Apr 19", r: "Cardinal Fire", p: "Mars", trait: "Bold & Impulsive" },
  taurus: { s: "♉", el: "Earth", e: "🌿", c: "#81C784", c2: "#A5D6A7", d: "Apr 20 – May 20", r: "Fixed Earth", p: "Venus", trait: "Stubborn & Sensual" },
  gemini: { s: "♊", el: "Air", e: "💨", c: "#FFD54F", c2: "#FFE082", d: "May 21 – Jun 20", r: "Mutable Air", p: "Mercury", trait: "Dual & Witty" },
  cancer: { s: "♋", el: "Water", e: "🌊", c: "#4FC3F7", c2: "#81D4FA", d: "Jun 21 – Jul 22", r: "Cardinal Water", p: "Moon", trait: "Emotional & Nurturing" },
  leo: { s: "♌", el: "Fire", e: "🦁", c: "#FFB74D", c2: "#FFCC80", d: "Jul 23 – Aug 22", r: "Fixed Fire", p: "Sun", trait: "Dramatic & Generous" },
  virgo: { s: "♍", el: "Earth", e: "🌾", c: "#AED581", c2: "#C5E1A5", d: "Aug 23 – Sep 22", r: "Mutable Earth", p: "Mercury", trait: "Perfectionist & Caring" },
  libra: { s: "♎", el: "Air", e: "⚖️", c: "#CE93D8", c2: "#E1BEE7", d: "Sep 23 – Oct 22", r: "Cardinal Air", p: "Venus", trait: "Charming & Indecisive" },
  scorpio: { s: "♏", el: "Water", e: "🦂", c: "#EF5350", c2: "#EF9A9A", d: "Oct 23 – Nov 21", r: "Fixed Water", p: "Pluto", trait: "Intense & Magnetic" },
  sagittarius: { s: "♐", el: "Fire", e: "🏹", c: "#AB47BC", c2: "#CE93D8", d: "Nov 22 – Dec 21", r: "Mutable Fire", p: "Jupiter", trait: "Free & Philosophical" },
  capricorn: { s: "♑", el: "Earth", e: "🏔️", c: "#78909C", c2: "#B0BEC5", d: "Dec 22 – Jan 19", r: "Cardinal Earth", p: "Saturn", trait: "Ambitious & Disciplined" },
  aquarius: { s: "♒", el: "Air", e: "🫧", c: "#26C6DA", c2: "#80DEEA", d: "Jan 20 – Feb 18", r: "Fixed Air", p: "Uranus", trait: "Rebel & Visionary" },
  pisces: { s: "♓", el: "Water", e: "🐟", c: "#7E57C2", c2: "#B39DDB", d: "Feb 19 – Mar 20", r: "Mutable Water", p: "Neptune", trait: "Dreamy & Intuitive" },
};

const REMED = [
  { t: "Diya Ritual", d: "Light a ghee diya tonight. Channel fire energy inward. Best during sunset.", i: "🪔", f: "Low Energy" },
  { t: "Green Thursday", d: "Wear green tomorrow. Jupiter's color grounds chaotic earth energy.", i: "💚", f: "Bad Luck" },
  { t: "Shiva Mantra", d: "Chant 'Om Namah Shivaya' 11 times before sleep. Saturn needs appeasing.", i: "🕉️", f: "Saturn Transit" },
  { t: "Sweet Charity", d: "Donate sweets to a child. Saturn eases for the generous.", i: "🍬", f: "Career Blocks" },
  { t: "Moon Water", d: "Keep water by your bed. Moon energy needs hydrating.", i: "🌙", f: "Emotional Chaos" },
  { t: "Fire Release", d: "Write 3 fears on paper, burn safely. Mars demands release.", i: "🔥", f: "Anger Issues" },
  { t: "Bird Feeding", d: "Feed birds at sunrise. Jupiter blesses those who nurture.", i: "🐦", f: "Blocked Abundance" },
  { t: "Silver Ring", d: "Wear silver on little finger. Stabilizes Moon's emotional pull.", i: "💍", f: "Mood Swings" },
];

const FD = "'Cormorant Garamond', serif";
const FB = "'DM Sans', sans-serif";
const FM = "'JetBrains Mono', monospace";

const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=JetBrains+Mono:wght@300;400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bd:#07060E;--bg:rgba(14,12,25,0.7);--gl:rgba(255,255,255,0.04);--gl2:rgba(255,255,255,0.07);--br:rgba(255,255,255,0.06);--bl:rgba(255,255,255,0.1);--tp:rgba(255,255,255,0.92);--ts:rgba(255,255,255,0.55);--tm:rgba(255,255,255,0.3);--ac:#C4A1FF;--a2:#FF8A9E;--a3:#7EB8FF;--gd:#D4A574;--gw:rgba(196,161,255,0.15)}
html,body,#root{height:100%;width:100%;background:var(--bd);color:var(--tp);font-family:${FB};-webkit-font-smoothing:antialiased;overflow:hidden}
input,textarea,button{font-family:inherit}
::-webkit-scrollbar{width:3px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:10px}
@keyframes fu{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes fi{from{opacity:0}to{opacity:1}}
@keyframes pu{0%,100%{opacity:0.4}50%{opacity:1}}
@keyframes sh{0%{background-position:-200% 0}100%{background-position:200% 0}}
@keyframes br{0%,100%{transform:scale(1)}50%{transform:scale(1.03)}}
@keyframes of{0%,100%{transform:translate(0,0) scale(1)}25%{transform:translate(10px,-15px) scale(1.05)}50%{transform:translate(-5px,-25px) scale(1)}75%{transform:translate(-15px,-10px) scale(0.95)}}
@keyframes cr{0%{transform:rotate(0deg) scale(1);opacity:0.3}50%{transform:rotate(180deg) scale(1.1);opacity:0.5}100%{transform:rotate(360deg) scale(1);opacity:0.3}}
@keyframes st{0%,100%{opacity:0.2;transform:scale(0.8)}50%{opacity:1;transform:scale(1.2)}}
@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}
`;

function BG() {
  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 0, overflow: "hidden", pointerEvents: "none" }}>
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 80% 60% at 20% 10%, rgba(90,40,120,0.25), transparent), radial-gradient(ellipse 60% 50% at 80% 80%, rgba(30,60,120,0.2), transparent), radial-gradient(ellipse 50% 40% at 50% 50%, rgba(120,50,80,0.1), transparent)" }} />
      {[{ sz: 280, x: "10%", y: "15%", cl: "rgba(140,80,200,0.08)", du: "20s", de: "0s" }, { sz: 200, x: "70%", y: "60%", cl: "rgba(80,140,220,0.06)", du: "25s", de: "5s" }, { sz: 160, x: "85%", y: "10%", cl: "rgba(200,80,120,0.05)", du: "18s", de: "2s" }, { sz: 120, x: "30%", y: "75%", cl: "rgba(100,180,160,0.06)", du: "22s", de: "8s" }].map((o, i) => (
        <div key={i} style={{ position: "absolute", left: o.x, top: o.y, width: o.sz, height: o.sz, borderRadius: "50%", background: o.cl, filter: "blur(60px)", animation: `of ${o.du} ease-in-out infinite`, animationDelay: o.de }} />
      ))}
      {Array.from({ length: 35 }).map((_, i) => (
        <div key={`s${i}`} style={{ position: "absolute", left: `${Math.random() * 100}%`, top: `${Math.random() * 100}%`, width: Math.random() * 2 + 1, height: Math.random() * 2 + 1, borderRadius: "50%", background: `rgba(${200 + Math.random() * 55}, ${200 + Math.random() * 55}, 255, ${Math.random() * 0.5 + 0.1})`, animation: `st ${3 + Math.random() * 4}s ease-in-out infinite`, animationDelay: `${Math.random() * 5}s` }} />
      ))}
      <div style={{ position: "absolute", inset: 0, opacity: 0.025, backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`, backgroundSize: "128px" }} />
    </div>
  );
}

const GC = ({ children, style = {}, onClick, d = 0 }) => (
  <div onClick={onClick} style={{ background: "var(--gl)", backdropFilter: "blur(40px)", WebkitBackdropFilter: "blur(40px)", border: "1px solid var(--br)", borderRadius: 24, padding: 24, position: "relative", overflow: "hidden", cursor: onClick ? "pointer" : "default", transition: "all 0.4s cubic-bezier(0.16,1,0.3,1)", animation: `fu 0.6s ease-out ${d}ms both`, ...style }}>{children}</div>
);

const Bd = ({ children, color = "var(--ac)", style = {} }) => (
  <span style={{ display: "inline-flex", alignItems: "center", gap: 4, padding: "4px 12px", borderRadius: 100, background: `${color}18`, color, fontSize: 11, fontWeight: 600, letterSpacing: 0.5, border: `1px solid ${color}25`, ...style }}>{children}</span>
);

const Bt = ({ children, v = "primary", style = {}, onClick, disabled = false }) => {
  const s = { primary: { background: "linear-gradient(135deg, #C4A1FF, #8B6FD4)", color: "#fff", border: "none", boxShadow: "0 4px 24px rgba(196,161,255,0.3)" }, secondary: { background: "var(--gl2)", color: "var(--tp)", border: "1px solid var(--bl)" }, ghost: { background: "transparent", color: "var(--ac)", border: "1px solid rgba(196,161,255,0.2)" }, gold: { background: "linear-gradient(135deg, #D4A574, #B8860B)", color: "#fff", border: "none", boxShadow: "0 4px 24px rgba(212,165,116,0.3)" } };
  return <button disabled={disabled} onClick={onClick} style={{ ...s[v], padding: "14px 28px", borderRadius: 16, fontSize: 14, fontWeight: 600, letterSpacing: 0.3, cursor: disabled ? "not-allowed" : "pointer", transition: "all 0.3s", opacity: disabled ? 0.5 : 1, fontFamily: FB, display: "inline-flex", alignItems: "center", justifyContent: "center", gap: 8, ...style }}>{children}</button>;
};

function Onboard({ onDone }) {
  const [step, setStep] = useState(0);
  const [name, setName] = useState("");
  const [sign, setSign] = useState(null);
  const [dob, setDob] = useState("");
  const signs = Object.entries(Z);

  if (step === 0) return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", padding: 32, textAlign: "center", position: "relative", zIndex: 1 }}>
      <div style={{ position: "absolute", width: 320, height: 320, borderRadius: "50%", border: "1px solid rgba(196,161,255,0.1)", animation: "cr 20s linear infinite" }} />
      <div style={{ position: "absolute", width: 240, height: 240, borderRadius: "50%", border: "1px solid rgba(255,138,158,0.08)", animation: "cr 15s linear infinite reverse" }} />
      <div style={{ position: "absolute", width: 400, height: 400, borderRadius: "50%", border: "1px solid rgba(126,184,255,0.05)", animation: "cr 28s linear infinite" }} />
      <div style={{ fontSize: 64, marginBottom: 24, animation: "fu 0.8s ease-out both", filter: "drop-shadow(0 0 40px rgba(196,161,255,0.4))" }}>✦</div>
      <h1 style={{ fontFamily: FD, fontSize: 56, fontWeight: 300, letterSpacing: -1, lineHeight: 1.1, marginBottom: 12, animation: "fu 0.8s ease-out 0.2s both", background: "linear-gradient(135deg, #fff 30%, #C4A1FF 70%, #FF8A9E)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>Aura</h1>
      <p style={{ fontFamily: FD, fontSize: 16, color: "var(--ts)", fontStyle: "italic", animation: "fu 0.8s ease-out 0.4s both", letterSpacing: 1 }}>Your Cosmic Bestie. No Filter. No Judgement.</p>
      <div style={{ marginTop: 48, animation: "fu 0.8s ease-out 0.6s both" }}><Bt onClick={() => setStep(1)} style={{ padding: "16px 48px", fontSize: 15, borderRadius: 20 }}>Begin Your Journey ✦</Bt></div>
      <p style={{ marginTop: 24, fontSize: 11, color: "var(--tm)", animation: "fu 0.8s ease-out 0.8s both" }}>Vedic Wisdom × Modern Chaos</p>
    </div>
  );

  if (step === 1) return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", padding: "48px 24px 24px", position: "relative", zIndex: 1 }}>
      <div style={{ animation: "fu 0.6s ease-out both" }}>
        <p style={{ fontSize: 12, color: "var(--ac)", letterSpacing: 3, textTransform: "uppercase", marginBottom: 8 }}>Step 1 of 3</p>
        <h2 style={{ fontFamily: FD, fontSize: 32, fontWeight: 300, marginBottom: 8 }}>What do we call you?</h2>
        <p style={{ fontSize: 14, color: "var(--ts)", marginBottom: 32 }}>The stars need a name to whisper to.</p>
      </div>
      <div style={{ animation: "fu 0.6s ease-out 0.2s both" }}>
        <input value={name} onChange={e => setName(e.target.value)} placeholder="Your name..." onKeyDown={e => e.key === "Enter" && name.trim() && setStep(2)}
          style={{ width: "100%", padding: "18px 24px", borderRadius: 16, background: "var(--gl)", border: "1px solid var(--bl)", color: "var(--tp)", fontSize: 18, fontFamily: FD, outline: "none", transition: "border-color 0.3s", letterSpacing: 0.5 }}
          onFocus={e => e.target.style.borderColor = "rgba(196,161,255,0.3)"} onBlur={e => e.target.style.borderColor = "var(--bl)"} />
      </div>
      <div style={{ marginTop: "auto", animation: "fu 0.6s ease-out 0.4s both" }}><Bt onClick={() => name.trim() && setStep(2)} disabled={!name.trim()} style={{ width: "100%", padding: 18 }}>Continue ›</Bt></div>
    </div>
  );

  if (step === 2) return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", padding: "48px 24px 24px", position: "relative", zIndex: 1 }}>
      <div style={{ animation: "fu 0.6s ease-out both" }}>
        <p style={{ fontSize: 12, color: "var(--ac)", letterSpacing: 3, textTransform: "uppercase", marginBottom: 8 }}>Step 2 of 3</p>
        <h2 style={{ fontFamily: FD, fontSize: 32, fontWeight: 300, marginBottom: 8 }}>When were you born?</h2>
        <p style={{ fontSize: 14, color: "var(--ts)", marginBottom: 24 }}>Accurate planetary positions need your birth date.</p>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 12, animation: "fu 0.6s ease-out 0.2s both" }}>
        <input type="date" value={dob} onChange={e => setDob(e.target.value)} style={{ width: "100%", padding: "16px 20px", borderRadius: 14, background: "var(--gl)", border: "1px solid var(--bl)", color: "var(--tp)", fontSize: 15, outline: "none", fontFamily: FB, colorScheme: "dark" }} />
        <p style={{ fontSize: 11, color: "var(--tm)", marginTop: 4 }}>Birth time makes predictions 10× more accurate (add later)</p>
      </div>
      <div style={{ marginTop: "auto", animation: "fu 0.6s ease-out 0.4s both" }}><Bt onClick={() => dob && setStep(3)} disabled={!dob} style={{ width: "100%", padding: 18 }}>Continue ›</Bt></div>
    </div>
  );

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", padding: "48px 24px 24px", position: "relative", zIndex: 1 }}>
      <div style={{ animation: "fu 0.6s ease-out both" }}>
        <p style={{ fontSize: 12, color: "var(--ac)", letterSpacing: 3, textTransform: "uppercase", marginBottom: 8 }}>Step 3 of 3</p>
        <h2 style={{ fontFamily: FD, fontSize: 32, fontWeight: 300, marginBottom: 8 }}>Your sign?</h2>
        <p style={{ fontSize: 14, color: "var(--ts)", marginBottom: 20 }}>You already know, don't you? 😏</p>
      </div>
      <div style={{ flex: 1, overflowY: "auto", paddingBottom: 80 }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10 }}>
          {signs.map(([k, da], i) => (
            <div key={k} onClick={() => setSign(k)} style={{ background: sign === k ? `linear-gradient(135deg, ${da.c}20, ${da.c2}15)` : "var(--gl)", border: `1px solid ${sign === k ? da.c + "40" : "var(--br)"}`, borderRadius: 18, padding: "16px 8px", textAlign: "center", cursor: "pointer", transition: "all 0.3s", animation: `fu 0.4s ease-out ${i * 40}ms both`, boxShadow: sign === k ? `0 4px 20px ${da.c}20` : "none" }}>
              <div style={{ fontSize: 28, marginBottom: 6 }}>{da.s}</div>
              <div style={{ fontSize: 12, fontWeight: 600, textTransform: "capitalize", color: sign === k ? da.c : "var(--tp)", marginBottom: 2 }}>{k}</div>
              <div style={{ fontSize: 9, color: "var(--tm)" }}>{da.d}</div>
            </div>
          ))}
        </div>
      </div>
      <div style={{ position: "absolute", bottom: 24, left: 24, right: 24 }}><Bt onClick={() => sign && onDone({ name, sign, dob })} disabled={!sign} style={{ width: "100%", padding: 18 }}>Enter the Cosmos ✦</Bt></div>
    </div>
  );
}

function Home({ user }) {
  const da = Z[user.sign];
  const [battery, setBattery] = useState(null);
  const [roast, setRoast] = useState(null);
  const [remedy, setRemedy] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    const load = async () => {
      setError("");
      const errs = [];
      // Battery
      try {
        const batteryRes = await apiPost("/api/battery", { user_id: user.id, sign: user.sign, dob: user.dob });
        if (active) setBattery(batteryRes);
      } catch (e) {
        errs.push(e.message || "Battery failed");
      }
      // Roast
      try {
        const roastRes = await apiPost("/api/roast", { user_id: user.id, sign: user.sign });
        if (active) setRoast(roastRes);
      } catch (e) {
        errs.push(e.message || "Roast failed");
      }
      // Remedy
      try {
        const remedyRes = await apiPost("/api/remedy", { user_id: user.id, sign: user.sign, concern: "general" });
        if (active) setRemedy(remedyRes);
      } catch (e) {
        errs.push(e.message || "Remedy failed");
      }
      if (active && errs.length) {
        setError(errs.join(" | "));
      }
    };
    load();
    return () => { active = false; };
  }, [user.id, user.sign, user.dob]);

  const bv = battery?.percentage ?? 60;
  const bc = bv > 70 ? "#00E676" : bv > 40 ? "#FFD740" : bv > 20 ? "#FF9100" : "#FF1744";
  const bm = bv > 70 ? "Star Power HIGH" : bv > 40 ? "Steady vibes" : bv > 20 ? "Low energy — lay low" : "CRITICAL — hibernate";
  const td = new Date();
  const dn = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const mn = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

  return (
    <div style={{ padding: "20px 16px 120px", overflowY: "auto", height: "100%" }}>
      <div style={{ marginBottom: 28, animation: "fu 0.6s ease-out both" }}>
        <p style={{ fontSize: 12, color: "var(--tm)", letterSpacing: 2, textTransform: "uppercase", marginBottom: 6 }}>{dn[td.getDay()]} • {mn[td.getMonth()]} {td.getDate()}</p>
        <h1 style={{ fontFamily: FD, fontSize: 32, fontWeight: 300 }}>Hey, {user.name} <span style={{ fontSize: 24 }}>{da.e}</span></h1>
        <p style={{ fontSize: 13, color: "var(--ts)", marginTop: 4 }}>{da.s} {user.sign.charAt(0).toUpperCase() + user.sign.slice(1)} • {da.r} • Ruled by {da.p}</p>
        {error && <p style={{ fontSize: 12, color: "#FF8A9E", marginTop: 6 }}>{error}</p>}
      </div>

      <GC d={100} style={{ marginBottom: 16, padding: "28px 24px" }}>
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, background: `radial-gradient(ellipse at 30% 30%, ${bc}10, transparent 70%)`, pointerEvents: "none", borderRadius: 24 }} />
        <div style={{ position: "relative", zIndex: 1 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <span style={{ fontSize: 11, letterSpacing: 3, color: "var(--tm)", textTransform: "uppercase", fontFamily: FD }}>Cosmic Battery</span>
            <Bd color={bc} style={{ fontSize: 10 }}>{bm}</Bd>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
            <div style={{ flex: 1, height: 32, borderRadius: 12, background: "rgba(255,255,255,0.05)", border: "1px solid var(--br)", overflow: "hidden" }}>
              <div style={{ height: "100%", borderRadius: 11, background: `linear-gradient(90deg, ${bc}90, ${bc})`, width: `${bv}%`, transition: "width 1.5s cubic-bezier(0.16,1,0.3,1)", boxShadow: `0 0 20px ${bc}40`, position: "relative" }}>
                <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(255,255,255,0.2), transparent)", borderRadius: 11 }} />
              </div>
            </div>
            <span style={{ fontFamily: FM, fontSize: 22, fontWeight: 500, color: bc, minWidth: 52, textAlign: "right" }}>{bv}%</span>
          </div>
          <p style={{ fontSize: 12, color: "var(--ts)", lineHeight: 1.6 }}>{battery?.message || "Pulling your current transits..."}</p>
        </div>
      </GC>

      <GC d={200} style={{ marginBottom: 16, borderLeft: `2px solid ${da.c}40` }}>
        <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
          <div style={{ width: 36, height: 36, borderRadius: 12, background: `${da.c}15`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, flexShrink: 0 }}>{da.s}</div>
          <div>
            <div style={{ fontSize: 11, color: "var(--tm)", letterSpacing: 2, textTransform: "uppercase", marginBottom: 8, fontFamily: FD }}>Today's Roast</div>
            <p style={{ fontSize: 14, lineHeight: 1.7 }}>{roast?.roast || "Warming up Aura's roast engine..."}</p>
          </div>
        </div>
      </GC>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 16 }}>
        {[{ ic: "💬", l: "Vibe Check", s: "Chat with Aura", cl: "#C4A1FF" }, { ic: "📸", l: "Receipts Judge", s: "Analyze screenshots", cl: "#FF8A9E" }, { ic: "💘", l: "Match Check", s: "Compatibility scan", cl: "#7EB8FF" }, { ic: "🪔", l: "Today's Upay", s: "Cosmic remedy", cl: "#D4A574" }].map((item, i) => (
          <GC key={i} d={300 + i * 80} style={{ padding: "18px 16px" }}>
            <div style={{ fontSize: 26, marginBottom: 10 }}>{item.ic}</div>
            <div style={{ fontSize: 13, fontWeight: 600, color: item.cl, marginBottom: 2 }}>{item.l}</div>
            <div style={{ fontSize: 11, color: "var(--tm)" }}>{item.s}</div>
          </GC>
        ))}
      </div>

      <GC d={600} style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, letterSpacing: 3, color: "var(--tm)", textTransform: "uppercase", marginBottom: 16, fontFamily: FD }}>Active Transits</div>
        {(battery?.active_transits || []).slice(0, 4).map((t, i) => (
          <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: i < 3 ? "1px solid var(--br)" : "none" }}>
            <div><div style={{ fontSize: 13, fontWeight: 500, marginBottom: 2 }}>{t.planet}</div><div style={{ fontSize: 11, color: "var(--tm)" }}>{t.effect}</div></div>
            <div style={{ textAlign: "right" }}><Bd color={t.status === "Retrograde" ? "#FF8A9E" : "#00E676"} style={{ fontSize: 9, marginBottom: 4 }}>{t.status}</Bd><div style={{ fontSize: 11, color: "var(--ts)" }}>{t.sign}</div></div>
          </div>
        ))}
        {(!battery || (battery.active_transits || []).length === 0) && (
          <p style={{ fontSize: 12, color: "var(--tm)" }}>Loading transits...</p>
        )}
      </GC>

      <GC d={700} style={{ background: "linear-gradient(135deg, rgba(212,165,116,0.08), rgba(184,134,11,0.04))", borderColor: "rgba(212,165,116,0.12)" }}>
        <div style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
          <div style={{ fontSize: 32 }}>{remedy?.icon || "🪔"}</div>
          <div>
            <div style={{ fontSize: 11, color: "var(--gd)", letterSpacing: 2, textTransform: "uppercase", marginBottom: 6, fontFamily: FD }}>Today's Upay</div>
            <p style={{ fontSize: 14, fontWeight: 500, marginBottom: 4 }}>{remedy?.title || "Daily Upay"}</p>
            <p style={{ fontSize: 13, color: "var(--ts)", lineHeight: 1.6 }}>{remedy?.description || "Aligning your energy..."}</p>
            <Bd color="var(--gd)" style={{ marginTop: 8, fontSize: 9 }}>For: {remedy?.for_concern || "general"}</Bd>
          </div>
        </div>
      </GC>
    </div>
  );
}

function Chat({ user }) {
  const [msgs, setMsgs] = useState([{ f: "a", t: `Hey ${user.name}! ✨ I've been looking at your chart and we need to TALK. What's on your mind?` }]);
  const [inp, setInp] = useState("");
  const [mode, setMode] = useState("b");
  const [typing, setTyping] = useState(false);
  const ref = useRef(null);

  useEffect(() => { ref.current && (ref.current.scrollTop = ref.current.scrollHeight); }, [msgs, typing]);

  const send = async () => {
    if (!inp.trim()) return;
    const txt = inp.trim();
    setInp("");
    setMsgs(p => [...p, { f: "u", t: txt }]);
    setTyping(true);

    try {
      const history = msgs.map(m => ({ role: m.f === "u" ? "user" : "assistant", content: m.t }));
      const data = await apiPost("/api/chat", {
        user_id: user.id,
        message: txt,
        mode: mode === "b" ? "bestie" : "guru",
        conversation_history: history,
      });
      setTyping(false);
      setMsgs(p => [...p, { f: "a", t: data.reply }]);
    } catch (e) {
      setTyping(false);
      setMsgs(p => [...p, { f: "a", t: e.message || "Mercury retrograde is messing with the connection. Try again?" }]);
    }
  };

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <div style={{ padding: "16px 20px", display: "flex", justifyContent: "space-between", alignItems: "center", background: "rgba(7,6,14,0.8)", backdropFilter: "blur(20px)", borderBottom: "1px solid var(--br)", zIndex: 2 }}>
        <div><h3 style={{ fontFamily: FD, fontSize: 20, fontWeight: 400 }}>Vibe Check</h3><p style={{ fontSize: 11, color: "var(--tm)" }}>{mode === "b" ? "Bestie Mode • Casual & Real" : "Guru Mode • Deep Vedic Analysis"}</p></div>
        <div style={{ display: "flex", background: "var(--gl)", borderRadius: 12, border: "1px solid var(--br)", overflow: "hidden" }}>
          {[["b", "💬 Bestie"], ["g", "🕉️ Guru"]].map(([m, l]) => (
            <button key={m} onClick={() => setMode(m)} style={{ padding: "8px 14px", fontSize: 11, fontWeight: 600, background: mode === m ? "rgba(196,161,255,0.15)" : "transparent", color: mode === m ? "var(--ac)" : "var(--tm)", border: "none", cursor: "pointer", textTransform: "uppercase", letterSpacing: 1, fontFamily: FB, transition: "all 0.3s" }}>{l}</button>
          ))}
        </div>
      </div>

      <div ref={ref} style={{ flex: 1, overflowY: "auto", padding: "16px 16px 8px" }}>
        {msgs.map((m, i) => (
          <div key={i} style={{ display: "flex", justifyContent: m.f === "u" ? "flex-end" : "flex-start", marginBottom: 12, animation: "fu 0.3s ease-out both" }}>
            {m.f === "a" && <div style={{ width: 32, height: 32, borderRadius: 12, marginRight: 8, flexShrink: 0, background: "linear-gradient(135deg, #C4A1FF30, #FF8A9E20)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, border: "1px solid var(--br)" }}>✦</div>}
            <div style={{ maxWidth: "78%", padding: "14px 18px", borderRadius: 20, background: m.f === "u" ? "linear-gradient(135deg, rgba(196,161,255,0.2), rgba(139,111,212,0.15))" : "var(--gl)", border: `1px solid ${m.f === "u" ? "rgba(196,161,255,0.2)" : "var(--br)"}`, borderBottomRightRadius: m.f === "u" ? 6 : 20, borderBottomLeftRadius: m.f === "a" ? 6 : 20 }}>
              <p style={{ fontSize: 14, lineHeight: 1.65 }}>{m.t}</p>
            </div>
          </div>
        ))}
        {typing && (
          <div style={{ display: "flex", gap: 8, marginBottom: 12, animation: "fi 0.3s ease" }}>
            <div style={{ width: 32, height: 32, borderRadius: 12, background: "linear-gradient(135deg, #C4A1FF30, #FF8A9E20)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, border: "1px solid var(--br)" }}>✦</div>
            <div style={{ padding: "12px 18px", borderRadius: 20, borderBottomLeftRadius: 6, background: "var(--gl)", border: "1px solid var(--br)" }}>
              <div style={{ display: "flex", gap: 4 }}>{[0, 1, 2].map(d => <div key={d} style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--ac)", animation: `pu 1.2s ease-in-out infinite`, animationDelay: `${d * 0.2}s` }} />)}</div>
            </div>
          </div>
        )}
      </div>

      <div style={{ padding: "12px 16px 24px", background: "rgba(7,6,14,0.85)", backdropFilter: "blur(20px)", borderTop: "1px solid var(--br)" }}>
        <div style={{ display: "flex", gap: 6, marginBottom: 10, overflowX: "auto", paddingBottom: 4 }}>
          {(mode === "b" ? ["Should I text them? 📱", "Why am I anxious?", "Will this week be good?", "Roast me 🔥"] : ["Read my Kundli", "Marriage timing", "Career guidance", "Dasha analysis"]).map((q, i) => (
            <button key={i} onClick={() => setInp(q)} style={{ padding: "6px 14px", borderRadius: 20, fontSize: 11, background: "var(--gl)", border: "1px solid var(--br)", color: "var(--ts)", cursor: "pointer", whiteSpace: "nowrap", fontFamily: FB, transition: "all 0.2s" }}>{q}</button>
          ))}
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <input value={inp} onChange={e => setInp(e.target.value)} onKeyDown={e => e.key === "Enter" && send()} placeholder={mode === "b" ? "Ask me anything..." : "Ask about your chart..."} style={{ flex: 1, padding: "14px 20px", borderRadius: 16, background: "var(--gl2)", border: "1px solid var(--bl)", color: "var(--tp)", fontSize: 14, outline: "none", fontFamily: FB }} />
          <button onClick={send} style={{ width: 48, height: 48, borderRadius: 16, background: inp.trim() ? "linear-gradient(135deg, #C4A1FF, #8B6FD4)" : "var(--gl2)", border: "none", color: "#fff", fontSize: 18, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", transition: "all 0.3s", boxShadow: inp.trim() ? "0 4px 20px rgba(196,161,255,0.3)" : "none" }}>↑</button>
        </div>
      </div>
    </div>
  );
}

function Receipts({ user }) {
  const [phase, setPhase] = useState("upload");
  const [result, setResult] = useState(null);
  const [imageData, setImageData] = useState("");
  const [error, setError] = useState("");
  const fileRef = useRef(null);

  const handleFile = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setImageData(reader.result || "");
    reader.readAsDataURL(file);
  };

  const analyze = async () => {
    if (!imageData) {
      setError("Please upload a screenshot first.");
      return;
    }
    setError("");
    setPhase("loading");
    try {
      const data = await apiPost("/api/receipts", {
        user_id: user.id,
        image_base64: imageData,
      });
      setResult(data);
      setPhase("result");
    } catch (e) {
      setPhase("upload");
      setError(e.message || "Failed to analyze screenshot");
    }
  };

  return (
    <div style={{ padding: "20px 16px 120px", overflowY: "auto", height: "100%" }}>
      <div style={{ animation: "fu 0.6s ease-out both" }}>
        <h2 style={{ fontFamily: FD, fontSize: 28, fontWeight: 400, marginBottom: 6 }}>📸 Receipts Judge</h2>
        <p style={{ fontSize: 13, color: "var(--ts)", lineHeight: 1.5 }}>Upload a screenshot. Get the cosmic truth.</p>
        {error && <p style={{ fontSize: 12, color: "#FF8A9E", marginTop: 6 }}>{error}</p>}
      </div>

      {phase === "upload" && (
        <div style={{ marginTop: 24 }}>
          <input ref={fileRef} type="file" accept="image/*" onChange={handleFile} style={{ display: "none" }} />
          <GC d={200} style={{ padding: "48px 24px", textAlign: "center", border: "2px dashed rgba(255,138,158,0.2)", cursor: "pointer" }} onClick={() => fileRef.current?.click()}>
            <div style={{ fontSize: 48, marginBottom: 16, animation: "br 3s ease-in-out infinite" }}>📲</div>
            <p style={{ fontSize: 16, fontWeight: 500, marginBottom: 8, fontFamily: FD }}>{imageData ? "Screenshot ready" : "Drop the receipts"}</p>
            <p style={{ fontSize: 13, color: "var(--ts)", lineHeight: 1.6, marginBottom: 20 }}>Upload a WhatsApp, Instagram, or text screenshot.<br />The cosmos will judge them.</p>
            <Bt v="ghost" style={{ pointerEvents: "none" }}>📎 Upload Screenshot</Bt>
          </GC>
          <div style={{ marginTop: 16 }}>
            <Bt onClick={analyze} disabled={!imageData} style={{ width: "100%" }}>Analyze Now ✦</Bt>
          </div>
        </div>
      )}

      {phase === "loading" && (
        <div style={{ textAlign: "center", padding: "60px 20px", animation: "fi 0.5s ease" }}>
          <div style={{ fontSize: 48, marginBottom: 24, animation: "br 1.5s ease-in-out infinite" }}>🔮</div>
          <h3 style={{ fontFamily: FD, fontSize: 22, fontWeight: 400, marginBottom: 12 }}>Reading the cosmos...</h3>
          <p style={{ fontSize: 13, color: "var(--ts)", marginBottom: 24 }}>Checking planetary positions at time of message</p>
          {["Extracting text & timestamps", "Mapping to planetary transits", "Calculating red flag score"].map((s, i) => (
            <div key={i} style={{ marginBottom: 12, animation: `fu 0.5s ease-out ${i * 400}ms both` }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}><span style={{ fontSize: 11, color: "var(--tm)" }}>{s}</span></div>
              <div style={{ height: 3, borderRadius: 2, background: "var(--gl2)", overflow: "hidden" }}><div style={{ height: "100%", borderRadius: 2, background: "linear-gradient(90deg, var(--ac), var(--a2))", animation: "sh 1.5s ease-in-out infinite", backgroundSize: "200% 100%", animationDelay: `${i * 300}ms`, width: "100%" }} /></div>
            </div>
          ))}
        </div>
      )}

      {phase === "result" && result && (
        <div style={{ marginTop: 20 }}>
          <GC d={0} style={{ textAlign: "center", padding: "32px 24px", background: "linear-gradient(135deg, rgba(255,138,158,0.08), rgba(196,161,255,0.05))", marginBottom: 16 }}>
            <div style={{ fontSize: 11, letterSpacing: 3, color: "var(--a2)", textTransform: "uppercase", marginBottom: 16, fontFamily: FD }}>Cosmic Verdict</div>
            <div style={{ fontSize: 64, fontFamily: FM, fontWeight: 500, color: result.toxic_score > 70 ? "#FF1744" : "#FF9100", lineHeight: 1, textShadow: `0 0 40px ${result.toxic_score > 70 ? "#FF174440" : "#FF910040"}`, marginBottom: 4 }}>{result.toxic_score}</div>
            <p style={{ fontSize: 12, color: "var(--tm)", marginBottom: 8 }}>Toxic Score</p>
            <Bd color="#FF1744">{result.red_flags?.length || 0} Red Flags Detected</Bd>
          </GC>
          <GC d={200} style={{ marginBottom: 12 }}><div style={{ fontSize: 11, letterSpacing: 2, color: "var(--ac)", textTransform: "uppercase", marginBottom: 10, fontFamily: FD }}>The Reading</div><p style={{ fontSize: 14, lineHeight: 1.7 }}>{result.verdict}</p></GC>
          <GC d={300} style={{ marginBottom: 12 }}><div style={{ fontSize: 11, letterSpacing: 2, color: "var(--a3)", textTransform: "uppercase", marginBottom: 10, fontFamily: FD }}>Planetary Context</div><p style={{ fontSize: 13, lineHeight: 1.6, color: "var(--ts)" }}>{result.planetary_context}</p></GC>
          <GC d={400} style={{ marginBottom: 16, borderLeft: "2px solid var(--gd)" }}><div style={{ fontSize: 11, letterSpacing: 2, color: "var(--gd)", textTransform: "uppercase", marginBottom: 10, fontFamily: FD }}>Aura's Advice</div><p style={{ fontSize: 13, lineHeight: 1.6, color: "var(--ts)" }}>{result.advice}</p></GC>
          <div style={{ display: "flex", gap: 8 }}><Bt v="ghost" onClick={() => { setPhase("upload"); setResult(null); }} style={{ flex: 1 }}>Analyze Another</Bt><Bt style={{ flex: 1 }}>Share Report ↗</Bt></div>
        </div>
      )}
    </div>
  );
}

function Match({ user }) {
  const [crush, setCrush] = useState(null);
  const [res, setRes] = useState(null);
  const [loading, setLoading] = useState(false);
  const ud = Z[user.sign];

  const check = async (c) => {
    setCrush(c); setLoading(true);
    try {
      const data = await apiPost("/api/match", {
        user_id: user.id,
        user_sign: user.sign,
        crush_sign: c,
      });
      setRes({
        sc: data.overall_score,
        t: data.toxic_level,
        v: data.verdict,
        breakdown: data.breakdown,
        cs: c,
        cd: Z[c],
      });
    } catch (e) {
      setRes({
        sc: 0,
        t: "Unknown",
        v: e.message || "Match analysis failed",
        breakdown: { emotional: 0, physical: 0, intellectual: 0, spiritual: 0 },
        cs: c,
        cd: Z[c],
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px 16px 120px", overflowY: "auto", height: "100%" }}>
      <div style={{ animation: "fu 0.6s ease-out both" }}>
        <h2 style={{ fontFamily: FD, fontSize: 28, fontWeight: 400, marginBottom: 6 }}>💘 Match Check</h2>
        <p style={{ fontSize: 13, color: "var(--ts)" }}>Pick their sign. We'll tell you if it's love or a lesson.</p>
      </div>

      {!crush ? (
        <div style={{ marginTop: 20 }}>
          <GC d={100} style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20, padding: "18px 20px" }}>
            <div style={{ width: 48, height: 48, borderRadius: 16, background: `${ud.c}15`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 26, border: `1px solid ${ud.c}30` }}>{ud.s}</div>
            <div><div style={{ fontSize: 15, fontWeight: 600, textTransform: "capitalize" }}>{user.name}</div><div style={{ fontSize: 12, color: ud.c }}>{user.sign} • {ud.el} {ud.e}</div></div>
            <div style={{ marginLeft: "auto", fontSize: 24, color: "var(--a2)" }}>♡</div>
            <div style={{ width: 48, height: 48, borderRadius: 16, background: "var(--gl2)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, border: "2px dashed var(--bl)" }}>?</div>
          </GC>
          <p style={{ fontSize: 11, color: "var(--tm)", letterSpacing: 2, textTransform: "uppercase", marginBottom: 12, animation: "fu 0.5s ease-out 0.2s both" }}>Select their sign</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8 }}>
            {Object.entries(Z).map(([k, d], i) => (
              <div key={k} onClick={() => check(k)} style={{ background: "var(--gl)", border: "1px solid var(--br)", borderRadius: 16, padding: "14px 6px", textAlign: "center", cursor: "pointer", transition: "all 0.3s", animation: `fu 0.4s ease-out ${i * 30}ms both` }}>
                <div style={{ fontSize: 22, marginBottom: 4 }}>{d.s}</div>
                <div style={{ fontSize: 10, textTransform: "capitalize", color: "var(--ts)" }}>{k}</div>
              </div>
            ))}
          </div>
        </div>
      ) : loading ? (
        <div style={{ textAlign: "center", padding: "60px 20px", animation: "fi 0.5s ease" }}>
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 20, marginBottom: 32 }}>
            <div style={{ fontSize: 48, animation: "br 1.5s ease-in-out infinite" }}>{ud.s}</div>
            <div style={{ fontSize: 24, color: "var(--a2)", animation: "pu 1s ease-in-out infinite" }}>♡</div>
            <div style={{ fontSize: 48, animation: "br 1.5s ease-in-out infinite 0.5s" }}>{Z[crush].s}</div>
          </div>
          <h3 style={{ fontFamily: FD, fontSize: 22, fontWeight: 400, marginBottom: 8 }}>Reading synastry...</h3>
          <p style={{ fontSize: 13, color: "var(--ts)" }}>Calculating {ud.el} × {Z[crush].el} compatibility</p>
        </div>
      ) : res && (
        <div style={{ marginTop: 20 }}>
          <GC d={0} style={{ textAlign: "center", padding: "32px 24px", marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 16, marginBottom: 20 }}>
              <div style={{ textAlign: "center" }}><div style={{ width: 56, height: 56, borderRadius: 18, background: `${ud.c}15`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28, border: `1px solid ${ud.c}30`, margin: "0 auto 6px" }}>{ud.s}</div><div style={{ fontSize: 11, textTransform: "capitalize", color: "var(--ts)" }}>{user.sign}</div></div>
              <div style={{ width: 64, height: 64, borderRadius: "50%", background: `conic-gradient(${res.sc > 70 ? "#00E676" : res.sc > 50 ? "#FFD740" : "#FF1744"} ${res.sc}%, var(--gl2) 0)`, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: `0 0 30px ${res.sc > 70 ? "#00E67620" : "#FF174420"}` }}>
                <div style={{ width: 52, height: 52, borderRadius: "50%", background: "var(--bd)", display: "flex", alignItems: "center", justifyContent: "center" }}><span style={{ fontFamily: FM, fontSize: 18, fontWeight: 600, color: res.sc > 70 ? "#00E676" : res.sc > 50 ? "#FFD740" : "#FF1744" }}>{res.sc}%</span></div>
              </div>
              <div style={{ textAlign: "center" }}><div style={{ width: 56, height: 56, borderRadius: 18, background: `${res.cd.c}15`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28, border: `1px solid ${res.cd.c}30`, margin: "0 auto 6px" }}>{res.cd.s}</div><div style={{ fontSize: 11, textTransform: "capitalize", color: "var(--ts)" }}>{res.cs}</div></div>
            </div>
            <Bd color={res.t === "Low" ? "#00E676" : res.t === "High" ? "#FF1744" : "#FFD740"}>Toxic Level: {res.t}</Bd>
          </GC>
          <GC d={200} style={{ marginBottom: 12 }}><div style={{ fontSize: 11, letterSpacing: 2, color: "var(--a2)", textTransform: "uppercase", marginBottom: 10, fontFamily: FD }}>The Verdict</div><p style={{ fontSize: 15, lineHeight: 1.7, fontFamily: FD }}>{res.v}</p></GC>
          <GC d={300} style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 11, letterSpacing: 2, color: "var(--tm)", textTransform: "uppercase", marginBottom: 14, fontFamily: FD }}>Compatibility Breakdown</div>
            {[
              { l: "Emotional", v: res.breakdown?.emotional ?? 0, c: "#4FC3F7" },
              { l: "Physical", v: res.breakdown?.physical ?? 0, c: "#FF8A9E" },
              { l: "Intellectual", v: res.breakdown?.intellectual ?? 0, c: "#C4A1FF" },
              { l: "Spiritual", v: res.breakdown?.spiritual ?? 0, c: "#D4A574" }
            ].map((dim, i) => (
              <div key={i} style={{ marginBottom: 10 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}><span style={{ fontSize: 11, color: "var(--ts)" }}>{dim.l}</span><span style={{ fontSize: 11, fontFamily: FM, color: dim.c }}>{dim.v}%</span></div>
                <div style={{ height: 4, borderRadius: 2, background: "var(--gl2)" }}><div style={{ height: "100%", borderRadius: 2, width: `${dim.v}%`, background: dim.c, transition: "width 1s ease", boxShadow: `0 0 8px ${dim.c}40` }} /></div>
              </div>
            ))}
          </GC>
          <div style={{ display: "flex", gap: 8 }}><Bt v="ghost" onClick={() => { setCrush(null); setRes(null); }} style={{ flex: 1 }}>Try Another</Bt><Bt style={{ flex: 1 }}>Share Match ↗</Bt></div>
        </div>
      )}
    </div>
  );
}

function Profile({ user, onUserUpdate }) {
  const da = Z[user.sign];
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const loadRazorpay = () => new Promise((resolve, reject) => {
    if (window.Razorpay) return resolve(true);
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.onload = () => resolve(true);
    script.onerror = () => reject(new Error("Failed to load Razorpay"));
    document.body.appendChild(script);
  });

  const handlePurchase = async (item, amount) => {
    const keyId = import.meta.env.VITE_RAZORPAY_KEY_ID;
    if (!keyId) {
      setError("Razorpay key not configured in frontend env");
      return;
    }
    setError("");
    setBusy(true);
    try {
      await loadRazorpay();
      const order = await apiPost("/api/payments/create-order", {
        user_id: user.id,
        item,
        amount,
      });

      const options = {
        key: keyId,
        amount: order.amount,
        currency: order.currency,
        name: "Aura AI",
        description: "Aura AI purchase",
        order_id: order.razorpay_order_id,
        handler: async (response) => {
          await apiPost("/api/payments/verify", {
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          });
          if (item === "inner_circle") {
            onUserUpdate({ is_premium: true });
          }
        },
        theme: { color: "#C4A1FF" }
      };

      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (e) {
      setError(e.message || "Payment failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ padding: "20px 16px 120px", overflowY: "auto", height: "100%" }}>
      <GC d={0} style={{ textAlign: "center", padding: "32px 24px", marginBottom: 16 }}>
        <div style={{ width: 80, height: 80, borderRadius: 24, margin: "0 auto 16px", background: `linear-gradient(135deg, ${da.c}30, ${da.c2}20)`, border: `2px solid ${da.c}40`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 36, boxShadow: `0 8px 32px ${da.c}20` }}>{da.s}</div>
        <h2 style={{ fontFamily: FD, fontSize: 26, fontWeight: 400, marginBottom: 4 }}>{user.name}</h2>
        <p style={{ fontSize: 13, color: da.c, textTransform: "capitalize", marginBottom: 12 }}>{user.sign} • {da.el} Sign</p>
        <div style={{ display: "flex", justifyContent: "center", gap: 6, flexWrap: "wrap" }}><Bd color={da.c}>{da.r}</Bd><Bd color="var(--gd)">Ruled by {da.p}</Bd><Bd color="var(--a3)">{da.trait}</Bd></div>
        {user.is_premium && <Bd color="var(--gd)" style={{ marginTop: 10 }}>Premium Active</Bd>}
      </GC>

      <GC d={200} style={{ padding: "28px 24px", marginBottom: 16, background: "linear-gradient(135deg, rgba(212,165,116,0.1), rgba(184,134,11,0.05), rgba(196,161,255,0.05))", borderColor: "rgba(212,165,116,0.2)" }}>
        <div style={{ position: "absolute", top: 16, right: 16 }}><Bd color="var(--gd)">✦ Inner Circle</Bd></div>
        <div style={{ fontSize: 11, letterSpacing: 3, color: "var(--gd)", textTransform: "uppercase", marginBottom: 12, fontFamily: FD }}>Unlock Everything</div>
        <h3 style={{ fontFamily: FD, fontSize: 22, fontWeight: 400, marginBottom: 12 }}>₹199/month</h3>
        {["Unlimited AI Chat (Bestie + Guru)", "Unlimited Screenshot Analysis", "Future Battery — next week's luck", "Deep Dive Annual Predictions", "Priority Cosmic Remedies"].map((f, i) => (
          <div key={i} style={{ fontSize: 13, color: "var(--ts)", padding: "5px 0", display: "flex", alignItems: "center", gap: 8 }}><span style={{ color: "var(--gd)", fontSize: 10 }}>✦</span>{f}</div>
        ))}
        <div style={{ marginTop: 16 }}><Bt v="gold" disabled={busy || user.is_premium} onClick={() => handlePurchase("inner_circle", 19900)} style={{ width: "100%" }}>{user.is_premium ? "Already Premium" : "Join Inner Circle"}</Bt></div>
        {error && <p style={{ fontSize: 12, color: "#FF8A9E", marginTop: 8 }}>{error}</p>}
      </GC>

      <p style={{ fontSize: 11, color: "var(--tm)", letterSpacing: 2, textTransform: "uppercase", marginBottom: 12, animation: "fu 0.5s ease-out 0.3s both" }}>Quick Buys</p>
      {[{ ic: "📸", t: "1× Receipts Judge", p: "₹29", d: "Analyze one screenshot", item: "receipts_single", amount: 2900 }, { ic: "📋", t: "2026 Deep Dive Report", p: "₹49", d: "Full year prediction PDF", item: "deep_dive_report", amount: 4900 }, { ic: "🪔", t: "Instant Upay", p: "₹11", d: "Personalized cosmic remedy", item: "instant_upay", amount: 1100 }].map((item, i) => (
        <GC key={i} d={400 + i * 100} style={{ display: "flex", alignItems: "center", gap: 14, padding: "16px 18px", marginBottom: 8 }}>
          <div style={{ fontSize: 28, flexShrink: 0 }}>{item.ic}</div>
          <div style={{ flex: 1 }}><div style={{ fontSize: 14, fontWeight: 500, marginBottom: 2 }}>{item.t}</div><div style={{ fontSize: 11, color: "var(--tm)" }}>{item.d}</div></div>
          <Bt v="secondary" onClick={() => handlePurchase(item.item, item.amount)} style={{ padding: "8px 16px", fontSize: 12, borderRadius: 12 }}>{item.p}</Bt>
        </GC>
      ))}

      <p style={{ fontSize: 11, color: "var(--tm)", letterSpacing: 2, textTransform: "uppercase", marginBottom: 12, marginTop: 16, animation: "fu 0.5s ease-out 0.5s both" }}>Remedy Library</p>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
        {REMED.slice(0, 6).map((r, i) => (
          <GC key={i} d={600 + i * 60} style={{ padding: "16px 14px" }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>{r.i}</div>
            <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4 }}>{r.t}</div>
            <div style={{ fontSize: 11, color: "var(--tm)", lineHeight: 1.5 }}>{r.d}</div>
            <Bd color="var(--gd)" style={{ marginTop: 8, fontSize: 9 }}>{r.f}</Bd>
          </GC>
        ))}
      </div>
    </div>
  );
}

export default function AuraApp() {
  const [user, setUser] = useState(null);
  const [tab, setTab] = useState("home");
  const [tr, setTr] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const stored = localStorage.getItem("aura_user");
    if (stored) {
      try { setUser(JSON.parse(stored)); } catch { /* ignore */ }
    }
  }, []);

  const handleOnboardDone = async ({ name, sign, dob }) => {
    setBusy(true);
    setError("");
    try {
      const data = await apiPost("/api/user", { name, sign, dob });
      const next = {
        id: data.id,
        name: data.name,
        sign: data.sign,
        dob: data.dob,
        is_premium: data.is_premium || false,
      };
      setUser(next);
      localStorage.setItem("aura_user", JSON.stringify(next));
    } catch (e) {
      setError(e.message || "Failed to create user");
    } finally {
      setBusy(false);
    }
  };

  const updateUser = (updates) => {
    setUser(prev => {
      const next = { ...prev, ...updates };
      localStorage.setItem("aura_user", JSON.stringify(next));
      return next;
    });
  };

  const sw = (t) => { if (t === tab) return; setTr(true); setTimeout(() => { setTab(t); setTr(false); }, 150); };

  const tabs = [{ id: "home", ic: "✦", l: "Home" }, { id: "chat", ic: "💬", l: "Vibe" }, { id: "receipts", ic: "📸", l: "Receipts" }, { id: "match", ic: "💘", l: "Match" }, { id: "profile", ic: "👤", l: "Profile" }];

  return (
    <div style={{ width: "100%", height: "100vh", position: "relative", overflow: "hidden", background: "var(--bd)" }}>
      <style>{CSS}</style>
      <BG />
      <div style={{ position: "relative", zIndex: 1, width: "100%", maxWidth: 430, height: "100%", margin: "0 auto", display: "flex", flexDirection: "column", background: "rgba(7,6,14,0.3)" }}>
        {!user ? (
          <>
            {error && <div style={{ padding: "10px 16px", background: "rgba(255,138,158,0.12)", color: "#FF8A9E", fontSize: 12 }}>{error}</div>}
            <Onboard onDone={handleOnboardDone} />
          </>
        ) : (
          <>
            {busy && <div style={{ padding: "8px 16px", fontSize: 11, color: "var(--tm)" }}>Working on it...</div>}
            <div style={{ flex: 1, overflow: "hidden", opacity: tr ? 0 : 1, transform: tr ? "translateY(8px)" : "translateY(0)", transition: "all 0.15s ease" }}>
              {tab === "home" && <Home user={user} />}
              {tab === "chat" && <Chat user={user} />}
              {tab === "receipts" && <Receipts user={user} />}
              {tab === "match" && <Match user={user} />}
              {tab === "profile" && <Profile user={user} onUserUpdate={updateUser} />}
            </div>
            <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, padding: "8px 8px 20px", background: "linear-gradient(to top, rgba(7,6,14,0.98) 60%, rgba(7,6,14,0.85) 80%, transparent)", backdropFilter: "blur(20px)", display: "flex", justifyContent: "space-around", alignItems: "center", zIndex: 10 }}>
              {tabs.map(t => {
                const a = tab === t.id;
                return (
                  <button key={t.id} onClick={() => sw(t.id)} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4, background: "none", border: "none", cursor: "pointer", padding: "8px 10px", borderRadius: 14, minWidth: 52 }}>
                    <div style={{ fontSize: t.id === "home" ? 18 : 16, transition: "transform 0.3s", transform: a ? "scale(1.15)" : "scale(1)", filter: a ? "drop-shadow(0 0 8px rgba(196,161,255,0.5))" : "none" }}>{t.ic}</div>
                    <span style={{ fontSize: 10, fontWeight: a ? 600 : 400, color: a ? "var(--ac)" : "var(--tm)", letterSpacing: 0.3, transition: "color 0.3s" }}>{t.l}</span>
                    {a && <div style={{ width: 4, height: 4, borderRadius: "50%", background: "var(--ac)", boxShadow: "0 0 8px var(--ac)", marginTop: -2 }} />}
                  </button>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
