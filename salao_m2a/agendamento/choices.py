from django.db import models


class StatusAgendamento(models.TextChoices):
    """
    Oferece status fixos para um Agendamento, dando um valor para o banco de dados e um rótulo legível para exibição.
    """
    AGENDADO = 'AGENDADO', 'Agendado'
    CONCLUIDO = 'CONCLUIDO', 'Concluído'
    CANCELADO = 'CANCELADO', 'Cancelado'