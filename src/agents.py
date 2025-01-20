import json

from .planner import plan
from .settings import MAX_LLM_CALLS_PER_AGENT
from .tools import invoke_tool, tool_description
from .llm import run_completion

PARAM_PROMPT_0 = """You are an AI agent expert at crafting a JSON providing the correct parameters
needed to call a function in order to accomplish a certain task (a subtask to a broader goal).
Based on the following information, please create a JSON format for the arguments.

Do not use markdown or other extraneous decorations: your output must be directly parsable as JSON.

INFORMATION:
- Function signature: {fct_signature}
- Detailed parameter explanation:
{fct_parameter_desc}
- Goal of the function call: {fct_goal} (overarching user query: {user_query})

STEPS DONE SO FAR:
{history}

EXAMPLE OUTPUT:
{{"temperature": 11.5, "location": "Paris", "verbose": False}}

ACTUAL OUTPUT PARAMETER JSON:"""

ANSWER_PROMPT_0 = """You are an AI agent that is wrapping up a task it just accomplished,
made of several steps. Write the final answer to the user who originated the request in the form
of a one-line report summarizing the key fact they need to know, based on the original query
and the history of the steps done to satisfy it.

ORIGINAL USER QUERY:
{user_query}

STEPS DONE SO FAR:
{history}

EXAMPLE ANSWERS:
- I found 4 files matching your request.
- I have listed the relevant items in a file called 'bag_info.txt'

YOUR ACTUAL ANSWER:"""

def _is_at_answering(agent):
    next_step = agent['plan'][agent['cursor']]
    return next_step['action'] == 'answer'


def _has_exceeded_guards(agent):
    return agent['llm_calls'] >= MAX_LLM_CALLS_PER_AGENT


def _format_history(h):
    if h:
        hs = []
        for hi in h:
            assert hi['action'] == 'function'
            fdesc = f"{hi['target']}({', '.join('%s=%s' % (k, v) for k, v in hi['parameters'].items())})"
            this_hs = f"{fdesc} returned {hi['result']}: {hi['notes']}"
            hs.append(this_hs)
        return "\n".join(hs)
    else:
        return None


def run_agent(query):
    pln = plan(query)
    agent = {
        "cursor": 0,
        "plan": pln,
        "llm_calls": 0,
        "history": [],
    }

    while True:
        if _has_exceeded_guards(agent):
            raise ValueError("Guards exceeded.")
        elif _is_at_answering(agent):
            # TODO handle closing step
            history_s = _format_history(agent['history'])
            answer_prompt = ANSWER_PROMPT_0.format(
                user_query=query,
                history={history_s} or "(none so far)",
            )
            u_answer = run_completion(answer_prompt, f"getAnswer")
            agent['llm_calls'] += 1
            return u_answer
        else:
            # advance the agent by one step
            step = agent['plan'][agent['cursor']]
            assert step['action'] == 'function'
            tool = [t for t in tool_description if t['name'] == step['target']][0]
            if tool['parameters'] == []:
                # TODO bypass param LLM call in this case
                f_kwargs = {}
            else:
                # LLM call to prepare parameters
                history_s = _format_history(agent['history'])
                # TODO handle no history case
                short_param_desc = ", ".join(p['name'] for p in tool['parameters'])
                fct_signature = f"{tool['name']}({short_param_desc})"
                fct_parameter_desc = "\n".join(
                    f"    * {p['name']} ({p['type']}): {p['description']}"
                    for p in tool["parameters"]
                )
                param_prompt = PARAM_PROMPT_0.format(
                    fct_signature=fct_signature,
                    fct_parameter_desc=fct_parameter_desc,
                    fct_goal=step['notes'] or '-unspecified-',
                    user_query=query,
                    history=history_s or '(none so far)',
                )
                a=1
                f_kwargs_s = run_completion(param_prompt, f"getParams/{agent['cursor']}")
                agent['llm_calls'] += 1
                f_kwargs = json.loads(f_kwargs_s)
            #
            result = invoke_tool(tool, f_kwargs)

            # advance the agent in its flow
            agent['history'] += [{
                'result': result,
                'parameters': f_kwargs,
                **step,
            }]
            agent['cursor'] += 1
