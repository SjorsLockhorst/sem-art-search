#!/bin/bash

if [ $# -ne 5 ]; then
    echo "Usage: $0 <total_amount> <amount_per_process> <num_processes> <retrieval_batch_size> <embedding_batch_size>"
    exit 1
fi

total_amount=$1         # The total number of images to retrieve (total work)
amount_per_process=$2   # The amount of images each process should handle
num_processes=$3        # The number of parallel processes to run
retrieval_batch_size=$4        # The retrieval batch size
embedding_batch_size=$5        # The embedding batch size

seq 0 $amount_per_process $((total_amount - amount_per_process)) | parallel -j $num_processes 'poetry run python -m etl.embed.embed --offset {} --count '"$amount_per_process"' --retrieval-batch-size' "$retrieval_batch_size"' --embedding-batch-size' "$embedding_batch_size"' '

echo "Parallel processes started to handle $total_amount images, each process handling $amount_per_process images with $num_processes parallel processes running."
