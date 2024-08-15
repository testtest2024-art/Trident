import argparse
import os
from datetime import datetime
import sys

from core.common.log import LOGGER
from core.common import utils
from core.cmd.obj.testjob import TestJob

def main():
    try:
        parser = _generate_parser()
        args = parser.parse_args()
        config_file = args.config_file
        if not utils.is_local_file(config_file):
            raise SystemExit(f"not found config({config_file}) file in local")
        config = utils.yaml2dict(args.config_file)
        print(config)
        job = TestJob(config)
        job.run()
        LOGGER.info("test job runs successfully.")
    except Exception as e:
        raise RuntimeError(f"test job runs failed, error: {e}.") from e


def _generate_parser():
    parser = argparse.ArgumentParser(description='Run Android automatic test tasks')

    parser.add_argument("-f",
                        "--config_file",
                        type=str,
                        help="run a test job, "
                            "and the config file must be yaml/yml file.")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser


if __name__ == '__main__':
    main()