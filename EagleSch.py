#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 03 15:36:15 2014

@author: Aaron Carlton uid89626@gmail.com
Pretty Dumb Text Parser
Scratch that, Eagle Schematic Object
https://docs.python.org/3/library/xml.dom.minidom.html
(c) CC BY-SA FOSS
7/3/2014 0.35 Cleaned up. made command line arguements work.
"""
#import string
#import re
import sys
import getopt

Version = "0.35"

from xml.dom import minidom

class EagleSch():
    def __init__(self, source=None):
        """Load source into self.document"""
        self.xmldoc = minidom.parse(source).documentElement

    def layers(self, newlayer=None):
        """get layers if called with no parameters, or set layers if given layers"""
        if newlayer is None:
            layerslist = [] #List of layers returned to caller
            layers = self.xmldoc.getElementsByTagName('layer') #Grab all layer data from XML DOM
            for node in layers: #Re-structure layers into list of dicts.
                #Copy xml layer to dictionary
                layer = {} #This layer
                for k, v in node.attributes.items():
                    layer[k] = v
                layerslist.append(layer) #Add This layer to layers list
            return layerslist
        else: #Update DOM with newlayer data
            #This will fail if they are not the same length
            layers = self.xmldoc.getElementsByTagName('layer') #Grab all layer data from XML DOM
            for n1, n2 in zip(newlayer, layers):
                for k, v in n1.items():
                    n2.setAttribute(k, v)

    def parts(self, new=None):
        """get parts if called with no parameters, or set parts if given new.\n
        Can be used to iterate over parts like: for part in sch.parts():"""
        if new is None:
            partslist = [] #List of parts returned to caller
            parts = self.xmldoc.getElementsByTagName('part') #Grab all parts data from XML DOM
            for node in parts: #Re-structure parts into list of dicts.
                #Copy xml part to dictionary
                part = {} #This part
                for k, v in node.attributes.items():
                    part[k] = v
                partslist.append(part) #Add This part to parts list
            return partslist
        else:
            #This will fail if they are not the same length
            parts = self.xmldoc.getElementsByTagName('part') #Grab all parts data from XML DOM
            for n1, n2 in zip(new, parts):
                for k, v in n1.items():
                    n2.setAttribute(k, v)

    def libraries(self): #<TODO> <FIXME>
        """Get Libraries if called with no parameters"""
        ##So far this only returns a list of library dicts.
        liblist = [] #List of layers returned to caller
        libs = self.xmldoc.getElementsByTagName('library') #Grab all Library data from XML DOM
        #libs are trees of each library.
        for node in libs: #Re-structure lib into list of dicts.
            #in node, get description, packages->package(description, wire, smd, text, rectangle), symbols->symbol(name, pin, wire, circle, text), devicesets(deviceset(name), description, gates(gate), devices(device), connects(connect), technologies(technology) )  #Copy xml layer to dictionary
            lib = {} #This lib
            for k, v in node.attributes.items():
                lib[k] = v
            bit = self._parse(node)
            print 'bit: {}'.format(bit)
            print 'type: {}'.format(node.nodeType)
            if bit is not None:
                finder, dic = bit
                lib[finder] = dic
            liblist.append(lib) #Add This lib to lib list
        return liblist

    def segments(self):
        """Get segments"""
        allsegs = []
        nets = self.xmldoc.getElementsByTagName('net')
        for net in nets:
            asegdict = {} #Contains e.g. {'name': [], 'class': [], 'pinref': [], 'wire': [], 'junction': [], 'label': []}
            for k, v in net.attributes.items():
                asegdict[k] = v
            seg = net.getElementsByTagName('segment')[0]
            for node in seg.childNodes:
                bit = self._parse(node)
                if bit is not None:
                    finder, dic = bit
                    #print finder, dic
                    if not finder in asegdict:
                        asegdict[finder] = [] #Create list for dic
                    asegdict[finder].append(dic)
            allsegs.append(asegdict)
        return allsegs

    def _parse(self, node):
        """Parse single XML Node"""
        #print('Looking for "parse_{}".'.format(node.__class__.__name__))
        parseMethod = getattr(self, "_parse_%s" % node.__class__.__name__, None)
        if parseMethod is None:
            print('"_parse_{}" Not found.'.format(node.__class__.__name__))
        else:
            return parseMethod(node)

    def _parse_Element(self, node):
        #print('Looking for "do_{}"'.format(node.tagName))
        handlerMethod = getattr(self, '_do_%s' % node.tagName, None)
        if handlerMethod is None:
            print('"_do_{}" Not Found'.format(node.tagName))
        else:
            return handlerMethod(node)
#        map(self.parse, node.childNodes) #Do Children

    def _parse_Text(self, node):
        pass
        #print "parse_Text routine found {}.".format(node.data)
#        map(self.parse, node.childNodes) #Do Children

    def _do_pinref(self, node):
        return node.nodeName, dict(node.attributes.items())

    def _do_wire(self, node):
        """Found a wire, return the node name, and the wire attributes."""
        return node.nodeName, dict(node.attributes.items())

    def _do_junction(self, node):
        return node.nodeName, dict(node.attributes.items())

    def _do_label(self, node):
        return node.nodeName, dict(node.attributes.items())

    def data(self, node):
        if node.hasAttributes():
            for key in node.attributes.keys():
                #print '{}:{}'.format(key, node.attributes[key].value)
                setattr(self, key, node.attributes[key].value)
        map(self.data, node.childNodes)

    def output(self, fname=None):
        """Output self.xmldoc to xml eagle schematic fname. \n
        If fname is none, default to 'out.sch'."""
        if fname is None:
            fname = 'out.sch'
        with open(fname, 'wb') as f:
            f.write(self.xmldoc.toxml())
            f.flush()
            f.close()

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hi:') #, ['help'])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h'):
            print('Give me an eagle schematic. I will look at it for you.')
            break
        elif opt in ('-i'):
            print('input: {}'.format(arg))
            fname = arg
#        elif opt in ('-o'):
#            print(arg)

    sch = EagleSch(fname)
