from datetime import timedelta

from django.contrib import admin
from django.db.models import Sum
from django.utils import timezone
from rangefilter.filters import DateRangeFilter

from .filtros import ValorRangeFilter
from .models import (
    Pessoa,
    Cliente,
    Servico,
    Funcionario,
    DataHorario,
    ServicoFuncionarioHorario,
    Agendamento
)
from .forms import (
    ClienteAdminForm,
    FuncionarioAdminForm,
    ServicoFuncionarioHorarioAdminForm,
    AgendamentoAdminForm
)


@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    search_fields = (
        'nome_completo',
        'celular',
        'cpf',
    )

    list_per_page = 20

    def get_fields(self, request, obj=None):
        if obj:
            return (
                'nome_completo',
                'data_nascimento',
                'cpf',
                'email',
                'celular',
                'ativo'
            )

        return (
            'nome_completo',
            'data_nascimento',
            'cpf',
            'email',
            'celular'
        )

    def get_list_display(self, request):
        if request.user.is_superuser:
            list_display = (
                'nome_completo',
                'data_nascimento',
                'cpf',
                'email',
                'celular',
                'ativo',
                'data_cadastro',
                'data_atualizacao',
            )

        elif request.user.groups.filter(name='Dono').exists():
            list_display = (
                'nome_completo',
                'data_nascimento',
                'cpf',
                'email',
                'celular',
            )

        elif request.user.groups.filter(name='Recepcionista').exists():
            list_display = (
                'nome_completo',
                'data_nascimento',
                'cpf',
                'email',
                'celular',
                'ativo'
            )

        else:
            list_display = (
                'id',
                'pessoa'
            )

        return list_display

    def get_list_filter(self, request):
        if request.user.is_superuser or request.user.groups.filter(name='Recepcionista').exists():
            list_filter = (
                'ativo',
            )

        else:
            list_filter = ()

        return list_filter


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    form = ClienteAdminForm
    search_fields = (
        'pessoa__nome_completo',
        'pessoa__cpf',
    )
    list_per_page = 20

    def get_fields(self, request, obj=None):
        if obj:
            return (
                'pessoa',
                'ativo',
            )

        return ('pessoa',)

    def get_list_display(self, request):
        if request.user.is_superuser:
            list_display = (
                'id',
                'pessoa',
                'get_ganho_previsto_mes',
                'get_ganho_total',
                'ativo',
                'data_cadastro',
                'data_atualizacao',
            )

        elif request.user.groups.filter(name='Dono').exists():
            list_display = (
                'id',
                'pessoa',
                'get_ganho_previsto_mes',
                'get_ganho_total',
            )

        elif request.user.groups.filter(name='Recepcionista').exists():
            list_display = (
                'id',
                'pessoa',
                'ativo',
            )

        else:
            list_display = (
                'id',
                'pessoa'
            )

        return list_display

    def get_list_filter(self, request):
        if request.user.is_superuser or request.user.groups.filter(name='Recepcionista').exists():
            list_filter = (
                'ativo',
            )

        else:
            list_filter = ()

        return list_filter

    @admin.display(description='Ganho Total')
    def get_ganho_total(self, obj):
        ganho_total = (Servico.objects.filter(
            servicofuncionariohorario__agendamento__cliente=obj,
            servicofuncionariohorario__agendamento__status='CONCLUIDO'
        ).values(
            'valor'
        ).aggregate(
            valor_total=Sum('valor')
        )['valor_total'])

        return f"R$ {ganho_total or 0:.2f}"

    @admin.display(description='Ganho Previsto (30 dias)')
    def get_ganho_previsto_mes(self, obj):
        hoje = timezone.now()
        proximos_trinta_dias = hoje + timedelta(days=30)

        ganho_previsto_mes = Servico.objects.filter(
            servicofuncionariohorario__agendamento__cliente=obj,
            servicofuncionariohorario__agendamento__status='AGENDADO',
            servicofuncionariohorario__data_horario__data_horario__range=(
                hoje,
                proximos_trinta_dias
            )
        ).aggregate(
            valor_previsto=Sum('valor')
        )['valor_previsto']

        return f"R$ {ganho_previsto_mes or 0:.2f}"


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    search_fields = (
        'nome_servico',
    )
    list_per_page = 20

    def get_fields(self, request, obj=None):
        if obj:
            return (
                'nome_servico',
                'valor',
                'duracao_minutos',
                'ativo',
            )

        return (
            'nome_servico',
            'valor',
            'duracao_minutos',
        )

    def get_list_display(self, request):
        if request.user.is_superuser:
            list_display = (
                'id',
                'nome_servico',
                'valor',
                'duracao_minutos',
                'ativo',
                'data_cadastro',
                'data_atualizacao',
            )

        elif request.user.groups.filter(name='Recepcionista').exists():
            list_display = (
                'id',
                'nome_servico',
                'valor',
                'duracao_minutos',
                'ativo',
            )

        else:
            list_display = (
                'id',
                'nome_servico',
                'valor',
                'duracao_minutos',
            )

        return list_display


    def get_list_filter(self, request):
        if request.user.is_superuser or request.user.groups.filter(name='Recepcionista').exists():
            list_filter = (
                'ativo',
                ValorRangeFilter
            )

        else:
            list_filter = ('valor',)

        return list_filter


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    form = FuncionarioAdminForm
    search_fields = (
        'pessoa__nome_completo',
        'pessoa__cpf',
        'servico__nome_servico'
    )
    list_per_page = 20

    def get_fields(self, request, obj=None):
        if obj:
            return (
                'pessoa',
                'servico',
                'ativo',
            )

        return (
            'pessoa',
            'servico',
        )

    def get_list_display(self, request):
        if request.user.is_superuser:
            list_display = (
                'id',
                'pessoa',
                'get_ganho_total',
                'get_ganho_previsto_mes',
                'get_servicos',
                'ativo',
                'data_cadastro',
                'data_atualizacao',
            )
        elif request.user.groups.filter(name='Dono').exists():
            list_display = (
                'id',
                'pessoa',
                'get_ganho_total',
                'get_ganho_previsto_mes',
                'get_servicos',
            )

        elif request.user.groups.filter(name='Recepcionista').exists():
            list_display = (
                'id',
                'pessoa',
                'get_servicos',
                'ativo',
            )

        else:
            list_display = (
                'id',
                'pessoa',
                'get_servicos',
            )

        return list_display

    def get_list_filter(self, request):
        if request.user.is_superuser or request.user.groups.filter(name='Recepcionista').exists():
            list_filter = (
                'ativo',
                'servico'
            )

        elif request.user.groups.filter(name='Dono').exists():
            list_filter = (
                'servico',
            )

        else:
            list_filter = ()

        return list_filter

    @admin.display(description='Serviço(s) que Executa')
    def get_servicos(self, obj):
        return ", ".join([s.nome_servico for s in obj.servico.all()])


    @admin.display(description='Ganho Total')
    def get_ganho_total(self, obj):
        ganho_total = (Servico.objects.filter(
            servicofuncionariohorario__agendamento__servico_funcionario_horario__funcionario=obj,
            servicofuncionariohorario__agendamento__status='CONCLUIDO'
        ).values(
            'valor'
        ).aggregate(
            valor_total=Sum('valor')
        )['valor_total'])

        return f"R$ {ganho_total or 0:.2f}"

    @admin.display(description='Ganho Previsto (30 dias)')
    def get_ganho_previsto_mes(self, obj):
        hoje = timezone.now()
        proximos_trinta_dias = hoje + timedelta(days=30)

        ganho_previsto_mes = Servico.objects.filter(
            servicofuncionariohorario__agendamento__servico_funcionario_horario__funcionario=obj,
            servicofuncionariohorario__agendamento__status='AGENDADO',
            servicofuncionariohorario__data_horario__data_horario__range=(
                hoje,
                proximos_trinta_dias
            )
        ).aggregate(
            valor_previsto=Sum('valor')
        )['valor_previsto']

        return f"R$ {ganho_previsto_mes or 0:.2f}"



@admin.register(DataHorario)
class DataHorarioAdmin(admin.ModelAdmin):
    search_fields = (
        'data_horario',
    )
    list_per_page = 20

    def get_fields(self, request, obj=None):
        if obj:
            return (
                'data_horario',
                'ativo',
            )

        return (
            'data_horario',
        )

    def get_list_display(self, request):
        if request.user.is_superuser:
            list_display = (
                'id',
                'data_horario',
                'ativo',
                'data_cadastro',
                'data_atualizacao',
            )

        elif request.user.groups.filter(name='Recepcionista').exists():
            list_display = (
                'id',
                'data_horario',
                'ativo',
            )

        else:
            list_display = (
                'id',
                'data_horario',
            )

        return list_display

    def get_list_filter(self, request):
        if request.user.is_superuser or request.user.groups.filter(name='Recepcionista').exists():
            list_filter = (
                'ativo',
                ('data_horario', DateRangeFilter),
            )

        else:
            list_filter = (('data_horario', DateRangeFilter),)

        return list_filter


@admin.register(ServicoFuncionarioHorario)
class ServicoFuncionarioHorarioAdmin(admin.ModelAdmin):
    form = ServicoFuncionarioHorarioAdminForm
    search_fields = (
        'funcionario__pessoa__nome_completo',
        'data_horario__data_horario',
        'servico__nome_servico',
    )
    autocomplete_fields = (
        'funcionario',
        'data_horario',
    )
    list_per_page = 20

    @admin.display(description='Serviço(s)')
    def get_servicos(self, obj):
        return ", ".join([s.nome_servico for s in obj.servico.all()])

    def get_fields(self, request, obj=None):
        if obj:
            return (
                'funcionario',
                'data_horario',
                'servico',
                'ativo',
            )

        return (
            'funcionario',
            'data_horario',
            'servico',
        )

    def get_list_display(self, request):
        if request.user.is_superuser:
            list_display = (
                'id',
                'funcionario',
                'data_horario',
                'get_servicos',
                'ativo',
                'data_cadastro',
                'data_atualizacao',
            )

        elif request.user.groups.filter(name='Recepcionista').exists():
            list_display = (
                'id',
                'funcionario',
                'data_horario',
                'get_servicos',
                'ativo',
            )

        else:
            list_display = (
                'id',
                'funcionario',
                'data_horario',
                'get_servicos',
            )

        return list_display

    def get_list_filter(self, request):
        if request.user.is_superuser or request.user.groups.filter(name='Recepcionista').exists():
            list_filter = (
                ('data_horario__data_horario', DateRangeFilter),
                'funcionario',
                'servico',
                'ativo',
            )

        else:
            list_filter = (
                ('data_horario__data_horario', DateRangeFilter),
                'funcionario',
                'servico',
            )

        return list_filter


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    form = AgendamentoAdminForm
    search_fields = (
        'cliente__pessoa__nome_completo',
        'servico_funcionario_horario__funcionario__pessoa__nome_completo',
        'status',
    )
    autocomplete_fields = (
        'cliente',
        'servico_funcionario_horario',
    )
    list_per_page = 20

    def get_fields(self, request, obj=None):
        if obj:
            return (
                'cliente',
                'servico_funcionario_horario',
                'status',
                'ativo',
            )

        return (
            'cliente',
            'servico_funcionario_horario',
            'status',
        )

    def get_list_display(self, request):
        if request.user.is_superuser:
            list_display = (
                'id',
                'cliente',
                'get_data_horario',
                'get_funcionario',
                'get_servicos',
                'status',
                'ativo',
                'data_cadastro',
                'data_atualizacao',
            )

        elif request.user.groups.filter(name='Recepcionista').exists():
            list_display = (
                'id',
                'cliente',
                'get_data_horario',
                'get_funcionario',
                'get_servicos',
                'status',
                'ativo',
            )

        else:
            list_display = (
                'id',
                'cliente',
                'get_data_horario',
                'get_funcionario',
                'get_servicos',
                'status',
            )

        return list_display

    def get_list_filter(self, request):
        if request.user.is_superuser or request.user.groups.filter(name='Recepcionista').exists():
            list_filter = (
                ('servico_funcionario_horario__data_horario__data_horario', DateRangeFilter),
                'status',
                'servico_funcionario_horario__funcionario',
                'ativo',
            )

        else:
            list_filter = (
                ('servico_funcionario_horario__data_horario__data_horario', DateRangeFilter),
                'status',
                'servico_funcionario_horario__funcionario',
            )

        return list_filter

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['servico_funcionario_horario'].label = 'Vaga de Atendimento'

        return form

    @admin.display(description='Serviço(s) Agendados')
    def get_servicos(self, obj):
        if obj.servico_funcionario_horario:
            return ", ".join([s.nome_servico for s in obj.servico_funcionario_horario.servico.all()])
        return "N/A"

    @admin.display(description='Funcionário')
    def get_funcionario(self, obj):
        return obj.servico_funcionario_horario.funcionario

    @admin.display(description='Data e Horário', ordering='servico_funcionario_horario__data_horario')
    def get_data_horario(self, obj):
        return obj.servico_funcionario_horario.data_horario

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['user_can_generate_report'] = (
                request.user.is_superuser or
                request.user.groups.filter(name='Dono').exists()
        )
        return super().changelist_view(request, extra_context=extra_context)