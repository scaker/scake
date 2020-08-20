# -*- coding: utf-8 -*-
class Node():
    def __init__(self, id, node_graph):
        self.id = id
        self.node_graph = node_graph
        self.degree = 0
        self.ancestor = []
        self.descendant = []
        self.active = True

    def _add_ancestor(self, id):
        if self.id == id:
            raise Exception('Graph cycle detected @ %s' % id)
        self.ancestor.append(id)
        self.ancestor = list(set(self.ancestor)) # unique
        pass

    def add_descendant(self, id):
        if self.id == id:
            raise Exception('Graph cycle detected @ %s' % id)
        self.descendant.append(id)
        self.descendant = list(set(self.descendant)) # unique
        self.degree = len(self.descendant)
        self.node_graph[id]._add_ancestor(self.id)
        pass

    def resolve(self):
        if self.degree != 0:
            raise Exception('Cannot resolve node with degree(%d) > 0.' % self.degree)

#         print('%s | self.ancestor' % self.id, self.ancestor)

        for anc_id in self.ancestor:
            anc_node = self.node_graph[anc_id]
            anc_node.descendant.remove(self.id)
            anc_node.degree = len(anc_node.descendant)

        self.active = False
        pass

    def __repr__(self):
        content = ''
        for d in self.descendant:
            line = '%s (%d)' % (self.id, self.degree) if self.degree > 0 else self.id
            line += ' -> '
            line += '%s (%d)' % (d, self[d].degree)  # if self[d].degree > 0 else d
            content = line

        if not self.descendant:
            content = '%s (%d)' % (self.id, self.degree)

        return content
        pass
