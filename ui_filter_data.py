from atom.api import Atom, List, Value, Bool, Int, Str, observe


class UiSource(Atom):
    id = Int()
    title = Str()
    filters = List()


class UiFilter(Atom):
    id = Int()
    title = Str()
    values = List()


class UiFilterValue(Atom):
    id = Int()
    title = Str()
    checked = Bool()

    @observe('checked')
    def filter_checked(self, change):
        print('checkbox id=%d title=%s checked=%s' % (self.id, self.title, self.checked))


class UiData(Atom):
    sources = List()
    selected_source_idx = Int(0)
    selected_source = Value()

    @observe('selected_source_idx')
    def update_filters(self, change):
        self.selected_source = self.sources[self.selected_source_idx]
