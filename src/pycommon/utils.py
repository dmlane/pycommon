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
    "Struct",
)


# noinspection SpellCheckingInspection
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


def touch(file_name, timestamp=None):
    """Creates a file if it doesn't exist and touches it with the given timestamp.
    Timestamp can be a datetime.timedelta or datetime.datetime object
    """
    with open(file_name, "a", encoding="utf-8") as handle:
        if timestamp is not None:
            if isinstance(timestamp, datetime.timedelta):
                new_time = datetime.datetime.utcnow() - timestamp
            elif isinstance(timestamp, datetime.datetime):
                new_time = timestamp
            else:
                raise ValueError(f"Invalid type for timestamp: {type(timestamp)}")
            epoch_seconds = (new_time - datetime.datetime(1970, 1, 1)).total_seconds()
            os.utime(handle.fileno(), (epoch_seconds, epoch_seconds))


def dict_merge(dct, merge_dct):
    """Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for key, _ in merge_dct.items():
        if key in dct and isinstance(dct[key], dict) and isinstance(merge_dct[key], dict):  # noqa
            dict_merge(dct[key], merge_dct[key])
        else:
            dct[key] = merge_dct[key]


class Struct:  # pylint: disable=too-few-public-methods
    """Lets you convert from a dictionary to a struct."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                self.__dict__[key] = Struct(**value)
            else:
                self.__dict__[key] = value

    def __repr__(self):
        return self.__recursive_repr(0, self)

    def __recursive_repr(self, indent, param):
        result = ""
        for attr in dir(param):
            if callable(getattr(param, attr)) or attr.startswith("__") or attr == "self":
                continue
            if isinstance(getattr(param, attr), Struct):
                result = (
                    result
                    + " " * indent
                    + attr
                    + "\n"
                    + self.__recursive_repr(indent + 2, getattr(param, attr))
                )
            else:
                result = result + " " * indent + attr + "=" + str(getattr(param, attr)) + "\n"
        return result
