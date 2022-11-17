from atom.api import Atom, Bool


class UiPopupState(Atom):
    is_saving = Bool(True)
    is_succeed = Bool(False)
