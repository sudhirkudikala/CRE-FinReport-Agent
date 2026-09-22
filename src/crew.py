import os
from pathlib import Path
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI

# Explicit, OS-independent absolute path anchoring via pathlib
BASE_DIR = Path(__file__).resolve().parent.parent

@CrewBase
class PafeIntelligentOrchestrator():
    """PAfE/PAX Intelligent Orchestrator multi-agent execution pipeline configuration."""

    # Resolves paths safely across Windows and macOS architectures dynamically
    agents_config = str(BASE_DIR / "config" / "agents.yaml")
    tasks_config = str(BASE_DIR / "config" / "tasks.yaml")

    def __init__(self) -> None:
        # Establish specialized LLM endpoints
        self.fast_llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL_NAME_FAST", "gpt-4o-mini"),
            temperature=0.0
        )
        self.advanced_llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL_NAME_ADVANCED", "gpt-4o"),
            temperature=0.0
        )

    # --- AGENT BLOCK DEFINITIONS ---

    @agent
    def telemetry_parser(self) -> Agent:
        from tools.mcp_mdx_tool import execute_mcp_mdx_orchestration
        # Update google_serper_search to the local import line
        from tools.finreport_diagnostics import parse_unstructured_pax_logs, extract_nested_mdx_queries, google_serper_search
        return Agent(
            config=self.agents_config['telemetry_parser'],
            llm=self.fast_llm,
            # Update Mount the tool into the execution array
            tools=[execute_mcp_mdx_orchestration, parse_unstructured_pax_logs, extract_nested_mdx_queries, google_serper_search],
            verbose=True,
            allow_delegation=False
        )


    @agent
    def underwriting_matcher(self) -> Agent:
        # REGISTER THE NEW DEPLOYED CRAG ENGINE HERE
        from tools.finance_diagnostics import audit_financial_data_lineage
        from tools.finreport_diagnostics import map_fault_to_underwriting_risk
        from tools.crag_evaluator_tool import grade_retrieval_context
        return Agent(
            config=self.agents_config['underwriting_matcher'],
            llm=self.advanced_llm,
            tools=[audit_financial_data_lineage, map_fault_to_underwriting_risk, grade_retrieval_context],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def epm_resolution_engine(self) -> Agent:
        from tools.escalation_tool import escalate_to_expert_with_servicenow
        return Agent(
            config=self.agents_config['epm_resolution_engine'],
            llm=self.fast_llm,
            tools=[escalate_to_expert_with_servicenow],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def executive_synthesis_bot(self) -> Agent:
        return Agent(
            config=self.agents_config['executive_synthesis_bot'],
            llm=self.fast_llm,
            tools=[],  # Pure markdown text compilation layer
            verbose=True,
            allow_delegation=False
        )

    # --- TASK BLOCK LINEAGE LINKING ---

    @task
    def parse_telemetry_task(self) -> Task:
        return Task(
            config=self.tasks_config['parse_telemetry_task'],
            agent=self.telemetry_parser()
        )

    @task
    def match_underwriting_task(self) -> Task:
        return Task(
            config=self.tasks_config['match_underwriting_task'],
            agent=self.underwriting_matcher()
        )

    @task
    def generate_resolution_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_resolution_task'],
            agent=self.epm_resolution_engine()
        )

    @task
    def format_output_task(self) -> Task:
        return Task(
            config=self.tasks_config['format_output_task'],
            agent=self.executive_synthesis_bot()
        )

    # --- CREW DEPLOYMENT BLOCK ---

    @crew
    def crew(self) -> Crew:
        """Assembles the coordinated financial systems support architecture."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # Guarantees rigid data lineage tracking
            verbose=True
        )
