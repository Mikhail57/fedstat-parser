import enaml
from enaml.qt.qt_application import QtApplication

from ui_filter_data import UiData, UiSource, UiFilter, UiFilterValue


def main():
    with enaml.imports():
        from grabber_view import Main

    app = QtApplication()
    sources = [
        UiSource(
            id=1,
            title='Мяу мяу мяу',
            filters=[
                UiFilter(
                    id=1,
                    title='First Filter',
                    values=[
                        UiFilterValue(id=1, title='Value 1', checked=False),
                        UiFilterValue(id=2, title='Value 2', checked=False),
                        UiFilterValue(id=3, title='Value 3', checked=False),
                    ]
                ),
                UiFilter(
                    id=2,
                    title='Second Filter',
                    values=[
                        UiFilterValue(id=1, title='Value 1', checked=True),
                    ]
                ),
                UiFilter(
                    id=3,
                    title='Third Filter',
                    values=[
                        UiFilterValue(id=1, title='Value 1', checked=False),
                        UiFilterValue(id=2, title='Value 2', checked=False),
                        UiFilterValue(id=3, title='Value 3', checked=False),
                    ]
                )
            ]
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
