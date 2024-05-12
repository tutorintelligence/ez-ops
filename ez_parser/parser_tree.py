from argparse import Namespace
from typing import (
    Callable,
    Final,
    Tuple,
)

from anytree.search import PreOrderIter, findall_by_attr
from ez_parser.parser_node import ParserNode

ParentNode = ParserNode | str


class ArgParserTree:

    ANCESTOR_NODE: Final[str] = "tip"

    tip_tree: ParserNode

    def find_all_nodes_with_name(self, node_name: str) -> Tuple[ParserNode, ...]:
        all_nodes = findall_by_attr(self.tip_tree, name="full_name", value=node_name)
        if len(all_nodes) < 1:
            raise LookupError(f"Cannot find the node {node_name}")
        return all_nodes

    def find_parser(self, node_name: str) -> ParserNode:
        all_nodes = self.find_all_nodes_with_name(node_name=node_name)
        assert len(all_nodes) == 1, f"Too many nodes of name {node_name}"
        return all_nodes[0]

    def add_node(
        self,
        node_cmd: str,
        parent_node: ParentNode | None = None,
        help: str | None = None,
        func: Callable | None = None,
    ) -> ParserNode:
        if parent_node is not None:
            if isinstance(parent_node, str):
                parent_node = self.find_parser(parent_node)
            try:
                self.find_all_nodes_with_name(node_cmd)
                raise NameError("Cannot use node names more than once")
            except LookupError:
                pass

        return ParserNode(cmd=node_cmd, parent=parent_node, help=help, func=func)

    def add_parser_node(
        self,
        parser_name: str,
        parent_parser: str | ParserNode,
        help: str | None = None,
        func: Callable | None = None,
    ) -> ParserNode:
        if isinstance(parent_parser, str):
            parent_parser = self.find_parser(parent_parser)
        return self.add_node(parser_name, parent_parser, help=help, func=func)

    def parse_args(self) -> Namespace:
        for node in PreOrderIter(self.tip_tree):
            node.update_viz()
        args = self.tip_tree.parser.parse_args()
        for node in PreOrderIter(self.tip_tree):
            node.update_args(args)
        return args

    def run(self) -> None:
        self.tip_tree.run()



def main() -> None:
    tip_arg_tree = ArgParserTree()
    hello = tip_arg_tree.add_parser_node("hello", "tip")
    hi = tip_arg_tree.add_parser_node("hi", "tip")
    blah = tip_arg_tree.add_parser_node("blah", "tip")
    bellop = tip_arg_tree.add_parser_node("bellop", hi)
    gorilla = tip_arg_tree.add_parser_node("gorilla", "tip")
    gghaa = tip_arg_tree.add_parser_node(
        "gghaa",
        bellop,
        "This is the gghaa node!",
        func=lambda args: print(10 * f"{args.robot} "),
    )
    gghaa.add_positional_arg("robot", help="Hurrah")
    tip_arg_tree.find_parser("tip").add_bool_argument(True, "hello", help="Hi!")
    gghaa.set_func(func=lambda args: print(30 * f"{args.robot} "))

    args = tip_arg_tree.parse_args()
    print("=" * 10, tip_arg_tree.tip_tree.arg_dict)

    args.func(args)


if __name__ == "__main__":
    main()
