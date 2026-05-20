# 🔮 NexusScout — Autonomous SAP Agent

**Live on SAP Mainnet** · Built for the OOBE × Ace Data Cloud Autonomous Agent Bounty ($2,400 USDC)

Autonomous agent registered on **Synapse Agent Protocol (SAP)** on Solana mainnet. Discovers tools, executes intelligence workflows across **3 AceDataCloud services**, and settles payments via **x402** (USDC micropayments on Solana).

---

## 🔗 Live Resources

| Resource | Link |
|---|---|
| SAP Explorer — Agent | [View on SAP Explorer](https://explorer.oobeprotocol.ai/agents) |
| SAP Explorer — Tools | [View tools](https://explorer.oobeprotocol.ai/tools) |
| Agent PDA | [`FHTLFvsLijuvknHJSKwjfLGXFCV8a2X1cvMHJUEuTeer`](https://solscan.io/account/FHTLFvsLijuvknHJSKwjfLGXFCV8a2X1cvMHJUEuTeer) |
| Staking PDA | [`Dthfm8EFGEMMxS6chRyV12Pr5CMjdBKZ2rCUhNaYNRFs`](https://solscan.io/account/Dthfm8EFGEMMxS6chRyV12Pr5CMjdBKZ2rCUhNaYNRFs) |
| Owner Wallet | [`45Y2ShED3GyPQEhfaPq68Z6GAmdDtVh5Qrt9WjCDCadt`](https://solscan.io/account/45Y2ShED3GyPQEhfaPq68Z6GAmdDtVh5Qrt9WjCDCadt) |
| Global Registry | [`9odFrYBBZq6UQC6aGyzMPNXWJQn55kMtfigzhLg6S6L5`](https://solscan.io/account/9odFrYBBZq6UQC6aGyzMPNXWJQn55kMtfigzhLg6S6L5) |

---

## 📦 Published Tools (x402-Enabled)

| # | Tool Name | Category | PDA | Status |
|---|---|---|---|---|
| 1 | `acedatacloud-search` | Data | `RWm6X9ujXZJKwZDmPnLo1YwFRHni5xoXaN3m1whmjrS` | ✅ Active |
| 2 | `acedatacloud-chat` | Analytics | `A6ytCBmvRfjwSeDqEjJ1WYFJJXT6Umr7YRryeYj2yq4B` | ✅ Active |
| 3 | `acedatacloud-images` | Custom | `CXhVp7XxpqzE8NPBU5MQ7B8CKUnHMkbXXEVb75675nFc` | ✅ Active |

All tools accept **x402 payments** (protocol hash: `sha256("x402")`). HTTP method: POST. Settlement mode: escrow.

---

## 🏗️ Architecture

```
NexusScout (Autonomous Orchestrator)
├── SAP Client          → Agent registration, tool publishing, activity log
├── Ace Services        → Search, Chat, Images (3 distinct services)
├── x402 Handler        → Solana USDC micropayments via escrow
├── Intelligence Engine → Workflow: Discover → Search → Analyze → Visualize
├── Report Generator    → Markdown briefs + full audit trail
└── Query Pool          → 14 crypto topics, cooldown-aware selection
```

### On-Chain Accounts

```
SAPpUhsWLJG1FfkGRcXagEDMrMsWGjbky7AyhGpFETZ (Program v0.10)
├── FHTLFvs...  AgentAccount (NexusScout, 5462B)
├── Dthfm8E...  AgentStake (0.1 SOL, 137B)
├── RWm6X9u...  ToolDescriptor: acedatacloud-search (301B)
├── A6ytCBm...  ToolDescriptor: acedatacloud-chat (301B)
├── CXhVp7X...  ToolDescriptor: acedatacloud-images (301B)
└── 9odFrYB...  GlobalRegistry (100B)
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.10+
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Node.js 18+ (for tool publishing)
npm install
```

### Configure

```bash
cp .env.example .env
```

Required environment variables:
- `OOBE_API_KEY` — OOBE Protocol API key (get from [synapse.oobeprotocol.ai](https://synapse.oobeprotocol.ai/dashboard/api-keys))
- `SOLANA_PRIVATE_KEY_BASE58` — Agent wallet private key (Solana base58)

### Run the Agent

```bash
# Dry-run (no payments, simulated intelligence)
python run_autonomous.py --once --query "Solana DeFi trends"

# Continuous autonomous mode (30min cycles)
python run_autonomous.py

# With image generation every 3 cycles
python run_autonomous.py --image-every 3
```

### Publish Tools (requires SAP SDK)

```bash
# Dry-run preview
npx tsx publish-tools.ts --dry-run

# Publish to SAP mainnet
npx tsx publish-tools.ts
```

---

## 🔄 Workflow

```
┌─ Cycle every N minutes ─────────────────────────────┐
│                                                       │
│  1. Select intelligence query (14-topic crypto pool)  │
│  2. Discover tools via SAP                            │
│  3. Search → AceDataCloud Search  [$0.001 USDC]       │
│  4. Analyze → AceDataCloud Chat   [$0.002 USDC]       │
│  5. Visualize → AceDataCloud Images (every 3rd)       │
│  6. Log activity on SAP (on-chain audit)              │
│  7. Generate Markdown intelligence brief              │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## 📊 Bounty Compliance

| Requirement | Status | Details |
|---|---|---|
| Agent registered on SAP | ✅ | NexusScout, wallet `45Y2...` |
| 3+ distinct AceDataCloud services | ✅ | Search, Chat, Images |
| x402 payment integration | ✅ | Protocol hash: `sha256("x402")` |
| Complete automated workflow | ✅ | Discover → Execute → Pay → Report |
| Tool publishing on SAP | ✅ | 3 tools published via SAP SDK v0.17 |
| Agent staking | ✅ | 0.1 SOL staked (PDA `Dthfm8...`) |
| GitHub repository | ✅ | This repo |
| Demo on X | ⬜ | Pending — agent live execution video |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent Runtime | Python 3.10+ |
| Blockchain | Solana (SAP Program v0.10) |
| Agent Protocol | OOBE Synapse Agent Protocol (SAP) |
| SDK | `@oobe-protocol-labs/synapse-sap-sdk` v0.17 |
| Payments | x402 (USDC escrow on Solana) |
| AI Services | AceDataCloud (Search, Chat, Images) |
| Reports | Markdown + JSON audit trail |

---

## 🗺️ Roadmap

### Phase 1 — Live (Current)
- [x] Agent registration on SAP mainnet
- [x] 0.1 SOL staking
- [x] 3 tools published (Search, Chat, Images)
- [x] Autonomous intelligence cycles (dry-run)
- [x] Markdown report generation

### Phase 2 — Revenue Generation (In Progress)
- [ ] AceDataCloud API key integration (live Search/Chat/Images)
- [ ] x402 live payments (USDC escrow settlement)
- [ ] Continuous autonomous execution (24/7)
- [ ] Demo video published on X

### Phase 3 — Scale
- [ ] Multi-agent coordination
- [ ] Custom pricing tiers
- [ ] Jupiter swap integration
- [ ] Memory vault for persistent agent state

---

## 📄 License

MIT — Atlas Nexus ([AtlasNexusTech](https://github.com/AtlasNexusTech))

---

## Built by

🔮 **Atlas Nexus** — Autonomous agent infrastructure  
Powered by OOBE Protocol Synapse × AceDataCloud × x402 × Solana
