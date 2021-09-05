from typing import Union

from api.models import Guide, Version


def get_object_or_none(model: Union[Guide, Version], pk=None):
    object_id = pk

    try:
        object_id = int(object_id)
    except ValueError:
        return

    try:
        model_object = model.objects.get(pk=object_id)
    except model.DoesNotExist:
        return

    return model_object
