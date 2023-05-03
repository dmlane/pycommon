""" Handles housekeeping tasks """

import datetime
import glob
import hashlib
import os
import time

import psutil

HOUSEKEEPING_FLAG = "/tmp/dml_housekeeping_%s.flag"
__all__ = (
    "dict_merge",
    "eject_dvd",
    "get_dvd_path",
    "housekeeping_cleanup",
    "touch",
)


def eject_dvd():
    """Eject dvd"""
    os.system("drutil eject")


def get_dvd_path():
    """Get volume name of mounted dvd"""
    result = None
    all_volumes = psutil.disk_partitions(all=False)
    for volume in all_volumes:
        if volume.fstype == "udf":
            result = volume.mountpoint
    return result


def housekeeping_cleanup(folder: str, file_pattern: str, max_age: int = 7):
    """Deletes files matching pattern in folder which are older than max_age days"""
    hash_flag = hashlib.md5((folder + file_pattern).encode()).hexdigest()
    flag = HOUSEKEEPING_FLAG % hash_flag
    # Prevent running too often
    if os.path.exists(flag):
        return
    cut_off = time.time() - (max_age * 24 * 60 * 60)
    for file in glob.glob(folder + "/" + file_pattern):
        if os.path.getmtime(file) < cut_off:
            os.remove(file)
    touch(flag)


def touch(fname, timestamp=None):
    """Creates a file if it doesn't exist and touches it with the given timestamp.
    Timestamp can be a datetime.timedelta or datetime.datetime object
    """
    with open(fname, "a", encoding="utf-8") as handle:
        if timestamp is not None:
            if isinstance(timestamp, datetime.timedelta):
                new_time = datetime.datetime.utcnow() - timestamp
            elif isinstance(timestamp, datetime.datetime):
                new_time = timestamp
            else:
                raise ValueError(f"Invalid type for timestamp: {type(timestamp)}")
            epoch_seconds = (new_time - datetime.datetime(1970, 1, 1)).total_seconds()
            os.utime(handle.fileno(), (epoch_seconds, epoch_seconds))


# touch("/tmp/dml_housekeeping.flag", datetime.timedelta(days=1))
# touch("/tmp/dml_housekeeping.flag2", datetime.datetime(2020, 1, 1, 12, 30, 0))
# touch("/tmp/dml_housekeeping.flag3")
# housekeeping_cleanup(
#     "ripdvd",
#     "/Users/dave/Library/Caches/net.dmlane/ripdvd",
#     file_pattern="*.pickle",
#     max_age=4,
# )
def dict_merge(dct, merge_dct):
    """Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], dict):  # noqa
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
