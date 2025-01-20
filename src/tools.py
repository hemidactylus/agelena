# comprehensive list of tools, extended description

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
        "description": "write a certaing text into a new file, identified by its name.",
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
