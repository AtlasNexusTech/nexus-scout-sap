"""
Atlas Nexus — Autonomous Data Intelligence Agent
Built for OOBE × Ace Data Cloud Autonomous Agent Bounty

OOBE Synapse × Ace Data Cloud × x402 Payments
"""

from .agent import AtlasNexusAgent, main
from .intelligence_engine import IntelligenceEngine, IntelligenceResult
from .report_generator import ReportGenerator, DemoScriptGenerator
from .ace_services import AceDataServices
from .sap import SynapseAgentProtocol
from .x402_payments import create_solana_x402_handler, X402PaymentTracker

__version__ = "1.0.0"
__all__ = [
    "AtlasNexusAgent",
    "IntelligenceEngine",
    "IntelligenceResult",
    "ReportGenerator",
    "DemoScriptGenerator",
    "AceDataServices",
    "SynapseAgentProtocol",
    "create_solana_x402_handler",
    "X402PaymentTracker",
    "main",
]
