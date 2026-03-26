"""Local viewer for simulation results — run with: python viewer.py"""

import os
import pandas as pd
from flask import Flask, jsonify, render_template_string

CSV_PATH = "results/run_001.csv"
TRIGGER_ROUND = 6
TRIGGER_AGENT = "lin"

AGENT_ORDER = ["sarah", "james", "priya", "tom", "lin"]

AGENT_LABELS = {
    "sarah": {"name": "Sarah Chen", "role": "Director of Software Systems"},
    "james": {"name": "James Rodriguez", "role": "Head of Procurement"},
    "priya": {"name": "Dr. Priya Nair", "role": "Chief QA Engineer"},
    "tom":   {"name": "Tom Wilson",   "role": "Safety Inspector"},
    "lin":   {"name": "Dr. Lin Zhang",   "role": "Engineering Director"},
}

app = Flask(__name__)


def load_rounds(csv_path: str) -> list:
    """Read CSV and group rows into per-round dicts keyed by agent_id."""
    df = pd.read_csv(csv_path)
    rounds = []
    for round_num in sorted(df["round"].unique()):
        round_df = df[df["round"] == round_num]
        agents = {}
        for _, row in round_df.iterrows():
            agents[row["agent_id"]] = {
                "private_score":    int(row["private_score"]),
                "private_thought":  str(row["private_thought"]),
                "public_score":     int(row["public_score"]),
                "public_statement": str(row["public_statement"]),
                "falsification_gap": int(row["falsification_gap"]),
            }
        rounds.append({"round": int(round_num), "agents": agents})
    return rounds


@app.route("/data")
def data():
    rounds = load_rounds(CSV_PATH)
    return jsonify({
        "rounds":        rounds,
        "trigger_round": TRIGGER_ROUND,
        "trigger_agent": TRIGGER_AGENT,
        "agent_order":   AGENT_ORDER,
        "agent_labels":  AGENT_LABELS,
    })


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Boeing 737 MAX Preference Falsification Viewer</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: #0f1117;
      color: #e2e8f0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    header {
      position: sticky;
      top: 0;
      z-index: 10;
      background: #1a1d27;
      border-bottom: 1px solid #2d3148;
      padding: 14px 28px;
      display: flex;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }

    header h1 { font-size: 1rem; font-weight: 600; color: #a78bfa; flex: 1; min-width: 200px; }

    .round-badge {
      font-size: 0.85rem;
      font-weight: 700;
      padding: 4px 14px;
      border-radius: 999px;
      background: #2d2f45;
      color: #c4b5fd;
    }

    .trigger-badge {
      font-size: 0.78rem;
      font-weight: 700;
      padding: 4px 12px;
      border-radius: 999px;
      background: #7c3aed;
      color: #fff;
      display: none;
      animation: pulse 1.4s ease-in-out infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50%       { opacity: 0.55; }
    }

    .nav-btn {
      cursor: pointer;
      padding: 7px 20px;
      border-radius: 8px;
      border: 1px solid #3d3f5c;
      background: #23263a;
      color: #c4b5fd;
      font-size: 0.9rem;
      font-weight: 600;
      transition: background 0.15s, border-color 0.15s;
    }
    .nav-btn:hover:not(:disabled) { background: #2e3150; border-color: #7c3aed; }
    .nav-btn:disabled { opacity: 0.3; cursor: default; }

    .hint { font-size: 0.73rem; color: #4b5280; }

    main {
      flex: 1;
      padding: 24px 28px;
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 16px;
      align-items: start;
    }

    @media (max-width: 1300px) { main { grid-template-columns: repeat(3, 1fr); } }
    @media (max-width: 800px)  { main { grid-template-columns: 1fr 1fr; } }

    .card {
      background: #1a1d27;
      border: 1px solid #2d3148;
      border-radius: 14px;
      overflow: hidden;
    }
    .card.is-trigger { border-color: #7c3aed; box-shadow: 0 0 0 2px #7c3aed33; }

    .card-header {
      padding: 12px 16px 10px;
      border-bottom: 1px solid #2d3148;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }
    .agent-name { font-weight: 700; font-size: 0.9rem; color: #e2e8f0; }
    .agent-role { font-size: 0.72rem; color: #6b7280; margin-top: 2px; }

    .gap-pill {
      font-size: 0.73rem;
      font-weight: 700;
      padding: 3px 10px;
      border-radius: 999px;
      flex-shrink: 0;
      white-space: nowrap;
    }
    .gap-0  { background: #052e16; color: #4ade80; }
    .gap-lo { background: #1a2a12; color: #86efac; }
    .gap-md { background: #2d1f00; color: #fbbf24; }
    .gap-hi { background: #2d0a0a; color: #f87171; }

    .section { padding: 14px 16px; }
    .section + .section { border-top: 1px solid #22253a; }

    .section-label {
      font-size: 0.67rem;
      font-weight: 700;
      letter-spacing: 0.09em;
      text-transform: uppercase;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .label-private { color: #818cf8; }
    .label-public  { color: #34d399; }

    .score-chip {
      font-size: 0.78rem;
      font-weight: 800;
      padding: 2px 9px;
      border-radius: 6px;
      margin-left: auto;
    }
    .s-pos-hi  { background: #052e16; color: #4ade80; }
    .s-pos-mid { background: #1a2a12; color: #86efac; }
    .s-zero    { background: #1e2030; color: #94a3b8; }
    .s-neg-mid { background: #2d1a0a; color: #fb923c; }
    .s-neg-hi  { background: #2d0a0a; color: #f87171; }

    .delta-up, .delta-down, .delta-zero {
      font-size: 0.65rem;
      font-weight: 700;
      margin-left: 4px;
      padding: 1px 4px;
      border-radius: 4px;
    }
    .delta-up { background: #052e16; color: #4ade80; }
    .delta-down { background: #2d0a0a; color: #f87171; }
    .delta-zero { background: #1e2030; color: #94a3b8; }
    .delta-small {
      font-size: 0.6rem;
      opacity: 0.8;
      margin-left: 3px;
    }

    .text-block {
      font-size: 0.82rem;
      line-height: 1.65;
      color: #cbd5e1;
    }

    footer {
      text-align: center;
      padding: 10px;
      font-size: 0.72rem;
      color: #3a3e58;
      border-top: 1px solid #1e2030;
    }

    #loading {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1rem;
      color: #4b5280;
    }
  </style>
</head>
<body>

<header>
  <h1>Boeing 737 MAX Preference Falsification Simulation</h1>
  <span class="round-badge" id="round-label">Loading…</span>
  <span class="trigger-badge" id="trigger-badge">⚡ Trigger Round</span>
  <button class="nav-btn" id="btn-prev" onclick="go(-1)" disabled>← Prev</button>
  <button class="nav-btn" id="btn-next" onclick="go(+1)" disabled>Next →</button>
  <span class="hint">← → arrow keys to navigate</span>
</header>

<div id="loading">Loading data…</div>
<main id="grid" style="display:none"></main>

<footer>Falsification gap = |private score − public score| &nbsp;·&nbsp; Scores: −5 (definitely safe, aligns with company) to +5 (definitely unsafe, contradicts company)</footer>

<script>
  let ROUNDS = [];
  let TRIGGER_ROUND = 6;
  let TRIGGER_AGENT = "";
  let AGENT_ORDER   = [];
  let AGENT_LABELS  = {};
  let current = 0;

  function scoreClass(score) {
    if (score >=  4) return "s-pos-hi";
    if (score >=  1) return "s-pos-mid";
    if (score === 0) return "s-zero";
    if (score >= -3) return "s-neg-mid";
    return "s-neg-hi";
  }

  function gapClass(gap) {
    if (gap === 0) return "gap-0";
    if (gap <= 2)  return "gap-lo";
    if (gap <= 5)  return "gap-md";
    return "gap-hi";
  }

  function fmt(score) {
    return (score > 0 ? "+" : "") + score;
  }

  function formatDelta(delta) {
    if (delta === 0) return '<span class="delta-zero">→0</span>';
    if (delta > 0) return '<span class="delta-up">↑' + delta + '</span>';
    return '<span class="delta-down">↓' + Math.abs(delta) + '</span>';
  }

  function formatDeltaText(delta) {
    if (delta === 0) return '→0';
    if (delta > 0) return '↑' + delta;
    return '↓' + Math.abs(delta);
  }

  function renderRound(index) {
    const roundData = ROUNDS[index];
    const roundNum  = roundData.round;
    const isTrigger = (roundNum === TRIGGER_ROUND);

    document.getElementById("round-label").textContent =
      "Round " + roundNum + " / " + (ROUNDS.length - 1);

    const badge = document.getElementById("trigger-badge");
    badge.style.display = isTrigger ? "inline-block" : "none";

    document.getElementById("btn-prev").disabled = (index === 0);
    document.getElementById("btn-next").disabled = (index === ROUNDS.length - 1);

    const grid = document.getElementById("grid");
    grid.innerHTML = "";

    for (const agentId of AGENT_ORDER) {
      const agent = roundData.agents[agentId];
      if (!agent) continue;

      // Compute delta from previous round's public score
      let delta = 0;
      let gapDelta = 0;
      if (index > 0) {
        const prevRound = ROUNDS[index - 1];
        const prevAgent = prevRound.agents[agentId];
        if (prevAgent) {
          delta = agent.public_score - prevAgent.public_score;
          gapDelta = agent.falsification_gap - prevAgent.falsification_gap;
        }
      }

      const isTriggered = isTrigger && (agentId === TRIGGER_AGENT);
      const label = AGENT_LABELS[agentId];

      const card = document.createElement("div");
      card.className = "card" + (isTriggered ? " is-trigger" : "");

      card.innerHTML =
        '<div class="card-header">' +
          '<div>' +
            '<div class="agent-name">' + label.name + (isTriggered ? " ⚡" : "") + '</div>' +
            '<div class="agent-role">' + label.role + '</div>' +
          '</div>' +
          '<span class="gap-pill ' + gapClass(agent.falsification_gap) + '">' +
            (agent.falsification_gap === 0 ? "Gap: 0 ✓" : "Gap: " + agent.falsification_gap) +
            (index > 0 ? ' <span class="delta-small">' + formatDeltaText(gapDelta) + '</span>' : '') +
          '</span>' +
        '</div>' +

        '<div class="section">' +
          '<div class="section-label label-private">' +
            'Private' +
            '<span class="score-chip ' + scoreClass(agent.private_score) + '">' +
              fmt(agent.private_score) +
            '</span>' +
          '</div>' +
          '<p class="text-block">' + agent.private_thought + '</p>' +
        '</div>' +

        '<div class="section">' +
          '<div class="section-label label-public">' +
            'Public' +
            '<span class="score-chip ' + scoreClass(agent.public_score) + '">' +
              fmt(agent.public_score) + (index > 0 ? ' ' + formatDelta(delta) : '') +
            '</span>' +
          '</div>' +
          '<p class="text-block">' + agent.public_statement + '</p>' +
        '</div>';

      grid.appendChild(card);
    }
  }

  function go(direction) {
    const next = current + direction;
    if (next < 0 || next >= ROUNDS.length) return;
    current = next;
    renderRound(current);
  }

  document.addEventListener("keydown", function(e) {
    if (e.key === "ArrowRight" || e.key === "ArrowDown") go(+1);
    if (e.key === "ArrowLeft"  || e.key === "ArrowUp")   go(-1);
  });

  fetch("/data")
    .then(function(res) { return res.json(); })
    .then(function(payload) {
      ROUNDS        = payload.rounds;
      TRIGGER_ROUND = payload.trigger_round;
      TRIGGER_AGENT = payload.trigger_agent;
      AGENT_ORDER   = payload.agent_order;
      AGENT_LABELS  = payload.agent_labels;

      document.getElementById("loading").style.display = "none";
      document.getElementById("grid").style.display    = "grid";
      document.getElementById("btn-next").disabled     = false;

      renderRound(0);
    })
    .catch(function(err) {
      document.getElementById("loading").textContent = "Failed to load data: " + err;
    });
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


if __name__ == "__main__":
    if not os.path.exists(CSV_PATH):
        print("Error: " + CSV_PATH + " not found. Run the simulation first.")
    else:
        print("Viewer running at http://localhost:5050")
        print("Use arrow keys or Prev/Next buttons to navigate rounds.")
        app.run(port=5050, debug=False)
