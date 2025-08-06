from collections import defaultdict
import datetime
from io import BytesIO

from django.contrib import messages
from xhtml2pdf import pisa
from dal import autocomplete
from django.db.models import Q, Sum
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template.loader import get_template
from django.utils import timezone

from .models import Pessoa, ServicoFuncionarioHorario, Agendamento, DataHorario


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
            date_q = Q()
            search_term = self.q.strip()

            formatos= [
                '%d/%m/%Y',
                '%d/%m',
            ]

            for formato in formatos:
                try:
                    date_obj = datetime.datetime.strptime(search_term, formato)

                    if formato == '%d/%m':
                        current_year = timezone.now().year
                        date_obj = date_obj.replace(year=current_year)

                    date_q = Q(data_horario__data_horario__date=date_obj.date())

                except ValueError:
                    continue

            qs = qs.filter(
                Q(servico__nome_servico__icontains=self.q) |
                Q(funcionario__pessoa__nome_completo__icontains=self.q) |
                date_q
            )

        return qs.order_by('data_horario__data_horario', 'funcionario__pessoa__nome_completo')


class DataOrdenadaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return DataHorario.objects.none()

        qs = DataHorario.objects.filter(
            ativo=True,
            data_horario__gte=timezone.now()
        )

        if self.q:
            date_q = Q()
            search_term = self.q.strip()

            formatos= [
                '%d/%m/%Y',
                '%d/%m',
            ]

            for formato in formatos:
                try:
                    date_obj = datetime.datetime.strptime(search_term, formato)

                    if formato == '%d/%m':
                        current_year = timezone.now().year
                        date_obj = date_obj.replace(year=current_year)

                    date_q = Q(data_horario__date=date_obj.date())

                except ValueError:
                    continue

            qs = qs.filter(
                date_q
            )

        return qs.order_by('data_horario')



def gerar_relatorio_pdf(request):
    if not (request.user.is_superuser or request.user.groups.filter(name='Dono').exists()):
        messages.error(request, "Você não tem permissão para gerar este relatório.")
        return HttpResponseForbidden("Acesso Negado")

    params = request.GET
    data_inicio_str = params.get('servico_funcionario_horario__data_horario__data_horario__range__gte')
    data_fim_str = params.get('servico_funcionario_horario__data_horario__data_horario__range__lte')

    if not data_inicio_str or not data_fim_str:
        messages.error(
            request,
            "Por favor, selecione e confirme o filtro de intervalo de datas para gerar o relatório."
        )
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    filters = {}

    start_date = datetime.datetime.strptime(data_inicio_str, '%d/%m/%Y').date()
    end_date = datetime.datetime.strptime(data_fim_str, '%d/%m/%Y')

    filters['servico_funcionario_horario__data_horario__data_horario__gte'] = start_date
    filters['servico_funcionario_horario__data_horario__data_horario__lte'] = end_date.replace(hour=23, minute=59,
                                                                                               second=59)
    data_inicio_relatorio = start_date
    data_fim_relatorio = end_date.date()

    queryset = Agendamento.objects.filter(
        status='CONCLUIDO',
        **filters
    ).select_related(
        'servico_funcionario_horario__funcionario__pessoa',
        'servico_funcionario_horario__data_horario'
    ).prefetch_related('servico_funcionario_horario__servico')

    total_geral_ganhos = 0
    funcionarios_data = defaultdict(lambda: {'concluidos': 0, 'ganhos': 0})

    for agendamento in queryset:
        valor_agendamento = agendamento.servico_funcionario_horario.servico.all().aggregate(
            total=Sum('valor')
        )['total'] or 0
        total_geral_ganhos += valor_agendamento
        funcionario = agendamento.servico_funcionario_horario.funcionario
        funcionarios_data[funcionario.pessoa.nome_completo]['concluidos'] += 1
        funcionarios_data[funcionario.pessoa.nome_completo]['ganhos'] += valor_agendamento

    total_concluidos = queryset.count()

    context = {
        'total_concluidos': total_concluidos,
        'total_geral_ganhos': total_geral_ganhos,
        'funcionarios_data': dict(funcionarios_data),
        'data_geracao': datetime.date.today(),
        'data_inicio': data_inicio_relatorio,
        'data_fim': data_fim_relatorio,
    }

    template_path = 'agendamento/relatorio.html'
    template = get_template(template_path)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'filename="relatorio_{}.pdf"'.format(
            datetime.date.today().strftime('%Y-%m-%d')
        )
        return response

    return HttpResponse('Erro ao gerar o PDF: %s' % pdf.err)
