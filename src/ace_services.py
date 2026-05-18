"""
Ace Data Cloud Service Wrappers.

Provides typed, logged access to 3+ distinct Ace Data Cloud services:
1. Search — real-time web search for crypto data
2. Chat — AI analysis and intelligence generation
3. Images — AI-generated visualizations (charts, infographics)

All services use x402 payments (no API key required).
"""

import logging
import time
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
    images: ServiceUsage = field(default_factory=lambda: ServiceUsage("images"))

    def summary(self) -> dict:
        """Bounty compliance: prove 3+ distinct services were used."""
        return {
            s.service: {
                "calls": s.calls,
                "estimated_cost_usdc": round(s.total_cost, 6),
            }
            for s in [self.search, self.chat, self.images]
            if s.calls > 0
        }


class AceDataServices:
    """High-level wrappers for Ace Data Cloud services."""

    def __init__(self, client: AceDataCloud):
        self.client = client
        self.registry = AceServiceRegistry(client=client)

    # ─── 1. Search ───────────────────────────────────────────
    def search_market_data(self, query: str) -> str:
        """Search for real-time crypto market data.

        Uses Ace Data Cloud's Search API for up-to-date information.
        Counts as 1 of the 3 required distinct services.
        """
        logger.info(f"🔍 Search: {query}")
        try:
            result = self.client.search.create(
                query=query,
                search_type="web",
            )
            content = str(result)
            self.registry.search.record(
                cost=0.001,  # estimated
                result_preview=content,
            )
            return content
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"[Search error: {e}]"

    # ─── 2. Chat / AI Analysis ───────────────────────────────
    def analyze(self, system_prompt: str, user_content: str,
                model: str = "gpt-4o-mini") -> str:
        """AI-powered analysis via chat completions.

        Uses Ace Data Cloud's Chat API. The 2nd required distinct service.
        """
        logger.info(f"🤖 AI Analysis [model={model}]")
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                max_tokens=2000,
            )
            content = response.choices[0].message.content
            self.registry.chat.record(
                cost=0.002,  # estimated for gpt-4o-mini
                result_preview=content,
            )
            return content
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return f"[Analysis error: {e}]"

    def summarize(self, text: str, max_tokens: int = 500) -> str:
        """Summarize long text into a concise brief."""
        return self.analyze(
            system_prompt="You are a crypto intelligence analyst. Summarize the following data into a concise, actionable brief. Focus on key metrics, trends, and anomalies.",
            user_content=text,
        )

    # ─── 3. Image Generation ─────────────────────────────────
    def generate_visual(self, prompt: str,
                        provider: str = "nano-banana") -> Optional[str]:
        """Generate an AI image (chart, infographic, or visual aid).

        Uses Ace Data Cloud's Images API. The 3rd required distinct service.
        Returns URL to generated image, or None on failure.
        """
        logger.info(f"🎨 Image generation [{provider}]: {prompt[:80]}...")
        try:
            task = self.client.images.generate(
                provider=provider,
                prompt=prompt,
            )
            # Wait for async image generation
            result = task.wait(timeout=120)
            url = getattr(result, "url", str(result))
            self.registry.images.record(
                cost=0.005,  # estimated
                result_preview=url,
            )
            logger.info(f"🎨 Image ready: {url}")
            return url
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return None

    @property
    def usage_report(self) -> dict:
        """Full usage report for bounty submission."""
        return self.registry.summary()
