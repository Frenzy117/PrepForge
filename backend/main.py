import argparse
import asyncio
import logging
from contextlib import asynccontextmanager

import dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage

from backend.agents.builder import create_builder
from backend.api.routes import analyze, jobs, query, upload, settings as settings_routes, report as report_routes
from backend.config import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        dotenv.load_dotenv()
        app.state.react_graph = create_builder()
        logger.info("Agent builder initialized successfully")
        yield
    except Exception as e:
        logger.exception("Failed to create agent: %s", e)
        raise


app = FastAPI(
    title="Prep Forge - Agentic Job Evaluation System",
    description="AI-powered job evaluation and resume analysis system",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
cors_origins = (
    settings.cors_origins.split(",")
    if isinstance(settings.cors_origins, str)
    else settings.cors_origins
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(settings_routes.router, prefix="/api", tags=["settings"])
app.include_router(report_routes.router, prefix="/api", tags=["report"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Prep Forge"}


def parse_args():
    parser = argparse.ArgumentParser(description="Job Evaluation Agent")
    parser.add_argument("--resume", required=True, help="Path to resume PDF or DOCX")
    parser.add_argument("--jobs", nargs="+", required=True, help="Job URLs")
    return parser.parse_args()


async def cli_main():
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
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
