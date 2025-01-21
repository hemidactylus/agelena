"""
python main.py How many files do I have called something with flower?

python main.py Locate at least one file named after Thor and create another file named Asathorr with the very same content
python main.py Locate at least one file with diamond in its name, then create another file named Asathorr with the very same content
python main.py Locate files about spiders, then read their content and tell me which one is a fictional story
python main.py --plan-only Find a file on reptiles. If it speaks of turtles, give me a report. Otherwise, I do not care at all.

python main.py --plan-only Check the news and if there are coup d\'etat please turn on the kettle for my tea
"""
import json
import sys

from agelena.agents import run_agent
from agelena.planner import create_plan

query0 = (
    "Find one files whose name suggests it is about reptiles, check if it "
    "speaks of geckos, and write a very short summary of the contents to a new file."
)


if __name__ == "__main__":
    args = sys.argv[1:]
    plan_only = "--plan-only" in args
    argsw = [a for a in args if a != "--plan-only"]
    if argsw:
        query = " ".join(argsw)
    else:
        query = query0
    print(f"QUERY:\n{query}\n")
    if plan_only:
        plan = create_plan(query)
        print("\nPLAN:")
        print(json.dumps(plan, indent=2))
    else:
        agent_response = run_agent(query)
        print(f"\nRESPONSE: {agent_response}")
