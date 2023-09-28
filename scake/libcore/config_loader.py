# -*- coding: utf-8 -*-
import logging
import os
from functools import reduce  # Python 3.5+

# https://omegaconf.readthedocs.io/en/latest/usage.html#from-a-yaml-file
from omegaconf import OmegaConf
from omegaconf.dictconfig import DictConfig
from omegaconf.listconfig import ListConfig

from . import sck_format
from .sck_format import SCK_ANNO_REF_START, SCK_REF_DELIMITER
from .sck_log import sck_log

_logger = logging.getLogger(__name__)

# https://stackoverflow.com/a/41689055


def flatten(d, pref=""):
    return reduce(
        lambda new_d, kv: isinstance(kv[1], dict)
        and {**new_d, **flatten(kv[1], pref + kv[0])}
        or {**new_d, pref + kv[0]: kv[1]},
        d.items(),
        {},
    )


# https://stackoverflow.com/a/72988392


def flatten2(it=None, sep="."):
    ot = {}

    if isinstance(it, dict):
        stack = list(it.items())[::-1]
    elif isinstance(it, list):
        stack = list(enumerate(it))[::-1]

    while stack:
        head = stack.pop()

        if isinstance(head[1], dict):
            stack = (
                stack
                + [(f"{head[0]}{sep}{item[0]}", item[1]) for item in head[1].items()][
                    ::-1
                ]
            )
        elif isinstance(head[1], list):
            stack = (
                stack
                + [
                    (f"{head[0]}{sep}{item[0]}", item[1]) for item in enumerate(head[1])
                ][::-1]
            )
        else:
            ot[head[0]] = head[1]

    return ot


class ConfigLoader:
    RESERVED_KEYS = ["_import", "_inherit"]

    """
        conf: YAML file path, dict, list, YAML string
    """

    # @plazy.tictoc()
    def __init__(
        self,
        conf={},
        base_config={},
        is_skip_error=False,
        home_path=None,
    ):
        self.conf = conf
        self.base_config = base_config
        self.is_skip_error = is_skip_error
        self.home_path = home_path

        self.config = self.load_config(
            self.conf, self.base_config, self.is_skip_error
        )  # OmegaConf

        # Slow code, poor performance
        # self.cfg_flatten = self.flatten(
        #     self.config,
        #     is_set_const_value=is_set_const_flatten_value,
        #     const_value=const_flatten_value,
        # )
        # self.is_use_flatten = is_use_flatten
        # if self.is_use_flatten:
        #     self.config = self.cfg_flatten

        # s_log("Loadded config", self.config, is_debug=True)

    def get_flatten_refs(self):
        result = flatten2(self.to_dict(resolve=False), SCK_REF_DELIMITER)
        res_keys = list(result.keys())
        new_keys = []
        for rk in res_keys:  # config/bar/a
            items = rk.split(SCK_REF_DELIMITER)
            if len(items) > 1:
                for i in range(len(items) - 1):
                    index = i + 1
                    new_keys.append(SCK_REF_DELIMITER.join(items[:-index]))
        new_keys = list(set(new_keys))
        final_result = res_keys + new_keys
        final_result = [SCK_ANNO_REF_START + k for k in final_result]
        return final_result

    # @plazy.tictoc()
    def flatten(
        self,
        omgconf,
        result=OmegaConf.create(),
        paths=[],
        is_set_const_value=False,
        const_value=None,
    ):
        if isinstance(omgconf, DictConfig):
            for k, v in omgconf.items():
                result[
                    sck_format.convert_list_to_sckref(
                        paths
                        + [
                            k,
                        ]
                    )
                ] = (
                    const_value if is_set_const_value else v
                )
                result = self.merge(
                    base=result,
                    new=self.flatten(
                        omgconf=v,
                        paths=paths
                        + [
                            k,
                        ],
                        is_set_const_value=is_set_const_value,
                        const_value=const_value,
                    ),
                )
        elif isinstance(omgconf, ListConfig):
            for idx, v in enumerate(omgconf):
                result[
                    sck_format.convert_list_to_sckref(
                        paths
                        + [
                            str(idx),
                        ]
                    )
                ] = (
                    const_value if is_set_const_value else v
                )
                result = self.merge(
                    base=result,
                    new=self.flatten(
                        omgconf=v,
                        paths=paths
                        + [
                            str(idx),
                        ],
                        is_set_const_value=is_set_const_value,
                        const_value=const_value,
                    ),
                )
        else:  # scalar
            return {}
        return result

    def merge(self, base, new):
        return OmegaConf.merge(base, new)

    # @plazy.tictoc()
    def read_config(self, conf, is_skip_error=False):
        if type(conf) == str and os.path.isfile(conf):
            return OmegaConf.load(conf)

        omg_config = OmegaConf.create()  # empty config
        try:
            omg_config = OmegaConf.create(conf)
        except Exception as e:
            _logger.error(e)
            if not is_skip_error:
                raise Exception(e)
        return omg_config

    def _get_inherit_list_recursive(
        self, cfg, traversed_paths, home_path, is_skip_error
    ):
        inherit_list = [x for x in cfg.get("_inherit", [])]

        result = []
        for cfg_path in inherit_list:
            path_conf_item = cfg_path
            if not os.path.isfile(path_conf_item):
                path_conf_item = os.path.abspath(os.path.join(home_path, cfg_path))

            if not os.path.isfile(path_conf_item):
                s_log(
                    "Config file not found (%s)" % str(path_conf_item), is_warning=True
                )
                continue

            if path_conf_item in traversed_paths:
                continue

            child_cfg = self.read_config(path_conf_item, is_skip_error)
            traversed_paths.append(path_conf_item)
            sub_result = self._get_inherit_list_recursive(
                child_cfg,
                traversed_paths,
                os.path.dirname(path_conf_item),
                is_skip_error,
            ) + [
                path_conf_item,
            ]
            result += sub_result

        return result

    # @plazy.tictoc()
    def load_config(self, conf, base_config, is_skip_error):
        base_cfg = self.read_config(base_config, is_skip_error)
        new_cfg = self.read_config(conf, is_skip_error)
        current_cfg = OmegaConf.merge(base_cfg, new_cfg)
        # inherit load
        inherit_order = self._get_inherit_list_recursive(
            current_cfg, [], self.home_path, is_skip_error
        )

        i_cfg = OmegaConf.create()
        for cfg_path in inherit_order:
            path_conf_item = (
                cfg_path
                if os.path.isfile(cfg_path)
                else os.path.abspath(
                    os.path.join(os.path.dirname(os.path.abspath(self.conf)), cfg_path)
                )
            )
            i_cfg = OmegaConf.merge(
                i_cfg, self.read_config(path_conf_item, is_skip_error)
            )
        i_cfg = OmegaConf.merge(i_cfg, current_cfg)
        i_cfg.pop("_inherit", [])

        return i_cfg

    # #very slow implementation!
    # def load_config(self, conf, base_config, is_skip_error):
    #     base_cfg = self.read_config(base_config, is_skip_error)
    #     new_cfg = self.read_config(conf, is_skip_error)
    #     current_cfg = self.merge(base=base_cfg, new=new_cfg)
    #     # inherit load
    #     inherit_list = current_cfg.get("_inherit", [])

    #     # s_log("inherit list", inherit_list, is_debug=True)

    #     if inherit_list and len(inherit_list) > 0:
    #         i_cfg = OmegaConf.create()
    #         for conf_item in inherit_list:
    #             # conf_item should be an absolute path or relative path
    #             # we check abs path first and then use rel path later
    #             path_conf_item = conf_item if os.path.isfile(conf_item) else os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(self.conf)), conf_item))
    #             i_cfg = self.merge(
    #                 base=i_cfg,
    #                 new=ConfigLoader(
    #                     conf=path_conf_item,
    #                     base_config=self.base_config,
    #                     is_skip_error=self.is_skip_error,
    #                 ).get_config(),
    #             )
    #         current_cfg = self.merge(base=i_cfg, new=current_cfg)
    #     return current_cfg

    def get_config(self):
        return self.config

    def to_dict(self, resolve=True):
        return OmegaConf.to_container(self.config, resolve=resolve)

    def get(self, key, default=None):
        """
        "scake.num_cpus", 10 => 4
        "scake[num_cpus]", 10 => 4
        """
        # https://omegaconf.readthedocs.io/en/latest/usage.html#omegaconf-select
        return OmegaConf.select(
            self.config, key, default=default, throw_on_resolution_failure=False
        )

    def __getitem__(self, key):
        return self.get(key, None)

    def set(self, key, value, force_add=True):
        OmegaConf.update(self.config, key, value, force_add=True)

    def __setitem__(self, key, value):
        self.set(key, value)


s_log = sck_log.register(obj_or_class=ConfigLoader)
