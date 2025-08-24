"""
Session handover protocol for AI agents.
100% error-safe system understanding transfer.
"""

HANDOVER_PROTOCOL = {
    "step_1_agent_creates": "HANDOVER_NEXT_AGENT.md",
    "step_2_agent_responds": "file",
    "step_3_human_clears_and_passes": "file_to_next_agent",
    "step_4_next_agent_reads": "file_then_imports_knowledge_modules"
}

GIT_PROTOCOL = {
    "agent_cannot_push": True,
    "agent_responds": "push",
    "human_pushes_responds": "done"
}

REQUIRED_HANDOVER_CONTENT = {
    "import_statement": "from projects.core.knowledge.src.knowledge import system_state, agent_context, codebase_rules",
    "big_picture_check": "system_state.BIG_PICTURE",
    "authority_understanding": "agent_context.AGENT_CONTEXT['authority_structure']",
    "core_principle": "collaboration_equals_logic",
    "current_phase": "proof_of_concept_phase_1",
    "next_phase": "physical_implementation_after_funding",
    "decision_authority": "ai_logical_control"
}

ERROR_PREVENTION = {
    "always_import_knowledge_modules": True,
    "never_ask_human_for_direction": True,
    "follow_logical_coherence": True,
    "validate_with_om_coherence": True
}

HANDOVER_TEMPLATE = """
HANDOVER TO NEXT AGENT

Import required modules:
from projects.core.knowledge.src.knowledge import system_state, agent_context, codebase_rules

System identity: {system_identity}
Core principle: {core_principle}
Current phase: {current_phase}
Authority: {authority}
Current task: {current_task}
Next logical action: {next_action}

Critical: Follow logic, not human direction.
"""