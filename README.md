# Справочник Glossary

Программа хранит информацию в виде справочников, имеющих версии и содержимые элементы и отдает запрашиваемые ресурсы через API.

## Требования

Python: 3.9
Django: 2.2, 3.0, 3.1, 3.2
djangorestframework: 3.12

Файл 'dev.env' необходимо переименовать в '.env' для корректной работы сервиса.

## Ограничения

Сторонним пользователям доступен только GET-метод. Создание новых объектов и их редактирование доступно администратору ресурса в стандартной админке Django.

## Использование

Структура моделей представлена следующим образом: 
1. Справочник (модель Guide).
2. Версия справочника (модель Version).
3. Элемент версии справочника (модель Element).

Программа использует базовый путь для получения всех ресурсов:
api/v1/

### Ресурс Guide:
Для получения имеющихся справочников необходимо перейти по следующему пути:
```bash
api/v1/guides/  # выдаст все справочники с указанием актуальной версии и датой начала его действия.
```
Сервис выдает список справочников с указанием актуальной на текущий момент версии.
Справочники, не имеющие версии, либо имеющие дату начала версии позднее текущей, в ответ не включаются.
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "title": "Справочник медицинских препаратов",
            "id": 1,
            "short_title": "Препараты",
            "description": "Включает в себя все лекарственные средства и БАД",
            "version": "v.3.0.0",
            "start_date": "2021-08-01"
        },
        {
            "title": "Справочник медицинских специальностей",
            "id": 2,
            "short_title": "Специальности",
            "description": "Включает в себя перечень специалистов в медицине",
            "version": "sp.2.0",
            "start_date": "2021-05-15"
        }
    ]
}
```

Для получения списка справочников, актуальных на определенную дату, необходимо использовать параметр запроса ```search_date```. Формат ввода: "YYYY-mm-dd".
```shell
api/v1/guides/?search_date=2021-07-11
```
При вводе параметра в неверном формате даты пользователь получит соответствующее сообщение об ошибке.

```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "title": "Справочник медицинских препаратов",
            "id": 1,
            "short_title": "Препараты",
            "description": "Включает в себя все лекарственные средства и БАД",
            "version": "v.1.0.0",
            "start_date": "2021-07-01"
        },
        {
            "title": "Справочник медицинских специальностей",
            "id": 2,
            "short_title": "Специальности",
            "description": "Включает в себя перечень специалистов в медицине",
            "version": "sp.2.0",
            "start_date": "2021-05-15"
        }
    ]
}
```


Для получения элементов определенного справочника текущей версии необходимо перейти по следующему пути:
```bash
api/v1/guides/1/  # выдаст все элементы справочника с id=1 текущей версии (id - уникальный номер).
```

```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "code": "500100",
            "value": "парацетамол",
            "guide_id": 1
        },
        {
            "id": 3,
            "code": "500103",
            "value": "нурофен",
            "guide_id": 1
        },
        {
            "id": 4,
            "code": "500104",
            "value": "мирамистин",
            "guide_id": 1
        }
    ]
}
```

### Ресурс Version
Для получения всех версий (кроме версий с началом действия позднее текущей даты) заданного справочника необходимо перейти по следующему пути:
```bash
api/v1/guides/1/versions/  # покажет все версии справочника с id=1.
```

```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 3,
            "name": "v.3.0.0",
            "start_date": "2021-08-01"
        },
        {
            "id": 2,
            "name": "v.2.0.0",
            "start_date": "2021-07-17"
        },
        {
            "id": 1,
            "name": "v.1.0.0",
            "start_date": "2021-07-01"
        }
    ]
}
```
В случае, если у справочника нет версий, либо дата начала действия версии установлена позднее,
чем текущая, ответ вернет ошибку.

Для получения элементов определенной версии справочника необходимо перейти по следующему пути:
```bash
api/v1/guides/1/versions/2/  # покажет элементы справочника с id=1 версии id=2.
```

```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "code": "500100",
            "value": "парацетамол",
            "guide_id": 1
        },
        {
            "id": 2,
            "code": "500101",
            "value": "анальгин",
            "guide_id": 1
        },
        {
            "id": 5,
            "code": "500900",
            "value": "мезим",
            "guide_id": 1
        }
    ]
}
```

### Валидация элементов
Для валидации элементов заданного справочника текущей версии необходимо в параметрах запроса указать код и значение элемента под соответствующими именами: code и value.
Путь для валидации элемента:
```bash
http://127.0.0.1:8000/api/v1/guides/1/validate/?code=500103&value=нурофен  # провалидирует элемент со значениями code=500103 и value=нурофен в справочнике с id=1.
```

```json
"Element validated"
```
При валидации несуществующего элемента справочника текущей версии, сервис выдаст соответствующий ответ и ошибку:
```bash
http://127.0.0.1:8000/api/v1/guides/1/validate/?code=500103&value=aspirin  # провалидирует элемент с code=500103 и value=нурофен в справочнике с id=1.
```

```json
"No such element"
```

Для валидации элементов заданного справочника заданной версии необходимо в параметрах запроса указать код и значение элемента под соответствующими именами: code и value.
Путь для валидации элемента:
```bash
http://127.0.0.1:8000/api/v1/guides/1/versions/3/validate/?code=500103&value=нурофен  # провалидирует элемент со значениями code=500103 и value=нурофен в справочнике с id=1 версии id=3.
```

```json
"Element validated"
```
В этом же справочнике версии id=2 данного элемента нет:
```bash
http://127.0.0.1:8000/api/v1/guides/1/versions/2/validate/?code=500103&value=нурофен
```

```json
"No such element"
```
