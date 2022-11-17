# How to create executable
```bash
pyinstaller -w --add-data "grabber_view.enaml;./" --hidden-import enaml.core.compiler_helpers --hidden-import enaml.core.api --
hidden-import enaml.layout.api --hidden-import enaml.widgets.api --hidden-import enaml.widgets.form --hidden-import enaml.stdlib.fields --hidden-import enaml.core.templates --hidden-import enaml.enamldef_meta -F .\main_ui.py
```