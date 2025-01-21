"""
python  main.py How many files do I have called 'test something'?

python  main.py Locate at least one file named after Thor and create another file named Qu with the very same content
"""
import sys

from agelena.agents import run_agent

query0 = (
    "Find one files whose name suggests it is about reptiles, check if it "
    "speaks of geckos, and write a very short summary of the contents to a new file."
)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        query = " ".join(args)
    else:
        query = query0
    print(f"QUERY:\n{query}\n")
    agent_response = run_agent(query)
    print(f"\nRESPONSE: {agent_response}")
