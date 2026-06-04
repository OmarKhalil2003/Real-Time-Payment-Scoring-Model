"""
MCP Client Manager

Manages connections to all three MCP servers (Customer History, Fraud Rules,
Fraud Explanation) using stdio transport. Each server runs as a subprocess
managed by the MCP SDK's ClientSession.

Provides high-level async methods that the ScoringService calls to enrich
fraud analysis with contextual intelligence from MCP servers.
"""

import os
import sys
import json
import logging
import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger("mcp-client")


def _get_server_script_path(filename: str) -> str:
    """Resolve the absolute path to an MCP server script."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)


class MCPClientManager:
    """
    Manages MCP client sessions to three fraud analysis servers.

    Uses stdio transport — each server runs as a subprocess child.
    Sessions are initialized once at startup and reused for all requests.
    """

    def __init__(self):
        self._sessions: dict[str, ClientSession] = {}
        self._exit_stack = AsyncExitStack()
        self._initialized = False

    async def initialize(self):
        """Start all MCP server subprocesses and establish sessions."""
        if self._initialized:
            return

        servers = {
            "customer_history": "customer_history_server.py",
            "fraud_rules": "fraud_rules_server.py",
            "explanation": "explanation_server.py",
        }

        python_path = sys.executable

        for name, script in servers.items():
            try:
                script_path = _get_server_script_path(script)
                server_params = StdioServerParameters(
                    command=python_path,
                    args=[script_path],
                )

                stdio_transport = await self._exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
                read_stream, write_stream = stdio_transport

                session = await self._exit_stack.enter_async_context(
                    ClientSession(read_stream, write_stream)
                )
                await session.initialize()

                self._sessions[name] = session
                logger.info(f"MCP server '{name}' connected successfully.")

            except Exception as e:
                logger.error(f"Failed to connect MCP server '{name}': {e}")

        self._initialized = True
        logger.info(
            f"MCP Client initialized with {len(self._sessions)}/{len(servers)} servers."
        )

    async def shutdown(self):
        """Gracefully close all MCP sessions and subprocesses."""
        try:
            await self._exit_stack.aclose()
            logger.info("MCP Client shut down.")
        except Exception as e:
            logger.error(f"Error during MCP shutdown: {e}")
        finally:
            self._sessions.clear()
            self._initialized = False

    # ------------------------------------------
    # High-Level Methods
    # ------------------------------------------

    async def get_customer_history(self, customer_id: str) -> dict:
        """
        Query MCP Server 1 for customer behavioral history.

        Returns a dict with total_transactions, average_amount,
        usual_country, previous_fraud_flags, last_transaction_hours.
        Falls back to empty dict on failure.
        """
        session = self._sessions.get("customer_history")
        if not session:
            logger.warning("Customer history MCP server not available.")
            return {}

        try:
            result = await session.call_tool(
                "get_customer_history",
                arguments={"customer_id": customer_id},
            )
            return json.loads(result.content[0].text)
        except Exception as e:
            logger.error(f"MCP get_customer_history failed: {e}")
            return {}

    async def evaluate_risk_rules(
        self, transaction: dict, customer_history: dict
    ) -> dict:
        """
        Query MCP Server 2 to evaluate fraud rules.

        Returns a dict with risk_score (0-100) and triggered_rules list.
        Falls back to neutral score on failure.
        """
        session = self._sessions.get("fraud_rules")
        if not session:
            logger.warning("Fraud rules MCP server not available.")
            return {"risk_score": 0, "triggered_rules": []}

        try:
            payload = json.dumps({
                "transaction": transaction,
                "customer_history": customer_history,
            })
            result = await session.call_tool(
                "evaluate_risk_rules",
                arguments={"transaction_json": payload},
            )
            return json.loads(result.content[0].text)
        except Exception as e:
            logger.error(f"MCP evaluate_risk_rules failed: {e}")
            return {"risk_score": 0, "triggered_rules": []}

    async def explain_fraud_decision(
        self,
        transaction: dict,
        customer_history: dict,
        score: float,
        triggered_rules: list = None,
    ) -> str:
        """
        Query MCP Server 3 to generate a human-readable explanation.

        Returns explanation string. Falls back to generic message on failure.
        """
        session = self._sessions.get("explanation")
        if not session:
            logger.warning("Explanation MCP server not available.")
            return "Explanation unavailable — MCP server not connected."

        try:
            result = await session.call_tool(
                "explain_fraud_decision",
                arguments={
                    "transaction_json": json.dumps(transaction),
                    "customer_history_json": json.dumps(customer_history),
                    "score": score,
                    "triggered_rules_json": json.dumps(triggered_rules or []),
                },
            )
            data = json.loads(result.content[0].text)
            return data.get("explanation", "No explanation generated.")
        except Exception as e:
            logger.error(f"MCP explain_fraud_decision failed: {e}")
            return "Explanation unavailable — MCP call failed."
