# Agelena Project

![A lovely lady A. labyrinthica](https://raw.githubusercontent.com/hemidactylus/agelena/main/pictures/age.png)

learning agents without obfuscation by frameworks.

## Setup

1. Create virtualenv (python 3.9+)
2. install from `requirements.txt`
3. ensure you export environment variables as exemplified in `.env.example`

Now you can try `python main.py [...]` as per examples in the first comment block of that file.

## Notable advancements

_In chronological order, i.e. increasing complexity of the agents' behaviour._

You can checkout the repository to the provided tag to experiment with a snapshot of the code at the various stages.

### Sequential planner

- tag: `sequential_planner`
- features: tool use, planner gives list of tools followed by conclusion to user

### Self-reflective flow control

- tag: `stop_and_rethink`
- features: planner can choose to set a re-thinking point later in the sequence, effectively allowing for "flow control" via periodic self-reflection checkpoints. Introduced 'macros' (non-function steps) to signal failure, conclusion and these re-planning checkpoints.

### (next milestone)

- features: each param-extraction LLM call allows for short-circuit bailout/rethink/failure outcome.