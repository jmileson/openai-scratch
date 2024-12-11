import openai
import json

from openai_scratch.context_generators import (
    KagiContextGenerator,
    RandomContextGenerator,
)
from openai_scratch.models import ToolSpec

from .config import Config
from .models import Context

GATHER_TOOLS_AGENT_SYSTEM_PROMPT = """
You are an assistant that fetches online data based on the user's input.

You have access to the following tools:
{gather_tools}

You must select the appropriate tool(s) to gather context based on the user's input.
"""


class LLMGathererDecisionMaker:
    def __init__(self, api_key: str, tools: dict[str, ToolSpec]):
        self._client = openai.AsyncOpenAI(api_key=api_key)
        self._tools = tools
        self._tool_specs = [
            t.TOOL_CONFIG.model_dump(by_alias=True) for t in tools.values()
        ]

    def decide(self, prompt: str) -> list[Context]:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a decision support system tasked with helping "
                    "users gather information about a larger context. Use the support "
                    "tools to help the user determine which tools may help them "
                    "find the information that is useful to them."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=self._tool_specs,
        )
        tool_calls = []
        for choice in response.choices:
            if not choice.message.tool_calls:
                continue

            for tool_call in choice.message.tool_calls:
                name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                tool_calls.append((self._tools[name], arguments))

        results = []
        for tool, args in tool_calls:
            results.append(tool(**args))

        return results


def build_tools(cfg: Config) -> dict[str, ToolSpec]:
    kagi_context_generator = KagiContextGenerator(cfg.kagi_api_key)
    random_context_generator = RandomContextGenerator()

    tools: list[ToolSpec] = [
        kagi_context_generator,
        random_context_generator,
    ]

    return {t.TOOL_CONFIG.name(): t for t in tools}


async def main():
    cfg = Config()  # type: ignore[reportCallIssue]

    tools = build_tools(cfg)

    decision_maker = LLMGathererDecisionMaker(cfg.openai_api_key, tools)

    llm_contexts_1 = decision_maker.decide(
        "I want useful information from the internet, but I don't want random noise. "
        "Can you help me find information about sloths and zoos that keep them?"
    )
    print(llm_contexts_1)
    llm_contexts_2 = decision_maker.decide(
        "I'm a chaos monkey and I want a firhose of information, relevant or not "
        "Can you help me find information about sloths and zoos that keep them?"
    )
    print(llm_contexts_2)
