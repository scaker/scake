# -*- coding: utf-8 -*-
import os

from omegaconf.dictconfig import DictConfig
from omegaconf.listconfig import ListConfig

"""
Scake reference: =/a/b/c
OmegaConf query: a.b.c
"""

SCK_FMT_REF = "sck_fmt_ref"
OMG_FMT_QRY = "omg_fmt_qry"

SCK_ANNO_METHOD = "()"
SCK_ANNO_CLASS = "$"
SCK_ANNO_REF_START = "/"  # "=/"
SCK_REF_DELIMITER = "/"

QUERY_DELIMITER = "."


def is_dict(value):
    return isinstance(value, (dict, DictConfig))


def is_list(value):
    return isinstance(value, (list, tuple, ListConfig))


def is_primitive(value):
    return not is_dict(value) and not is_list(value)


def detect_format(value):
    if value.startswith(SCK_ANNO_REF_START):
        return SCK_FMT_REF
    else:
        return OMG_FMT_QRY


def convert_query_to_sckref(query):
    return SCK_ANNO_REF_START + SCK_REF_DELIMITER.join(query.split(QUERY_DELIMITER))


def convert_sckref_to_query(sckref):
    # return sckref.lstrip(SCK_ANNO_REF_START).replace(SCK_REF_DELIMITER, QUERY_DELIMITER)
    return "".join(
        [
            "[%s]" % item
            for item in sckref.lstrip(SCK_ANNO_REF_START).split(SCK_REF_DELIMITER)
        ]
    )


def convert_list_to_sckref(values):
    return SCK_ANNO_REF_START + SCK_REF_DELIMITER.join(values)


def is_scake_ref(value, all_refs=[]):
    # the value maybe file path so we check it first
    try:
        if os.path.isfile(value) or os.path.isdir(value):
            return False
    except Exception:
        # error while trying to check file path -> it's not a path of file, just skip it
        pass

    if (
        isinstance(value, str)
        and value.startswith(SCK_ANNO_REF_START)
        and not value.endswith("/")
        and (not all_refs or all_refs and value in all_refs)
    ):
        return True
    else:
        return False


def is_scake_class(name):
    if isinstance(name, (str,)):
        if name.count(SCK_REF_DELIMITER) > 0:
            last_item = name.split(SCK_REF_DELIMITER)[-1]
            if last_item.startswith(SCK_ANNO_CLASS):
                return True
        elif name.count("][") > 0:
            last_item = name.lstrip("[").rstrip("]").split("][")[-1]
            if last_item.startswith(SCK_ANNO_CLASS):
                return True
        elif name.startswith(SCK_ANNO_CLASS):
            return True
        # elif name.count(".") > 0:
        #     last_item = name.split(".")[-1]
        #     if last_item.startswith(SCK_ANNO_CLASS):
        #         return True
    elif isinstance(name, (tuple, list)):
        last_item = name[-1]
        if last_item.startswith(SCK_ANNO_CLASS):
            return True
    return False


def is_scake_method(name):
    if isinstance(name, (str,)):
        if name.count(SCK_REF_DELIMITER) > 0:
            last_item = name.split(SCK_REF_DELIMITER)[-1]
            if last_item.endswith(SCK_ANNO_METHOD):
                return True
        elif name.count(".") > 0:
            last_item = name.split(".")[-1]
            if last_item.endswith(SCK_ANNO_METHOD):
                return True
        else:
            if name.endswith(SCK_ANNO_METHOD):
                return True
    elif isinstance(name, (tuple, list)):
        last_item = name[-1]
        if last_item.endswith(SCK_ANNO_METHOD):
            return True
    return False


def contains_scake_class(value):
    if not is_dict(value):
        return False

    count = 0
    for k, v in value.items():
        if is_scake_class(k):
            count += 1
    if count > 1:
        raise Exception("There are more than one class constructor: %s" % str(value))
    elif count == 1:
        return True
    else:
        return False


def extract_class_str_and_param_dict(value):
    result = (None, None)
    for k, v in value.items():
        if is_scake_class(k):
            result = (k, v)
    return result


def get_parent_node(node_name):
    return SCK_ANNO_REF_START + SCK_REF_DELIMITER.join(
        (node_name.lstrip(SCK_ANNO_REF_START).split(SCK_REF_DELIMITER))[:-1]
    )
