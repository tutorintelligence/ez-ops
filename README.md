# ez-ops
The ez-ops package provides a suite of utility functions for building a python DevOps platform from the ground up. This tooling may not be unique or state-of-the-art but it attempts to improve the efficiency of DevOps developers. The biggest component of this package, the `ez-parser` library, adds a much better API than the argparse library for interacting with large terminal applications that require many nested subcommands. See the [ez-parser section](#ez-parser) for more information.  

## ez-parser
This library is a simple wrapper around the Python Argparse library, especially useful for large, devops codebases with many command-tools. It tries to abstract away much of the argparse complexity, lack of typing, and repeated boilerplate code. It also adds visualization to help messages for users trying to navigate complex command-line tools.
