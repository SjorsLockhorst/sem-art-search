seq 0 100 1000 | parallel -j 4 'python -m etl.embed.embed --offset {} --count 100'
