# ✦ Aura AI — Backend

**Your Cosmic Bestie. No Filter. No Judgement.**

Vedic astrology engine powered by Swiss Ephemeris + Gemini AI.

---

## Quick Start

```bash
# 1. Clone and enter directory
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your API keys (at minimum: GEMINI_API_KEY)

# 5. Run the server
uvicorn main:app --reload --port 8000

# 6. Open docs
# → http://localhost:8000/docs (Swagger UI — test all endpoints)
# → http://localhost:8000/redoc (Alternative docs)
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Vibe Check — Chat with Aura (Bestie/Guru mode) |
| `POST` | `/api/receipts` | Receipts Judge — Screenshot analysis |
| `POST` | `/api/match` | Match Check — Zodiac compatibility |
| `POST` | `/api/battery` | Cosmic Battery — Today's energy % |
| `POST` | `/api/roast` | Roast — Savage zodiac roast |
| `POST` | `/api/remedy` | Upay — Personalized Vedic remedy |
| `POST` | `/api/user` | Create user profile |
| `POST` | `/api/payments/create-order` | Razorpay order |
| `POST` | `/api/payments/verify` | Verify payment |
| `GET`  | `/health` | Health check |

---

## Architecture

```
Frontend (React PWA / Flutter)
    ↓ HTTPS
FastAPI Backend (this repo)
    ├── Pyswisseph → Real astronomical calculations
    ├── Gemini Flash → Bestie mode (fast, cheap)
    ├── Gemini Pro → Guru mode (deep analysis)
    ├── Gemini Vision → Screenshot analysis
    ├── Supabase → User data, chat history
    └── Razorpay → Payments (₹29 micro-txns, ₹199 subscription)
```

---

## How Astrological Calculations Work

### The Engine: Pyswisseph (Swiss Ephemeris)
- **NASA-grade accuracy** for planetary positions
- Uses **Lahiri Ayanamsa** (sidereal/Vedic system, not Western tropical)
- Calculates all 9 Vedic planets: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu

### What Gets Calculated
1. **User's Birth Chart**: Moon sign (Rashi), Nakshatra, Pada from DOB
2. **Current Transits**: Where all planets are RIGHT NOW in the sky
3. **House Positions**: Which house each planet occupies relative to user's Moon
4. **Aspects**: Conjunctions, oppositions, trines, squares between planets
5. **Retrogrades**: Which planets are moving backwards
6. **Combustion**: Which planets are too close to the Sun

### The Cosmic Battery Algorithm
```
Start: 60 (neutral)
Moon in houses 1,4,5,7,9,10,11 → +12
Moon in houses 6,8,12 → -15
Jupiter in houses 1,5,9,11 → +10
Saturn in houses 1,4,7,8,10,12 → -10
Mercury Retrograde → -7
Mars in bad houses → -8
Venus in good houses → +5
Final: Clamp to 5-98
```

---

## Connecting Frontend to Backend

Replace the mock data in the React app with API calls:

```javascript
// In Chat component, replace the mock send function:

const send = async () => {
  if (!input.trim()) return;
  const userMsg = input.trim();
  setInput("");
  setMessages(prev => [...prev, { from: "user", text: userMsg }]);
  setTyping(true);

  try {
    const res = await fetch("https://your-api.com/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: user.id,
        message: userMsg,
        mode: mode === "b" ? "bestie" : "guru",
        conversation_history: messages.map(m => ({
          role: m.from === "user" ? "user" : "assistant",
          content: m.text,
        })),
      }),
    });
    const data = await res.json();
    setTyping(false);
    setMessages(prev => [...prev, { from: "aura", text: data.reply }]);
  } catch (err) {
    setTyping(false);
    setMessages(prev => [...prev, {
      from: "aura",
      text: "Mercury retrograde is messing with the connection. Try again? 🔮"
    }]);
  }
};
```

---

## Deployment

### Option A: Railway (Recommended — $5/mo)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway init
railway up
```

### Option B: Render (Free tier available)
1. Push to GitHub
2. Connect repo on render.com
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

### Option C: VPS (DigitalOcean $6/mo)
```bash
# On your server
git clone your-repo
cd backend
pip install -r requirements.txt
cp .env.example .env  # Fill in keys

# Run with gunicorn for production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Cost Breakdown

| Component | Monthly Cost |
|-----------|-------------|
| Gemini Flash (Bestie chat) | ~$50 at 100k messages |
| Gemini Pro (Guru + Vision) | ~$150 at 50k calls |
| Pyswisseph | Free (local calculation) |
| Supabase (DB) | Free → $25 at scale |
| Railway/Render (hosting) | $5-$15 |
| **Total at 50k users** | **~$240/month** |

---

## TODO for Production

- [ ] Supabase integration for user storage
- [ ] Rate limiting (3 free messages/day, then paywall)
- [ ] Razorpay payment flow
- [ ] Push notifications (daily Vibe + Battery)
- [ ] WebSocket for real-time chat (instead of HTTP polling)
- [ ] Redis caching for battery calculations (cache per sign per hour)
- [ ] Admin dashboard for analytics
- [ ] Share image generator (for Receipts + Match reports)

---

**Built for the Aura AI project. The stars are watching. ✦**


---

## Production (Render + Supabase + Vercel)

### Supabase Setup
1. Create a Supabase project.
2. Run the SQL in `supabase_schema.sql` in the Supabase SQL editor.
3. Use the **Service Role Key** for backend access (never expose it to frontend).

### Render (Backend)
1. Create a new Web Service from this repo.
2. Root directory: `backend`
3. Environment: Docker
4. Set environment variables:
   - `APP_ENV=prod`
   - `GEMINI_API_KEY=...`
   - `SUPABASE_URL=...`
   - `SUPABASE_KEY=...` (service role)
   - `CORS_ORIGINS=https://<your-vercel-domain>`
   - `RAZORPAY_KEY_ID=...` (later)
   - `RAZORPAY_KEY_SECRET=...` (later)

The service will expose the API at `https://<your-render-domain>`.

### Vercel (Frontend)
1. Create a new Vercel project from this repo.
2. Set **Root Directory** to `frontend`.
3. Environment variables:
   - `VITE_API_BASE_URL=https://<your-render-domain>`
   - `VITE_RAZORPAY_KEY_ID=...` (later)
4. Build command: `npm run build`
5. Output directory: `dist`

---
