"""
Reference wiring for the MoC agent on smolagents 1.25.0 + transformers.

This shows how the persona (moc_instructions.MOC_INSTRUCTIONS) plugs into smolagents
*features* instead of being baked into a monolithic prompt. Adapt paths/model id to
your hardware. Run on the CPU-only backends already detected in agent.py by swapping
TransformersModel for InferenceClientModel / LiteLLMModel(ollama) as needed.
"""

from smolagents import CodeAgent, ToolCallingAgent, TransformersModel, tool

from moc_instructions import MOC_INSTRUCTIONS


# --- Tools: smolagents auto-renders these into the system prompt via {{tools}} ---
# Wrap your existing NixTools / HyprlandTools methods as @tool functions. Example:
@tool
def nix_search(query: str) -> str:
    """Search nixpkgs for a package.

    Args:
        query: The package name or keyword to search for.
    """
    from tools import NixTools
    return str(NixTools().nix_search(query))


# --- Local model via the transformers library ---
# device_map="auto" offloads to GPU if present; pick a code-capable instruct model.
model = TransformersModel(
    model_id="Qwen/Qwen2.5-Coder-7B-Instruct",
    device_map="auto",
    max_new_tokens=4096,
)


# --- Sub-agents become managed_agents, auto-rendered via {{managed_agents}} ---
researcher = ToolCallingAgent(
    tools=[],                      # e.g. web_search, web_fetch
    model=model,
    name="researcher",
    description="Researches up-to-date Nix packages, options, and documentation. "
                "Call when local context is outdated or insufficient.",
)


agent = CodeAgent(
    tools=[nix_search],
    model=model,
    managed_agents=[researcher],
    instructions=MOC_INSTRUCTIONS,      # persona appended to the built-in prompt
    planning_interval=3,                # the "meta-cognition / look before you leap" step
    additional_authorized_imports=[     # the execution guardrail (NOT prose)
        "subprocess", "pathlib", "json",
    ],
    max_steps=12,
    # executor_type="docker",           # stronger sandbox than the default local executor
)

if __name__ == "__main__":
    agent.run("Audit the flake and report any options that are deprecated.")
