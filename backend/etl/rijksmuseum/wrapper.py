from enum import StrEnum

import httpx
import lxml.etree
from loguru import logger

from db.crud import save_objects_to_database
from db.models import ArtObjects
from etl.sources import ArtSource


class DescriptionLanguages(StrEnum):
    NL = "nl"
    EN = "en"


SUCCESS_CODE = 200


class Client:
    BASE_OAI_URL = "https://www.rijksmuseum.nl/api/oai"

    def __init__(self, language: DescriptionLanguages, api_key: str):
        self.api_key = api_key
        self.language = language
        self.xml_url = f"{self.BASE_OAI_URL}/{api_key}"
        self.failed_limits = []
        self.failed_art_objects = []

    def _remove_namespaces(self, tree: lxml.etree._Element) -> lxml.etree._Element:
        """Remove namespaces from the XML tree for easier XPath queries."""
        for elem in tree.iter():
            if not hasattr(elem.tag, "find"):
                continue  # Skip comments or processing instructions
            index = elem.tag.find("}")
            if index != -1:
                elem.tag = elem.tag[index + 1 :]
        return tree

    def _fetch_objects_from_xml_api(self) -> None:
        """Fetch art objects from the Rijksmuseum XML API and save them to the database."""
        verb = "ListRecords"
        set_param = "subject:PublicDomainImages"
        metadata_prefix = "oai_WPCM"

        params = {
            "verb": verb,
            "set": set_param,
            "metadataPrefix": metadata_prefix,
        }

        batch_art_objects: list[ArtObjects] = []
        total_saved = 0

        with httpx.Client() as client:
            while True:
                try:
                    response = client.get(self.xml_url, params=params)
                    response.raise_for_status()
                except httpx.HTTPError as e:
                    logger.error(f"Error fetching data: {e}")
                    break

                # Parse the XML content
                try:
                    tree = lxml.etree.fromstring(response.content)  # noqa: S320
                except lxml.etree.XMLSyntaxError as e:
                    logger.error(f"Error parsing XML: {e}")
                    break

                # Remove namespaces
                tree = self._remove_namespaces(tree)

                # Use XPath expressions without namespaces
                records = tree.xpath(".//record")

                for record in records:
                    # Extract data using XPath
                    object_id = record.xpath(".//identifier/text()")
                    title = record.xpath(".//title/text()")
                    image_url = record.xpath(".//format/text()")
                    creator = record.xpath(".//creator/text()")

                    # Clean up the creator's name if needed
                    creator_name = ""
                    if creator:
                        creator_text = creator[0]
                        if "|Name=" in creator_text:
                            creator_name = creator_text.split("|Name=")[1].split("|")[0].strip()
                        else:
                            creator_name = creator_text.strip()

                    if not (object_id and title and image_url and creator_name):
                        continue

                    art_object = ArtObjects(
                        original_id=object_id[0],
                        image_url=image_url[0],
                        long_title=title[0],
                        artist=creator_name,
                        source=ArtSource.RIJKSMUSEUM,
                    )

                    batch_art_objects.append(art_object)

                save_objects_to_database(batch_art_objects)
                total_saved += len(batch_art_objects)

                logger.info(f"Total art objects saved: {total_saved}")

                batch_art_objects = []

                # Check for resumptionToken to fetch next set of art objects
                resumption_token = tree.xpath(".//resumptionToken/text()")
                if resumption_token:
                    params = {"verb": "ListRecords", "resumptionToken": resumption_token[0]}
                else:
                    break

    def get_all_objects_with_image(self) -> None:
        """Public method to fetch all art objects with images."""
        self._fetch_objects_from_xml_api()
