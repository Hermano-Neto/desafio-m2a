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
        name='vaga-disponivel-odernada-autocomplete',
    ),
]