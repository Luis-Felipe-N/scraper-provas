from django.urls import path

from .views import BancaListView, ScrapeBancaView, ScrapeStatusView

app_name = 'scraper'

urlpatterns = [
    path('bancas/', BancaListView.as_view(), name='bancas-list'),
    path('executar/', ScrapeBancaView.as_view(), name='scrape-executar'),
    path('status/', ScrapeStatusView.as_view(), name='scrape-status'),
]
