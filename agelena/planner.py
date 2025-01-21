PLANNER_PROMPT_0 = """You are a planner AI that is very good at coming up with a plan to accomplish a complex task,
given a user request and a set of possible 'tools' to use in the form of functions that you can call.

Plans are simple flat lists of action names, i.e. function names / special macros, one per line,
preferrably followed by a colon and a very terse textual explanation of the rationale for the step.

The exact nature of the function arguments is of no concern of you yet: all you need to do is to lay out a logical
sequence of actions (a 'plan') that gets you closer to completing the required task.

Plans MUST have the special macro REPORT_TO_USER as their final step, which marks completion.
Do not use functions that are not provided in the "available functions" below.
Use functions sparingly, for example if the query requires no files to be created, don't.

If there is no way to accomplish the request, be honest and return a single-step plan just saying:
- FAILURE: <optional reason for the failure>

EXAMPLE PLAN: (where the identifiers here are function names)
- get_current_date
- get_weather_info
- get_user_preferences: this is later needed to tailor the message to what the user expects.
- prepare_message_text
- send_message_to_user: briefly describe the successful completion of the task in an email.
- REPORT_TO_USER: report whether the required task succeeded.

AVAILABLE FUNCTIONS:
{tools_short}

AVAILABLE SPECIAL MACROS:
  - REPORT_TO_USER
  - FAILURE

USER REQUEST: {query}

YOUR PLAN:"""

from .tools import tool_description
from .llm import run_completion

tool_description_short = "\n".join(
    f"  - {tool['name']}: {tool['description']}" for tool in tool_description
)

tool_names = {td['name'] for td in tool_description}
macro_names = {"REPORT_TO_USER", "FAILURE"}
assert macro_names & tool_names == set()

def _syntax_check_plan(plan):
    if not plan:
        raise ValueError("Empty plan.")
    prev, last = plan[:-1], plan[-1]
    if last["action_type"] != "macro":
        raise ValueError("Plan ends in wrong action type")
    if last["target"] not in {"REPORT_TO_USER", "FAILURE"}:
        raise ValueError("Plan ends in wrong target")
    if any(p['action_type'] != 'function' for p in prev):
        raise ValueError("Plan has nonfunctions before last step.")


def create_plan(query):
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
            tgt = rest.split(":")[0].strip()
            notes = rest.split(":")[1].strip()
        else:
            tgt = rest.strip()
            notes = None
        if tgt in macro_names:
            final_plan.append({"action_type": "macro", "target": tgt, "notes": notes})
        elif tgt in tool_names:
            final_plan.append({"action_type": "function", "target": tgt, "notes": notes})
        else:
            raise ValueError(f"Unknown action in plan: '{tgt}'.")
    _syntax_check_plan(final_plan)
    return final_plan
