import logging
import threading
from typing import List, Callable, Optional

import pandas as pd
from enaml.application import schedule

from fedstat import FedStatApi
from filter_field import FilterField
from ui_filter_data import UiFilterValue, UiFilter


class UiSourceAdapter:

    def load(self, callback: Callable[[Optional[List[UiFilter]], Optional[Exception]], None]):
        raise NotImplementedError()

    def save(self, ui_params: List[UiFilter], output_file_name: str, callback: Callable[[bool], None]):
        raise NotImplementedError()


class FedstatUiSourceAdapter(UiSourceAdapter):

    def __init__(self):
        self.indicator_id = 57796
        self.fedstat = FedStatApi()
        self.params: List[FilterField] = []

    def load(self, callback: Callable[[Optional[List[UiFilter]], Optional[Exception]], None]):
        def internal():
            try:
                schedule(callback, args=(self.__load(), None))
            except Exception as e:
                logging.error('Exception handling load', exc_info=e)
                schedule(callback, args=(None, e))

        threading.Thread(target=internal).start()

    def __load(self) -> List[UiFilter]:
        self.params = self.fedstat.get_data_ids(self.indicator_id)
        selectable_filters = filter(lambda f: len(f.values) > 1, self.params)
        filters = [
            UiFilter(
                id=f.id,
                title=f.title,
                values=[
                    UiFilterValue(
                        id=v.id,
                        title=v.title,
                        checked=v.checked
                    ) for v in f.values
                ]
            ) for f in selectable_filters
        ]
        return filters

    def save(self, ui_params: List[UiFilter], output_file_name: str, callback: Callable[[bool], None]):
        def internal():
            try:
                schedule(callback, args=(self.__save(ui_params, output_file_name),))
            except Exception as e:
                logging.error('Error saving data', exc_info=e)
                schedule(callback, args=(False,))

        threading.Thread(target=internal).start()

    def __save(self, ui_params: List[UiFilter], output_file_name: str) -> bool:
        for param in self.params:
            ui_param: Optional[UiFilter] = next((u for u in ui_params if u.id == param.id), None)
            if ui_param is None:
                continue
            for val in param.values:
                ui_v: Optional[UiFilterValue] = next((v for v in ui_param.values if v.id == val.id), None)
                if ui_v is None:
                    continue
                val.checked = ui_v.checked
        data = self.fedstat.get_data(self.indicator_id, self.params).data
        df = pd.json_normalize(data)
        df['Классификатор объектов административно-территориального деления (ОКАТО)'] \
            .replace('Российская Федерация', 'RU', inplace=True)
        df['period'].replace(
            to_replace={'январь': '01', 'февраль': '02', 'март': '03', 'апрель': '04', 'май': '05', 'июнь': '06',
                        'июль': '07', 'август': '08', 'сентябрь': '09', 'октябрь': '10', 'ноябрь': '11',
                        'декабрь': '12'},
            inplace=True
        )
        df['Виды показателя'].replace(
            to_replace={'К предыдущему месяцу': 'month',
                        'К декабрю предыдущего года': 'last_year_december',
                        'К соответствующему периоду предыдущего года': 'year',
                        'Отчетный месяц к соответствующему месяцу предыдущего года': 'reporting_month'},
            inplace=True
        )
        df['year'] = df['year'].astype(str)
        df['date'] = '01.' + df['period'] + '.' + df['year']
        df.drop(columns=['year', 'period'], inplace=True)
        df.to_csv(output_file_name, index=False)
        return True
