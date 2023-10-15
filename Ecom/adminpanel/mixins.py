from .models import Size


def get_count():
    return Size.objects.count()