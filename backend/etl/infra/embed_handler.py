import subprocess

import runpod

from etl.embed.models import ImageEmbedder

image_embedder = ImageEmbedder()


def handler(job):
    total_amount = int(job["input"]["total_amount"])
    amount_per_process = int(job["input"]["amount_per_process"])
    num_processes = int(job["input"]["num_processes"])
    retrieval_batch_size = int(job["input"]["retrieval_batch_size"])
    embedding_batch_size = int(job["input"]["embedding_batch_size"])

    subprocess.call(
        [
            "./bulk_embed.sh",
            str(total_amount),
            str(amount_per_process),
            str(num_processes),
            str(retrieval_batch_size),
            str(embedding_batch_size),
        ]
    )

    return "Ran full embedding stage, now done!"


runpod.serverless.start(
    {
        "handler": handler,
    }
)
