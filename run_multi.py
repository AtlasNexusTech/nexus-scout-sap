#!/usr/bin/env python3
"""Multi-cycle test — generate real x402 payment volume."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from autonomous_workflow import AutonomousAgent

agent = AutonomousAgent(agent_name='AtlasNexusScout', run_interval=1)

for i in range(3):
    sep = '=' * 50
    print(f'\n{sep}')
    print(f'CYCLE {i+1}/3')
    print(sep)
    result = agent.run_cycle()
    svcs = result.get('services_used', [])
    cost = result.get('total_cost_usdc', 0)
    print(f'Services: {svcs}')
    print(f'Cost: ${cost:.6f} USDC')
    print(f'Report: {result.get("report", "N/A")}')

total = agent.payment_tracker.total_usdc
print(f'\n💰 TOTAL VOLUME: ${total:.6f} USDC')
print(f'📊 Total payments: {len(agent.payment_tracker.payments)}')
print(f'📄 Reports: examples/')
agent.shutdown()
