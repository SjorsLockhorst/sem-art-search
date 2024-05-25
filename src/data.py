from datasets import load_dataset, Image

dataset = load_dataset(
    "parquet", data_files="../data/train-00000-of-00072.parquet")
print(dataset)
