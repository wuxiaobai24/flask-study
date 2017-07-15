from flask import Blueprint

main = Blueprint('main',__name__)

from . import views,errors
from ..models import Permission

#在模板中全局访问，只是在模板中
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
