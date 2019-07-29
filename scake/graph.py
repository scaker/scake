# -*- coding: utf-8 -*-
from .node import Node


class NodeGraph():
    def __init__(self, scake):
        self._flat_ids = {}
        self._scake = scake
        pass

    def __getitem__(self, id):
        return self._flat_ids.get(id, None)

    def _init_empty_node(self, ids):
        for id in ids:
            if id not in self._flat_ids:
                self._flat_ids[id] = Node(id, self)
            pass
        pass

    def add_node(self, id, des_paths=[]):
        self._init_empty_node(des_paths+[id])
        target_node = self._flat_ids[id]
        for des_id in des_paths:
            target_node.add_descendant(des_id)
        pass

    def get_node_order(self, keep_active=True, filtered_types=None, reverse=False):
        """
            filtered_types: ["class", "method"]
        """
        nodes = list(self._flat_ids.values())
        if keep_active:
            nodes = [n for n in nodes if n.active]
        sorted_nodes = sorted(nodes, key=lambda n: (n.degree, n.id), reverse=reverse)
        if filtered_types:
            sorted_nodes = [n for n in sorted_nodes if self._scake._rule.check_type(key=n.id) in filtered_types]
        return sorted_nodes

    def __repr__(self):
        content = []
        nodes = self.get_node_order()
        for n in nodes:
            for d in n.descendant:
                line = '%s (%d)' % (n.id, n.degree) if n.degree > 0 else n.id
                line += ' -> '
                line += '%s (%d)' % (d, self[d].degree)  # if self[d].degree > 0 else d
                content.append(line)

            if not n.descendant:
                if not n.active:
                    content.append('[-] %s (%d)' % (n.id, n.degree))
                else:
                    content.append('%s (%d)' % (n.id, n.degree))

            # for a in n.ancestor:
            #     line = '%s (%d)' % (n.id, n.degree) if n.degree > 0 else n.id
            #     line += ' <- '
            #     line += '%s (%d)' % (a, self[a].degree) if self[a].degree > 0 else a
            #     content.append(line)
        return """
NodeGraph:
%(_content)s
        """ % {
            '_content': '\n'.join(content)
        }
