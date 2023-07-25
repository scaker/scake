# -*- coding: utf-8 -*-
import inspect
import logging
from functools import partial

from .sck_singleton import SckSingleton

_logger = logging.getLogger(__name__)


class SckLog(SckSingleton):
    """
    Usage:
        slog = sck_log.register(name="Flow", obj=graph)
        slog("abc", "def", "gnh")
    """

    def __init__(self):
        pass

    def register(
        self,
        name=None,
        obj_or_class=None,
        delimiter=" ",
        is_debug=False,
        is_info=False,
        is_warning=False,
        is_error=False,
    ):
        """
        log_debug = sck_log.register(name="Graph", obj=graph_ref, is_debug=True)
        log_debug(m="Hello World!")

        slog = sck_log.register(name="GFlow")
        slog("GNode detected", is_info=True)
        """
        cls_name = (
            obj_or_class.__name__
            if inspect.isclass(obj_or_class)
            else obj_or_class.__class__.__name__
        )
        return partial(
            self.log,
            cls_name=cls_name,
            name=name,
            delimiter=delimiter,
            is_debug=is_debug,
            is_info=is_info,
            is_warning=is_warning,
            is_error=is_error,
        )

    def log(
        self,
        *messages,
        cls_name=None,
        name=None,
        delimiter=" ",
        is_debug=False,
        is_info=False,
        is_warning=False,
        is_error=False,
    ):
        """
        "[$SckGraph][exec] <val1> | <val2> | <val3>"
        """
        # cls_name x name => prefix
        prefix = []
        prefix.append(f"[${cls_name}]") if cls_name else None
        prefix.append(f"[{name}") if name else None
        prefix = "".join(prefix)

        # messages[] x delimiter => msg_str
        msg_str = delimiter.join([str(m) for m in messages])

        final_msg = (
            "%s %s" % (prefix, msg_str)
            if prefix and msg_str
            else (msg_str if msg_str else (prefix if prefix else ""))
        )
        if is_debug:
            _logger.debug(final_msg)

        if is_info:
            _logger.info(final_msg)

        if is_warning:
            _logger.warning(final_msg)

        if is_error:
            _logger.error(final_msg)


sck_log = SckLog()
