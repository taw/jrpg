#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Spatial index for JRPG 2

# TODO: should the index be functional or imperative ?
class Index:
    def __init__(self):
        self.elements = []
        self.index = None
    def add(self, rect, element):
        self.elements.append((rect,element))
        self.index = None
    # Some slow algorithms
    # FIXME: don't use
#    def intersect_idx(self, idx2):
#        if not self.index: self.build_index()
#        res = Index()
#        for (r1,e1) in self.elements:
#            for (r2,e2) in idx2.elements:
#                # FIXME: what's the proper method ?
#                r3 = r1.intersect(r2)
#                res.add(r3, (e1,e2))
#        return res
    def intersect_rect(self, r2):
        res = []
        def intersect_rect_aux(box):
            (i_bb,i_type,contents) = box
            if r2.colliderect(i_bb):
                if i_type:
                    intersect_rect_aux(contents[0])
                    intersect_rect_aux(contents[1])
                else:
                    res.append((r2.clip(i_bb), contents))
        if not self.index: self.build_index()
        intersect_rect_aux(self.index)
        return res
    def intersects_rect_p(self, r2):
        def intersects_rect_p_aux(box):
            (i_bb,i_type,contents) = box
            if r2.colliderect(i_bb):
                if i_type:
                    return(intersects_rect_p_aux(contents[0]) or
                           intersects_rect_p_aux(contents[1]))
                else:
                    return True
            return False
        if not self.index: self.build_index()
        return intersects_rect_p_aux(self.index)
    # Build some acceleration structure
    # This is a 1D index
    # If it's too slow, switch to 2D-indexing
    def contains_rect_p(self, bb):
        def contains_rect_p_aux(box):
            (i_bb,i_type,contents) = box
            if i_bb.contains(bb):
                if i_type:
                    return(contains_rect_p_aux(contents[0]) or
                           contains_rect_p_aux(contents[1]))
                else:
                    return True
            return False
        if not self.index: self.build_index()
        return contains_rect_p_aux(self.index)
    def build_index(self):
        def build_index_aux(start, end):
            if start == end:
                return (self.elements[start][0], 0, self.elements[start][1])
            mid = start + (end-start)/2
            a_i = build_index_aux(start, mid)
            b_i = build_index_aux(mid+1, end)
            c_bb = a_i[0].union(b_i[0])
            return (c_bb, 1, (a_i, b_i))

        # x-sort
        self.elements.sort()
        self.index = build_index_aux(0, len(self.elements)-1)
