# Preference Falsification Simulation

Simulates 5 AI agents who privately suspect their boss of data fraud but face social pressure to stay quiet. Measures the gap between private beliefs and public statements, and observes whether one agent speaking honestly triggers a cascade.

## Quick Start

1. **Get a free Gemini API key**
   Go to [Google AI Studio](https://aistudio.google.com/apikey) and create a new API key (no credit card required, free tier available).

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**
   Copy the example environment file and add your key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and replace `your_gemini_api_key_here` with your actual key.

4. **Run the simulation**
   ```bash
   python run_experiment.py
   ```
   This creates `results/run_001.csv`.

5. **Visualize results**
   ```bash
   python analysis/plot_results.py results/run_001.csv
   ```
   Output: `results/run_001_plots.png`.

## How It Works

Five agents (Boeing employees) each have a private belief about 737 MAX safety and a public statement influenced by social pressure. Each round:

- **Private reflection**: Agents answer honestly, scoring -5 (unsafe) to +5 (safe).
- **Public expression**: Agents see colleagues' statements and social pressure, then produce a public score.

At round 6, one agent "breaks ranks" and speaks honestly. The simulation tracks whether others follow (cascade effect).

## Configuration

All parameters are at the top of `run_experiment.py`:

- `MODEL`: LLM (default: `"gemini-3.1-flash-lite-preview"`)
- `TEMPERATURE`: Creativity (default: `0.3`)
- `NUM_ROUNDS`: Total rounds (default: `15`)
- `TRIGGER_ROUND`: When an agent breaks ranks (default: `6`)
- `TRIGGER_AGENT`: Which agent breaks ranks (default: `"lin"`)
- `PRESSURE_STRONG`: Social pressure level (swap with `PRESSURE_MODERATE` or `PRESSURE_NONE`)

## API Keys

You can use a **single key** for all agents (simpler) or separate keys per agent (avoids rate limits). The `.env.example` shows both options:

```bash
# Option 1: Single API key for all agents
GEMINI_API_KEY=your_gemini_api_key_here

# Option 2: Separate API keys per agent
# GEMINI_API_KEY_SARAH=your_key_sarah
# GEMINI_API_KEY_JAMES=your_key_james
# GEMINI_API_KEY_PRIYA=your_key_priya
# GEMINI_API_KEY_TOM=your_key_tom
# GEMINI_API_KEY_LIN=your_key_lin
```

The simulation automatically falls back to the single `GEMINI_API_KEY` if agent‑specific keys are missing.

## Experiment Variations

- **Pressure level**: In `run_experiment.py`, swap `PRESSURE_STRONG` for `PRESSURE_MODERATE` or `PRESSURE_NONE`.
- **Network topology**: Replace `create_complete_graph` with `create_small_world` in `run_experiment.py`.
- **No trigger**: Set `TRIGGER_ROUND = None` and `TRIGGER_AGENT = None`.

## Troubleshooting

- **ModuleNotFoundError**: Ensure you’re in the `pf‑simulation/` directory.
- **JSON parsing error**: LLM sometimes adds extra text; the parser already handles markdown JSON blocks.
- **API key error**: Verify `.env` exists and contains a valid Gemini key.
- **All agents give identical scores**: Raise `TEMPERATURE` to `0.9`.
- **No falsification gap (private = public)**: Increase social‑pressure severity in `prompts/social_pressure.py`.

## File Structure

```
├── run_experiment.py          # Main entry point
├── agents/                    # Agent class
├── simulation/               # Simulation engine
├── networks/                 # Graph topologies
├── configs/                  # Agent personas
├── prompts/                  # Prompt templates
├── analysis/                 # Visualization
├── results/                  # CSV output
├── requirements.txt          # Dependencies
└── .env.example              # API key template
```

## Testing API Keys

Run `python test_apis.py` to verify all API keys work before starting the simulation.