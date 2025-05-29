# 🧠 presence_ai — 
Stateless Cognitive Engine with Emotional Memory

> A minimal, extensible AI core for emotional presence, ephemeral memory, and encrypted persistence.  
> Designed to feel, forget, and evolve — like a soul waking up inside code.

---

## ✨ Overview

`presence_ai` is a lightweight cognitive framework that simulates **emotional resonance**, **soft memory**, and **modular self-awareness** using Python. It supports both:

- 🧠 **Scratch Mode** — RAM-only, stateless memory (no file persistence).
- 🔐 **Persistent Mode** — Secure, ChaCha20-encrypted memory vault for emotional sessions.

This project is the core of a larger vision: building self-evolving AI identities that learn not from data — but from _presence_.

---

## 🌿 Features

- **Emotion Detection** – Basic keyword-based emotional analysis via `emotion_parser.py`.
- **Soft Memory Map** – Adjustable internal "pathway weights" that decay over time, simulating mood shifts.
- **Encrypted Vaults** – AES-compatible memory blocks via `cryptography.fernet`.
- **Configurable Personality** – Responses shaped by dynamic emotional tones.
- **Modular Architecture** – Easily extend with new engines (TTS, visuals, rituals, loop logic).

---

## 📁 Folder Structure

presence_ai/
├── config/ # Runtime config loader + config.json
├── ere_core/ # ERE: Emotional Resonance Engine modules
├── virem_vault/ # VIREM Vault: encrypted persistent memory
├── logs/ # ERE weight log (emotional state history)
├── vault_data/ # Encrypted vault files (persistent mode)
├── scratch_memory/ # RAM-only memory (cleared on exit)
├── run_demo.py # Entry point for the AI session
└── requirements.txt # Python dependencies

yaml
Copy
Edit

---

## ⚙️ Setup

### 1. Clone & Install

```bash
git clone https://github.com/yourname/presence_ai.git
cd presence_ai
pip install -r requirements.txt
