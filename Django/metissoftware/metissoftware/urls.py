from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('wms.views',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'index', name='index'),
    url(r'^new_client.html', 'new_client', name='new_client'),
    url(r'^delete_client/',  'delete_client', name='delete_client'),
    url(r'^clients/', 'print_clients', name='print_clients'),
    url(r'^client_details/', 'client_details', name='client_details'),
    url(r'^login/$', login, {'template_name': 'wms/login.html'}),
    url(r'^logout/$', logout, {'next_page': '/'}),
    url(r'^appointments/', 'appointments', name='appointments'),
    url(r'^create_appointment/', 'create_appointment', name='create_appointment'),
    url(r'^query_api/', 'queryAPI', name='queryAPI'),
    url(r'^buy_stock/', 'buyStock', name='buyStock'),
    url(r'^sell_stock/', 'sell_stock', name='sell_stock'),
    url(r'^withdraw_cash/', 'withdraw_cash', name='withdraw_cash'),
    url(r'^deposit_cash/', 'deposit_cash', name='deposit_cash'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
