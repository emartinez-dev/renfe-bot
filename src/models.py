from pydantic import BaseModel, Field

class StationRecord(BaseModel):
    """Represents a Station, using Renfe's data definition. It can be seen at the file
    assets/station.json"""

    name: str = Field(description="Station name")
    code: str = Field(description="Renfe code for this station")
