from typing import List, Optional

import enaml
from enaml.qt.qt_application import QtApplication

from ui_filter_data import UiData, UiSource, UiFilter
from ui_source_adapter import FedstatUiSourceAdapter


def on_save_clicked(self: UiSource, file_path):
    if not file_path:
        return
    self.adapter.save(self.filters, file_path, lambda r: print(f'Result: {r}'))


def on_selected(self: UiSource):
    self.is_loading = True
    self.is_error = False

    def callback(filters: Optional[List[UiFilter]], exception: Optional[Exception]):
        print(f'callback: {filters}, {exception}')
        self.is_loading = False
        if filters:
            self.filters = filters
        if exception:
            self.is_error = True
            if exception is IOError:
                self.error_msg = 'Ошибка сети…'
            else:
                self.error_msg = 'Неизвестная ошибка…'

    self.adapter.load(callback)


def main():
    with enaml.imports():
        from grabber_view import Main

    app = QtApplication()
    sources = [
        UiSource(
            id=57796,
            title='Индексы цен на прочую продукцию (затраты, услуги) инвестиционного назначения с 2017 г.',
            filters=[],
            adapter=FedstatUiSourceAdapter(),
            on_save_clicked=on_save_clicked,
            on_selected=on_selected,
        ),
        # UiSource(
        #     id=2,
        #     title='Мур мур мур',
        #     filters=[]
        # )
    ]
    view = Main(ui_data=UiData(sources=sources, selected_source=sources[0]))
    view.show()

    app.start()


if __name__ == '__main__':
    main()
