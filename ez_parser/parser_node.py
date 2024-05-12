import argparse
from argparse import ArgumentParser, Namespace, _SubParsersAction
from functools import cached_property
from typing import IO, Any, Callable, Dict, Iterable, List, Optional, Tuple, Type

from anytree import AsciiStyle, NodeMixin, RenderTree


class DerivedArgumentParser(ArgumentParser):
    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        self.parser_tree = kwargs.pop("parser_tree")
        super().__init__(*args, **kwargs)

    def print_help(self, file: IO[str] | None = None) -> None:
        super().print_help(file)
        print("", end="")
        print("\nTip Argument Parser Tree\n")
        print(self.parser_tree)
        print("")


class ParserNodeBase:
    arg_dict: Dict[str, Any] = dict()
    updated: bool = False

    def __init__(
        self,
        cmd: str,
        parser_tree: str,
        parent_subparser: _SubParsersAction | None,
        help: str,
        func: Callable | None = None,
    ) -> None:
        self.cmd = cmd

        if parent_subparser is None:
            self.parser = DerivedArgumentParser(
                parser_tree=parser_tree, prog=cmd, description=help
            )
        else:
            self.parser: DerivedArgumentParser = parent_subparser.add_parser(
                parser_tree=parser_tree,
                name=cmd,
                help=help,
                description=help,
            )

        if func is None:
            func = lambda: self.parser.print_help()  # noqa: E731
        self.set_func(func=func)

    def __getitem__(self, item: str) -> Any:
        arg_val = self.arg_dict[item.replace("-", "")]
        assert (
            arg_val != NotImplemented
        ), "Parser node must be updated before variable extraction. Something is very wrong."
        return arg_val

    @cached_property
    def subparser(self) -> _SubParsersAction:
        return self.parser.add_subparsers(title=self.cmd + "_subcommands")

    def _check_cmd_args(
        self,
        positional_arg: str | None = None,
        long_optional_arg: str | None = None,
        short_optional_arg: str | None = None,
        dest: str | None = None,
    ) -> Tuple[str, Tuple[str, ...]]:
        assert (
            positional_arg or long_optional_arg or short_optional_arg
        ), "Must have at least one arg type"

        arg_ls: List[str] = list()
        if positional_arg is not None:
            assert (
                positional_arg.find("-") == -1
            ), "Cannot have dash in a positional arg"
            assert (
                long_optional_arg is None and short_optional_arg is None
            ), "Cannot have both a positional and optional arg"
            arg_ls.append(positional_arg)

        if long_optional_arg is not None:
            count = long_optional_arg.count("-")
            assert count == 2 or count == 0, "Must have 0 or 2 dashes."
            arg_ls.append("--" + long_optional_arg.replace("-", ""))

        if short_optional_arg is not None:
            assert short_optional_arg.count("-") < 2, "Must have fewer than 2 dashes"
            arg_ls.append("-" + short_optional_arg.replace("-", ""))

        var_name: str
        if dest is not None:
            var_name = dest
        elif len(arg_ls) == 1:
            var_name = arg_ls[0]
        elif len(arg_ls) == 2:
            var_name = long_optional_arg
        else:
            raise NotImplementedError(
                "There should be no cases where len(arg_ls) is greater than 2"
            )

        return var_name, tuple(arg_ls)

    def add_argument(
        self,
        positional_arg: str | None = None,
        long_optional_arg: str | None = None,
        short_optional_arg: str | None = None,
        help: str | None = None,
        action: str | None = None,
        type: Type | None = None,
        nargs: int | str | None = None,
        default: object = None,
        required: bool | None = None,
        choices: Iterable | None = None,
        dest: str | None = None,
    ) -> str:
        """
        This function returns the string corresponding to the arg name. It __DOES NOT__ return the arg itself!
        To get the arg value, use:
            my_var_name = parser_node.add_argument(...)
            ...
            parser_node[my_var_name]
        """

        assert help is not None, "Help string must be populated!"
        var_name, cmd_args_tup = self._check_cmd_args(
            positional_arg, long_optional_arg, short_optional_arg, dest
        )

        if type is not None:
            assert default is None or isinstance(
                default, type
            ), f"Default must be of type {type}"

        arg_dict = {
            "action": action,
            "type": type,
            "nargs": nargs,
            "default": default,
            "required": required,
            "choices": choices,
            "dest": dest,
        }

        self.parser.add_argument(
            *cmd_args_tup,
            help=help,
            **{key: val for key, val in arg_dict.items() if val is not None},
        )
        self.arg_dict[var_name.replace("-", "")] = NotImplemented
        return var_name

    def add_bool_argument(
        self,
        default: bool,
        long_optional_arg: str | None = None,
        short_optional_arg: str | None = None,
        dest: str | None = None,
        help: str | None = None,
    ) -> str:
        action = "store_false" if default else "store_true"
        return self.add_argument(
            long_optional_arg=long_optional_arg,
            short_optional_arg=short_optional_arg,
            action=action,
            required=False,
            dest=dest,
            help=help,
        )

    def add_positional_arg(
        self,
        positional_arg_name: str,
        choices: Iterable | None = None,
        type: Type | None = None,
        help: str | None = None,
    ) -> str:
        return self.add_argument(
            positional_arg=positional_arg_name, choices=choices, type=type, help=help
        )

    def add_single_optional_arg(
        self,
        long_optional_arg_name: str,
        help: str,
        type: Type = str,
        short_optional_arg_name: str | None = None,
        default: object = None,
    ) -> str:
        return self.add_argument(
            long_optional_arg=long_optional_arg_name,
            short_optional_arg=short_optional_arg_name,
            help=help,
            type=type,
            default=default,
        )

    def set_func(self, func: Callable) -> None:
        self.arg_dict["func"] = func
        self.parser.set_defaults(func=func)

    def run(self) -> None:
        self["func"]()


class ParserNode(ParserNodeBase, NodeMixin):
    def __init__(
        self,
        cmd: str,
        parent: Optional["ParserNode"],
        help: str,
        func: Callable,
    ) -> None:
        self.cmd = cmd
        self.full_name = cmd if parent is None else parent.full_name + "_" + cmd
        self.parent = parent
        super(ParserNode, self).__init__(
            cmd=cmd,
            parser_tree=self.viz(),
            parent_subparser=None if parent is None else parent.subparser,
            help=help,
            func=func,
        )

    def viz(self) -> str:
        return RenderTree(self, style=AsciiStyle()).by_attr(attrname="cmd")

    def update_viz(self) -> None:
        self.parser.parser_tree = self.viz()

    def update_args(self, args: Namespace) -> None:
        for key in self.arg_dict.keys():
            key = key.replace("-", "")
            self.arg_dict[key] = vars(args).get(key, None)
        self.updated = True
