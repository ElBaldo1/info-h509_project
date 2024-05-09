## api file where should we take the data from

import re
from datetime import datetime
from functools import lru_cache
from typing import Literal, Union

import bs4
import pydantic
import requests

RAW_HEADER = """Host: www.belgiantrain.be
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Pragma: no-cache
Cache-Control: no-cache
TE: trailers"""


FIXED_CARRIAGE_SIZE = 18.4
FACILITIES_CLASS = "train-details-visual__facilities"
TRAIN_FACILITIES_CLASS = "train-details-facilities"

SOURCE_URL = (
    "https://www.belgiantrain.be/api/routeplanner/GetTrainComposition/?from={FROM_ID}&to={TO_ID}&trainNumber={"
    "TRAIN_NUMBER}&depDateTime={DEPARTURE_TIME}&hasdeparted=False&occupancyLevel=1"
)


class Carriage(pydantic.BaseModel):
    carriage_type: str
    model: str
    classes: list[int]
    facilities: list[Literal["accessible_toilet", "toilet", "bike"]]
    carriage_size: float


class Train(pydantic.BaseModel):
    facilities: list[Literal["airconditioning", "heating"]]
    occupancy: Literal["low", "medium", "high"]
    carriages_count: int
    carriages: list[Carriage]


@lru_cache(maxsize=1)
def make_session():
    session = requests.Session()
    session.headers = {
        header.split(": ")[0]: header.split(": ")[1]
        for header in RAW_HEADER.split("\n")
    }

    return session


def parse_carriage(li: bs4.Tag) -> Carriage:
    classes = list(map(int, re.findall("<span>([1-2])</span>", str(li))))
    # carriage type is the class of the li
    carriage_type = "_".join(li["class"])
    model = li["title"]
    # Faciltieis can be extracted from the child div with the facilities class
    # then each svg possesses a title child with the facility name
    facilities = [
        svg.find("title").text
        for svg in li.find("div", class_=FACILITIES_CLASS).find_all("svg")
    ]
    # Replace spaces with underscores
    facilities = [facility.replace(" ", "_") for facility in facilities]

    carriage_size = FIXED_CARRIAGE_SIZE  # meters

    return Carriage(
        carriage_type=carriage_type,
        model=model,
        classes=classes,
        facilities=facilities,
        carriage_size=carriage_size,
    )


def parse_carriages(soup: bs4.BeautifulSoup) -> list[Carriage]:
    return [parse_carriage(li) for li in soup.find("ol").find_all("li")]


def parse_train_composition(
    soup: bs4.BeautifulSoup, carriages: list[Carriage]
) -> Train:
    # Get the train facilities
    ul_container = soup.find("ul", class_=TRAIN_FACILITIES_CLASS)
    air_conditioning = ul_container.find("li", title="Airconditioning") is not None
    heating = ul_container.find("li", title="Heating") is not None
    # occupancy can be extracted occupancy-row-title-32
    occupancy = (
        ul_container.find("div", class_="occupancy-row-title-32")
        .text.replace("Expected occupancy: ", "")
        .lower()
    )

    train_facilities = []
    if air_conditioning:
        train_facilities.append("airconditioning")

    if heating:
        train_facilities.append("heating")

    return Train(
        facilities=train_facilities,
        occupancy=occupancy,
        carriages_count=len(carriages),
        carriages=carriages,
    )


def parse_sncb_html_compositions(html_data: str) -> Train:
    soup = bs4.BeautifulSoup(html_data, "html.parser")

    carriages = parse_carriages(soup)

    return parse_train_composition(soup, carriages)


def get_train_composition(
    from_id: str, to_id: str, train_number: str, departure_time: datetime
) -> Union[Train, None]:
    """
    Get the train composition from the SNCB website
    :param from_id: The station id of the departure station
    :param to_id: The station id of the arrival station
    :param train_number: The SNCB train number
    :param departure_time: The departure time of the train
    :return: The train composition, or None if an error occured

    >>> get_train_composition("008814001", "008814008", "IC", datetime(2024, 4, 24, 12, 15))
    """
    # Remove leading zeros
    from_id = from_id.lstrip("0")
    to_id = to_id.lstrip("0")

    response = make_session().get(
        SOURCE_URL.format(
            FROM_ID=from_id,
            TO_ID=to_id,
            TRAIN_NUMBER=train_number,
            DEPARTURE_TIME=departure_time.strftime("%m/%d/%Y %H:%M:%S"),
        )
    )
    response.raise_for_status()

    try:
        return parse_sncb_html_compositions(response.text)
    except AttributeError:
        return None


if __name__ == "__main__":
    get_train_composition("008814001", "008814008", "IC", datetime(2022, 1, 1, 12, 0))
