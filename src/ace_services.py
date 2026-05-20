"""
Ace Data Cloud Service Wrappers — Real x402 SDK calls.

Uses 3 distinct Ace Data Cloud services:
1. Search — ace.search.google() via x402
2. Chat — ace.openai.chat.completions.create() via x402
3. Embeddings — ace.openai.embeddings.create() via x402 (3rd distinct service)

All services use x402 payments (Solana USDC) — no API token required.
"""

import logging
from typing import Optional
from dataclasses import dataclass, field

from acedatacloud import AceDataCloud

logger = logging.getLogger(__name__)


@dataclass
class ServiceUsage:
    """Track service usage for bounty compliance."""
    service: str
    calls: int = 0
    total_cost: float = 0.0
    last_result: Optional[str] = None

    def record(self, cost: float, result_preview: str = ""):
        self.calls += 1
        self.total_cost += cost
        self.last_result = result_preview[:200] if result_preview else ""


@dataclass
class AceServiceRegistry:
    """Registry of Ace Data Cloud services used by the agent."""
    client: AceDataCloud
    search: ServiceUsage = field(default_factory=lambda: ServiceUsage("search"))
    chat: ServiceUsage = field(default_factory=lambda: ServiceUsage("chat"))
    embeddings: ServiceUsage = field(default_factory=lambda: ServiceUsage("embeddings"))

    def summary(self) -> dict:
        """Bounty compliance: prove 3+ distinct services were used."""
        return {
            s.service: {
                "calls": s.calls,
                "estimated_cost_usdc": round(s.total_cost, 6),
            }
            for s in [self.search, self.chat, self.embeddings]
            if s.calls > 0
        }


class AceDataServices:
    """High-level wrappers for Ace Data Cloud services via x402."""

    def __init__(self, client: AceDataCloud):
        self.client = client
        self.registry = AceServiceRegistry(client=client)

    # ─── 1. Search ───────────────────────────────────────────
    def search_market_data(self, query: str) -> str:
        """Search for real-time data via Ace Data Cloud Google Search.

        Uses x402 payment handler (no API token needed).
        Counts as 1 of the 3 required distinct services.
        """
        logger.info(f"🔍 Search: {query}")
        try:
            result = self.client.search.google(query=query)
            # result is a dict with 'answer_box', 'organic_results', etc.
            organic = result.get("organic_results", [])
            snippets = []
            for r in organic[:5]:
                title = r.get("title", "")
                snippet = r.get("snippet", "")
                snippets.append(f"- {title}\n  {snippet}")
            content = "\n".join(snippets) if snippets else str(result)[:2000]

            self.registry.search.record(
                cost=0.001,
                result_preview=content,
            )
            return content
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"[Search error: {e}]"

    # ─── 2. Chat / AI Analysis ───────────────────────────────
    def analyze(self, system_prompt: str, user_content: str,
                model: str = "gpt-4o-mini") -> str:
        """AI-powered analysis via OpenAI chat (Ace Data Cloud).

        Uses ace.openai.chat.completions.create() via x402.
        Counts as the 2nd required distinct service.
        """
        logger.info(f"🤖 AI Analysis [model={model}]")
        try:
            resp = self.client.openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                max_tokens=2000,
            )
            content = resp["choices"][0]["message"]["content"]
            self.registry.chat.record(
                cost=0.002,
                result_preview=content,
            )
            return content
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return f"[Analysis error: {e}]"

    def summarize(self, text: str, max_tokens: int = 500) -> str:
        """Summarize long text into a concise brief."""
        return self.analyze(
            system_prompt=(
                "You are a crypto intelligence analyst. Summarize the following "
                "data into a concise, actionable brief. Focus on key metrics, "
                "trends, and anomalies."
            ),
            user_content=text,
        )

    # ─── 3. Embeddings (3rd distinct service) ────────────────
    def compute_embeddings(self, text: str,
                           model: str = "text-embedding-3-small") -> list[float]:
        """Compute text embeddings via OpenAI embeddings API.

        Uses ace.openai.embeddings.create() via x402.
        Counts as the 3rd required distinct service.
        """
        logger.info(f"🧬 Embeddings [{model}]: {text[:60]}...")
        try:
            resp = self.client.openai.embeddings.create(
                model=model,
                input=text,
            )
            embedding = resp["data"][0]["embedding"]
            self.registry.embeddings.record(
                cost=0.0001,
                result_preview=f"dim={len(embedding)}",
            )
            return embedding
        except Exception as e:
            logger.error(f"Embeddings failed: {e}")
            return []

    @property
    def usage_report(self) -> dict:
        """Full usage report for bounty submission."""
        return self.registry.summary()
