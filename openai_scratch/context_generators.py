import json
import random

import kagiapi

from .models import Context, Function, Parameters, Tool, Type


# NOTE: this can be replicated for other sources as well
class KagiContextGenerator:
    TOOL_CONFIG = Tool(
        function=Function(
            name="kagi_context_generator",
            description=(
                "Get top search results from Kagi, use the when users need information "
                "about search results, like top hits, sites or recent headlines, but "
                "they don't need detail about those hits."
            ),
            parameters=Parameters(
                properties={
                    "search_string": {
                        "description": (
                            "A string formatted for use with Kagi's enrichment API to "
                            "add additional info the requested information."
                        ),
                        "type": Type.STR,
                    }
                },
                required=["search_string"],
            ),
        )
    )

    def __init__(self, api_key: str):
        self._client = kagiapi.KagiClient(api_key)

    def __call__(self, search_string: str) -> Context:
        # TODO: I would call search, but it's in closed beta
        response = self._client.enrich(search_string)

        text = ""
        for k, v in response.items():
            text += f"{k}: {json.dumps(v)}\n"

        return Context(text=text)


class RandomContextGenerator:
    TOOL_CONFIG = Tool(
        function=Function(
            name="random_context_generator",
            description=(
                "Get some random information. Use this when users want random nonsense "
                "added into their contexts because they're chaos monkies"
            ),
            parameters=Parameters(
                properties={},
                required=[],
            ),
        )
    )

    def __call__(self) -> Context:
        return Context(text=f"The square root of 100 is {random.randint(1, 100)}")
