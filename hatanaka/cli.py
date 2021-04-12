import argparse
import sys
import warnings
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional

from hatanaka import __version__, compress, compress_on_disk, decompress, decompress_on_disk, \
    rnxcmp_version

__all__ = ['decompress_cli', 'compress_cli']


def decompress_cli(args: Optional[List[str]] = None) -> int:
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description='Decompress compressed RINEX files.',
        epilog='This program will decompress any RINEX files compressed with Hatanaka compression'
               '(.crx|.##d) and/or with a conventional compression format (.gz|.Z|.zip|.bz2) to '
               'their plain RINEX counterpart. Already decompressed files are ignored. '
               'Exit codes: 0 - success, 1 - error, 2 - warning.'
    )
    parser.add_argument('files', type=Path, nargs='*',
                        help='Compressed RINEX files. '
                             'stdin and stdout are used if no input files are provided.')
    parser.add_argument(
        '-s', '--skip-strange-epochs', action='store_true',
        help='This option may be used for salvaging usable data when middle of the'
             'Compact RINEX file is missing. The data after the missing part, are, however, '
             'useless until the compression operation of all data are initialized at some epoch. '
             'Combination with use of -e option of RNX2CRX may be effective.\n'
             'Caution: It is assumed that no change in the list of data types '
             'happens in the lost part of the data.')
    _add_common_args(parser)
    args = parser.parse_args(args)
    return _run(decompress, decompress_on_disk, args, skip_strange_epochs=args.skip_strange_epochs)


def compress_cli(args: Optional[List[str]] = None) -> int:
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description='Compress RINEX files.',
        epilog='This program applies Hatanaka and optionally a conventional '
               'compression (gzip by default) to any provided RINEX files. '
               'Already compressed files are ignored. '
               'Exit codes: 0 - success, 1 - error, 2 - warning.'
    )
    parser.add_argument('files', type=Path, nargs='*',
                        help='RINEX files. '
                             'stdin and stdout are used if no input files are provided.')
    parser.add_argument('-c', '--compression', default='gz', choices=['gz', 'bz2', 'none'],
                        help='which compression to apply in addition to Hatanaka compression '
                             '(default: gz)')
    parser.add_argument(
        '-s', '--skip-strange-epochs', action='store_true',
        help='warn and skip strange epochs instead of raising an exception')
    parser.add_argument(
        '-e', '--reinit-every-nth', type=int, metavar='#',
        help='Initialize the compression operation at every # epochs. '
             'When some part of the Compact RINEX file is lost, the data can not be recovered '
             'thereafter until all the data arc are initialized for differential operation. '
             'This option may be used to increase chances to recover parts of data by using '
             'the --skip-strange-epochs option of rinex-decompress at the cost of '
             'increasing the file size.')
    _add_common_args(parser)
    args = parser.parse_args(args)
    return _run(compress, compress_on_disk, args,
                compression=args.compression,
                skip_strange_epochs=args.skip_strange_epochs,
                reinit_every_nth=args.reinit_every_nth)


def _run(func, func_on_disk, args, **kwargs):
    missing_files = [x for x in args.files if not x.exists()]
    if missing_files:
        for f in missing_files:
            print(f"Error: '{str(f)}' was not found", file=sys.stderr)
            exit(1)

    for in_file in args.files:
        with _record_warnings() as warning_list:
            out_file = func_on_disk(in_file, **kwargs)
        if out_file == in_file:
            print(f'{str(in_file)} is already {func.__name__}ed')
        else:
            print(f'Created {str(out_file)}')
        assert out_file.exists()
        if args.delete:
            if len(warning_list) == 0 and in_file != out_file:
                in_file.unlink()
                print(f'Deleted {str(in_file)}')

    if len(args.files) == 0:
        with _record_warnings() as warning_list:
            converted = func(sys.stdin.buffer.read(), **kwargs)
            sys.stdout.buffer.write(converted)

    if len(warning_list) > 0:
        return 2
    return 0


def _add_common_args(parser):
    parser.add_argument('-d', '--delete', action='store_true',
                        help='delete the input file if conversion '
                             'finishes without any errors and warnings')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--rnxcmp-version', action='version', version=rnxcmp_version)


@contextmanager
def _record_warnings():
    with warnings.catch_warnings(record=True) as warning_list:
        yield warning_list
    for w in warning_list:
        warnings.showwarning(message=w.message, category=w.category, filename=w.filename,
                             lineno=w.lineno, file=w.file, line=w.line)
