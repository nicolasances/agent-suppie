"""
Toto Tome Scraper - Microservice for scraping and processing tome content.

Uses TotoMicroservice framework for:
- Configuration management
- API controller with FastAPI
- Message bus for event handling

Run with: python app.py
"""
import asyncio
import os
from config.config import MyConfig
from totoms import ( TotoMicroservice, TotoMicroserviceConfiguration, TotoEnvironment, APIConfiguration, AgentsConfiguration, )
from totoms.TotoMicroservice import APIEndpoint, determine_environment

from dlg.hello import say_hello
from agent.suppie_agent import SuppieAgent

def get_microservice_config() -> TotoMicroserviceConfiguration:
    """Create and return the microservice configuration."""
    return TotoMicroserviceConfiguration(
        service_name="suppie-agent",
        base_path="/suppieagent",
        environment=TotoEnvironment(
            hyperscaler=os.getenv("HYPERSCALER", "gcp").lower(),
            hyperscaler_configuration=determine_environment()
        ),
        custom_config=MyConfig,
        api_configuration=APIConfiguration(
            api_endpoints=[
                APIEndpoint(method="GET", path="/hello", delegate=say_hello),
            ]
        ),
        agents_configuration=AgentsConfiguration(
            agents=[SuppieAgent]
        ),
    )


async def main():
    """Main entry point for running the microservice."""
    microservice = await TotoMicroservice.init(get_microservice_config())
    port = int(os.getenv("PORT", "8080"))
    await microservice.start(port=port)


if __name__ == "__main__":
    asyncio.run(main())
