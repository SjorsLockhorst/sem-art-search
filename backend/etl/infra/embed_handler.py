import runpod

from etl.embed.embed import run_embed_stage
from etl.embed.models import ImageEmbedder

image_embedder = ImageEmbedder()

def handler(job):
    run_embed_stage(
        image_embedder,
        image_count=int(job["input"]["count"]),
        batch_size=int(job["input"]["batch_size"]),
    )
    return "Ran full embedding stage, now done!"


runpod.serverless.start(
    {
        "handler": handler,
    }
)
