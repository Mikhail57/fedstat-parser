import pandas as pd

from fedstat import FedStatApi


def want_to_change(prompt: str) -> bool:
    return input(prompt + ' (y/n/+/-): ').strip() in ('y', '+')


INDICATOR_ID = int(input('Введите айди показателя (или оставьте пустым для 57796): ').strip() or 57796)

fedstat = FedStatApi()
print('Получение параметров…')
params = fedstat.get_data_ids(INDICATOR_ID)
print('Полученные параметры:')
for p in params:
    print('Параметр: ' + p.title)
    for v in p.values:
        print('\t({0}) {1} ({2})'.format(str(v.id), v.title, ('+' if v.checked else '-')))
    if len(p.values) == 1:
        continue
    want_do_changes = want_to_change('Вы хотите изменить стандартные значения?')
    if want_do_changes:
        print('Параметр: ' + p.title)
        for v in p.values:
            v.checked = want_to_change('\t({0}) {1}'.format(str(v.id), v.title))

print('Получение данных…')
sdmx_parser = fedstat.get_data(INDICATOR_ID, params)
data = sdmx_parser.data
df = pd.json_normalize(data)
df.to_csv('result.csv')
print('Данные сохранены в result.csv')
