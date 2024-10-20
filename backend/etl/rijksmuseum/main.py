from config import EtlSettings
from etl.errors import ExtractError
from etl.rijksmuseum.wrapper import Client, DescriptionLanguages

etl_settings = EtlSettings()  # type: ignore  # noqa: PGH003


def fetch_art_objects(
    api_key: str = etl_settings.rijksmuseum_api_key, language: DescriptionLanguages = DescriptionLanguages.EN
):
    """
    Fetch the art objects from the Rijksmuseum API.
    """
    try:
        client = Client(language=language, api_key=api_key)
        return client.get_all_objects_with_image()
    except Exception as e:
        raise ExtractError(msg=str(e)) from e
