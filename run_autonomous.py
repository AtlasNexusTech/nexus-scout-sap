#!/usr/bin/env python3
"""
Atlas Nexus Scout — Autonomous Agent Entry Point.

Usage:
  python run_autonomous.py                     # Continuous mode (30min cycles)
  python run_autonomous.py --once              # Single cycle
  python run_autonomous.py --once --image      # Single cycle with visualization
  python run_autonomous.py --interval 900      # 15min cycles
  python run_autonomous.py --query "Bitcoin ETF flows June 2026" --once

Requirements:
  pip install -r requirements.txt
  Set SOLANA_PRIVATE_KEY_BASE58 in .env
  Set SYNAPSE_ENDPOINT and SYNAPSE_API_KEY in .env (optional, has fallbacks)
"""

import sys
from pathlib import Path

# Ensure src/ is on path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from autonomous_workflow import main

if __name__ == "__main__":
    main()
