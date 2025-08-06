# agendamento/views.py

from dal import autocomplete
from django.db.models import Q
from django.utils import timezone

from .models import Pessoa, ServicoFuncionarioHorario

class PessoaDisponivelAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Pessoa.objects.none()

        qs = Pessoa.objects.filter(
            cliente__isnull=True,
            funcionario__isnull=True
        )

        if self.q:
            qs = qs.filter(
                Q(nome_completo__icontains=self.q) |
                Q(celular__icontains=self.q) |
                Q(cpf__icontains=self.q)
            )

        return qs


class VagaDisponivelOrdenadaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ServicoFuncionarioHorario.objects.none()

        qs = ServicoFuncionarioHorario.objects.filter(
            ativo=True,
            agendamento__isnull=True,
            data_horario__data_horario__gte=timezone.now()
        )

        if self.q:
            qs = qs.filter(
                Q(servico__nome_servico__icontains=self.q) |
                Q(funcionario__pessoa__nome_completo__icontains=self.q) |
                Q(data_horario__data_horario__icontains=self.q)
            )


        return qs.order_by('data_horario__data_horario', 'funcionario__pessoa__nome_completo')