from typing import List

import chompjs
import requests
from bs4 import BeautifulSoup, Tag
from requests import Session
from requests.adapters import HTTPAdapter, Retry

from filter_field import FilterField, FilterOrientation, FilterValue
from sdmx_parser import SdmxParser
from variables import FEDSTAT_URL_BASE


class FedStatApi:

    def __init__(self, base_url: str = FEDSTAT_URL_BASE):
        self.__base_url = base_url
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        self.__http: Session = http

    def get_data_ids(self, indicator_id: int, timeout_seconds: int = 180) -> List[FilterField]:
        indicator_url = '/'.join([self.__base_url, 'indicator', str(indicator_id)])
        html_page = self.__http.get(indicator_url, timeout=timeout_seconds)
        parsed_page = BeautifulSoup(html_page.text)

        def has_required_tag(tag: Tag) -> bool:
            return tag.name == 'script' and 'new FGrid' in tag.text

        js_text = parsed_page.find(has_required_tag).text
        js_filters = self.__get_filters_from_js(js_text)
        js_default_data_ids = self.__get_default_data_ids(js_text)

        result: List[FilterField] = []
        for filter_id, filter_description in js_filters.items():
            filter_id = int(filter_id)
            result_filter = FilterField(
                id=filter_id,
                title=filter_description['title'],
                orientation=self.__get_filter_orientation(filter_id, js_default_data_ids),
                values=self.__parse_filter_values(filter_description['values'])
            )
            result.append(result_filter)
        return result

    def get_data(self, indicator_id: int, filter_fields: List[FilterField]) -> SdmxParser:
        indicator_post_url = self.__base_url + '/indicator/data.do?format=sdmx'
        indicator_title = list(filter(lambda f: f.id == 0, filter_fields))[0].values[0].title

        post_filters = [
            ('id', indicator_id),
            ('title', indicator_title)
        ]
        for filter_field in filter_fields:
            for filter_value in filter_field.values:
                if not filter_value.checked:
                    continue
                post_filters.append(('selectedFilterIds', str(filter_field.id) + '_' + str(filter_value.id)))
                if filter_field.orientation == FilterOrientation.FILTER:
                    post_filters.append(('filterObjectIds', filter_field.id))
                elif filter_field.orientation == FilterOrientation.LINE:
                    post_filters.append(('lineObjectIds', filter_field.id))
                elif filter_field.orientation == FilterOrientation.COLUMN:
                    post_filters.append(('columnObjectIds', filter_field.id))
                elif filter_field.orientation == FilterOrientation.GROUP:
                    post_filters.append(('groupObjectIds', filter_field.id))
        sdmx_response = self.__http.post(indicator_post_url, data=post_filters)
        sdmx_response.encoding = 'utf-8'  # fedstat returns wrong encoding
        return SdmxParser(sdmx_response.text)

    @staticmethod
    def __get_filter_orientation(filter_id, js_default_data_ids):
        if filter_id == 0:
            return FilterOrientation.FILTER
        if filter_id in js_default_data_ids[FilterOrientation.LINE]:
            return FilterOrientation.LINE
        if filter_id in js_default_data_ids[FilterOrientation.GROUP]:
            return FilterOrientation.GROUP
        if filter_id in js_default_data_ids[FilterOrientation.FILTER]:
            return FilterOrientation.FILTER
        return FilterOrientation.COLUMN

    @staticmethod
    def __parse_filter_values(filter_values: dict) -> List[FilterValue]:
        result: List[FilterValue] = []

        for value_id, value_description in filter_values.items():
            value = FilterValue(
                id=int(value_id),
                title=value_description['title'],
                order=int(value_description['order']),
                checked=value_description['checked']
            )
            result.append(value)
        return result

    @staticmethod
    def __get_filters_from_js(js_code: str) -> dict:
        data_ids_start = js_code.find('filters: {')
        data_ids_end = js_code.find('left_columns: [')
        js_data_ids_indexed_text = js_code[data_ids_start:data_ids_end].strip()[:-1]
        return chompjs.parse_js_object(js_data_ids_indexed_text)

    @staticmethod
    def __get_default_data_ids(js_code: str) -> dict:
        data_ids_start = js_code.find('left_columns: [')
        data_ids_end = js_code.find('grid.init();')
        js_text = '{' + js_code[data_ids_start:data_ids_end].strip()[:-2]
        columns = chompjs.parse_js_object(js_text)
        return {
            FilterOrientation.LINE: columns['left_columns'],
            FilterOrientation.GROUP: columns['groups'],
            FilterOrientation.FILTER: columns['filterObjectIds'],
            FilterOrientation.COLUMN: columns['top_columns']
        }
