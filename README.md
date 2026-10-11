# ReelsFilter

Auto-categorize Facebook Saved Reels via Telegram.

Send a reel URL to a Telegram bot → AI classifies it → result saved to Google Sheets.

**Cost: $0** — everything runs locally.

```
You (Telegram)  →  n8n (local)  →  Ollama (local)  →  Google Sheets
```

---

## Prerequisites

- A machine that stays on (or runs whenever you want to categorize reels)
- [Docker](https://docs.docker.com/get-docker/) installed
- A Google account
- A Telegram account

---

## Setup

### 1. Install Ollama

Ollama runs the AI model locally on your machine.

**macOS**
```bash
brew install ollama
```
Or download the desktop app from https://ollama.com/download

**Windows**
Download and run the installer from https://ollama.com/download

**Linux**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Pull the classification model (one-time download, ~2 GB):
```bash
ollama pull llama3.2
```

Start Ollama (keep this running):
```bash
ollama serve
```

Verify it works:
```bash
ollama run llama3.2 "Reply with JSON: {\"hello\": true}"
```

> On macOS/Windows, the desktop app keeps Ollama running automatically.

---

### 2. Install n8n via Docker

```bash
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  --add-host=host.docker.internal:host-gateway \
  docker.n8n.io/n8nio/n8n
```

> `--add-host=host.docker.internal:host-gateway` lets n8n reach Ollama running
> on your host machine. This flag is required on Linux; Docker Desktop on
> macOS/Windows handles it automatically.

Open n8n at **http://localhost:5678** and create a local account.

---

### 3. Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts
3. Copy the **bot token** (looks like `123456789:ABCdef...`)
4. Send any message to your new bot so n8n can receive your chat ID

---

### 4. Set up Google Sheets

#### Create the spreadsheet
1. Go to [Google Sheets](https://sheets.google.com) and create a new sheet
2. Rename the first tab to **Reels**
3. Add these headers in row 1: `URL`, `Category`, `Confidence`, `Date`
4. Copy the spreadsheet ID from the URL:
   `docs.google.com/spreadsheets/d/**YOUR_ID_HERE**/edit`

#### Create Google OAuth2 credentials
1. Go to https://console.cloud.google.com and create a new project
2. Go to **APIs & Services → Enable APIs** → enable **Google Sheets API**
3. Go to **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
4. Application type: **Desktop app** → create → download the JSON
5. Note the **Client ID** and **Client Secret** from the downloaded file

---

### 5. Add credentials in n8n

#### Telegram
1. In n8n: **Credentials → New → Telegram**
2. Paste your bot token → Save

#### Google Sheets
1. In n8n: **Credentials → New → Google Sheets OAuth2**
2. Paste your Client ID and Client Secret
3. Click **Connect** and authorize with your Google account → Save

---

### 6. Import the workflow

1. In n8n: click **+** (new workflow) → **Import from file**
2. Select `workflow.json` from this repo
3. Open each node that shows a credential warning and select your saved credentials:
   - **Telegram Trigger** → select your Telegram credential
   - **Send Confirmation** → select your Telegram credential
   - **Save to Google Sheets** → select your Google Sheets credential, then pick your spreadsheet and sheet
4. Click **Activate** (toggle in top right)

---

## Usage

1. Make sure Ollama is running (`ollama serve` or desktop app)
2. Make sure n8n is running (`docker start n8n` or it auto-starts)
3. Send any Facebook Reel URL to your Telegram bot
4. You'll get a reply like:
   ```
   ✅ Saved!
   Category: film
   Confidence: 0.92
   Date: 2026-10-11
   ```
5. Open your Google Sheet — a new row will be there

---

## Customizing Categories

Open the **Classify with Ollama** node in n8n and edit the prompt.
The default categories are:

```
language, game, book, film, study, food, travel, tech, other
```

Also update the list in the **Parse Response** code node so invalid
categories still fall back to `other` correctly.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| n8n can't reach Ollama | Make sure Ollama is running. On Linux, confirm `--add-host=host.docker.internal:host-gateway` is in your Docker command |
| Ollama returns wrong format | Try a larger model: `ollama pull llama3.1:8b` and update the model name in the HTTP node |
| Google Sheets node fails | Re-authorize the credential in n8n → Credentials |
| Bot doesn't respond | Check the n8n executions tab for errors; make sure the workflow is **Active** |

---

## Stopping / Starting

```bash
docker stop n8n    # stop n8n
docker start n8n   # start n8n again (workflow stays active)
```

n8n data (workflows, credentials) is stored in `~/.n8n` on your machine.
