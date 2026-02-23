from langchain_core.messages import HumanMessage
import logging
import asyncio
import dotenv
import argparse
from backend.Builder import create_builder
# from agents.builder import create_builder
# from fastapi import FastAPI, HTTPException, Form, UploadFile, File
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware
# from config import get_settings
# from api.routes import query
# from api.models import QueryRequest, QueryResponse
# from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     try:
#         app.state.react_graph = create_builder()
#         yield
#     except Exception as e:
#         logger.exception("Failed to create agent: %s",e)
#         raise

# app = FastAPI(title='Prep Forge - Agentic Job Evaluation System', lifespan=lifespan)

# settings = get_settings()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.cors_origins if hasattr(settings, 'cors_origins') else ["http://localhost:5173"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(query.router, tags=["query"])
# if __name__ == "__main__":

    # import uvicorn
    # uvicorn.run("main:app", host="0.0.0.0", port=8000,reload=True)

def parse_args():
    parser = argparse.ArgumentParser(description="Job Evaluation Agent")
    parser.add_argument("--resume", required = True, help="Path to resume PDF")
    parser.add_argument("--jobs", nargs="+", required=True, help = "Job URLs")
    return parser.parse_args()

async def main():
    args = parse_args()
    job_urls_str = "\n".join(f"  - {url}" for url in args.jobs)
    job_urls = [
    'https://www.indeed.com/viewjob?jk=40781386989fa311&from=shareddesktop_copy',
    'https://www.indeed.com/viewjob?jk=ad7e3ed1af2823b4&from=shareddesktop_copy',
    'https://www.indeed.com/viewjob?jk=348becd57110a790&from=shareddesktop_copy'
    ]

    dotenv.load_dotenv()
    react_graph = create_builder()
    messages = [HumanMessage(content=f"""
    Can you take a look at my resume at the location '{args.resume}' and these {len(args.jobs)} job applications and tell me which one is the most suitable for my experience?

    {job_urls_str}
    """)]

    result = await react_graph.ainvoke({"messages": messages})
    for m in result['messages']:
        m.pretty_print()

if __name__ == "__main__":
    asyncio.run(main())