"""
Intelligence Engine — Data Collection & Analysis Pipeline.

Orchestrates: data fetching → AI analysis → embeddings → report synthesis.
Uses 3 distinct Ace Data Cloud services via x402 payments.
"""

import logging
from typing import Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class IntelligenceResult:
    """Complete result of an intelligence run."""

    query: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Raw data
    search_results: str = ""
    ai_analysis: str = ""
    embedding_dim: int = 0
    visualization_url: Optional[str] = None

    # Payment audit
    total_cost_usdc: float = 0.0
    services_used: list[str] = field(default_factory=list)

    # Log
    run_log: list[str] = field(default_factory=list)

    def log(self, message: str):
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        entry = f"[{ts}] {message}"
        self.run_log.append(entry)
        logger.info(entry)

    def summary(self) -> str:
        return (
            f"Intelligence run for '{self.query}'\n"
            f"Services used: {', '.join(self.services_used)}\n"
            f"Total cost: ${self.total_cost_usdc:.6f} USDC\n"
            f"Run log: {len(self.run_log)} steps"
        )


class IntelligenceEngine:
    """Core intelligence pipeline.

    Flow: Search → Analyze → Embeddings → Report
    All 3 Ace Data Cloud services used via x402 payments.
    """

    def __init__(self, ace_services, payment_tracker):
        """
        Args:
            ace_services: AceDataServices instance
            payment_tracker: X402PaymentTracker instance
        """
        self.services = ace_services
        self.payments = payment_tracker

    def run(self, query: str, generate_image: bool = False) -> IntelligenceResult:
        """Execute a complete intelligence run.

        1. Search for data via Ace Data Cloud Search (service #1)
        2. AI analysis via Ace Data Cloud Chat — OpenAI (service #2)
        3. Embeddings via Ace Data Cloud Embeddings (service #3)
        4. Track all payments via x402

        Returns:
            IntelligenceResult with all outputs and audit trail
        """
        result = IntelligenceResult(query=query)

        # ─── Step 1: Data Collection (Search) ───
        result.log(f"Starting intelligence run: '{query}'")
        result.log("Step 1/3: Searching via Ace Data Cloud...")

        result.search_results = self.services.search_market_data(
            f"crypto {query} market data analysis latest"
        )
        result.services_used.append("search")
        self.payments.record("search", 0.001)
        result.total_cost_usdc += 0.001
        result.log(f"  Search complete ({len(result.search_results)} chars)")

        # ─── Step 2: AI Analysis (Chat) ───
        result.log("Step 2/3: AI analysis via Ace Data Cloud Chat (GPT-4o-mini)...")

        analysis_prompt = f"""Analyze the following search results about '{query}' from a crypto intelligence perspective.
Provide:
1. Key findings and trends
2. Market sentiment assessment
3. Actionable insights
4. Risk factors to watch

Search results:
{result.search_results[:3000]}
"""
        result.ai_analysis = self.services.analyze(
            system_prompt=(
                "You are an elite crypto intelligence analyst. Provide concise, "
                "data-driven analysis with specific metrics and actionable insights. "
                "Be direct — no fluff."
            ),
            user_content=analysis_prompt,
        )
        result.services_used.append("chat")
        self.payments.record("chat", 0.002)
        result.total_cost_usdc += 0.002
        result.log(f"  Analysis complete ({len(result.ai_analysis)} chars)")

        # ─── Step 3: Embeddings (3rd distinct service) ───
        result.log("Step 3/3: Computing embeddings via Ace Data Cloud...")
        embedding = self.services.compute_embeddings(
            f"{query}: {result.ai_analysis[:500]}"
        )
        result.services_used.append("embeddings")
        result.embedding_dim = len(embedding)
        self.payments.record("embeddings", 0.0001)
        result.total_cost_usdc += 0.0001
        result.log(f"  Embeddings complete (dim={result.embedding_dim})")

        result.log(
            f"✓ Intelligence run complete — {len(result.services_used)} services, "
            f"${result.total_cost_usdc:.6f} USDC"
        )
        return result
