# -*- coding: utf-8 -*-

SEPARATOR = '/'

class Scake():   

    def __init__(self, config):
        self._config = config
        self._config_dict = config
        self._flat_dict = self._build_config(self._config_dict)
        
        # loop on flat dict and copy dependent attributes
        # TODO
        
        print('_flat_dict', self._flat_dict)
        
        pass
        
    def __getitem__(self, key):
        item_value = self._flat_dict[key]
        if self._is_scake_annotation(item_value):
            item_value = self._get_scake_item(anno=item_value)
        return item_value
        
    def __setitem__(self, key, value):
        self._flat_dict[key] = value
        
    def __len__(self):
        return len(self._flat_dict)
        
    def __repr__(self):
        return """
            Scake Object:
                * _config: %(_config)s
                * _flat_dict: %(_flat_dict)s
        """ % {
            '_config': self._config,
            '_flat_dict': str(self._flat_dict)
        }
        
    def _is_scake_annotation(self, anno):
        return isinstance(anno, str) and anno.startswith('_%s'%SEPARATOR)
        
    def _scake_annotation_to_scake_key(self, anno):
        return SEPARATOR.join(anno.split(SEPARATOR)[1:])
        
    def _get_scake_item(self, anno):
        if self._is_scake_annotation(anno):
            key = self._scake_annotation_to_scake_key(anno)
            value = self._flat_dict[key]
            return self._get_scake_item(value)
        else:
            return anno
        
    def _merge_dicts(self, keep, target, prefix, separator=SEPARATOR):
        for k, v in target.items():
            keep[prefix + separator + k] = v
        return keep
        
    def _build_config(self, config):
        flat_dict = {}
        if isinstance(config, dict):
            for k, v in config.items():
                sub_flat_dict = self._build_config(v)
                if sub_flat_dict:
                    flat_dict = self._merge_dicts(keep=flat_dict, target=sub_flat_dict, prefix=k)
                flat_dict[k] = v                
        elif isinstance(config, list) or isinstance(config, tuple):
            for idx, v in enumerate(config):
                sub_flat_dict = self._build_config(v)
                if sub_flat_dict:
                    flat_dict = self._merge_dicts(keep=flat_dict, target=sub_flat_dict, prefix=str(idx))
                flat_dict[str(idx)] = v
            pass
        else:
            return None        
        return flat_dict
        
