"""
python  main.py How many files do I have called 'test something'?

python  main.py Locate at least one file named after Thor and create another file named Qu with the very same content
"""

import sys

query0 = (
    "Find one files whose name suggests it is about flowers, check if it "
    "speaks of dahlias, and write a one-sentence summary of content to a new file."
)

from src.planner import plan

if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        query = " ".join(args)
    else:
        query = query0
    print(f"QUERY:\n{query}\n")
    pln = plan(query)
    print(f"PLAN: {pln}")
