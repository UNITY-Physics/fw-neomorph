import flywheel
import json
import pandas as pd
from datetime import datetime
import re
import os
import shutil

import logging


log = logging.getLogger(__name__)

#  Module to identify the correct template use for the subject VBM analysis based on age at scan
#  Need to get subject identifiers from inside running container in order to find the correct template from the SDK

    # -------------------  Concatenate the data  -------------------  #

def housekeeping(demographics):

    acq = demographics['acquisition'].values[0]
    sub = demographics['subject'].values[0]

    filePath = '/flywheel/v0/work/All_volumes.csv'
    volumes = pd.read_csv(filePath, sep='\s+', engine='python') #index_col=False,
    df = pd.concat([demographics.reset_index(drop=True), volumes.reset_index(drop=True)], axis=1)
    out_name = f"{acq}_volumes.csv"
    outdir = ('/flywheel/v0/output/' + out_name)
    df.to_csv(outdir, index=False)

    seg_file = '/flywheel/v0/work/Final_segmentation_atlas.nii.gz'
    new_seg_file = '/flywheel/v0/output/' + acq + '_segmentation.nii.gz'
    try:
        shutil.copy(seg_file, new_seg_file)
        log.info(f"Copied segmentation file to {new_seg_file}")
    except FileNotFoundError:
        log.warning(f"Segmentation file not found: {seg_file}")

    QC_montage = '/flywheel/v0/work/montage_final_segmentation_atlas.png'
    new_QC_montage = '/flywheel/v0/output/' + acq + '_QC-montage.png'
    try:
        shutil.copy(QC_montage, new_QC_montage)
        log.info(f"Copied QC montage to {new_QC_montage}")
    except FileNotFoundError:
        log.warning(f"QC montage file not found: {QC_montage}")