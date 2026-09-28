from .bootstrap import init_otel
from .models import patch_models


def post_load():
    init_otel()
    patch_models()
