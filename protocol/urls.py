from django.conf.urls import url
from .views import get_emails, list_categories, show_categories

urlpatterns = [
    url(r'^get-emails/$',
        get_emails, name="get_emails"),
    url(r'^/json/$',
        list_categories, name="protocol_categories_json"),
    url(r'^/$',
        show_categories, name="protocol_categories"),
]
