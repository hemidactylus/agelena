import json

from .planner import create_plan
from .settings import MAX_LLM_CALLS_PER_AGENT
from .tools import invoke_tool, tool_description
from .llm import run_completion

PARAM_PROMPT_0 = """You are an AI agent expert at crafting a JSON providing the correct parameters
needed to call a function in order to accomplish a certain task (a subtask to a broader goal).
Based on the following information, please create a JSON format for the arguments.

Do not use markdown or other extraneous decorations: your output must be directly parsable as JSON.

If for some reason the best outcome is NOT to call the function,
rather to re-think the course of action to the broader user query,
you can return the following special JSON:
{{"__macro": "STOP_AND_REPLAN"}}

If the history collected so far shows that it is hopeless to continue, and that the task
cannot be completed at all, you can return the following special JSON:
{{"__macro": "FAILURE", "__notes": "<succinct reason for bailing out>"}}

If you can already give a final success report/answer to the user, you can return
the following special JSON:
{{"__macro": "ANSWER_USER", "__message": "<final message to user>"}}

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
    return next_step['action_type'] == 'answer'


def _has_exceeded_guards(agent):
    return agent['llm_calls'] >= MAX_LLM_CALLS_PER_AGENT


def _format_history(h):
    if h:
        hs = []
        for hi in h:
            if hi['action_type'] == 'function':
                fdesc = f"{hi['target']}({', '.join('%s=%s' % (k, v) for k, v in hi['parameters'].items())})"
                this_hs = f"{fdesc} returned {hi['result']}: {hi['notes']}"
                hs.append(this_hs)
            elif hi['action_type'] == 'macro':
                if hi['target'] == 'STOP_AND_REPLAN':
                    this_hs = 'The agent has stopped to consider what happened so far and devised a new segment of the plan.'
                else:
                    raise ValueError(f"Unknown macro type for history summary: '{hi['target']}'")
                hs.append(this_hs)
        return "\n".join(hs)
    else:
        return None


def run_agent(query):
    plan = create_plan(query)
    if plan[-1]["action_type"] == "macro" and plan[-1]["target"] == "FAILURE":
        notes = plan[-1]["notes"]
        if notes:
            raise ValueError(f"Agent cannot accomplish request: {notes}.")
        else:
            raise ValueError(f"Agent cannot accomplish request.")
    agent = {
        "cursor": 0,
        "plan": plan,
        "llm_calls": 1,
        "history": [],
    }

    while True:
        if _has_exceeded_guards(agent):
            raise ValueError("Guards exceeded.")

        next_step = agent['plan'][agent['cursor']]
        if next_step['action_type'] == 'macro':
            if next_step['target'] == 'ANSWER_USER':
                return next_step["message"]
            elif next_step['target'] == 'REPORT_TO_USER':
                history_s = _format_history(agent['history'])
                answer_prompt = ANSWER_PROMPT_0.format(
                    user_query=query,
                    history={history_s} or "(none so far)",
                )
                u_answer = run_completion(answer_prompt, f"getAnswer")
                agent['llm_calls'] += 1
                agent['plan'] += [{
                    "action_type": "macro",
                    "target": "ANSWER_USER",
                    "message": u_answer,
                }]
                agent['cursor'] += 1
            elif next_step['target'] == 'STOP_AND_REPLAN':
                history_s = _format_history(agent['history'])
                next_plan = create_plan(query, history_so_far=history_s)
                agent['llm_calls'] += 1
                agent['plan'] = agent['plan'] + next_plan
                # advance the agent in its flow
                agent['history'] += [next_step]
                agent['cursor'] += 1
            elif next_step['target'] == 'FAILURE':
                notes = next_step["notes"]
                if notes:
                    raise ValueError(f"Agent declared defeat midway through execution: {notes}.")
                else:
                    raise ValueError(f"Agent declared defeat midway through execution.")
            else:
                raise ValueError(f"unknown macro '{next_step['target']}'")
        elif next_step['action_type'] == 'function':
            tool = [t for t in tool_description if t['name'] == next_step['target']][0]
            if tool['parameters'] == []:
                # bypass param LLM call in this case
                f_kwargs = {}
            else:
                # LLM call to prepare parameters
                history_s = _format_history(agent['history'])
                # TODO handle no history case more gracefully in prompt
                short_param_desc = ", ".join(p['name'] for p in tool['parameters'])
                fct_signature = f"{tool['name']}({short_param_desc})"
                fct_parameter_desc = "\n".join(
                    f"    * {p['name']} ({p['type']}): {p['description']}"
                    for p in tool["parameters"]
                )
                param_prompt = PARAM_PROMPT_0.format(
                    fct_signature=fct_signature,
                    fct_parameter_desc=fct_parameter_desc,
                    fct_goal=next_step['notes'] or '-unspecified-',
                    user_query=query,
                    history=history_s or '(none so far)',
                )
                f_kwargs_s = run_completion(
                    param_prompt,
                    f"getParams[step {agent['cursor']}]/{next_step['target']}",
                )
                agent['llm_calls'] += 1
                f_kwargs = json.loads(f_kwargs_s)
            #
            if "__macro" in f_kwargs:
                # the param-extraction has diverted into another flow
                macro_name = f_kwargs["__macro"]
                print(f"    ParamExtractionReturnedMacro({f_kwargs})")
                if macro_name == "STOP_AND_REPLAN":
                    agent['plan'] = agent['plan'][:agent["cursor"]] + [{
                        "action_type": "macro",
                        "target": "STOP_AND_REPLAN",
                        "notes": None,
                    }]
                elif macro_name == "FAILURE":
                    agent['plan'] = agent['plan'][:agent["cursor"]] + [{
                        "action_type": "macro",
                        "target": "FAILURE",
                        "notes": f_kwargs["__notes"],
                    }]
                elif macro_name == "ANSWER_USER":
                    agent['plan'] = agent['plan'][:agent["cursor"]] + [{
                        "action_type": "macro",
                        "target": "ANSWER_USER",
                        "message": f_kwargs["__message"],
                    }]
                else:
                    raise ValueError(f"Unknown macro in param-extraction diversion: '{macro_name}'")
            else:
                result = invoke_tool(tool, f_kwargs)

                # advance the agent in its flow
                agent['history'] += [{
                    'result': result,
                    'parameters': f_kwargs,
                    **next_step,
                }]
                agent['cursor'] += 1
