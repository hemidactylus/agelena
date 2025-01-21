# comprehensive list of tools, extended description

from .fstools import fs_find, fs_grep


tool_description = [
    {
        "name": "find",
        "description": "Find files whose name matches a certain substring, case-insensitive.",
        "parameters": [
            {
                "name": "pattern",
                "type": "string",
                "description": "a substring for matching file names.",
            },
        ],
    },
    {
        "name": "grep",
        "description": "Returns the lines of a certain file that contain a certain substring, case-insensitive.",
        "parameters": [
            {
                "name": "file",
                "type": "string",
                "description": "name of the file to inspect.",
            },
            {
                "name": "pattern",
                "type": "string",
                "description": "substring to look for within the file.",
            },
        ],
    },
    {
        "name": "cat",
        "description": "read the full content of a certain file.",
        "parameters": [
            {
                "name": "file",
                "type": "string",
                "description": "name of the file to open.",
            },
        ],
    },
    {
        "name": "create",
        "description": "write a certain text into a new file, identified by its name.",
        "parameters": [
            {
                "name": "file",
                "type": "string",
                "description": "name of the file to create.",
            },
            {
                "name": "content",
                "type": "string",
                "description": "full content to write into the file.",
            },
        ],
    },
]


def invoke_tool(tool, args_dict):
    tool_name = tool["name"]
    print(f"    ToolInvoke {tool_name} / {args_dict}")
    if tool_name == "find":
        result = fs_find(**args_dict)
    elif tool_name == "grep":
        result = fs_grep(**args_dict)
    elif tool_name == "cat":
        1/0
        return "This is a wonderful treatise on dahlias. Dahlias are pretty flowers requiring little sunlight. They need water. Do not plan near pine trees. Trim leaves often."
    elif tool_name == "create":
        1/0
        return "Done."
    else:
        1/0

    print(f"    ToolResult {tool_name} -> {result}")
    return result
