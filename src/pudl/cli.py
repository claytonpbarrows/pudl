"""A command line interface (CLI) to the main PUDL ETL functionality.

This script generates datapacakges based on the datapackage settings enumerated
in the settings_file which is given as an argument to this script. If the
settings has empty datapackage parameters (meaning there are no years or
tables included), no datapacakges will be generated. If the settings include a
datapackage that has empty parameters, the other valid datatpackages will be
generated, but not the empty one. If there are invalid parameters (meaning a
year that is not included in the pudl.constant.working_years), the build will
fail early on in the process.

The datapackages will be stored in "PUDL_OUT" in the "datapackge" subdirectory.
Currently, this function only uses default directories for "PUDL_IN" and
"PUDL_OUT" (meaning those stored in $HOME/.pudl.yml). To setup your default
pudl directories see the pudl_setup script (pudl_setup --help for more details).
"""

import argparse
import logging
import pathlib
import sys

import coloredlogs
import yaml

import pudl

logger = logging.getLogger(__name__)


def parse_command_line(argv):
    """
    Parse script command line arguments. See the -h option.

    Args:
        argv (list): command line arguments including caller file name.

    Returns:
        dict: A dictionary mapping command line arguments to their values.

    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        dest='settings_file',
        type=str,
        default='',
        help="path to YAML datapackage settings file.")
    parser.add_argument(
        '-c',
        '--clobber',
        action='store_true',
        help="""Clobber existing datapackages if they exist. If clobber is not
        included but the datapackage bundle directory already exists the _build
        will fail. Either the pkg_bundle_name in the settings_file needs to be
        unique or you need to include --clobber""",
        default=False)
    arguments = parser.parse_args(argv[1:])
    return arguments


def main():
    """Parse command line and initialize PUDL DB."""
    # Display logged output from the PUDL package:
    logger = logging.getLogger(pudl.__name__)
    log_format = '%(asctime)s [%(levelname)8s] %(name)s:%(lineno)s %(message)s'
    coloredlogs.install(fmt=log_format, level='INFO', logger=logger)

    args = parse_command_line(sys.argv)
    with pathlib.Path(args.settings_file).open() as f:
        script_settings = yaml.safe_load(f)

    try:
        pudl_in = script_settings["pudl_in"]
    except KeyError:
        pudl_in = pudl.workspace.setup.get_defaults()["pudl_in"]
    try:
        pudl_out = script_settings["pudl_out"]
    except KeyError:
        pudl_out = pudl.workspace.setup.get_defaults()["pudl_out"]

    pudl_settings = pudl.workspace.setup.derive_paths(
        pudl_in=pudl_in, pudl_out=pudl_out)

    logger.info('verifying that the data we need exists in the data store')
    flattened_params_dict = pudl.etl.get_flattened_etl_parameters(
        script_settings['pkg_bundle_settings'])
    pudl.helpers.verify_input_files(flattened_params_dict['ferc1_years'],
                                    flattened_params_dict['eia923_years'],
                                    flattened_params_dict['eia860_years'],
                                    flattened_params_dict['epacems_years'],
                                    flattened_params_dict['epacems_states'],
                                    pudl_settings)

    pudl.etl.generate_data_packages(
        script_settings['pkg_bundle_settings'],
        pudl_settings,
        debug=False,
        pkg_bundle_name=script_settings['pkg_bundle_name'],
        clobber=args.clobber)


if __name__ == "__main__":
    sys.exit(main())
