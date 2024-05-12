from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Type, TypeVar

from ez_parser.parser_node import ParserNode

ArgAdderT = TypeVar("ArgAdderT", bound="ArgAdderBase")


@dataclass
class ArgAdderBase(Generic[ArgAdderT], ABC):
    _parser_node: ParserNode

    def __getitem__(self, item: str) -> Any:
        return self._parser_node[item]

    @classmethod
    @abstractmethod
    def add_to(
        cls: Type[ArgAdderT], parser_node: ParserNode, **kwargs: Any
    ) -> ArgAdderT:
        pass

    @property
    def parser_node(self) -> ParserNode:
        return self._parser_node
