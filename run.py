#!/usr/bin/env python
"""The run script."""
import faulthandler
import builtins
import logging
import os

# qemu/amd64-on-arm stability guards for numpy/pandas-backed imports
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_CORETYPE", "Haswell")
os.environ.setdefault("MKL_DEBUG_CPU_TYPE", "5")

# pyarrow can segfault under qemu (amd64 emulation on arm64) during pandas import.
# Force pandas to treat pyarrow as unavailable and use the standard numpy backend.
_original_import = builtins.__import__


def _import_without_pyarrow(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "pyarrow" or name.startswith("pyarrow."):
        raise ImportError("pyarrow disabled for qemu compatibility")
    return _original_import(name, globals, locals, fromlist, level)


builtins.__import__ = _import_without_pyarrow

# import flywheel functions
from flywheel_gear_toolkit import GearToolkitContext

# from utils.parseOutput import parseOutput

# The gear is split up into 2 main components. The run.py file which is executed
# when the container runs. The run.py file then imports the rest of the gear as a
# module.

log = logging.getLogger(__name__)

def main(context: GearToolkitContext) -> None:
    """Parses config and runs."""
    from utils.parser import parse_config
    from utils.command_line import exec_command

    input_path, age, demographics = parse_config(context)
    
    print("running main.sh...")
    # Run via bash so execute bit is not required and bash syntax is supported
    command = f"bash /flywheel/v0/app/main.sh {input_path}"
    # Execute the command
    exec_command(command, shell=True, cont_output=True)

    # Run housekeeping
    from utils.join_data import housekeeping

    print("running housekeeping...")
    housekeeping(demographics)

    # Run Segmentation QC
    from utils.Inspect_segmentations import SegQC

    print("running segmentation QC...")
    subject_label = demographics['subject'].values[0]
    SegQC(input_path, subject_label)

# Only execute if file is run as main, not when imported by another module
if __name__ == "__main__":  # pragma: no cover
    faulthandler.enable()

    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gear_context:

        # Initialize logging, set logging level based on `debug` configuration
        # key in gear config.
        gear_context.init_logging()

        # Pass the gear context into main function defined above.
        main(gear_context)