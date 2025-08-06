import random
from datetime import timedelta
from faker import Faker
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from agendamento.models import (
    Pessoa,
    Cliente,
    Funcionario,
    Servico,
    DataHorario,
    ServicoFuncionarioHorario,
    Agendamento,
)

# --- CONSTANTES DE CONFIGURAÇÃO ---
TOTAL_PESSOAS = 10000
TOTAL_FUNCIONARIOS_PERFIL = 60
FUNCIONARIOS_INATIVOS = 40

# Novos usuários a serem criados
NUM_DONOS = 1
NUM_RECEPCIONISTAS = 5
NUM_FUNCIONARIOS_USUARIOS = 20

TOTAL_CLIENTES = TOTAL_PESSOAS - (NUM_DONOS + NUM_RECEPCIONISTAS + TOTAL_FUNCIONARIOS_PERFIL)


class Command(BaseCommand):
    """
    Comando do Django para limpar e popular o banco de dados com dados de teste.
    """

    help = 'Limpa e popula o banco de dados com dados de teste completos, incluindo usuários e permissões.'

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Ponto de entrada principal para a execução do comando. Organiza a chamada dos métodos auxiliares na ordem
        correta para popular o banco.
        """

        self.stdout.write("Iniciando a configuração completa do salão...")

        self._limpar_dados()
        self._criar_grupos_e_permissoes()
        servicos = self._criar_servicos()
        pessoas = self._criar_pessoas()
        self._criar_usuarios_e_perfis(pessoas)
        self._atribuir_servicos_especializados(servicos)
        self._criar_horarios_disponiveis()
        self._criar_vagas_de_atendimento()
        self._criar_agendamentos()

        self.stdout.write(self.style.SUCCESS('Configuração do salão concluída com sucesso!'))

    def _limpar_dados(self):
        """
        Remove todos os dados das tabelas do app 'agendamento', bem como usuários (exceto superusuários) e grupos, para
        garantir um novo começo.
        """

        self.stdout.write("Limpando dados existentes...")
        Agendamento.objects.all().delete()
        ServicoFuncionarioHorario.objects.all().delete()
        DataHorario.objects.all().delete()
        Cliente.objects.all().delete()
        Funcionario.objects.all().delete()
        Servico.objects.all().delete()
        Pessoa.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        Group.objects.all().delete()
        self.stdout.write("Dados limpos.")

    def _criar_grupos_e_permissoes(self):
        """
        Cria os grupos de usuários (Dono, Recepcionista e Funcionário) atribuindo cada um a um conjunto específico de
        permissões.
        """

        self.stdout.write("Criando grupos e definindo permissões...")

        app_models = [
            Pessoa,
            Cliente,
            Funcionario,
            Servico,
            DataHorario,
            ServicoFuncionarioHorario,
            Agendamento
        ]

        content_types = []
        for model in app_models:
            content_types.append(ContentType.objects.get_for_model(model))

        perm_recepcionista = Permission.objects.filter(content_type__in=content_types)
        grupo_recepcionista, _ = Group.objects.get_or_create(name='Recepcionista')
        grupo_recepcionista.permissions.set(perm_recepcionista)

        perm_funcionario = Permission.objects.filter(
            content_type__in=content_types,
            codename__startswith='view_'
        )
        grupo_funcionario, _ = Group.objects.get_or_create(name='Funcionário')
        grupo_funcionario.permissions.set(perm_funcionario)

        perm_dono = Permission.objects.filter(content_type__in=content_types)
        perm_excluir_dono = Permission.objects.filter(
            content_type__in=[
                ContentType.objects.get_for_model(DataHorario),
                ContentType.objects.get_for_model(ServicoFuncionarioHorario)
            ]
        ).exclude(codename__startswith='view_')

        perm_dono_final = perm_dono.exclude(pk__in=perm_excluir_dono.values_list('pk', flat=True))
        grupo_dono, _ = Group.objects.get_or_create(name='Dono')
        grupo_dono.permissions.set(perm_dono_final)

        self.stdout.write("Grupos e permissões criados.")

    def _criar_servicos(self):
        """
        Popula o banco de dados com uma lista predefinida de serviços e combos oferecidos pelo salão.
        """

        self.stdout.write("Criando serviços...")
        servicos_data = [
            {'nome_servico': 'Corte de Cabelo (Feminino)', 'valor': 90.00, 'duracao_minutos': 60},
            {'nome_servico': 'Corte de Cabelo (Masculino)', 'valor': 50.00, 'duracao_minutos': 30},
            {'nome_servico': 'Corte de Cabelo (Infantil)', 'valor': 45.00, 'duracao_minutos': 30},
            {'nome_servico': 'Aparar Franja', 'valor': 25.00, 'duracao_minutos': 30},
            {'nome_servico': 'Lavagem Simples', 'valor': 30.00, 'duracao_minutos': 30},
            {'nome_servico': 'Hidratação Simples', 'valor': 80.00, 'duracao_minutos': 60},
            {'nome_servico': 'Hidratação Profunda (Reconstrução)', 'valor': 150.00, 'duracao_minutos': 90},
            {'nome_servico': 'Escova (Cabelo Curto)', 'valor': 50.00, 'duracao_minutos': 30},
            {'nome_servico': 'Escova (Cabelo Médio)', 'valor': 70.00, 'duracao_minutos': 60},
            {'nome_servico': 'Escova (Cabelo Longo)', 'valor': 90.00, 'duracao_minutos': 60},
            {'nome_servico': 'Pintura (Raiz)', 'valor': 150.00, 'duracao_minutos': 120},
            {'nome_servico': 'Pintura (Global)', 'valor': 220.00, 'duracao_minutos': 150},
            {'nome_servico': 'Mechas / Luzes', 'valor': 350.00, 'duracao_minutos': 240},
            {'nome_servico': 'Escova Progressiva', 'valor': 300.00, 'duracao_minutos': 180},
            {'nome_servico': 'Botox Capilar', 'valor': 180.00, 'duracao_minutos': 120},
            {'nome_servico': 'Penteado para Festas', 'valor': 150.00, 'duracao_minutos': 90},
            {'nome_servico': 'Penteado para Noivas (com prévia)', 'valor': 500.00, 'duracao_minutos': 180},

            # --- UNHAS ---
            {'nome_servico': 'Manicure (Tradicional)', 'valor': 30.00, 'duracao_minutos': 30},
            {'nome_servico': 'Pedicure (Tradicional)', 'valor': 40.00, 'duracao_minutos': 30},
            {'nome_servico': 'Esmaltação em Gel', 'valor': 80.00, 'duracao_minutos': 60},
            {'nome_servico': 'Aplicação de Unha de Gel', 'valor': 150.00, 'duracao_minutos': 120},
            {'nome_servico': 'Manutenção de Unha de Gel', 'valor': 100.00, 'duracao_minutos': 90},
            {'nome_servico': 'Spa dos Pés', 'valor': 70.00, 'duracao_minutos': 60},
            {'nome_servico': 'Plástica dos Pés', 'valor': 90.00, 'duracao_minutos': 60},

            # --- ROSTO E ESTÉTICA FACIAL ---
            {'nome_servico': 'Maquiagem Social (Dia)', 'valor': 120.00, 'duracao_minutos': 60},
            {'nome_servico': 'Maquiagem Festa (Noite)', 'valor': 180.00, 'duracao_minutos': 90},
            {'nome_servico': 'Maquiagem Noiva (com prévia)', 'valor': 600.00, 'duracao_minutos': 150},
            {'nome_servico': 'Design de Sobrancelha (Pinça)', 'valor': 40.00, 'duracao_minutos': 30},
            {'nome_servico': 'Design de Sobrancelha com Henna', 'valor': 60.00, 'duracao_minutos': 60},
            {'nome_servico': 'Micropigmentação de Sobrancelha', 'valor': 450.00, 'duracao_minutos': 150},
            {'nome_servico': 'Extensão de Cílios (Fio a Fio)', 'valor': 180.00, 'duracao_minutos': 120},
            {'nome_servico': 'Lash Lifting', 'valor': 130.00, 'duracao_minutos': 90},
            {'nome_servico': 'Limpeza de Pele Simples', 'valor': 100.00, 'duracao_minutos': 60},
            {'nome_servico': 'Limpeza de Pele Profunda com Extração', 'valor': 150.00, 'duracao_minutos': 90},
            {'nome_servico': 'Peeling de Diamante', 'valor': 120.00, 'duracao_minutos': 60},

            # --- DEPILAÇÃO (Cera) ---
            {'nome_servico': 'Depilação Buço', 'valor': 20.00, 'duracao_minutos': 30},
            {'nome_servico': 'Depilação Axilas', 'valor': 30.00, 'duracao_minutos': 30},
            {'nome_servico': 'Depilação Meia Perna', 'valor': 40.00, 'duracao_minutos': 30},
            {'nome_servico': 'Depilação Perna Inteira', 'valor': 70.00, 'duracao_minutos': 60},
            {'nome_servico': 'Depilação Virilha Simples', 'valor': 45.00, 'duracao_minutos': 30},
            {'nome_servico': 'Depilação Virilha Completa', 'valor': 60.00, 'duracao_minutos': 60},

            # --- ESTÉTICA CORPORAL E BEM-ESTAR ---
            {'nome_servico': 'Massagem Relaxante (50 min)', 'valor': 120.00, 'duracao_minutos': 60},
            {'nome_servico': 'Massagem Modeladora (Sessão)', 'valor': 100.00, 'duracao_minutos': 60},
            {'nome_servico': 'Drenagem Linfática (Sessão)', 'valor': 110.00, 'duracao_minutos': 60},
            {'nome_servico': 'Banho de Lua (Douramento de pelos)', 'valor': 90.00, 'duracao_minutos': 90},

            # --- COMBOS DE CABELO ---
            {'nome_servico': 'Combo: Corte Feminino + Lavagem', 'valor': 110.00, 'duracao_minutos': 90},
            {'nome_servico': 'Combo: Corte Feminino + Escova (Média)', 'valor': 150.00, 'duracao_minutos': 120},
            {'nome_servico': 'Combo: Lavagem + Escova (Média)', 'valor': 90.00, 'duracao_minutos': 60},
            {'nome_servico': 'Combo: Corte + Hidratação Simples + Escova', 'valor': 220.00, 'duracao_minutos': 180},
            {'nome_servico': 'Combo: Pintura (Raiz) + Escova (Curta)', 'valor': 185.00, 'duracao_minutos': 150},

            # --- COMBOS DE MÃOS E PÉS ---
            {'nome_servico': 'Combo: Manicure + Pedicure (Tradicional)', 'valor': 65.00, 'duracao_minutos': 60},
            {'nome_servico': 'Combo: Manicure + Spa dos Pés', 'valor': 90.00, 'duracao_minutos': 90},
            {'nome_servico': 'Combo: Pedicure + Plástica dos Pés', 'valor': 120.00, 'duracao_minutos': 90},

            # --- COMBOS FACIAIS ---
            {'nome_servico': 'Combo Olhar: Design de Sobrancelha + Lash Lifting', 'valor': 160.00,
             'duracao_minutos': 120},
            {'nome_servico': 'Combo Rosto Limpo: Limpeza Profunda + Peeling de Diamante', 'valor': 250.00,
             'duracao_minutos': 150},
            {'nome_servico': 'Combo Rápido: Design de Sobrancelha + Buço', 'valor': 55.00, 'duracao_minutos': 30},

            # --- COMBOS DE DEPILAÇÃO ---
            {'nome_servico': 'Combo Depilação 1: Meia Perna + Virilha Simples + Axilas', 'valor': 105.00,
             'duracao_minutos': 90},
            {'nome_servico': 'Combo Depilação 2: Perna Inteira + Virilha Completa + Axilas', 'valor': 150.00,
             'duracao_minutos': 120},

            # --- PACOTES ESPECIAIS (FESTAS) ---
            {'nome_servico': 'Pacote Festa Essencial: Penteado + Maquiagem Social', 'valor': 310.00,
             'duracao_minutos': 150},
            {'nome_servico': 'Pacote Formanda/Madrinha: Penteado + Maquiagem + Manicure', 'valor': 330.00,
             'duracao_minutos': 180},
            {'nome_servico': 'Pacote Noiva Prata: Penteado (c/ prévia) + Maquiagem (c/ prévia) + Manicure',
             'valor': 1100.00, 'duracao_minutos': 300},
            {
            'nome_servico': 'Pacote Noiva Ouro: Penteado (c/ prévia) + Maquiagem (c/ prévia) + Manicure + Pedicure + Design de Sobrancelha',
            'valor': 1200.00, 'duracao_minutos': 360},
        ]

        servicos = []
        for data in servicos_data:
            servicos.append(Servico(**data))

        Servico.objects.bulk_create(servicos)
        self.stdout.write(f"{len(servicos)} serviços criados.")

        return list(Servico.objects.all())

    def _criar_pessoas(self):
        """
        Cria um grande volume de registros de Pessoas com dados fictícios usando a biblioteca Faker.
        """

        self.stdout.write("Criando pessoas...")
        faker = Faker('pt_BR')
        pessoas_a_criar = [
            Pessoa(
                nome_completo=faker.name(),
                email=faker.unique.email(),
                cpf=faker.unique.cpf(),
                celular=faker.msisdn()[:11],
                data_nascimento=faker.date_of_birth(minimum_age=16, maximum_age=80),
            ) for _ in range(TOTAL_PESSOAS)
        ]
        Pessoa.objects.bulk_create(
            pessoas_a_criar,
            batch_size=1000
        )
        self.stdout.write(f"{TOTAL_PESSOAS} pessoas criadas.")

        return list(Pessoa.objects.all())

    def _criar_usuarios_e_perfis(self, pessoas):
        """
        Converte os registros de Pessoa em usuários do sistema (Dono, Recepcionista e Funcionário) e perfis
        (Funcionario e Cliente).
        """

        self.stdout.write("Criando usuários, funcionários e clientes...")
        random.shuffle(pessoas)

        grupo_dono = Group.objects.get(name='Dono')
        grupo_recepcionista = Group.objects.get(name='Recepcionista')
        grupo_funcionario = Group.objects.get(name='Funcionário')

        senha_padrao = 'teste1234'

        pessoas.pop()

        # Cria o usuário do dono
        user_dono = User.objects.create_user(
            username='Dono',
            password=senha_padrao,
            is_staff=True
        )
        user_dono.groups.add(grupo_dono)

        # Cria os (as) receptionistas
        for i in range(NUM_RECEPCIONISTAS):
            pessoas.pop()
            user_rec = User.objects.create_user(
                username=f'recepcionista_{i + 1}',
                password=senha_padrao,
                is_staff=True
            )
            user_rec.groups.add(grupo_recepcionista)

        funcionarios_com_login = []

        # Cria os funcionários
        for i in range(NUM_FUNCIONARIOS_USUARIOS):
            pessoa_func = pessoas.pop()
            user_func = User.objects.create_user(
                username=f'funcionario_{i + 1}',
                password=senha_padrao,
                is_staff=True
            )
            user_func.groups.add(grupo_funcionario)
            funcionarios_com_login.append(Funcionario(pessoa=pessoa_func))

        outros_funcionarios = [Funcionario(pessoa=pessoas.pop()) for _ in
                               range(TOTAL_FUNCIONARIOS_PERFIL - NUM_FUNCIONARIOS_USUARIOS)]

        todos_funcionarios = funcionarios_com_login + outros_funcionarios
        Funcionario.objects.bulk_create(todos_funcionarios)

        clientes = []
        for p in pessoas:
            clientes.append(Cliente(pessoa=p))

        Cliente.objects.bulk_create(clientes)

        self.stdout.write(
            f"Usuários criados: 1 Dono, {NUM_RECEPCIONISTAS} Recepcionistas, {NUM_FUNCIONARIOS_USUARIOS} Funcionários.")
        self.stdout.write(f"Perfis criados: {TOTAL_FUNCIONARIOS_PERFIL} Funcionários, {len(clientes)} Clientes.")

    def _atribuir_servicos_especializados(self, servicos):
        """
        Distribui os serviços entre os funcionários de forma controlada, garantindo que cada serviço seja coberto por
        pelo menos um profissional e que cada profissional tenha um conjunto variado de serviços.
        """

        self.stdout.write("Atribuindo serviços de forma aleatória e controlada...")
        funcionarios = list(Funcionario.objects.all())
        servicos_lista = list(servicos)

        if not funcionarios:
            self.stdout.write(self.style.WARNING("Nenhum funcionário encontrado para atribuir serviços."))
            return

        # Atribuição de serviço ao funcionário
        for servico in servicos_lista:
            funcionario_escolhido = random.choice(funcionarios)
            funcionario_escolhido.servico.add(servico)

        # limitador de quantidade de serviços
        for func in funcionarios:
            servicos_atuais_count = func.servico.count()

            if servicos_atuais_count >= 10:
                continue

            limite_para_adicionar = 10 - servicos_atuais_count
            num_servicos_extras = random.randint(0, limite_para_adicionar)

            if num_servicos_extras > 0:
                servicos_extras = random.sample(servicos_lista, k=num_servicos_extras)
                func.servico.add(*servicos_extras)

        self.stdout.write("Serviços distribuídos com sucesso.")

    def _criar_horarios_disponiveis(self):
        """
        Cria todos os slots de DataHorario em intervalos de 30 minutos para um período extenso (passado e futuro),
        servindo como base para as vagas de atendimento.
        """

        self.stdout.write("Criando datas e horários disponíveis...")
        start_date = timezone.now().date() - timedelta(days=90)
        end_date = timezone.now().date() + timedelta(days=180)
        current_date = start_date
        horarios = []

        while current_date <= end_date:
            if current_date.weekday() < 6:  # Segunda a Sábado (0-5)
                start_hour, end_hour = 8, 19
            else:  # Domingo (6)
                start_hour, end_hour = 9, 15

            for hour in range(start_hour, end_hour):
                for minute in [0, 30]:
                    dt = timezone.make_aware(
                        timezone.datetime(current_date.year, current_date.month, current_date.day, hour, minute))
                    horarios.append(DataHorario(data_horario=dt))
            current_date += timedelta(days=1)

        DataHorario.objects.bulk_create(horarios, batch_size=1000)
        self.stdout.write(f"{len(horarios)} slots de data/horário criados.")

    def _criar_vagas_de_atendimento(self):
        """
        Cria as Vagas de Atendimento, associando funcionários a horários específicos com base em padrões de trabalho
        aleatórios e atribuindo serviços ou combos de serviços a cada vaga.
        """

        self.stdout.write("Criando vagas de atendimento (com possíveis combos)...")
        funcionarios = list(Funcionario.objects.filter(ativo=True))
        horarios_todos = list(DataHorario.objects.all())
        vagas_criadas = []

        # Distribuição de horário para funcionários, com lógica básica de dias de trabalho
        for func in funcionarios:
            padrao_trabalho = random.choice(['integral', 'manha', 'tarde', 'fds'])

            for horario in horarios_todos:
                dia_da_semana = horario.data_horario.weekday()
                hora = horario.data_horario.hour
                trabalha_neste_horario = False

                if padrao_trabalho == 'integral' and dia_da_semana < 5:
                    trabalha_neste_horario = True

                elif padrao_trabalho == 'manha' and dia_da_semana < 6 and hora < 13:
                    trabalha_neste_horario = True

                elif padrao_trabalho == 'tarde' and dia_da_semana < 6 and hora >= 13:
                    trabalha_neste_horario = True

                elif padrao_trabalho == 'fds' and dia_da_semana >= 5:
                    trabalha_neste_horario = True

                if trabalha_neste_horario:
                    vagas_criadas.append(ServicoFuncionarioHorario(
                        funcionario=func,
                        data_horario=horario
                    ))

        ServicoFuncionarioHorario.objects.bulk_create(vagas_criadas, batch_size=1000)
        self.stdout.write(f"{len(vagas_criadas)} vagas base criadas.")

        self.stdout.write("Atribuindo serviços e combos às vagas...")
        todas_as_vagas = ServicoFuncionarioHorario.objects.all()
        for vaga in todas_as_vagas.iterator():
            servicos_do_funcionario = list(vaga.funcionario.servico.all())

            if not servicos_do_funcionario:
                continue

            if random.random() < 0.3 and len(servicos_do_funcionario) > 1:
                servicos_para_vaga = random.sample(servicos_do_funcionario, k=min(len(servicos_do_funcionario), 2))

            else:
                servicos_para_vaga = random.sample(servicos_do_funcionario, k=1)
            vaga.servico.set(servicos_para_vaga)
        self.stdout.write("Serviços e combos atribuídos.")

    def _criar_agendamentos(self):
        """
        Simula o uso real do sistema criando um grande número de agendamentos, ocupando uma porcentagem significativa
        das vagas disponíveis e atribuindo status aleatórios a eles.
        """

        self.stdout.write("Criando agendamentos...")
        vagas_disponiveis = list(ServicoFuncionarioHorario.objects.all())
        clientes_ativos = list(Cliente.objects.filter(ativo=True))

        if not vagas_disponiveis or not clientes_ativos:
            self.stdout.write(self.style.WARNING("Não há vagas ou clientes ativos para criar agendamentos."))
            return

        total_agendamentos = int(len(vagas_disponiveis) * 0.90)
        vagas_para_agendar = random.sample(vagas_disponiveis, k=total_agendamentos)

        agendamentos = []
        for vaga in vagas_para_agendar:
            agendamentos.append(Agendamento(
                cliente=random.choice(clientes_ativos),
                servico_funcionario_horario=vaga,
                status=random.choice(['AGENDADO', 'CONCLUIDO', 'CANCELADO'])
            ))

        Agendamento.objects.bulk_create(agendamentos, batch_size=1000)
        self.stdout.write(f"{len(agendamentos)} agendamentos criados.")
