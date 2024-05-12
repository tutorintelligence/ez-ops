from abc import ABC, abstractmethod
from typing import (
    Generic,
    Iterator,
    Type,
    TypeVar,
)

from ez_ops.ez_parser.parser_node import ParserNode
from ez_ops.ez_parser.parser_tree import ArgParserTree

ParentNode = ParserNode | str


ArgParseHandlerT = TypeVar("ArgParseHandlerT", bound="ArgParseHandlerBase")


class ArgParseHandlerBase(Generic[ArgParseHandlerT], ABC):
    """
    For every derived ArgParseHandler, you will need to define the following variables:
     - cmd -> the command used to activate the parser
     - help -> the help message
     - children -> children ArgParseHandlers

    You can also optionally define the following function:
     - set_args() -> define what args you'll need
    """

    @property
    @abstractmethod
    def cmd(self) -> str:
        pass

    @property
    @abstractmethod
    def help(self) -> str:
        pass

    @property
    @abstractmethod
    def children(self) -> Iterator[Type[ArgParseHandlerT]]:
        pass

    def __init__(self, arg_tree: ArgParserTree, parent: ParentNode | None):
        self.arg_tree = arg_tree
        self.parent = parent
        self.node = self.arg_tree.add_node(
            self.cmd, parent_node=self.parent, help=self.help
        )
        self.set_args(self.node)

    @classmethod
    def start_tree(cls) -> ArgParseHandlerT:
        tree = ArgParserTree()
        parser_handler_orig = cls(tree, None)
        parser_handler_orig.arg_tree.tip_tree = parser_handler_orig.node
        return parser_handler_orig

    def spawn(self) -> None:
        for child in self.children:
            child(self.arg_tree, self.node).spawn()

    def set_args(self, node: ParserNode) -> None:
        """
        OPTIONAL

        Define any arguments you want for the given command.
         - set_..._arg() sets a specific argument
         - set_func() sets the function to run
        """

        pass