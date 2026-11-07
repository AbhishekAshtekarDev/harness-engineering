"""harnesslab: a small, readable agent harness for learning harness engineering.

Every part of the harness is a separate module you can read in one sitting:

    models       the model adapters (scripted, Anthropic, OpenAI)
    tools        tool definitions, schema validation, the default coding toolset
    permissions  allow / ask / deny rules and the path guard
    workspace    per-task workspaces and the command runner
    hooks        code the harness runs before and after tool calls
    trace        spans, JSONL traces and a text waterfall
    checks       verification: tests, forbidden files, composite verifiers
    state        task state, progress log and feature list
    loop         the agent loop with budgets and stop conditions
    evals        trials, graders, pass@k and pass^k
"""
from .loop import AgentLoop, Budget, RunResult
from .models import Model, ModelTurn, ScriptedModel, ToolCall
from .permissions import PathGuard, PermissionPolicy, Rule
from .tools import Tool, ToolError
from .trace import Tracer

__all__ = [
    "AgentLoop", "Budget", "RunResult", "Model", "ModelTurn", "ScriptedModel",
    "ToolCall", "PathGuard", "PermissionPolicy", "Rule", "Tool", "ToolError", "Tracer",
]
