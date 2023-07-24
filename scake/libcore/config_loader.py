# -*- coding: utf-8 -*-
import os

# https://omegaconf.readthedocs.io/en/latest/usage.html#from-a-yaml-file
from omegaconf import OmegaConf
from omegaconf.dictconfig import DictConfig
from omegaconf.listconfig import ListConfig
from omegaconf.errors import ConfigKeyError
from . import sck_format

import logging

_logger = logging.getLogger(__name__)


class ConfigLoader:
    RESERVED_KEYS = ["_import", "_inherit"]

    """
        conf: YAML file path, dict, list, YAML string
    """

    def __init__(
        self,
        conf={},
        base_config={},
        is_skip_error=False,
        is_set_const_flatten_value=False,
        const_flatten_value=None,
        is_use_flatten=False,
    ):
        self.conf = conf
        self.base_config = base_config
        self.is_skip_error = is_skip_error
        self.config = self.load_config(
            self.conf, self.base_config, self.is_skip_error
        )  # OmegaConf object
        self.const_flatten_value = const_flatten_value
        self.cfg_flatten = self.flatten(
            self.config,
            is_set_const_value=is_set_const_flatten_value,
            const_value=const_flatten_value,
        )
        self.is_use_flatten = is_use_flatten
        if self.is_use_flatten:
            self.config = self.cfg_flatten

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
                pass
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
            pass
        else:  # scalar
            return {}
        return result

    def merge(self, base, new):
        return OmegaConf.merge(base, new)

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

    def load_config(self, conf, base_config, is_skip_error):
        base_cfg = self.read_config(base_config, is_skip_error)
        new_cfg = self.read_config(conf, is_skip_error)
        current_cfg = self.merge(base=base_cfg, new=new_cfg)
        # inherit load
        inherit_list = current_cfg.get("_inherit", [])
        if inherit_list and len(inherit_list) > 0:
            i_cfg = OmegaConf.create()
            for conf_item in inherit_list:
                i_cfg = self.merge(
                    base=i_cfg,
                    new=ConfigLoader(
                        conf=conf_item,
                        base_config=self.base_config,
                        is_skip_error=self.is_skip_error,
                    ).get_config(),
                )
            current_cfg = self.merge(base=i_cfg, new=current_cfg)
        return current_cfg

    def get_config(self):
        return self.config

    def get_flatten_config(self):
        return self.cfg_flatten

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
