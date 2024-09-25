import runpod

from etl.bulk_embed import embed_in_parallel
from etl.embed.models import ImageEmbedder

ImageEmbedder()  # Preload image embedder


def handler(job):
    total_amount = int(job["input"]["total_amount"])
    num_processes = int(job["input"]["num_processes"])
    retrieval_batch_size = int(job["input"]["retrieval_batch_size"])
    embedding_batch_size = int(job["input"]["embedding_batch_size"])

    embed_in_parallel(total_amount, num_processes, retrieval_batch_size, embedding_batch_size)

    return "Ran full embedding stage, now done!"


runpod.serverless.start(
    {
        "handler": handler,
    }
)
