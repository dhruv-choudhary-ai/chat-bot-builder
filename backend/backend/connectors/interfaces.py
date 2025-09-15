from abc import ABC, abstractmethod
from typing import Generator, List

from backend.connectors.models import Document

SecondsSinceUnixEpoch = float
GenerateDocumentsOutput = Generator[List[Document], None, None]


class LoadConnector(ABC):
    @abstractmethod
    def load_from_state(self) -> GenerateDocumentsOutput:
        raise NotImplementedError


class PollConnector(ABC):
    @abstractmethod
    def poll_source(
        self, start: SecondsSinceUnixEpoch, end: SecondsSinceUnixEpoch
    ) -> GenerateDocumentsOutput:
        raise NotImplementedError
