from django.conf.urls import patterns, url
from views import LayerUploadView, LayerListView
from views import index, calculate, detail

urlpatterns = patterns(
    '',
    url(r'^$', LayerListView.as_view(), name='index'),
    url(r'^calculate/$', calculate, name='calculate'),
    url(r'^add/$', LayerUploadView.as_view(), name='create'),
    url(r'^(?P<layer_slug>[\w\-]+)/$', detail, name='layer_detail'),
)
