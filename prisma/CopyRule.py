#!/usr/bin/env python

from .Rule import Rule

class CopyRule(Rule):

    def __init__(self,hist,srcID,srcField,dstID,dstField,ptype):
        Rule.__init__(self,hist,srcID,srcField,dstID,dstField)
        self.ptype = ptype

    def __str__(self):
        return 'ID {!s} {!s} {!s} {!s} {!s}'.format(self.hist,self.srcID,self.srcField, self.dstID, self.dstField)

    def __repr__(self):
        return '{!r} {!r} {!r} {!r} {!r} {!r}'.format(self.hist,self.srcID,self.srcField, self.dstID, self.dstField, self.ptype)

