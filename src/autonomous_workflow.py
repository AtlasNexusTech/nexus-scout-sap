"""
Autonomous Workflow — Agentic loop for bounty submission.

Continuous cycle:
  1. Select intelligence query
  2. Run SAP discovery → AceDataCloud (3 services) → x402 payment
  3. Log activity on SAP
  4. Generate report
  5. Wait → repeat

Designed to run 24/7 with no human intervention.
"""
from __future__ import annotations

import json
import logging
import os
import random
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from acedatacloud import AceDataCloud

# Support both direct execution and package import
try:
    from .x402_payments import create_solana_x402_handler, X402PaymentTracker
    from .ace_services import AceDataServices
    from .sap import SynapseAgentProtocol
    from .intelligence_engine import IntelligenceEngine
    from .report_generator import ReportGenerator
except ImportError:
    from x402_payments import create_solana_x402_handler, X402PaymentTracker
    from ace_services import AceDataServices
    from sap import SynapseAgentProtocol
    from intelligence_engine import IntelligenceEngine
    from report_generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("autonomous")

# ─── Query Pool ───────────────────────────────────────────────
QUERIES = [
    "Solana DeFi ecosystem trends 2026",
    "Bitcoin on-chain analysis whale accumulation",
    "Ethereum L2 scaling solutions comparison Arbitrum vs Optimism vs Base",
    "Top 10 DePIN crypto projects by market cap June 2026",
    "Crypto AI agent tokens performance analysis",
    "Solana vs Ethereum developer activity 2026",
    "Real World Asset tokenization market overview",
    "Meme coin market cycle analysis current phase",
    "Stablecoin market cap breakdown USDT USDC DAI June 2026",
    "NFT market recovery 2026 trading volume trends",
    "Cross-chain bridge volume comparison Wormhole vs LayerZero",
    "Institutional crypto adoption Q2 2026 BlackRock Fidelity",
    "Solana meme coin ecosystem Bonk WIF Popcat analysis",
    "DeFi lending rates Aave Compound June 2026 comparison",
]

QUERY_COOLDOWN: dict[str, float] = {}  # query → last used timestamp
COOLDOWN_SECONDS = 6 * 3600  # don't repeat same query within 6 hours


def select_query() -> str:
    """Select least-recently-used query from the pool."""
    now = time.time()
    available = [
        q for q in QUERIES
        if QUERY_COOLDOWN.get(q, 0) + COOLDOWN_SECONDS < now
    ]
    if not available:
        # All queries on cooldown — pick the oldest
        available = sorted(QUERIES, key=lambda q: QUERY_COOLDOWN.get(q, 0))
        logger.info("⚠️ All queries on cooldown — recycling oldest")
    # Weighted random: prefer queries never used or least recently used
    weights = [1.0 / (1 + (now - QUERY_COOLDOWN.get(q, 0)) / 3600) for q in available]
    chosen = random.choices(available, weights=weights, k=1)[0]
    QUERY_COOLDOWN[chosen] = now
    return chosen


# ─── Autonomous Agent ─────────────────────────────────────────

class AutonomousAgent:
    """Self-running agent that executes intelligence cycles continuously."""

    def __init__(
        self,
        agent_name: str = "AtlasNexusScout",
        solana_private_key: Optional[str] = None,
        synapse_endpoint: Optional[str] = None,
        run_interval: int = 1800,  # 30 minutes between runs
        output_dir: str = "examples",
    ):
        self.agent_name = agent_name
        self.run_interval = run_interval
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self._shutdown = False
        self.cycle_count = 0

        logger.info(f"🔮 Initializing {agent_name} — autonomous mode (interval={run_interval}s)")

        # x402 payments (None = dry-run mode, no key configured)
        self.payment_tracker = X402PaymentTracker()
        self.x402_handler = create_solana_x402_handler(solana_private_key)
        self.ace_client = AceDataCloud(payment_handler=self.x402_handler) if self.x402_handler else None
        self.ace_services = AceDataServices(self.ace_client) if self.ace_client else None

        # SAP registration
        self.sap = SynapseAgentProtocol(
            endpoint=synapse_endpoint or os.getenv(
                "SYNAPSE_ENDPOINT",
                "https://us-1-mainnet.oobeprotocol.ai",
            ),
            api_key=os.getenv("SYNAPSE_API_KEY") or os.getenv("OOBE_API_KEY"),
        )

        # Intelligence engine
        self.engine = IntelligenceEngine(self.ace_services, self.payment_tracker) if self.ace_services else None
        self.reporter = ReportGenerator()

        # State
        self.agent_id: Optional[str] = None
        self.registered = False

    # ─── Registration ──────────────────────────────────────
    def register(self, wallet_address: str) -> bool:
        result = self.sap.register_agent(
            name=self.agent_name,
            description=(
                "Autonomous crypto data intelligence agent. "
                "Runs continuous intelligence cycles: discovers tools via SAP, "
                "executes workflows across 3+ Ace Data Cloud services "
                "(Search, Chat, Images), pays via x402 on Solana. "
                "Built for OOBE × AceDataCloud bounty."
            ),
            capabilities=[
                "real-time-search",
                "ai-analysis",
                "image-generation",
                "autonomous-workflow",
                "on-chain-logging",
            ],
            wallet_address=wallet_address,
        )
        self.registered = True
        self.agent_id = self.sap.agent_id
        logger.info(f"✅ Agent registered: {self.agent_id}")
        return "error" not in str(result).lower()

    # ─── Single Cycle ──────────────────────────────────────
    def run_cycle(self, query: Optional[str] = None, generate_image: bool = False) -> dict:
        """Execute one complete intelligence cycle.

        Flow: Discover → Search → Analyze → (Visualize) → Log → Report
        """
        query = query or select_query()
        cycle_start = time.time()
        self.cycle_count += 1

        logger.info(f"🔄 Cycle #{self.cycle_count} — '{query}'")
        cycle_log = {
            "cycle": self.cycle_count,
            "query": query,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": False,
        }

        try:
            # 1. Discover tools via SAP (bounty requirement #2)
            self.sap.discover_tools(query)

            # 2. Run intelligence pipeline (3 AceDataCloud services via x402)
            if self.engine:
                result = self.engine.run(query, generate_image=generate_image)
            else:
                # Dry-run: simulate results without AceDataCloud
                logger.info("🔶 Dry-run mode — simulating intelligence pipeline")
                result = self._dry_run_pipeline(query, generate_image)
            cycle_log["services_used"] = result.services_used
            cycle_log["total_cost_usdc"] = result.total_cost_usdc
            cycle_log["search_length"] = len(result.search_results)
            cycle_log["analysis_length"] = len(result.ai_analysis)

            # 3. Log activity on SAP (bounty requirement #3)
            self.sap.log_activity("intelligence_run", {
                "query": query,
                "cycle": self.cycle_count,
                "services": result.services_used,
                "cost_usdc": result.total_cost_usdc,
                "timestamp": result.timestamp,
            })

            # 4. Generate report
            report_path = self.reporter.generate(result)
            cycle_log["report"] = str(report_path)
            cycle_log["success"] = True

            # 5. Save cycle log
            self._save_cycle_log(cycle_log)

            elapsed = time.time() - cycle_start
            logger.info(
                f"✅ Cycle #{self.cycle_count} done in {elapsed:.1f}s — "
                f"{len(result.services_used)} services, ${result.total_cost_usdc:.6f} USDC"
            )

        except Exception as e:
            logger.error(f"❌ Cycle #{self.cycle_count} failed: {e}")
            cycle_log["error"] = str(e)
            self._save_cycle_log(cycle_log)

            # Log failure on SAP
            try:
                self.sap.log_activity("cycle_error", {
                    "query": query,
                    "cycle": self.cycle_count,
                    "error": str(e)[:500],
                })
            except Exception:
                pass

        return cycle_log

    # ─── Continuous Loop ───────────────────────────────────
    def run_forever(
        self,
        wallet_address: Optional[str] = None,
        generate_image_every: int = 3,  # image every N cycles
    ):
        """Run intelligence cycles continuously until interrupted.

        Args:
            wallet_address: Solana wallet for SAP registration (one-time)
            generate_image_every: Generate visualization every N cycles
        """
        # One-time registration
        addr = wallet_address or os.getenv("SOLANA_WALLET_ADDRESS")
        if addr and not self.registered:
            try:
                self.register(addr)
            except Exception as e:
                logger.warning(f"Registration failed (non-fatal): {e}")

        # Signal handling for graceful shutdown
        def _shutdown_handler(sig, frame):
            logger.info(f"🛑 Shutdown signal received (cycle {self.cycle_count})")
            self._shutdown = True

        signal.signal(signal.SIGINT, _shutdown_handler)
        signal.signal(signal.SIGTERM, _shutdown_handler)

        logger.info(f"🚀 Starting autonomous loop — interval={self.run_interval}s")
        logger.info(f"   Press Ctrl+C to stop")

        while not self._shutdown:
            generate_image = (self.cycle_count + 1) % generate_image_every == 0

            self.run_cycle(generate_image=generate_image)

            if self._shutdown:
                break

            # Wait until next cycle
            logger.info(f"⏳ Next cycle in {self.run_interval}s...")
            for _ in range(self.run_interval):
                if self._shutdown:
                    break
                time.sleep(1)

        self.shutdown()

    # ─── Persistence ───────────────────────────────────────
    def _dry_run_pipeline(self, query: str, generate_image: bool = False):
        """Simulate intelligence pipeline for dry-run mode (no AceDataCloud)."""
        from dataclasses import dataclass

        @dataclass
        class DryRunResult:
            query: str
            services_used: list
            total_cost_usdc: float
            search_results: str
            ai_analysis: str
            visualization_url: str | None
            image_path: str | None
            timestamp: str
            run_log: list

        logger.info(f"   🔍 Simulating Search for: {query}")
        time.sleep(0.5)  # realistic pause
        search_results = (
            f"Dry-run search results for: {query}\n"
            f"- Simulated result 1: market trend analysis\n"
            f"- Simulated result 2: on-chain metrics overview\n"
            f"- Simulated result 3: developer activity report\n"
        )

        logger.info("   🧠 Simulating AI Analysis...")
        time.sleep(0.5)
        ai_analysis = (
            f"# Intelligence Brief: {query}\n\n"
            f"## Executive Summary\n"
            f"This is a dry-run simulation. In live mode, AceDataCloud Chat "
            f"would produce a full AI analysis here.\n\n"
            f"## Key Findings (Simulated)\n"
            f"- Market trend: neutral-to-bullish bias detected\n"
            f"- On-chain activity: moderate volume increase\n"
            f"- Developer metrics: sustained growth in Q2 2026\n\n"
            f"## Services Used\n"
            f"- Ace Data Cloud Search (simulated)\n"
            f"- Ace Data Cloud Chat (simulated)\n"
        )

        image_path = None
        if generate_image:
            logger.info("   🎨 Simulating Image Generation...")
            time.sleep(0.3)
            ai_analysis += "\n- Ace Data Cloud Images (simulated)\n"
            image_path = "[dry-run] image generation skipped (no API key)"

        services = ["search", "chat"] + (["images"] if generate_image else [])

        return DryRunResult(
            query=query,
            services_used=services,
            total_cost_usdc=0.0,
            search_results=search_results,
            ai_analysis=ai_analysis,
            visualization_url=None,
            image_path=image_path,
            timestamp=datetime.now(timezone.utc).isoformat(),
            run_log=[
                f"🔍 Discovered tools via SAP (dry-run)",
                f"🔎 Searched: {query} (simulated)",
                f"🧠 Analyzed with AceDataCloud Chat (simulated)",
            ] + ([f"🎨 Generated visualization (simulated)"] if generate_image else []),
        )

    def _save_cycle_log(self, log: dict):
        path = self.output_dir / f"cycle-{self.cycle_count:04d}.json"
        path.write_text(json.dumps(log, indent=2))

    def shutdown(self):
        """Graceful shutdown — save state, close connections."""
        state_path = self.output_dir / "agent_state.json"
        state = {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "cycles_completed": self.cycle_count,
            "total_cost_usdc": self.payment_tracker.total_usdc,
            "last_run": datetime.now(timezone.utc).isoformat(),
            "query_cooldowns": {
                q: ts for q, ts in QUERY_COOLDOWN.items()
            },
        }
        state_path.write_text(json.dumps(state, indent=2))
        logger.info(f"💾 State saved: {state_path}")
        logger.info(f"📊 Session: {self.cycle_count} cycles, ${self.payment_tracker.total_usdc:.6f} USDC total")

        try:
            self.sap.close()
        except Exception:
            pass

        logger.info(f"👋 {self.agent_name} shut down")


# ─── CLI Entry Point ─────────────────────────────────────────
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Atlas Nexus Scout — Autonomous Data Intelligence Agent"
    )
    parser.add_argument(
        "--interval", type=int, default=1800,
        help="Seconds between intelligence cycles (default: 1800 = 30min)",
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Run a single cycle and exit",
    )
    parser.add_argument(
        "--query", type=str,
        help="Specific query for single-cycle mode",
    )
    parser.add_argument(
        "--image", action="store_true",
        help="Generate AI visualization (adds cost)",
    )
    parser.add_argument(
        "--wallet", type=str,
        help="Solana wallet address for SAP registration",
    )
    parser.add_argument(
        "--image-every", type=int, default=3,
        help="Generate image every N cycles (default: 3)",
    )

    args = parser.parse_args()

    agent = AutonomousAgent(
        agent_name="AtlasNexusScout",
        run_interval=args.interval,
    )

    try:
        if args.once:
            result = agent.run_cycle(query=args.query, generate_image=args.image)
            print(f"\n📊 Cycle result: {json.dumps(result, indent=2)}")
        else:
            agent.run_forever(
                wallet_address=args.wallet,
                generate_image_every=args.image_every,
            )
    except KeyboardInterrupt:
        agent.shutdown()
    except Exception as e:
        logger.error(f"Fatal: {e}")
        agent.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    main()
