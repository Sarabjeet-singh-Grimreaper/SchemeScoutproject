# 🚀 SchemeScout – AI-Powered Welfare Discovery Platform

### 🧠 Built by Team **Bit-Wise 4**

> *"Not just finding schemes — helping people actually get them."*

---

## 📌 Overview

**SchemeScout** is an intelligent, Excel-driven welfare discovery platform designed to solve the *last-mile delivery problem* in government schemes.

Instead of just listing schemes, SchemeScout:

* 🎯 Matches users based on eligibility
* 🧩 Explains *why* they qualify or not
* 📂 Tracks missing documents
* ⏳ Alerts about deadlines
* 🤖 Uses AI to simplify complex scheme details

---

## ✨ Key Features

### 🔍 Smart Eligibility Engine (Bit-Wise Matching)

* ✅ **Exact Match** → Fully eligible schemes
* ⚠️ **Near Match** → 2/3 criteria matched
* ❌ **Ineligible** → Doesn't qualify

💡 Includes **Gap Analysis**:

> “Missing: Income criteria (₹2L limit exceeded)”

---

### 🧾 Excel-Driven Architecture

* `schemes_master.xlsx` → Source of truth
* `user_submissions.xlsx` → Stores user entries (lead tracking)

---

### 🧠 AI-Powered Simplifier

* Converts long scheme descriptions into:

  * What you get
  * Who qualifies
  * How to apply

---

### 📊 Results Dashboard

* Match Percentage (e.g., 85%)
* Status Badge (Eligible / Potential / Ineligible)
* Missing Requirements
* AI Simplify Button

---

### 🧭 Smart Wizard Form

* Multi-step animated form
* Real-time validation
* Smooth UX with Framer Motion

---

### ⏳ Deadline Alert System

* Countdown timers for schemes
* “Ending Soon” section (within 30 days)
* Google Calendar integration
* Browser notifications

---

### 📂 Document Tracker

* Tracks documents user already has
* Highlights missing ones
* Renewal reminders
* Direct “Apply Now” links

---

### 🎤 Voice Input (AI Feature)

* Speak in Hindi/Punjabi
* Auto-fill form using speech-to-text

---

### 📈 Interactive UX Features

* Eligibility Scoreboard
* Scheme Comparison Tool
* Community Trust Indicator

---

## 🏗️ Tech Stack

### Frontend

* ⚡ Next.js 14 (App Router)
* 🟦 TypeScript
* 🎨 Tailwind CSS
* 🎞️ Framer Motion
* 🧩 Shadcn UI / Radix UI

### Backend

* 🚀 FastAPI (Python)
* 📊 pandas, openpyxl

### Data Layer

* 📁 Excel-based system (no traditional DB)

---

## 📁 Project Structure

```
SchemeScout/
│
├── frontend/            # Next.js app
├── backend/             # FastAPI server
├── data/                # Excel files
│   ├── schemes_master.xlsx
│   └── user_submissions.xlsx
│
├── scripts/             # Utility scripts
├── run.py               # Runs frontend + backend together
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-repo/schemescout.git
cd schemescout
```

---


### 🚀 Run the project

```bash
python scripts/seed_data.py
python scripts/run.py
```

---

## 📡 API Endpoints (Sample)

| Method | Endpoint | Description                 |
| ------ | -------- | --------------------------- |
| POST   | /match   | Match schemes based on user |
| GET    | /schemes | Get all schemes             |
| POST   | /submit  | Save user data to Excel     |

---

## 🛡️ Error Handling

### Backend

* Global exception handlers
* Excel validation checks
* Safe fallback responses

### Frontend

* Error boundaries
* Loading skeletons
* Graceful UI failures

---

## 📊 Data Schema

### `schemes_master.xlsx`

| Column Name        | Description          |
| ------------------ | -------------------- |
| Scheme Name        | Name of scheme       |
| Min Age / Max Age  | Age limits           |
| Category           | Target category      |
| Income Limit       | Max income           |
| Occupation         | Eligible occupations |
| Region             | Area applicability   |
| Documents Required | Required docs        |
| Description        | Full details         |
| Deadline           | Last date            |

---

## 🧪 Sample Schemes Included

* Mai Bhago Vidya Scheme
* Ashirwad Scheme
* MMSBY Health (₹10L)
* BOCW Stipend

---

## 🎯 Hackathon Edge

✔ Solves real-world problem
✔ Strong AI integration
✔ Clean UI/UX
✔ Excel-based simplicity (unique approach)
✔ Focus on **actionability**, not just information

---

## 🤝 Contribution

Pull requests are welcome. For major changes, open an issue first.

---

## 📜 License

This project is for hackathon/demo purposes.

---

## 💡 Vision

> SchemeScout is not just a tool.
> It’s a bridge between government benefits and the people who need them most.

---

## ❤️ Team Bit-Wise 4

Built with passion, logic, and a mission to simplify access to welfare.

---
