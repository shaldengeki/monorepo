import decimal
from dataclasses import dataclass


@dataclass
class TotalAmounts:
    steps: int
    active_minutes: int
    distance_km: decimal.Decimal

    def copy(self) -> "TotalAmounts":
        return TotalAmounts(
            steps=self.steps,
            active_minutes=self.active_minutes,
            distance_km=self.distance_km,
        )
