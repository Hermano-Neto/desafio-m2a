from django.db import models


class StatusAgendamento(models.TextChoices):
    AGENDADO = 'AGENDADO', 'Agendado'
    CONCLUIDO = 'CONCLUIDO', 'Concluído'
    CANCELADO = 'CANCELADO', 'Cancelado'