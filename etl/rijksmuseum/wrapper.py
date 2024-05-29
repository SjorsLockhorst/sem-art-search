import httpx
from enum import StrEnum


class DescriptionLanguages(StrEnum):
    NL = "nl"
    EN = "en"


class ArtObject:
    def __init__(
        self,
        id: str,
        webImage: str | None,
        longTitle: str,
        principalOrFirstMaker: str,
    ):
        self.id = id
        self.webImage = webImage
        self.longTitle = longTitle
        self.principalOrFirstMaker = principalOrFirstMaker

    def __repr__(self):
        return (
            f"ArtObject(id={self.id}, webImage={self.webImage}, "
            f"longTitle={self.longTitle}, principalOrFirstMaker={self.principalOrFirstMaker})"
        )


class Client:
    def __init__(self, language: DescriptionLanguages, api_key: str):
        self.url = f"https://www.rijksmuseum.nl/api/{language}/collection?key={api_key}&imgonly=True"

    def get_image_objects(self, amount_of_objects: int = 10_000) -> list[ArtObject]:
        """Function used to retrieve the first 10_000 objects from the Rijksmuseum API.
        The ps query parameter is used to set number of results per page, with a max of 100. The p query parameter is for navigating to the next page.
        Note that p * ps cannot exceed 10,000.
        Parameters
        ----------
        amount_of_objects : int, optional
            Number of objects to be retrieved by the API, by default 10_000

        Returns
        -------
        List[ArtObject]
            A list of ArtObjects containing the ID, image url, title and artist of the object
        """

        all_results = []
        ps = 100  # Number of results per page
        p = 1  # Page index
        total_retrieved = 0
        limit = amount_of_objects  # The maximum number of results to retrieve

        while total_retrieved < limit:
            # Calculate the max ps to ensure p * ps <= 10,000
            max_ps_for_current_page = 10000 // p
            if ps > max_ps_for_current_page:
                ps = max_ps_for_current_page

            params = {"ps": ps, "p": p}
            response = httpx.get(self.url, params=params)
            if response.status_code != 200:
                print(f"Error fetching results: {response.status_code}")
                break

            data = response.json()
            results = data.get("artObjects", [])

            # Extract only the specified fields and construct an ArtObject
            for result in results:
                extracted_data = ArtObject(
                    id=result.get("id"),
                    webImage=result.get("webImage", {}).get("url"),
                    longTitle=result.get("longTitle"),
                    principalOrFirstMaker=result.get("principalOrFirstMaker"),
                )
                all_results.append(extracted_data)

            total_retrieved += len(results)

            if len(results) < ps:
                break

            p += 1
            if total_retrieved >= limit:
                break

        return all_results
