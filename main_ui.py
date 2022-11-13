import threading
from typing import List

import enaml
import pandas as pd
from enaml.qt.qt_application import QtApplication

from fedstat import FedStatApi
from filter_field import FilterField, FilterValue
from ui_filter_data import UiData, UiSource, UiFilter, UiFilterValue

INDICATOR_ID = 57796
fedstat = FedStatApi()
params = None


def on_save_clicked(self):
    if not params:
        return

    data = fedstat.get_data(INDICATOR_ID, list(map(lambda f: FilterField(
        id=f.id,
        values=map(lambda v: FilterValue(
            id=v.id,
            checked=v.checked,
            title='',
            order=0,
        ), f.values),
        title='',

    ), self.filters))).data
    df = pd.json_normalize(data)
    df.to_csv('result.csv')


def on_selected(self):
    self.is_loading = True
    self.is_error = False

    try:
        global params
        params = fedstat.get_data_ids(INDICATOR_ID)
        self.filters = list(map(lambda p: UiFilter(
            id=p.id,
            title=p.title,
            values=list(map(lambda v: UiFilterValue(
                id=v.id,
                title=v.title,
                checked=v.checked
            ), p.values))
        ), params))
    except IOError as e:
        self.is_error = True
        self.error_msg = 'Ошибка сети…'
    except Exception as e:
        self.is_error = True
        self.error_msg = 'Неизвестная ошибка…'
    finally:
        self.is_loading = False


def main():
    with enaml.imports():
        from grabber_view import Main

    app = QtApplication()
    sources = [
        UiSource(
            id=57796,
            title='Индексы цен на прочую продукцию (затраты, услуги) инвестиционного назначения с 2017 г.',
            filters=[],
            on_save_clicked=on_save_clicked,
            on_selected=on_selected,
        ),
        UiSource(
            id=2,
            title='Мур мур мур',
            filters=[]
        )
    ]
    view = Main(ui_data=UiData(sources=sources, selected_source=sources[0]))
    view.show()

    app.start()


if __name__ == '__main__':
    main()
