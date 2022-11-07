from __future__ import annotations

import logging
from typing import List, Optional
from xml.etree.ElementTree import ElementTree

from utils import is_iterable
from variables import XML_NS


class SdmxParser:

    def __init__(self, file_content: str):
        self._file_content = file_content

    @staticmethod
    def _get_text(
            node: Optional[ElementTree],
            tags: List | str | None = None,
            default: str = '',
            ns: dict = XML_NS,
            strip: bool = True
    ) -> str:
        """
        Gets the value (text) of a given XML node / children with an optional default value.
        :param node: the parent XML node
        :param tags: a single child tag or list of child tags in hierarchical order to get the target node.
        :param default: default value returned in case of failure
        :param ns: XML namespace schema (default = rsengine::XML_NS)
        :param strip: whether to apply `strip()` to the retrieved text value to get rid of leading / trailing spaces
        :return: found value / `default` on failure
        """
        if node is None:
            return default
        if tags:
            if is_iterable(tags):
                for tag in tags:
                    node = node.find(tag, ns)
                    if node is None:
                        return default
            else:
                node = node.find(tags, ns)
                if node is None:
                    return default
        return node.text.strip() if strip else node.text

    # Gets the value (text) of a given attribute of an XML node / its children
    # with an optional default value.
    # @param node `ElementTree node` the parent XML node
    # @param attr `str` the attribute name (key)
    # @param tags `list` | `str` | `None` a single child tag or list of child tags in
    # hierarchical order (`[child, sub-child, sub-sub-child, ...]`) to get the target node.
    # If `None`, the parent node is the target one.
    # @param default `str` default value returned in case of failure
    # @param ns `dict` XML namespace schema (default = rsengine::XML_NS)
    # @param strip `bool` whether to apply `strip()` to the retrieved text value
    # to get rid of leading / trailing spaces
    # @returns `str` found value / `default` on failure
    # @see [Python ElementTree API](https://docs.python.org/3.8/library/xml.etree.elementtree.html)
    # @see \_get_text()
    @staticmethod
    def _get_attr(
            node: ElementTree,
            attr: str,
            tags: List | str | None = None,
            default: str = '',
            ns: dict = XML_NS,
            strip: bool = True
    ) -> str:
        if node is None:
            return default
        if tags:
            if is_iterable(tags):
                for tag in tags:
                    node = node.find(tag, ns)
                    if node is None:
                        return default
            else:
                node = node.find(tags, ns)
                if node is None:
                    return default
        sub = node.get(attr)
        if sub is None:
            return default
        return sub.strip() if strip else sub

    # Parses and collects the CodeLists section of a dataset XML.
    # @param ds_rootnode `ElementTree node` the parent node containing 'CodeLists'
    # @returns `dict` CodeLists section converted into a dictionary in the format:<br>
    # ```
    # {
    #  'code-name': {'name': '<full name>', 'values': [('<id>', '<description>'), ...]},
    #  'code-name': {...}
    # }
    # ```
    def get_codes(self, ds_root_node: ElementTree):
        codelists = ds_root_node.find('message:CodeLists', XML_NS)
        d_codes = {}

        for item in codelists.iterfind('structure:CodeList', XML_NS):
            name = self._get_attr(item, 'id')
            d_codes[name] = {'name': self._get_text(item, 'structure:Name'),
                             'values': dict([(self._get_attr(code, 'value'),
                                              self._get_text(code, 'structure:Description'))
                                             for code in item.iterfind('structure:Code', XML_NS)])}
        return d_codes

    # Parses and collects the DataSet section of a dataset XML.
    # @param ds_rootnode `ElementTree node` the parent node containing 'DataSet'
    # @param codes `dict` CodeLists section as a dictionary -- see \_get_codes()
    # @param max_row `int` limit of data points to collect from the XML
    # (`-1` = no limit)
    # @returns `list` DataSet section as a list of data values in the format:<br>
    # ```
    # [('classifier', 'class', 'unit', 'period of observation', int('observation year'), float('observation value')), ...]
    # ```
    def get_data(self, ds_root_node: ElementTree, codes: dict):
        dataset = ds_root_node.find('message:DataSet', XML_NS)
        if not dataset:
            return []
        data: List[dict] = []
        for item in dataset.iterfind('generic:Series', XML_NS):
            try:
                # period and unit
                period, unit = ('', '')
                try:
                    for attr in item.find('generic:Attributes', XML_NS).iterfind('generic:Value', XML_NS):
                        concept = self._get_attr(attr, 'concept')
                        val = self._get_attr(attr, 'value')
                        if concept == 'EI':
                            unit = val
                        elif concept == 'PERIOD':
                            period = val
                except:
                    period, unit = ('', '')

                # year
                try:
                    year = int(self._get_text(item, ['generic:Obs', 'generic:Time'], '0'))
                except:
                    year = 0

                # value
                try:
                    val = float(self._get_attr(item, 'value', ['generic:Obs', 'generic:ObsValue'], '0.0')
                                .replace(',', '.')
                                .replace(' ', '')
                                )
                except:
                    val = 0.0

                # classifier and class
                try:
                    classifiers_with_values_list = []
                    for key_item in item.find('generic:SeriesKey', XML_NS).iterfind('generic:Value', XML_NS):
                        key_concept = self._get_attr(key_item, 'concept')
                        key_key = self._get_attr(key_item, 'value')

                        classifier = codes[key_concept]['name']
                        cl = codes[key_concept]['values'][key_key]
                        classifiers_with_values_list.append((classifier, cl))
                    record_dict = dict(classifiers_with_values_list)
                    record_dict.update({
                        'value': val,
                        'period': period,
                        'ei': unit,
                        'year': year
                    })
                    data.append(record_dict)
                except Exception as e:
                    logging.error(e)
            except Exception as err:
                logging.error(err)
                break

        return data
