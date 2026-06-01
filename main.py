import asyncio
import logging

import dotenv
from langchain_core.messages import HumanMessage

from backend.agents.builder import create_builder

logger = logging.getLogger(__name__)


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description="Job Evaluation Agent")
    parser.add_argument("--resume", required=True, help="Path to resume PDF or DOCX")
    parser.add_argument("--jobs", nargs="+", required=True, help="Job URLs")
    return parser.parse_args()


async def main():
    args = parse_args()
    job_urls_str = "\n".join(f"  - {url}" for url in args.jobs)

    dotenv.load_dotenv()
    react_graph = create_builder()
    messages = [
        HumanMessage(
            content=f"""
    Can you take a look at my resume at the location '{args.resume}' and these {len(args.jobs)} job applications and tell me which one is the most suitable for my experience?

    {job_urls_str}
    """
        )
    ]

    result = await react_graph.ainvoke({"messages": messages})
    for m in result["messages"]:
        m.pretty_print()


if __name__ == "__main__":
    asyncio.run(main())
