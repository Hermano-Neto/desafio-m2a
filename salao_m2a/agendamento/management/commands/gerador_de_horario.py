from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from agendamento.models import DataHorario

class Command(BaseCommand):
    help = 'Garante que existam horários de atendimento criados para os próximos 6 meses.'

    def handle(self, *args, **options):
        self.stdout.write("Verificando e criando horários futuros...")

        hoje = timezone.now().date()
        data_limite = hoje + timedelta(days=180) # 6 meses a frente

        # Encontra a última data já cadastrada no banco
        ultimo_horario = DataHorario.objects.order_by('-data_horario').first()

        # Se não houver nenhum horário, começa a partir de hoje.
        # Se houver, começa a partir do dia seguinte ao último cadastrado.
        if ultimo_horario:
            data_inicial = ultimo_horario.data_horario.date() + timedelta(days=1)
        else:
            data_inicial = hoje

        if data_inicial > data_limite:
            self.stdout.write(self.style.SUCCESS('Horários já existem para os próximos 6 meses. Nenhuma ação necessária.'))
            return

        horarios_a_criar = []
        current_date = data_inicial

        while current_date <= data_limite:
            if current_date.weekday() < 6:  # Segunda a Sábado (0-5)
                start_hour, end_hour = 8, 19
            else:  # Domingo (6)
                start_hour, end_hour = 9, 15

            for hour in range(start_hour, end_hour):
                for minute in [0, 30]:
                    dt = timezone.make_aware(
                        timezone.datetime(current_date.year, current_date.month, current_date.day, hour, minute)
                    )
                    horarios_a_criar.append(DataHorario(data_horario=dt))

            current_date += timedelta(days=1)

        if horarios_a_criar:
            DataHorario.objects.bulk_create(horarios_a_criar)
            self.stdout.write(self.style.SUCCESS(f'{len(horarios_a_criar)} novos horários criados com sucesso até {data_limite}.'))
        else:
            self.stdout.write("Nenhum novo horário precisou ser criado.")