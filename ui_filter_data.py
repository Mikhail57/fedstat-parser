from atom.api import Atom, List, Value, Bool, Int, Str, Callable, observe


class UiSource(Atom):
    id = Int()
    title = Str()
    filters = List()

    is_loading = Bool()
    is_error = Bool()
    error_msg = Str()

    on_selected = Callable()
    on_save_clicked = Callable()
    on_reload_clicked = Callable()


class UiFilter(Atom):
    id = Int()
    title = Str()
    values = List()


class UiFilterValue(Atom):
    id = Int()
    title = Str()
    checked = Bool()


class UiData(Atom):
    sources = List()
    selected_source_idx = Int(0)
    selected_source = Value()

    @observe('selected_source_idx')
    def update_filters(self, change):
        self.selected_source = self.sources[self.selected_source_idx]
        self.selected_source.on_selected(self.selected_source)
