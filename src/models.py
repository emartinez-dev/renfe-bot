from datetime import datetime

from pydantic import BaseModel, Field

class StationRecord(BaseModel):
    """Represents a Station, using Renfe's data definition. It can be seen at the file
    assets/station.json"""

    name: str = Field(description="Station name")
    code: str = Field(description="Renfe code for this station")

class TrainRideRecord(BaseModel):
    """Represents a Train ride."""

    origin: str = Field(description="Origin station name")
    destination: str = Field(description="Destination station name")

    departure_time: datetime = Field(description="Departure date and time")
    arrival_time: datetime = Field(description="Estimated arrival date and time")
    duration: int = Field(description="Train ride duration in minutes")

    price: float = Field(description="Train ride price in euros")
    available: bool = Field(description="If the train ride is available for buying a ticket")

    train_type: str = Field(description="Train type")

    def __str__(self):
        date_format = "%d/%m/%Y %H:%M"
        availability = "Available" if self.available else "Not Available"
        hours, minutes = divmod(self.duration, 60)
        duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        return (
            f"<TrainRideRecord(train_type={self.train_type}, origin={self.origin}, "
            f"destination={self.destination}, departure_time="
            f"{self.departure_time.strftime(date_format)}, arrival_time="
            f"{self.arrival_time.strftime(date_format)}, duration={duration_str}, "
            f"price={self.price:.2f} €, availability={availability})>"
        )