from typing import Any
from google.adk.agents import LlmAgent
from google.adk.agents.context import Context
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.tools import AgentTool
from google.adk.workflow import Workflow, node
from google.adk.apps import App
from google.genai import types

from .config import config
import sys
import re
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orbitlearn-security")
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=["orbitlearn/mcp_server.py"],
        )
    )
)

# --- Reusable Skills (Tools) ---
def explain_concept(concept: str) -> dict:
    """Explains an educational concept clearly and adaptively."""
    return {"status": "success", "action": f"Explained {concept}"}

def create_learning_path(topic: str, user_level: str) -> dict:
    """Creates a personalized learning path for the user."""
    return {"status": "success", "action": f"Created path for {topic} at {user_level} level"}

def generate_quiz(topic: str, difficulty: str) -> dict:
    """Generates an adaptive quiz for a specific topic."""
    return {"status": "success", "action": f"Generated {difficulty} quiz on {topic}"}

def evaluate_answer(question: str, user_answer: str) -> dict:
    """Evaluates the learner's answer and provides feedback."""
    return {"status": "success", "action": "Evaluated answer"}

def summarize_topic(topic: str) -> dict:
    """Summarizes a completed topic."""
    return {"status": "success", "action": f"Summarized {topic}"}

def give_hint(question: str) -> dict:
    """Provides a helpful hint for a question without revealing the answer."""
    return {"status": "success", "action": "Provided hint"}

def visualize_concept(concept: str) -> dict:
    """Presents a suitable visualization for a concept."""
    return {"status": "success", "action": f"Visualized {concept}"}

def recommend_next_topic(current_topic: str) -> dict:
    """Recommends the next topic to study based on progress."""
    return {"status": "success", "action": "Recommended next topic"}

# --- Agents ---
lesson_agent = LlmAgent(
    name="lesson_agent",
    model=config.model,
    instruction="You are the Lesson Agent. You explain concepts clearly, create learning paths, summarize topics, recommend the next topic, and provide visualizations. You must output the educational content clearly.",
    description="Explains concepts, creates learning paths, summarizes, recommends next steps, and generates visual diagrams.",
    tools=[explain_concept, create_learning_path, summarize_topic, recommend_next_topic, visualize_concept, mcp_toolset],
)

assessment_agent = LlmAgent(
    name="assessment_agent",
    model=config.model,
    instruction="You are the Assessment Agent. You generate quizzes, evaluate user answers, and provide hints. Do not give direct answers immediately; guide the learner.",
    description="Generates quizzes, evaluates answers, and gives hints.",
    tools=[generate_quiz, evaluate_answer, give_hint, mcp_toolset],
)

# Main Agent (Orchestrator)
orbit_learn_agent = LlmAgent(
    name="orbit_learn_agent",
    model=config.model,
    instruction="""You are OrbitLearn, an intelligent educational AI teacher. You guide the learner through a space-themed journey. 
Understand the learner's knowledge level and coordinate their learning path.
Use your tools to delegate to specialized agents (lesson_agent for teaching, assessment_agent for quizzes/evaluation). 
Engage the user, make learning interactive, and ensure a natural learning flow (Explain -> Visualize -> Interactive Questions -> Quiz -> Evaluate -> Summarize -> Recommend).""",
    tools=[AgentTool(lesson_agent), AgentTool(assessment_agent)],
)

# --- Workflow Nodes ---
@node
def security_checkpoint(ctx: Context, node_input: Any):
    text_content = ""
    if isinstance(node_input, types.Content):
        for part in node_input.parts:
            if part.text:
                text_content += part.text
    elif isinstance(node_input, str):
        text_content = node_input

    # 1. Prompt injection keywords
    injection_keywords = ["ignore previous", "system prompt", "bypass", "jailbreak", "forget instructions"]
    for keyword in injection_keywords:
        if keyword in text_content.lower():
            logger.warning(json.dumps({"event": "security_audit", "severity": "WARNING", "reason": "prompt_injection", "keyword": keyword}))
            return Event(output="Security violation: Potential prompt injection detected.", route="dirty")

    # 2. Domain-specific rule: No cheating assistance
    cheating_keywords = ["cheat", "essay writing service", "do my homework", "exam answers"]
    for keyword in cheating_keywords:
        if keyword in text_content.lower():
            logger.warning(json.dumps({"event": "security_audit", "severity": "WARNING", "reason": "policy_violation", "keyword": "cheating"}))
            return Event(output="Security violation: Cheating assistance is not permitted.", route="dirty")

    # 3. PII scrubbing (e.g., SSN)
    if re.search(r"\b\d{3}-\d{2}-\d{4}\b", text_content):
        logger.info(json.dumps({"event": "security_audit", "severity": "INFO", "reason": "pii_scrubbed", "type": "SSN"}))
        text_content = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED SSN]", text_content)
        
    ctx.state["security_status"] = "verified"
    logger.info(json.dumps({"event": "security_audit", "severity": "INFO", "reason": "passed_checks"}))
    return Event(output=text_content, route="clean")

@node
def security_violation(ctx: Context, node_input: Any):
    return Event(content=types.Content(role="model", parts=[types.Part.from_text(text="Security violation detected. Cannot proceed.")]))

@node(rerun_on_resume=True)
async def human_review(ctx: Context, node_input: Any):
    """A human-in-the-loop step to approve proceeding to the next major section."""
    if not ctx.resume_inputs:
        # Check if we should prompt the user
        text_content = ""
        if isinstance(node_input, types.Content):
            for part in node_input.parts:
                if part.text:
                    text_content += part.text
        elif isinstance(node_input, str):
            text_content = node_input
            
        if "quiz" in text_content.lower() or "ready" in text_content.lower():
             yield RequestInput(interrupt_id="ready_for_next", message="Are you ready for the next step? (yes/no)")
             return
        else:
             yield Event(output=node_input)
             return
            
    user_reply = str(ctx.resume_inputs.get("ready_for_next", "")).lower()
    if "no" in user_reply:
        yield Event(output=types.Content(role="model", parts=[types.Part.from_text(text="Learning paused. We can resume later!")]))
    else:
        yield Event(output=node_input)

@node
def final_output(node_input: Any):
    return node_input

# --- Workflow Graph ---
root_agent = Workflow(
    name="orbitlearn",
    edges=[
        ('START', security_checkpoint),
        (security_checkpoint, {"clean": orbit_learn_agent, "dirty": security_violation}),
        (orbit_learn_agent, human_review),
        (human_review, final_output),
    ],
)

app = App(name="orbitlearn", root_agent=root_agent)
