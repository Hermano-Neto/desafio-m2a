from dal import autocomplete
from django import forms
from django.urls import reverse_lazy
from django_select2.forms import Select2MultipleWidget
from .models import Pessoa, Cliente, Funcionario, Servico, ServicoFuncionarioHorario, Agendamento

pessoa_autocomplete_widget = autocomplete.ModelSelect2(
    url=reverse_lazy('agendamento:pessoa-disponivel-autocomplete'),
    attrs={'data-placeholder': 'Busque pelo nome ou CPF'}
)

class ClienteAdminForm(forms.ModelForm):
    pessoa = forms.ModelChoiceField(
        queryset=Pessoa.objects.all(),
        widget=pessoa_autocomplete_widget
    )

    class Meta:
        model = Cliente
        fields = '__all__'


class FuncionarioAdminForm(forms.ModelForm):
    pessoa = forms.ModelChoiceField(
        queryset=Pessoa.objects.all(),
        widget=autocomplete.ModelSelect2(
            url=reverse_lazy('agendamento:pessoa-disponivel-autocomplete'),
            attrs={'data-placeholder': 'Busque pelo nome ou CPF'}
        )
    )

    servico = forms.ModelMultipleChoiceField(
        queryset=Servico.objects.all(),
        widget=Select2MultipleWidget,
        label='Serviços que Executa',
    )

    class Meta:
        model = Funcionario
        fields = '__all__'


class ServicoFuncionarioHorarioAdminForm(forms.ModelForm):
    servico = forms.ModelMultipleChoiceField(
        queryset=Servico.objects.all(),
        widget=Select2MultipleWidget,
        label='Serviços que Executa',
    )

    class Meta:
        model = ServicoFuncionarioHorario
        fields = '__all__'


class AgendamentoAdminForm(forms.ModelForm):
    servico_funcionario_horario = forms.ModelChoiceField(
        queryset=ServicoFuncionarioHorario.objects.all(),
        help_text= 'Busque por horário, funcionário e/ou serviço',
        widget=autocomplete.ModelSelect2(
            url=reverse_lazy('agendamento:vaga-disponivel-odernada-autocomplete'),
)
    )

    class Meta:
        model = Agendamento
        fields = '__all__'

