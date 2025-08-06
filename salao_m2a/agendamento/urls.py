from django.urls import path
from . import views

app_name = 'agendamento'

urlpatterns = [
    path(
        'pessoa-disponivel-autocomplete/',
        views.PessoaDisponivelAutocomplete.as_view(),
        name='pessoa-disponivel-autocomplete'
    ),

    path(
        'vaga-disponivel-ordenada-autocomplete/',
        views.VagaDisponivelOrdenadaAutocomplete.as_view(),
        name='vaga-disponivel-ordenada-autocomplete',
    ),

    path(
        'data-ordenada-autocomplete/',
        views.DataOrdenadaAutocomplete.as_view(),
        name='data-ordenada-autocomplete',
    ),

    path(
        'relatorio-pdf/',
        views.gerar_relatorio_pdf,
        name='relatorio-pdf'
    ),
]