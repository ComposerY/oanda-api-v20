# -*- encoding: utf-8 -*-
"""dynamically add the classes for definition representations.

Most of the endpoint groups have some definitions that apply. These are
in the definitions package. It is conveniant to have access by a class
representing a specific group of definitions instead of a dictionary.
"""
import sys
from importlib import import_module
import six


dyndoc = """Definition representation of {cls}

    Definitions used in requests and responses. This
    class provides the ID and the description of the definitions.

    >>> import {PTH} as def{mod}
    >>> print def{mod}.{cls}.{firstItem}
    {orig}
    >>> c = def{mod}.{cls}()
    >>> print c[c.{firstItem}]
    {firstItemVal}

"""

_doc = """
    .. note::

       attribute name *{}* is renamed to *{}*, value stil is *{}*. This
       means that a lookup stil applies.
"""


def make_definition_classes(mod):
    """Dynamically create the definition classes from module 'mod'."""
    rootpath = "oandapyV20"
    PTH = "{}.definitions.{}".format(rootpath, mod)

    M = import_module(PTH)
    for cls, cldef in M.definitions.items():

        orig, fiV = next(six.iteritems(cldef))
        fiK = orig.replace('-', '_')
        # create the docstring dynamically
        clsdoc = dyndoc.format(cls=cls,
                               PTH=PTH,
                               mod=mod,
                               firstItem=fiK, orig=orig,
                               firstItemVal=fiV)

        # Since we can't change the docstring afterwards (it's readonly)
        # figure this out before and not during ...
        for K, V in cldef.items():
            attrName = K
            if "-" in K:
                attrName = K.replace('-', '_')
                adoc = _doc.format(K, attrName, K)
                clsdoc += adoc

        # the class
        dyncls = type(cls, (object,), {'__doc__': clsdoc})

        definitions = dict()
        for K, V in cldef.items():
            attrName = K
            if "-" in K:
                attrName = K.replace('-', '_')
            setattr(dyncls, attrName, K)  # set as class attributes
            definitions.update({K: V})    # for mapping by __getitem__

        def mkgi(definitions):
            def __getitem__(self, definitionID):
                self._definitions = definitions
                return self._definitions[definitionID]
            return __getitem__

        setattr(dyncls, "__getitem__", mkgi(definitions))
        setattr(sys.modules["{}.definitions.{}".format(rootpath, mod)],
                cls, dyncls)

definitionModules = [
    'accounts',
    'instruments',
    'orders',
    'pricing',
    'primitives',
    'trades',
    'transactions'
]

# dynamically create all the definition classes from the modules
for M in definitionModules:
    make_definition_classes(M)
