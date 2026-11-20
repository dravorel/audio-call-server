from dataclasses import dataclass, asdict


@dataclass
class AudioChunk:
    index: int
    user_id: str
    timestamp: float
    duration: float
    codec: str
    sample_rate: int
    channels: int
    data: bytes

    def metadata(self) -> dict:
        return {k: v for k, v in asdict(self).items() if k != "data"}
