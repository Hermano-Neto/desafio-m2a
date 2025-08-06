from dal import autocomplete
from django import forms
from django.urls import reverse_lazy
from django_select2.forms import Select2MultipleWidget
from .models import Pessoa, Cliente, Funcionario, Servico, ServicoFuncionarioHorario, Agendamento, DataHorario

pessoa_autocomplete_widget = autocomplete.ModelSelect2(
    url=reverse_lazy('agendamento:pessoa-disponivel-autocomplete'),
    attrs={'data-placeholder': 'Busque pelo nome ou CPF'}
)

class ClienteAdminForm(forms.ModelForm):
    """
    Formulário para o admin do modelo Cliente. Substitui o campo de seleção padrão de 'pessoa' por um widget de
    autocomplete para facilitar a busca de pessoas disponíveis.
    """
    pessoa = forms.ModelChoiceField(
        queryset=Pessoa.objects.all(),
        widget=pessoa_autocomplete_widget
    )

    class Meta:
        model = Cliente
        fields = '__all__'


class FuncionarioAdminForm(forms.ModelForm):
    """
    Formulário para o admin do modelo Funcionario. Customiza o campo 'pessoa' com um widget de autocomplete e o campo
    'servico' com um widget de seleção múltipla aprimorado.
    """
    pessoa = forms.ModelChoiceField(
        queryset=Pessoa.objects.all(),
        widget=pessoa_autocomplete_widget
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
    """
    Formulário para o admin de Vagas de Atendimento (ServicoFuncionarioHorario). Aplica widgets de seleção aprimorados
    para os campos 'servico' e 'data_horario', facilitando a criação da vaga de atendimento.
    """
    servico = forms.ModelMultipleChoiceField(
        queryset=Servico.objects.all(),
        widget=Select2MultipleWidget,
        label='Serviços que Executa',
    )

    data_horario = forms.ModelChoiceField(
        queryset=DataHorario.objects.all(),
        label='Data',
        widget=autocomplete.ModelSelect2(
            url=reverse_lazy('agendamento:data-ordenada-autocomplete'),
            attrs={'data-placeholder': 'Busque pela data (ex: 25/12/2025)'}
        )
    )

    class Meta:
        model = ServicoFuncionarioHorario
        fields = '__all__'


class AgendamentoAdminForm(forms.ModelForm):
    """
    Formulário para o admin do modelo Agendamento. Otimiza o processo de agendamento ao substituir o campo de seleção de
    'servico_funcionario_horario' por um widget de autocomplete avançado.
    """
    servico_funcionario_horario = forms.ModelChoiceField(
        queryset=ServicoFuncionarioHorario.objects.all(),
        help_text= 'Busque por data, funcionário ou serviço',
        widget=autocomplete.ModelSelect2(
            url=reverse_lazy('agendamento:vaga-disponivel-ordenada-autocomplete'),
)
    )

    class Meta:
        model = Agendamento
        fields = '__all__'
