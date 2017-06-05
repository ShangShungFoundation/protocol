from django.conf.urls import url
from views import watch, notify_message, list_categories, show_categories

urlpatterns = [
    # url(r'^watch/(?P<participant_id>\d+)/$',
    #     finance.payment.paypal, name="paypal_pay"),
    url(r'^watch/$',
        watch, name="gmail_watch"),
    url(r'^notify-message/$',
        notify_message, name="gmail_notify_message"),
    url(r'^/json/$',
        list_categories, name="protocol_categories_json"),
    url(r'^/$',
        show_categories, name="protocol_categories"),
]
