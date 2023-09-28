# -*- coding: utf-8 -*-
import inspect
import logging
import os
import sys

import ray
from omegaconf import OmegaConf

from .libcore.config_loader import ConfigLoader
from .libcore.sck_graph import SckGraph

logging.addLevelName(
    logging.INFO, "\x1b[1;34m%s\x1b[0m" % logging.getLevelName(logging.INFO)
)
logging.addLevelName(
    logging.WARNING, "\x1b[1;33m%s\033[1;0m" % logging.getLevelName(logging.WARNING)
)
logging.addLevelName(
    logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR)
)
# https://stackoverflow.com/a/23874319
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    # format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s@%(funcName)s: %(message)s",
    format="%(asctime)s.%(msecs)03d %(levelname)s %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
_logger = logging.getLogger(__name__)


class Scake(object):
    # @plazy.tictoc()
    def __init__(self, config={}, module_dir=[], is_ray=False, is_live=False):
        self.module_dir = module_dir
        self.config = config
        self.is_ray = is_ray
        self.is_live = is_live

        try:
            conf_home = (
                os.path.dirname(os.path.abspath(config))
                if os.path.isfile(config)
                else os.path.dirname(os.path.abspath(inspect.stack()[1].filename))
            )
        except Exception:
            conf_home = False
        self._conf = ConfigLoader(conf=self.config, home_path=conf_home)
        self._conf_flatten = OmegaConf.to_container(
            ConfigLoader(
                conf=self.config,
                is_set_const_flatten_value=False,
                const_flatten_value=None,
                is_use_flatten=True,
                home_path=conf_home,
            ).get_config(),
            resolve=False,
        )
        self.graph = SckGraph(
            scake=self,
            config=self._conf.get_config(),
            all_refs=list(self._conf_flatten.keys()),
        )

        if self.module_dir:
            if isinstance(self.module_dir, (tuple, list)):
                self.load_modules(self.module_dir)
            else:
                self.load_module(self.module_dir)
        self.load_modules(self._conf.get("_import", []), conf_dir=conf_home)

        # initialize ray pool
        if self.is_ray:
            num_cpus = self.get("scake.num_cpus", 4)
            ray.init(num_cpus=num_cpus)
            _logger.info("Initialized RAY server with %d cores!" % num_cpus)

        # _logger.info("Done init Scake, elapsed time info: %s", str(plazy.get_tictoc()))

    def load_modules(self, module_dirs, conf_dir=False):
        if not module_dirs:
            return
        for md in module_dirs:
            self.load_module(md, conf_dir=conf_dir)

    # @plazy.tictoc()
    def load_module(self, module_dir, conf_dir=False):
        if not module_dir:
            return

        module_dir_with_conf_dir = os.path.join(conf_dir, module_dir) if conf_dir else False
        module_dir_with_current_py_dir = os.path.join(os.path.dirname(__file__), module_dir)
        module_dir_abs = os.path.abspath(module_dir)

        for mdir in (module_dir_with_conf_dir, module_dir_abs, module_dir, module_dir_with_current_py_dir):
            if mdir and os.path.isdir(mdir):
                sys.path.append(mdir)
                break

        # if os.path.isdir(module_dir):  # abs path
        #     sys.path.append(module_dir)
        #     _logger.error("debug loaded %s", str(module_dir))
        # else: # may be a relative path, try conf_dir
        #     if os.path.isdir(module_dir_with_conf_dir):
        #         sys.path.append(os.path.abspath(module_dir_with_conf_dir))

        #         _logger.error("debug loaded %s", str(os.path.abspath(module_dir_with_conf_dir)))
        #     elif os.path.isdir(module_dir_with_current_py_dir):
        #         sys.path.append(os.path.abspath(module_dir_with_current_py_dir))

        #         _logger.error("debug loaded %s", str(os.path.abspath(module_dir_with_current_py_dir)))

    def get(self, key, default=None, live=None):
        """
        "scake.num_cpus", 10 => 4
        "scake[num_cpus]", 10 => 4
        """
        live = self.is_live if live is None else live
        return self.graph.query(key=key, default=default, live=live)

    def __getitem__(self, key):
        return self.get(key=key, default=None, live=None)

    # def set(self, key, value, force_add=True):
    #     self._conf.set(key, value, force_add=force_add)

    # def __setitem__(self, key, value):
    #     self.set(key, value)

    def __call__(self, node_names=[]):
        return self.graph.query(keys=node_names, live=True)
