PLANNER_PROMPT_0 = """You are a planner AI that is very good at coming up with a plan to accomplish a complex task,
given a user request and a set of possible tools to use in the form of functions that you can call.

The exact nature of the function arguments is of no concern of you yet: all you need to do is to lay out a logical
sequence of actions (a 'plan') that lead to completing the required task. Do not use functions that are not
provided in the "available functions" below.

Do not express control flow with "if", indentation or the like. Plans are simple flat lists of function names,
preferrably followed by a colon and a very terse textual explanation of the step rationale.

EXAMPLE PLAN: (where the identifiers here are function names)
- get_current_date
- get_weather_info
- get_user_preferences: this is later needed to tailor the message to what the user expects.
- prepare_message_text
- send_message_to_user

AVAILABLE FUNCTIONS:
{tools_short}

USER REQUEST: {query}

YOUR PLAN:"""

from .tools import tool_description
from .llm import run_completion

tool_description_short = "\n".join(
    f"'{tool['name']}': {tool['description']}" for tool in tool_description
)


def _validate_fct(fct):
    assert any(fct == td['name'] for td in tool_description)


def plan(query):
    planner_prompt = PLANNER_PROMPT_0.format(
        tools_short=tool_description_short,
        query=query,
    )
    response = run_completion(planner_prompt, label="planner")
    rlines = [l.strip() for l in response.split("\n") if l.strip()]
    final_plan = []
    for rl in rlines:
        assert rl[:2] == "- "
        rest = rl[2:]
        if ":" in rest:
            fct = rest.split(":")[0].strip()
            notes = rest.split(":")[1].strip()
        else:
            fct = rest.strip()
            notes = None
        _validate_fct(fct)
        final_plan.append({"action": "function", "target": fct, "notes": notes})
    final_plan.append({"action": "answer", "target": None, "notes": None})
    return final_plan
