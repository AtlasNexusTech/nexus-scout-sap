"""
Autonomous Data Intelligence Agent — OOBE Synapse × Ace Data Cloud

Complete autonomous agent that:
1. Registers on Synapse Agent Protocol
2. Discovers Ace Data Cloud tools
3. Executes intelligence workflows using 3+ services via x402
4. Generates professional reports with full audit trail
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from acedatacloud import AceDataCloud

from .x402_payments import create_solana_x402_handler, X402PaymentTracker
from .ace_services import AceDataServices
from .sap import SynapseAgentProtocol
from .intelligence_engine import IntelligenceEngine
from .report_generator import ReportGenerator, DemoScriptGenerator

# Load .env
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class AtlasNexusAgent:
    """Autonomous Data Intelligence Agent.

    Built for the OOBE × Ace Data Cloud Autonomous Agent Bounty ($2,400 USDC).
    """

    def __init__(
        self,
        agent_name: str = "AtlasNexusDataIntel",
        solana_private_key: Optional[str] = None,
        synapse_endpoint: Optional[str] = None,
        synapse_api_key: Optional[str] = None,
    ):
        self.agent_name = agent_name
        self.version = "1.0.0"

        logger.info(f"🔮 Initializing {agent_name} v{self.version}")

        # x402 payments (Solana)
        self.payment_tracker = X402PaymentTracker()
        self.x402_handler = create_solana_x402_handler(solana_private_key)

        # Ace Data Cloud client (x402-only, no API key)
        self.ace_client = AceDataCloud(payment_handler=self.x402_handler)
        self.ace_services = AceDataServices(self.ace_client)

        # Synapse Agent Protocol
        self.sap = SynapseAgentProtocol(
            endpoint=synapse_endpoint or os.getenv("SYNAPSE_ENDPOINT", "https://staging.oobeprotocol.ai:8080/rpc"),
            api_key=synapse_api_key or os.getenv("SYNAPSE_API_KEY"),
        )

        # Intelligence engine
        self.engine = IntelligenceEngine(self.ace_services, self.payment_tracker)

        # Report generation
        self.reporter = ReportGenerator()
        self.demo_generator = DemoScriptGenerator()

        # Agent state
        self.registered = False
        self.agent_id: Optional[str] = None

    def register(self, wallet_address: str) -> dict:
        """Register agent on Synapse Agent Protocol.

        Bounty requirement #1: agent must be registered on SAP.
        """
        result = self.sap.register_agent(
            name=self.agent_name,
            description="Autonomous crypto data intelligence agent. "
                        "Discovers tools via SAP, executes workflows across "
                        "Ace Data Cloud services (Search, Chat, Images), "
                        "pays via x402. Built on OOBE Protocol.",
            capabilities=[
                "real-time-search",
                "ai-analysis",
                "image-generation",
                "data-intelligence",
            ],
            wallet_address=wallet_address,
        )
        self.registered = True
        self.agent_id = self.sap.agent_id
        logger.info(f"✅ Agent registered: {self.agent_id}")
        return result

    def discover(self) -> list[dict]:
        """Discover available tools through SAP."""
        tools = self.sap.discover_tools("crypto data intelligence")
        logger.info(f"🔍 Discovered {len(tools)} tools via SAP")
        return tools

    def run_intelligence(self, query: str, generate_image: bool = False):
        """Execute a complete intelligence run.

        Full workflow: Search → Analyze → (Visualize) → Report
        All services paid via x402, logged for audit.

        Args:
            query: Natural language query (crypto topic, token, etc.)
            generate_image: Whether to generate an AI visualization

        Returns:
            IntelligenceResult with all outputs
        """
        logger.info(f"🚀 Running intelligence on: '{query}'")
        return self.engine.run(query, generate_image=generate_image)

    def generate_report(self, result) -> str:
        """Generate a Markdown intelligence brief."""
        return self.reporter.generate(result)

    def generate_demo_script(self, sample_query: str) -> str:
        """Generate demo walkthrough for bounty submission."""
        run_log = {
            "services_detail": [
                {"name": "Search", "calls": 1, "cost": 0.001},
                {"name": "Chat", "calls": 1, "cost": 0.002},
                {"name": "Images", "calls": 1, "cost": 0.005},
            ],
            "total_cost": 0.008,
        }
        return self.demo_generator.generate(
            self.agent_name, sample_query, run_log
        )

    def audit(self) -> dict:
        """Full audit trail for bounty compliance."""
        return {
            "agent": {
                "name": self.agent_name,
                "version": self.version,
                "sap_id": self.agent_id,
                "registered": self.registered,
            },
            "services": self.ace_services.usage_report,
            "payments": self.payment_tracker.summary,
        }

    def close(self):
        """Clean up connections."""
        self.sap.close()
        logger.info(f"👋 {self.agent_name} shut down")


# ─── CLI Entry Point ──────────────────────────────────────────
def main():
    """CLI entry point for running the agent."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Atlas Nexus Autonomous Data Intelligence Agent"
    )
    parser.add_argument("query", nargs="?", default="Solana ecosystem",
                       help="Intelligence query (e.g., 'Solana DeFi trends')")
    parser.add_argument("--name", default="AtlasNexusDataIntel",
                       help="Agent name for SAP registration")
    parser.add_argument("--wallet", help="Solana wallet for SAP registration")
    parser.add_argument("--image", action="store_true",
                       help="Generate AI visualization (extra cost)")
    parser.add_argument("--register-only", action="store_true",
                       help="Only register agent, don't run intelligence")
    parser.add_argument("--demo", action="store_true",
                       help="Generate demo script instead of full run")

    args = parser.parse_args()

    agent = AtlasNexusAgent(agent_name=args.name)

    try:
        # Register on SAP
        wallet = args.wallet or os.getenv("SOLANA_WALLET_ADDRESS")
        if wallet:
            reg = agent.register(wallet)
            print(f"\n📋 Agent registered: {json.dumps(reg, indent=2)}")

            if args.register_only:
                return

        # Discover tools
        tools = agent.discover()
        print(f"\n🔧 Available tools: {len(tools)}")

        if args.demo:
            demo = agent.generate_demo_script(args.query)
            path = Path("examples") / "demo-script.md"
            path.parent.mkdir(exist_ok=True)
            path.write_text(demo)
            print(f"\n📄 Demo script saved to {path}")
            return

        # Run intelligence
        print(f"\n🚀 Running intelligence on: '{args.query}'")
        result = agent.run_intelligence(args.query, generate_image=args.image)

        # Generate report
        report_path = agent.generate_report(result)
        print(f"\n📄 Report: {report_path}")

        # Audit
        print(f"\n🔍 Audit: {json.dumps(agent.audit(), indent=2)}")

    finally:
        agent.close()


if __name__ == "__main__":
    main()
