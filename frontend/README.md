# Aura AI — Frontend (Vite + React)

## Local Dev
```bash
npm install
cp .env.example .env
npm run dev
```

## Vercel Deploy
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `dist`
- Env Vars:
  - `VITE_API_BASE_URL=https://<your-render-domain>`
  - `VITE_RAZORPAY_KEY_ID=...` (when ready)
