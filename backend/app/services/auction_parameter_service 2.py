"""
auction_parameter_service.py - Resolution des parametres d'agents auctions

Description:
Construit un snapshot de configuration reproductible pour chaque run en
fusionnant default parameter set et overrides explicites.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.models.agent_definition import AgentDefinition
from app.models.agent_parameter_set import AgentParameterSet


def resolve_agent_run_parameters(
    db: Session,
    definition: AgentDefinition,
    parameter_set_id: int | None,
    overrides: dict[str, Any] | None,
) -> tuple[AgentParameterSet | None, dict[str, Any]]:
    """Retourne le parameter set retenu et le snapshot final merge."""
    parameter_set = None
    if parameter_set_id is not None:
        parameter_set = db.query(AgentParameterSet).filter(AgentParameterSet.id == parameter_set_id).first()
        if parameter_set and parameter_set.agent_definition_id != definition.id:
            raise ValueError("Le parameter set n'appartient pas a cet agent")
    else:
        parameter_set = (
            db.query(AgentParameterSet)
            .filter(
                AgentParameterSet.agent_definition_id == definition.id,
                AgentParameterSet.is_default == True,  # noqa: E712
            )
            .order_by(AgentParameterSet.version.desc(), AgentParameterSet.id.desc())
            .first()
        )

    parameter_snapshot = dict(parameter_set.parameters_json or {}) if parameter_set else {}
    parameter_snapshot.update(overrides or {})
    return parameter_set, parameter_snapshot
