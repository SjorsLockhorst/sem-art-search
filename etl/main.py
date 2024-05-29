from dotenv import load_dotenv
from rijksmuseum.wrapper import Client, DescriptionLanguages
import os
from errors import MissingApiKeyError

load_dotenv()


def main():
    api_key = os.getenv("RIJKSMUSEUM_API_KEY")
    if not api_key:
        raise MissingApiKeyError("No API Key found in the env variables")
    c = Client(language=DescriptionLanguages.NL, api_key=api_key)
    art_objects = c.get_image_objects(amount_of_objects=25)

    print(art_objects)


if __name__ == "__main__":
    main()
