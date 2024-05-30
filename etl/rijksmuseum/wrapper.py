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

    # TODO: Implement saving to a sqlite file
    def _save_objects_to_sqlite(self):
        pass

    # TODO: Implement this
    def _get_objects_with_known_artist(self):
        artists = [
            "George Hendrik Breitner",
            "Jan Luyken",
            "Ed van der Elsken",
            "Reinier Vinkeles (I)",
            "Marius Bauer",
            "Isaac Israels",
            "Johannes Tavenraat",
            "Daniel Nikolaus Chodowiecki",
            "Willem Witsen",
            "Aat Veldhoen",
            "Vincent Samuel Mentzel",
            "anoniem (Monumentenzorg)",
            "Bernard Picart",
            "Antonio Tempesta",
            "Carel Adolph Lion Cachet",
            "unknown",
            "Rembrandt van Rijn",
            "Simon Fokke",
            "Jacob Houbraken",
            "Romeyn de Hooghe",
            "Philips Galle",
            "Meissener Porzellan Manufaktur",
            "Richard Nicolaüs Roland Holst",
            "Jozef Israëls",
            "Jacques de Gheyn (II)",
            "Johan Michaël Schmidt Crans",
            "Willem Diepraam",
            "Jan Veth",
            "Crispijn van de Passe (I)",
            "Wenceslaus Hollar",
            "Frans Hogenberg",
            "Caspar Luyken",
            "Stefano della Bella",
            "Michel Wolgemut",
            "Anton Mauve",
            "Hendrick Goltzius",
            "Virgilius Solis",
            "Johann Sadeler (I)",
            "Adriaen Collaert",
            "Reinier Willem Petrus de Vries (1874-1953)",
            "Jacques Callot",
            "Jeanne Bieruma Oosting",
            "Leo Gestel",
            "Cornelis Vreedenburgh",
            "Gerrit Willem Dijsselhof",
            "Jan van de Velde (II)",
            "Pieter Schenk (I)",
            "veuve Delpech (Naudet)",
            "Christoffel van Sichem (II)",
            "Anselmus Boëtius de Boodt",
            "Carel Nicolaas Storm van 's-Gravesande",
            "Willem Cornelis Rip",
            "Johannes of Lucas van Doetechum",
            "Theo van Hoytema",
            "Reijer Stolk",
            "Israël Silvestre",
            "Eva Charlotte Pennink-Boelen",
            "Jan Caspar Philips",
            "Hendrik Spilman",
            "Charles Donker",
            "Simon Frisius",
            "Claude Mellan",
            "Crispijn van de Passe (II)",
            "Giorgio Sommer",
            "Abraham Rademaker",
            "Hieronymus Wierix",
            "Jean Lepautre",
            "Giovanni Battista Piranesi",
            "Manufactuur Oud-Loosdrecht",
            "Delizy",
            "Albert Greiner",
            "Carel Christiaan Antony Last",
            "Anthonie van den Bos",
            "Antoon Derkinderen",
            "Jan Punt",
            "Johannes Wierix",
            "Isaac Weissenbruch",
            "Claes Jansz. Visscher (II)",
            "August Allebé",
            "Jacob Matham",
            "Johan Braakensiek",
            "Johannes Immerzeel",
            "Carel Willink",
            "Maria Vos",
            "Lodewijk Schelfhout",
            "Aegidius Sadeler (II)",
            "Joseph Maes",
            "Cornelis Galle (I)",
            "Bernard Willem Wierink",
            "Jacob Folkema",
            "Adrianus Eversen",
            "Johannes Josephus Aarts",
            "Philip Zilcken",
            "Andries Jager",
            "Nicolaes de Bruyn",
            "Woodbury & Page",
            "Neue Photographische Gesellschaft",
            "Gustav Schnitzler",
            "William England",
        ]

    # TODO: Implement this
    def _get_objects_with_unknown_artist(self):
        artist = "anonymous"
        object_types = [
            "print",
            "photograph",
            "photomechanical print",
            "drawing",
            "stereograph",
            "carte-de-visite",
            "jeton",
            "fragment",
            "plate (dishes)",
            "cabinet photograph",
            "history medal",
            "furniture",
            "bowl",
            "tile",
            "medal",
            "coin",
            "sculpture",
            "text sheet",
            "lid",
            "tissue stereograph",
            "vase",
            "frame",
            "magazine",
            "Indian miniature",
            "painting",
            "light (window)",
            "figure",
            "pot",
            "ship model",
            "siege coin",
            "demonstration model",
            "box",
            "dish",
            "miniature",
            "chandelier",
            "half model",
            "musical instrument",
            "goblet",
            "builder's model",
            "jewellery",
            "manuscript",
            "decorated paper",
            "marbled paper",
            "brocade paper",
            "service (set)",
            "candlestick",
            "cup",
            "ribbon (material)",
            "chest",
            "brooch",
            "spoon",
            "copy",
            "collage (visual work)",
            "miniature (painting)",
            "pipe",
            "table",
            "percussion instrument",
            "button",
            "document",
            "textile materials",
            "scrapbook",
            "award medal",
            "handkerchief",
            "photomontage",
            "cloth",
            "Oriental rug",
            "scarf",
            "book",
            "sample",
            "tile tableau",
            "comb",
            "wind instrument",
            "poem",
            "relief (sculpture)",
            "flintlock pistol",
            "tureen",
            "case",
            "hat",
            "fully rigged model",
            "locket",
            "toy",
            "pendant (jewelry)",
            "monetary tokens",
            "scale model",
            "playing card",
            "sword",
            "drinking glass",
            "part",
            "paste paper",
            "Persian miniature",
            "drum",
            "show model",
            "floor tile",
            "gameboard",
            "elements (of musical instruments)",
            "letter",
            "sabre",
            "salt (condiment vessel)",
            "lock",
            "mule (shoe)",
        ]

    # TODO: See if it makes sense to make this async to improve performance
    def get_initial_10_000_objects(
        self,
    ) -> list[ArtObject]:
        """Function used to retrieve the first 10_000 objects from the Rijksmuseum API.
        The ps query parameter is used to set number of results per page, with a max of 100. The p query parameter is for navigating to the next page.
        Note that p * ps cannot exceed 10,000.

        Returns
        -------
        List[ArtObject]
            A list of ArtObjects containing the ID, image url, title and artist of the object
        """

        all_results = []
        ps = 100  # Number of results per page. Cannot exceed 100
        p = 1  # Page index
        total_retrieved = 0
        limit = 10_000

        while total_retrieved < limit:
            print(
                f"Fetching {ps} objects on page {p} - total fetched so far: {total_retrieved}"
            )
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

            p += 1
            if total_retrieved >= limit:
                break

        return all_results

    def get_all_objects_with_image(self):
        objects_with_known_artist = self._get_objects_with_known_artist()
        objects_with_unknown_artist = self._get_objects_with_unknown_artist()
