import runpod

from etl.main import main


async def handler(job):
    main()


runpod.serverless.start(
    {
        "handler": handler,
    }
)
