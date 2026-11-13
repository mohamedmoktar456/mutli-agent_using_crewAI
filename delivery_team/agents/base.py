"""Shared base definition for a delivery specialist."""

from __future__ import annotations

from dataclasses import dataclass

from crewai import Agent, LLM


@dataclass(frozen=True)
class SpecialistRole:
    role: str
    goal: str
    backstory: str
    allow_delegation: bool = False

    def create_agent(self, llm: LLM) -> Agent:
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=llm,
            allow_delegation=self.allow_delegation,
            max_iter=6 if self.allow_delegation else 2,
            max_execution_time=90 if self.allow_delegation else 60,
            verbose=True,
        )
