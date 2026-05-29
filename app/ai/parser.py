import re
from dataclasses import dataclass


@dataclass
class ParsedMessage:
    """A conversational block extracted from <message> tags."""

    content: str


@dataclass
class ParsedFile:
    """A code block extracted from <file> tags."""

    path: str
    content: str


@dataclass
class ParsedResponse:
    """The complete parsed result — all messages and all files."""

    messages: list[ParsedMessage]
    files: list[ParsedFile]
    raw: str  # original unparsed text, stored for debugging/history


# Regex patterns for extracting tagged blocks.
#
# re.DOTALL makes '.' match newlines too — critical because
# file content spans many lines.
#
# (.*?) is a non-greedy match — it captures the shortest possible
# string between the opening and closing tags. Without the '?',
# if there were two <message> blocks, it would match from the first
# opening tag all the way to the LAST closing tag, swallowing
# everything in between.

MESSAGE_PATTERN = re.compile(r"<message>(.*?)</message>", re.DOTALL)
FILE_PATTERN = re.compile(r'<file\s+name="([^"]+)">(.*?)</file>', re.DOTALL)


def parse_response(raw_text: str) -> ParsedResponse:
    """
    Parse the complete LLM output into structured messages and files.

    Example input:
        <message>I've updated the button color.</message>

        <file name="src/components/ProfileCard.tsx">
        import React from 'react';
        ...
        </file>

    Example output:
        ParsedResponse(
            messages=[ParsedMessage(content="I've updated the button color.")],
            files=[ParsedFile(path="src/components/ProfileCard.tsx", content="import React...")],
            raw="<message>I've updated..."
        )
    """
    messages = [
        ParsedMessage(content=match.group(1).strip())
        for match in MESSAGE_PATTERN.finditer(raw_text)
    ]

    files = [
        ParsedFile(path=match.group(1).strip(), content=match.group(2).strip())
        for match in FILE_PATTERN.finditer(raw_text)
    ]

    return ParsedResponse(messages=messages, files=files, raw=raw_text)
