from __future__ import annotations

__all__ = ["run", "main"]
import os
import sys
import io
import argparse
from typing import Optional
from gada.program import Program
from gada import datadir


def split_unknown_args(argv: list[str]) -> tuple[list[str], list[str]]:
    """Separate known command-line arguments from unknown one.
    Unknown arguments are separated from known arguments by
    the special **--** argument.
    :param argv: command-line arguments
    :return: tuple (known_args, unknown_args)
    """
    for i in range(len(argv)):
        if argv[i] == "--":
            return argv[:i], argv[i + 1 :]

    return argv, []


def run(target: str, inputs: Optional[dict] = None) -> dict:
    """Run a Gada node or program.

    .. code-block:: python

        >>> import gada
        >>>
        >>> gada.run("max", {"a": 1, "b": 2})
        {'out': 2}
        >>>

    :param target: name of a node or path to a program
    :param inputs: inputs passed to the node or program
    :return: node or program outputs
    """
    # Load gada configuration
    gada_config = datadir.load_config()

    # Check command format
    if not target.endswith(".yml"):
        prog = Program.from_node(target)
    else:
        prog = Program.load(target)

    return prog.run(inputs=inputs)


def main(
    argv: Optional[list[str]] = None,
    *,
    stdin=None,
    stdout=None,
    stderr=None,
):
    """Gada main:

    .. code-block:: python

        >>> import gada
        >>>
        >>> # Overwrite "gada/test/testnodes/config.yml" for this test
        >>> gada.test_utils.write_testnodes_config({
        ...     'nodes': {
        ...         'echo': {
        ...             'runner': 'generic',
        ...             'bin': 'echo'
        ...         }
        ...     }
        ... })
        >>>
        >>> # Need to create fake stdin and stdout for unittests
        >>> with gada.test_utils.PipeStream() as stdin:
        ...     with gada.test_utils.PipeStream() as stdout:
        ...         # Run node with CLI arguments
        ...         gada.main(
        ...             ['gada', 'testnodes.echo', 'hello'],
        ...             stdin=stdin.reader,
        ...             stdout=stdout.writer,
        ...             stderr=stdout.writer
        ...         )
        ...
        ...         # Close writer end so we can read form it
        ...         stdout.writer.close()
        ...
        ...         # Read node output
        ...         stdout.reader.read().decode().strip()
        'hello'
        >>>

    The three parameters ``stdin``, ``stdout`` or ``stderr`` are provided as a convenience
    for writing unit tests when you can't use ``sys.stdin`` or ``sys.stdout``, or simply
    when you want to be able to read from the output.

    :param argv: command line arguments
    :param stdin: input stream
    :param stdout: output stream
    :param stderr: error stream
    """
    argv = sys.argv if argv is None else argv

    parser = argparse.ArgumentParser(prog="gada", description="Help")
    parser.add_argument("target", type=str, help="target to run")
    parser.add_argument(
        "argv", type=str, nargs=argparse.REMAINDER, help="additional CLI arguments"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbosity level")
    args = parser.parse_args(args=argv[1:])
    node_argv, gada_argv = split_unknown_args(args.argv)

    run(target=args.target, argv=node_argv, stdin=stdin, stdout=stdout, stderr=stderr)


if __name__ == "__main__":
    main(sys.argv)
