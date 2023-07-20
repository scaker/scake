
"""
Scake reference: =/a/b/c
OmegaConf query: a.b.c
"""

SCK_FMT_REF = "sck_fmt_ref"
OMG_FMT_QRY = "omg_fmt_qry"

SCK_ANNO_METHOD = "()"
SCK_ANNO_CLASS = "$"
SCK_ANNO_REF_START = "=/"
SCK_REF_DELIMITER = "/"

QUERY_DELIMITER = "."

def detect_format(value):
    if value.startswith(SCK_ANNO_REF_START):
        return SCK_FMT_REF
    else:
        return OMG_FMT_QRY

def convert_query_to_sckref(query):
    return SCK_ANNO_REF_START + SCK_REF_DELIMITER.join(query.split(QUERY_DELIMITER))

def convert_sckref_to_query(sckref):
    return sckref.replace(SCK_ANNO_REF_START, "").replace(QUERY_DELIMITER, SCK_REF_DELIMITER)

def convert_list_to_sckref(values):
    return SCK_ANNO_REF_START + SCK_REF_DELIMITER.join(values)

def is_scake_ref(value):
    if isinstance(value, str) and value.startswith(SCK_ANNO_REF_START):
        return True
    else:
        return False

def is_scake_class(name):
    if isinstance(name, (str,)):
        if name.count(SCK_REF_DELIMITER):
            last_item = name.split(SCK_REF_DELIMITER)[-1]
            if last_item.startswith(SCK_ANNO_CLASS):
                return True
        elif name.count(".") > 0:
            last_item = name.split(".")[-1]
            if last_item.startswith(SCK_ANNO_CLASS):
                return True
    elif isinstance(name, (tuple, list)):
        last_item = name[-1]
        if last_item.startswith(SCK_ANNO_CLASS):
            return True
    return False                

def is_scake_method(name):
    if isinstance(name, (str,)):
        if name.count(SCK_REF_DELIMITER):
            last_item = name.split(SCK_REF_DELIMITER)[-1]
            if last_item.endswith(SCK_ANNO_METHOD):
                return True
        elif name.count(".") > 0:
            last_item = name.split(".")[-1]
            if last_item.endswith(SCK_ANNO_METHOD):
                return True
        else:
            if name.count(SCK_ANNO_METHOD) > 0:
                return True
    elif isinstance(name, (tuple, list)):
        last_item = name[-1]
        if last_item.endswith(SCK_ANNO_METHOD):
            return True
    return False