import os
from pathlib import Path

import yaml
from crewai import Agent, Crew, Process, Task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from error_handling import (
    APIError,
    ConfigurationError,
    DataProcessingError,
    ErrorSeverity,
    log_error,
    retry,
)

# Load environment variables
load_dotenv()


class ProductResearchCrew:
    def __init__(self, products):
        self.products = products
        self.config_dir = Path("config")
        self.agents_config = self._load_config("agents.yaml")
        self.tasks_config = self._load_config("tasks.yaml")
        # Initialize tools with proper parameters
        serper_api_key = os.getenv("SERPER_API_KEY")
        if not serper_api_key:
            log_error(
                ConfigurationError(
                    "Serper API key not found in environment variables",
                    severity=ErrorSeverity.WARNING,
                    details={"env_var": "SERPER_API_KEY"},
                )
            )

        # SerperDevTool uses the SERPER_API_KEY environment variable
        os.environ["SERPER_API_KEY"] = serper_api_key or ""

        # Initialize tools
        self.tools = {
            "ScrapeWebsiteTool": ScrapeWebsiteTool(),
            "SerperDevTool": SerperDevTool(),
        }

    def _load_config(self, filename):
        """Load configuration from YAML file"""
        config_path = self.config_dir / filename
        try:
            with open(config_path, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            error = ConfigurationError(
                f"Configuration file not found: {filename}",
                severity=ErrorSeverity.CRITICAL,
                details={"path": str(config_path)},
            )
            log_error(error)
            raise error
        except yaml.YAMLError as e:
            error = ConfigurationError(
                f"Invalid YAML in configuration file: {filename}",
                severity=ErrorSeverity.CRITICAL,
                details={"path": str(config_path), "error": str(e)},
            )
            log_error(error)
            raise error

    @retry(max_attempts=3, retry_exceptions=[APIError])
    def _create_llm(self, agent_config):
        """Create LLM based on agent configuration"""
        llm_config = agent_config.get("llm", {})
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            error = ConfigurationError(
                "OpenRouter API key not found in environment variables",
                severity=ErrorSeverity.CRITICAL,
                details={"env_var": "OPENROUTER_API_KEY"},
            )
            log_error(error)
            raise error

        try:
            # Import SecretStr for API key
            from pydantic import SecretStr

            # Create LLM with the correct parameter names and types
            return ChatOpenAI(
                base_url=llm_config.get("base_url", "https://openrouter.ai/api/v1"),
                api_key=SecretStr(api_key) if api_key else None,
                model=llm_config.get("model", "meta-llama/llama-3-8b-instruct"),
            )
        except Exception as e:
            error = APIError(
                f"Failed to initialize LLM: {str(e)}",
                severity=ErrorSeverity.CRITICAL,
                details={
                    "model": llm_config.get("model", "meta-llama/llama-3-8b-instruct")
                },
            )
            log_error(error)
            raise error

    def _get_tools_for_agent(self, agent_name):
        """Get tools for an agent based on tasks configuration"""
        tools = []
        for task_name, task_config in self.tasks_config.items():
            if task_config.get("agent") == agent_name and "tools" in task_config:
                for tool_name in task_config["tools"]:
                    if tool_name in self.tools:
                        tools.append(self.tools[tool_name])
        return tools

    def create_agent(self, agent_name):
        """Create an agent based on configuration"""
        if agent_name not in self.agents_config:
            error = ConfigurationError(
                f"Agent '{agent_name}' not found in configuration",
                severity=ErrorSeverity.ERROR,
                details={
                    "agent_name": agent_name,
                    "available_agents": list(self.agents_config.keys()),
                },
            )
            log_error(error)
            raise error

        agent_config = self.agents_config[agent_name]
        llm = self._create_llm(agent_config)
        tools = self._get_tools_for_agent(agent_name)

        try:
            return Agent(
                role=agent_config.get("role", ""),
                goal=agent_config.get("goal", ""),
                backstory=agent_config.get("backstory", ""),
                tools=tools,
                llm=llm,
                verbose=True,
            )
        except Exception as e:
            error = ConfigurationError(
                f"Failed to create agent '{agent_name}': {str(e)}",
                severity=ErrorSeverity.ERROR,
                details={"agent_name": agent_name, "config": agent_config},
            )
            log_error(error)
            raise error

    @retry(max_attempts=2)
    def kickoff(self):
        try:
            # Create agents
            agents = {}
            for agent_name in self.agents_config:
                agents[agent_name] = self.create_agent(agent_name)

            # Create tasks
            tasks = []
            task_objects = {}

            # First pass: create all tasks without context
            for task_name, task_config in self.tasks_config.items():
                agent_name = task_config.get("agent")
                if agent_name not in agents:
                    error = ConfigurationError(
                        f"Agent '{agent_name}' not found for task '{task_name}'",
                        severity=ErrorSeverity.ERROR,
                        details={
                            "task_name": task_name,
                            "agent_name": agent_name,
                            "available_agents": list(agents.keys()),
                        },
                    )
                    log_error(error)
                    raise error

                # Customize description for product-specific tasks
                description = task_config.get("description", "")
                if "research_task" in task_name and self.products:
                    description = f"Research {', '.join(self.products)} specifications"
                elif "comparison_task" in task_name and self.products:
                    description = (
                        f"Compare {', '.join(self.products)} features objectively"
                    )

                try:
                    task = Task(
                        description=description,
                        agent=agents[agent_name],
                        expected_output=task_config.get("expected_output", ""),
                        output_file=task_config.get("output_file", None),
                    )

                    task_objects[task_name] = task
                    tasks.append(task)
                except Exception as e:
                    error = ConfigurationError(
                        f"Failed to create task '{task_name}': {str(e)}",
                        severity=ErrorSeverity.ERROR,
                        details={"task_name": task_name, "config": task_config},
                    )
                    log_error(error)
                    raise error

            # Second pass: add context to tasks
            for task_name, task_config in self.tasks_config.items():
                if "context" in task_config:
                    context_task_name = task_config["context"]
                    if context_task_name in task_objects:
                        task_objects[task_name].context = [
                            task_objects[context_task_name]
                        ]

            # Create and run the crew
            try:
                crew = Crew(
                    agents=list(agents.values()),
                    tasks=tasks,
                    process=Process.sequential,
                    verbose=True,
                )

                # Ensure output directory exists
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)

                return crew.kickoff()
            except Exception as e:
                error = DataProcessingError(
                    f"Error during crew execution: {str(e)}",
                    severity=ErrorSeverity.ERROR,
                    details={
                        "agents": list(agents.keys()),
                        "tasks": list(task_objects.keys()),
                    },
                )
                log_error(error)
                raise error

        except Exception as e:
            if not isinstance(e, (ConfigurationError, DataProcessingError, APIError)):
                error = DataProcessingError(
                    f"Unexpected error during kickoff: {str(e)}",
                    severity=ErrorSeverity.ERROR,
                )
                log_error(error)
                raise error
            raise
