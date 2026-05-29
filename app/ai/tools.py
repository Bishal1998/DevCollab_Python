TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_file_content",
            "description": (
                "Retrieve the content of one or more files from the project. "
                "Use this when you need to read existing files to understand "
                "the codebase before making changes. Pass the exact file paths "
                "as they appear in the file tree."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file paths to retrieve, e.g. ['src/App.tsx', 'src/utils/api.ts']",
                    }
                },
                "required": ["paths"],
            },
        },
    }
]
