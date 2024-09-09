import runpod
import asyncio

from etl.extract import run_extract_stage

async def handler(job):
    await run_extract_stage()
    return "Done extracting from API"

runpod.serverless.start({
        "handler": handler,
    }
)
