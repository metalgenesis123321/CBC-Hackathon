# InterviewCoach AI

**AI-Powered Mock Interview Platform with 3D Scene & Structured STAR Feedback**

> HackASU 2026 — Claude Builder Club | Track 3: Economic Empowerment & Education

---

## Problem Statement

Existing interview prep platforms rely on static questions, lack adaptability to user responses, and deliver bulk feedback all at once. They don't support interactive follow-ups or clarification, making it difficult for users to truly understand and improve their answers in a dynamic, real-world interview context.

**Specifically:**

* **No follow-up questions** — Real interviewers probe deeper based on what you said. Every existing tool just moves to the next unrelated question.
* **No way to ask about your feedback** — You get a score and a wall of text. You can't ask "why was my Result section weak?" There's no conversation.
* **No replay** — You can't re-listen to what you actually said. You forget your mistakes within minutes.
* **Static question banks** — The same generic questions regardless of your company, role, or weak areas. Nothing adapts.
* **No adaptive difficulty or presentation** — Questions don't get harder as you improve, and feedback is dumped as a wall of text instead of being spoken, highlighted, and interactive.
* **Interview coaching costs $200–500/session** — First-gen students, career changers, and non-native speakers are hit the hardest.

**We built InterviewCoach AI to solve all of this:** a free, voice-first mock interview platform where an AI interviewer sits across from you in a 3D office, asks real company-specific questions, generates adaptive follow-ups, scores your STAR structure sentence-by-sentence, speaks personalized feedback out loud, and lets you ask questions about your score — all in real time. The first interview prep tool that gives you **feedback on the feedback**.

---

## What Makes This Different

* **Claude-powered 3D interaction (Artifacts)** — We leveraged Claude Artifacts to help design and simulate the interactive 3D interview experience, enabling rapid iteration on conversational UI + visual behavior.

* **Real-time spoken feedback** — The AI interviewer talks through what went well and what needs work, instead of dropping a wall of text.

* **Feedback on the feedback** — Ask follow-up questions like "Why was my Result weak?" and get a rewrite plus coaching guidance.

* **Adaptive to the user** — Questions, follow-ups, and coaching adjust to your weak areas and improvement over time.

* **3D interview experience** — A realistic interview scene makes the practice feel closer to a real conversation than a chatbox.

---

## What It Does

InterviewCoach helps job seekers practice interviews in an immersive 3D office environment. Users upload a resume, choose a target company and role, and receive personalized questions based on real interview data. They answer by voice, get real-time transcription, and receive structured STAR feedback with sentence-level analysis, delivery analysis, follow-up questions, and coaching plans.

---

## Key Features

* 🧍‍♂️ **3D Interview Scene** — Immersive mock interview environment
* 🎤 **Voice-First Interaction** — Speak answers with real-time transcription
* 🧠 **Adaptive AI Interviewer** — Dynamic questions and follow-ups based on your answers
* 📊 **STAR Scoring** — Situation, Task, Action, Result breakdown
* ✍️ **Sentence-Level Feedback** — Rewrites and targeted improvements
* 💬 **Ask About Feedback** — Interactive Q&A on your performance
* 📈 **Progress Tracking** — Weak areas and score trends over time
* 🏢 **Company-Specific Prep** — Tailored questions for top companies
* 🔁 **Adaptive Practice** — Focuses on your weak areas as you improve
* ☁️ **Cloud Sync** — Sessions and feedback saved automatically

---

## How We Used Each Sponsor

| Sponsor                    | What We Built With It                                                                                                                                                      | Why It's Core                                                          |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **Anthropic Claude Haiku** | Interviewer brain for spoken feedback, follow-up questions, ask-about-feedback Q&A, coaching plans, adaptive guidance, and Claude Artifacts for 3D interaction prototyping | Makes the experience feel like a real interviewer instead of a chatbot |
| **InsForge**               | AI Model Gateway, PostgreSQL database, and pgvector semantic matching                                                                                                      | Powers the backend for sessions, answers, progress, and search         |
| **TinyFish**               | AI browser automation for scraping interview experiences                                                                                                                   | Keeps questions grounded in real, current interview patterns           |

---

## Architecture

```text
Frontend (Next.js)
├── Login / Onboarding
├── Dashboard + History
├── 3D Interview Scene (Three.js)
└── Voice Pipeline
    ├── Speechmatics STT
    └── Web Speech API TTS

API Routes (Next.js)
├── /api/auth/google/*
├── /api/parse-resume
├── /api/generate-questions
├── /api/mock-feedback
├── /api/cloud-*
└── /api/match-question

Backend
├── InsForge AI Model Gateway
│   ├── Gemini 2.5 Flash Lite for analysis, research, and scoring
│   └── Claude Haiku for interviewer-style feedback and follow-ups
└── InsForge PostgreSQL + pgvector
```

---

## Data Flow

1. User registers or logs in with email/password or Google OAuth.
2. User completes onboarding with resume, role, and company details.
3. The app researches real interview patterns and generates personalized questions.
4. The user answers by voice.
5. Speechmatics transcribes the response in real time.
6. Gemini scores STAR structure, sentence quality, and delivery.
7. Claude turns the analysis into natural spoken feedback and follow-ups.
8. Progress, weak areas, and full feedback are saved for history and review.

---

## Tech Stack

* **Frontend:** Next.js 14, TypeScript, Tailwind CSS, Three.js
* **Backend:** Next.js API Routes
* **AI Gateway:** InsForge Model Gateway
* **AI Models:** Gemini 2.5 Flash Lite, Claude Haiku
* **Database:** InsForge PostgreSQL 15 + pgvector
* **Auth:** JWT, bcryptjs, Google OAuth
* **Voice STT:** Speechmatics Realtime API
* **Voice TTS:** Web Speech API
* **PDF Parsing:** Gemini multimodal API
* **DOCX Parsing:** jszip

---

## Setup & Run

### Prerequisites

* Node.js 18+
* InsForge account with PostgreSQL and Model Gateway enabled

### Installation

```bash
git clone https://github.com/metalgenesis123321/CBC-Hackathon.git
cd interview-coach
npm install
```

### Environment Variables

Create `.env.local`:

```env
AI_MODEL=google/gemini-2.5-flash-lite
GEMINI_API_KEY=your_gemini_api_key
INSFORGE_PROJECT_URL=https://your-project.us-east.insforge.app
INSFORGE_API_KEY=your_insforge_api_key
INSFORGE_ANON_KEY=your_anon_key
INSFORGE_DB_URL=postgresql://postgres:password@your-project.us-east.database.insforge.app:5432/insforge?sslmode=require
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET=your_jwt_secret
SPEECHMATICS_API_KEY=your_speechmatics_api_key
TINYFISH_API_KEY=your_tinyfish_api_key
```

### Run Locally

```bash
npm run dev
```

### Deploy to Vercel

```bash
vercel --prod
```

Add the environment variables above in Vercel and register the OAuth redirect URI:
`https://your-domain.vercel.app/api/auth/google/callback`

---

## API Endpoints

### Authentication

* `POST /api/auth/register` — Register with email/password
* `POST /api/auth/login` — Login with email/password
* `GET /api/auth/google` — Start Google OAuth
* `GET /api/auth/google/callback` — Google OAuth callback
* `GET /api/auth/me` — Get current user
* `POST /api/auth/profile` — Update user profile
* `POST /api/auth/logout` — Clear auth cookie

### AI & Interview

* `POST /api/feedback` — STAR feedback for one answer
* `POST /api/mock-feedback` — Dual-model feedback pipeline
* `POST /api/adaptive` — Generate adaptive sessions or analyze progress
* `POST /api/research` — Scrape and synthesize real interview data
* `POST /api/parse-resume` — Extract resume text from PDF, DOCX, or TXT
* `POST /api/parse-profile` — AI profile extraction from resume text

### Data

* `POST /api/db` — Database operations
* `POST /api/cloud-save-answer` — Save answer with full analysis
* `POST /api/cloud-save-session` — Save session summary
* `POST /api/vector` — Vector similarity search

---

## Ethical Design

We believe AI interview tools carry real responsibility. Here's how we address potential harms:

| Concern                          | How We Address It                                                                                                                                                         |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AI replacing human mentors**   | Every feedback screen is labeled "AI-Generated" and the app explicitly states it supplements, not replaces, human mentorship                                              |
| **Privacy of spoken answers**    | Audio is transcribed in real time via Speechmatics WebSocket — raw audio is never uploaded or stored on our servers. Transcripts are stored only if the user opts to save |
| **Cultural bias in feedback**    | STAR framework scoring evaluates structure and content, not accent, grammar, or cultural communication style. We don't penalize non-native English patterns               |
| **Encouraging scripted answers** | Follow-up questions probe deeper into answers to test authenticity. The system rewards genuine experience over rehearsed responses                                        |
| **Overconfidence in AI scores**  | Scores are presented as practice indicators with context ("Getting There", "Almost Ready"), not as definitive hiring predictions                                          |
| **Data ownership**               | Users can see exactly what data is stored (profile, transcripts, scores) and all data is tied to their account                                                            |

---

## Team

Built for HackASU 2026 Claude Builder Club Hackathon

**Track:** Economic Empowerment & Education

---

## License

MIT

---

**We are not just scoring interviews. We are making AI feedback understandable, memorable, and actionable.**
