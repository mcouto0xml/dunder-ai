"""
Inter-Agent Communication Module
Handles JSON-based message passing between agents
"""

import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime


class AgentMessage:
    """Structured message for inter-agent communication"""

    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        payload: Dict[str, Any],
        request_id: Optional[str] = None,
    ):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.payload = payload
        self.request_id = request_id or f"{from_agent}_{datetime.now().timestamp()}"
        self.timestamp = datetime.now().isoformat()

    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(
            {
                "from_agent": self.from_agent,
                "to_agent": self.to_agent,
                "message_type": self.message_type,
                "payload": self.payload,
                "request_id": self.request_id,
                "timestamp": self.timestamp,
            },
            indent=2,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type,
            "payload": self.payload,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_json(cls, json_str: str) -> "AgentMessage":
        """Create message from JSON string"""
        data = json.loads(json_str)
        return cls(
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            message_type=data["message_type"],
            payload=data["payload"],
            request_id=data.get("request_id"),
        )


class AgentMessageBroker:
    """
    Message broker for routing messages between agents
    """

    def __init__(self):
        self.message_log = []

    async def send_message(
        self, from_agent: str, to_agent: str, message_type: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send a message to another agent and wait for response

        Args:
            from_agent: Sender agent name
            to_agent: Receiver agent name
            message_type: Type of message (e.g., "COMPLIANCE_CHECK", "SEND_EMAIL")
            payload: Message payload with request data

        Returns:
            Response from the target agent as a dictionary
        """
        # Create message
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
        )

        # Log the message
        self.message_log.append({"direction": "SENT", "message": message.to_dict()})

        print(f"\n📨 MESSAGE SENT:")
        print(message.to_json())

        # Route to appropriate agent
        response = await self._route_message(message)

        # Log response
        self.message_log.append({"direction": "RECEIVED", "message": response})

        print(f"\n📬 MESSAGE RECEIVED:")
        print(json.dumps(response, indent=2))

        return response

    async def _route_message(self, message: AgentMessage) -> Dict[str, Any]:
        """Route message to the appropriate agent handler"""

        if message.to_agent == "COMPLIANCE":
            return await self._handle_compliance_message(message)
        elif message.to_agent == "EMAIL":
            return await self._handle_email_message(message)
        elif message.to_agent == "ORCHESTRATOR":
            return await self._handle_orchestrator_message(message)
        else:
            return {
                "status": "ERROR",
                "error": f"Unknown agent: {message.to_agent}",
                "request_id": message.request_id,
            }

    async def _handle_compliance_message(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle messages to Compliance Agent"""
        try:
            import sys
            import os

            sys.path.append(
                os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            )
            from agentCompliance.agent import run_agent

            question = message.payload.get("question", "")
            response_text, success = await run_agent(question)

            return {
                "status": "SUCCESS" if success else "ERROR",
                "request_id": message.request_id,
                "response": {
                    "compliance_response": response_text,
                    "is_violation": "não permite" in response_text.lower()
                    or "não é permitido" in response_text.lower()
                    or "não pode" in response_text.lower(),
                    "question": question,
                },
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "request_id": message.request_id,
                "error": str(e),
            }

    async def _handle_email_message(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle messages to Email Agent"""
        try:
            import sys
            import os

            sys.path.append(
                os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            )
            from agentEmail.agent import send_email

            recipient = message.payload.get("recipient", "")
            subject = message.payload.get("subject", "")
            body = message.payload.get("body", "")

            response_text = await send_email(recipient, subject, body)

            return {
                "status": "SUCCESS",
                "request_id": message.request_id,
                "response": {
                    "email_sent": True,
                    "recipient": recipient,
                    "subject": subject,
                    "result": response_text,
                },
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "request_id": message.request_id,
                "error": str(e),
            }

    async def _handle_orchestrator_message(
        self, message: AgentMessage
    ) -> Dict[str, Any]:
        """Handle messages to Orchestrator Agent"""
        try:
            import sys
            import os

            sys.path.append(
                os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            )
            from orchestrator.agent import handle_request

            data_request = message.payload.get("data_request", "")
            response_text = await handle_request(data_request)

            return {
                "status": "SUCCESS",
                "request_id": message.request_id,
                "response": {"data": response_text, "request": data_request},
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "request_id": message.request_id,
                "error": str(e),
            }

    def get_message_log(self) -> list:
        """Get all messages sent/received"""
        return self.message_log


# Global message broker instance
message_broker = AgentMessageBroker()
