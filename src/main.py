import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find most simliar art work based on semantic similarity between user query, and image embeddings.")

    parser.add_argument(
        "query", type=str, help="The search query to find art works with."
    )

    parser.add_argument(
        "top-k", type=int, default=1, help="The amount of most similar images to show."
    )
    args = parser.parse_args()
    print(args)

