from django.db import models
from django.core.validators import RegexValidator

from .choices import StatusAgendamento

class BaseModel(models.Model):
    ativo = models.BooleanField(
        verbose_name='Ativo',
        default=True
    )
    data_cadastro = models.DateTimeField(
        verbose_name='Data de Cadastro',
        auto_now_add=True
    )
    data_atualizacao = models.DateTimeField(
        verbose_name='Data de Atualização',
        auto_now=True
    )

    class Meta:
        abstract = True


class Pessoa(BaseModel):
    validador_celular = RegexValidator(
        regex=r'^\(\d{2}\) \d{5}-\d{4}$',
        message="O número de celular deve estar no formato: (XX) XXXXX-XXXX"
    )

    validador_cpf = RegexValidator(
        regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
        message="O CPF deve estar no formato: XXX.XXX.XXX-XX"
    )

    nome_completo = models.CharField(
        verbose_name='Nome Completo',
        max_length=255
    )
    data_nascimento = models.DateField(
        verbose_name='Data de Nascimento',
        null=True,
        blank=True
    )
    cpf = models.CharField(
        verbose_name='CPF',
        max_length=14,
        unique=True,
        help_text='Digite o CPF no formato: XXX.XXX.XXX-XX',
        validators=[validador_cpf]
    )
    email = models.EmailField(
        verbose_name='E-mail',
        unique=True
    )
    celular = models.CharField(
        verbose_name='Celular com DDD',
        max_length=15,
        help_text='Digite o número do celular dentro do padrão (XX) XXXXX-XXXX',
        validators=[validador_celular]
    )


    class Meta:
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'

    def __str__(self):
        return self.nome_e_sobrenome

    @property
    def nome_e_sobrenome(self):
        if not self.nome_completo:
            return ""
        partes = self.nome_completo.strip().split()

        if len(partes) > 1:
            return f"{partes[0]} {partes[-1]}"
        else:
            return partes[0]


class Cliente(BaseModel):
    pessoa = models.OneToOneField(
        Pessoa,
        verbose_name='Pessoa',
        on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.pessoa.nome_e_sobrenome


class Servico(BaseModel):
    nome_servico = models.CharField(
        verbose_name='Nome do serviço',
        max_length=100
    )
    valor = models.DecimalField(
        verbose_name='Valor',
        max_digits=7,
        decimal_places=2
    )
    duracao_minutos = models.PositiveIntegerField(
        verbose_name='Duração em Minutos',
        default=30
    )

    def __str__(self):
        return self.nome_servico


class Funcionario(BaseModel):
    pessoa = models.OneToOneField(
        Pessoa,
        verbose_name='Pessoa',
        on_delete=models.PROTECT
    )
    servico = models.ManyToManyField(
        Servico,
        verbose_name='Serviços que Executa'
    )

    def __str__(self):
        return self.pessoa.nome_e_sobrenome


class DataHorario(BaseModel):
    data_horario = models.DateTimeField(
        verbose_name='Data'
    )

    def __str__(self):
        return self.data_horario.strftime("%d/%m/%Y %H:%M")


class ServicoFuncionarioHorario(BaseModel):
    funcionario = models.ForeignKey(
        Funcionario,
        verbose_name='Funcionario',
        on_delete=models.PROTECT
    )

    servico = models.ManyToManyField(
        Servico,
        verbose_name='Serviço(s)'
    )

    data_horario = models.ForeignKey(
        DataHorario,
        verbose_name='Data',
        on_delete=models.PROTECT
    )

    class Meta:
        unique_together = ('funcionario', 'data_horario')
        verbose_name = 'Vaga de Atendimento'
        verbose_name_plural = 'Vagas de Atendimento'

    def __str__(self):
        nomes_servicos = ", ".join([s.nome_servico for s in self.servico.all()])
        return f'{self.funcionario} - {self.data_horario} - Serviços: {nomes_servicos}'


class Agendamento(BaseModel):
    cliente = models.ForeignKey(
        Cliente,
        verbose_name='Cliente',
        on_delete=models.SET_NULL,
        null=True
    )

    servico_funcionario_horario = models.OneToOneField(
        ServicoFuncionarioHorario,
        verbose_name='Vaga de Atendimento',
        on_delete=models.PROTECT,
        default=None
    )

    status = models.CharField(
        verbose_name='Status',
        max_length=20,
        choices=StatusAgendamento.choices,
        default=StatusAgendamento.AGENDADO,
    )

    def __str__(self):
        nome_cliente = self.cliente.pessoa.nome_e_sobrenome if self.cliente else "Cliente Removido"
        return f"{nome_cliente} - {self.servico_funcionario_horario}"