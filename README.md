# Sistema de Agendamento para Salão de Beleza

![Python](https://img.shields.io/badge/Python-3.13.3-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2.4-green.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Descrição do Projeto

Este projeto é uma aplicação web desenvolvida em Django para um salão de beleza, com o objetivo de organizar e gerenciar seus agendamentos de forma eficiente. O sistema permite o cadastro de clientes, serviços e funcionários, além de uma robusta gestão de agendamentos e a geração de relatórios de desempenho.

O desenvolvimento foi guiado pela necessidade de uma ferramenta funcional, clara e com alta performance, pensando na escalabilidade do negócio.

## Tabela de Conteúdos

- [Funcionalidades](#funcionalidades)
  - [Funcionalidades Principais (Requisitos)](#funcionalidades-principais-requisitos)
  - [Funcionalidades Adicionais (Extras)](#funcionalidades-adicionais-extras)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Configuração do Ambiente e Instalação](#configuração-do-ambiente-e-instalação)
- [Fluxo de Uso Básico](#fluxo-de-uso-básico)
- [Usuários e Níveis de Acesso](#usuários-e-níveis-de-acesso)
- [Licença](#licença)

## Funcionalidades

### Funcionalidades Principais (Requisitos)

-   **Cadastro de Clientes, Serviços e Equipe:** Interface administrativa completa para gerenciar as entidades fundamentais do negócio.
-   **Gestão de Agendamentos:** Ferramenta para agendar serviços para clientes com profissionais específicos, incluindo data, hora e status do agendamento (`Agendado`, `Concluído`, `Cancelado`).
-   **Acompanhamento de Serviços (Relatório):** Geração de um relatório que mostra o total de serviços concluídos dentro de um período de tempo especificado.
-   **Atenção à Performance:** Sistema projetado para ser rápido e eficiente, com atenção especial à performance do relatório para suportar um grande volume de agendamentos.
- 
### Funcionalidades Adicionais (Extras)

Além dos requisitos básicos, foram implementados diversos recursos para enriquecer a experiência do usuário e a inteligência do sistema:

-   **Otimização de Performance (Solução N+1):** Para atender ao requisito de performance, a consulta do relatório foi otimizada com `select_related` e `prefetch_related`, evitando o problema de "N+1 queries" e garantindo que a geração do PDF seja rápida, mesmo com milhares de registros.
-   **Scripts de Povoamento do Banco:** Para acelerar os testes e a configuração inicial, foram criados dois comandos de gerenciamento:
    -   `popular_banco`: Popula todas as tabelas com dados de exemplo, incluindo a criação automática de usuários com perfis distintos (1 Dono, 5 Recepcionistas, 20 Funcionários).
    -   `gerador_de_horario`: Popula o banco com horários de atendimento para os próximos 6 meses, automatizando uma regra de negócio crucial do salão.
-   **Visualização por Nível de Acesso:** A interface do Django Admin se adapta ao tipo de usuário logado (Superusuário, Dono, Recepcionista), mostrando ou ocultando campos e filtros relevantes para cada perfil.
-   **Buscas com Autocomplete:** Nos formulários de agendamento e cadastro, campos de relacionamento utilizam autocomplete para facilitar a busca e melhorar a usabilidade.
-   **Filtragem Inteligente:** Para evitar agendamentos duplicados, o campo de seleção de "Vaga de Atendimento" é dinâmico: ele oculta automaticamente as vagas que já foram preenchidas, mostrando apenas horários realmente disponíveis. Assim como Pessoas, para a criação de funcionário ou cliente.
-   **Filtros Personalizados:** Criação de filtros customizados no admin, como o filtro por faixa de preço para serviços.
-   **Métricas Financeiras no Admin:** As listagens de Clientes e Funcionários exibem colunas com o cálculo de ganho total e ganho previsto, oferecendo insights financeiros diretamente na interface.

## Tecnologias Utilizadas

-   **Python:** 3.13.3
-   **Django:** 5.2.4
-   **Banco de Dados:** SQLite (padrão do Django, fácil de configurar)
-   **Ambiente Virtual:** `venv`

### Dependências (requirements.txt)

```txt
# Core do projeto
Django

# Geração de PDF a partir de HTML
xhtml2pdf

# Widgets avançados para o Django Admin (autocomplete e selects)
django-autocomplete-light
django-select2

# Filtro de data por intervalo no admin
django-rangefilter
```

## Configuração do Ambiente e Instalação

Siga os passos abaixo para rodar o projeto localmente.

**1. Pré-requisitos:**
   - Ter o Python 3.13.3 ou superior instalado.
   - Ter o Git instalado.

**2. Clone o Repositório:**
   ```bash
   git clone https://github.com/Hermano-Neto/desafio-m2a.git
   ```

**3. Crie e Ative o Ambiente Virtual:**
   ```bash
   # Criar o ambiente virtual
   python -m venv .venv

   # Ativar no Windows (PowerShell)
   .\.venv\Scripts\Activate.ps1

   # Ativar no Linux/macOS
   source .venv/bin/activate
   ```

**4. Instale as Dependências:**
   ```bash
   pip install -r requirements.txt
   ```

**5. Aplique as Migrações do Banco de Dados:**
   Este comando cria a estrutura do banco de dados.
   ```bash
   python manage.py migrate
   ```

**6. Povoamento do Banco de Dados (Opcional, mas Recomendado):**
   Para poupar tempo de cadastro manual, você pode usar os scripts para popular o banco.
   ```bash
   # 1. Popula o banco com dados de exemplo (clientes, funcionários, etc.)
   python manage.py popular_banco


   # 2. Gera os horários de atendimento para os próximos 6 meses
   python manage.py gerador_de_horario
   ```
   *Nota: O script `popular_banco` já cria usuários. Se preferir criar o seu próprio superusuário, pule esta etapa e use o comando `python manage.py createsuperuser`.*

**7. Rode o Servidor de Desenvolvimento:**
   ```bash
   python manage.py runserver
   ```
   Acesse a aplicação em `http://127.0.0.1:8000/admin` e faça login com um dos usuários criados.


## Fluxo de Uso Básico

Para realizar um agendamento completo, o sistema segue um fluxo de trabalho lógico, garantindo que todos os dados necessários sejam cadastrados previamente. Siga as etapas abaixo na interface do **Django Admin**:

1.  **Cadastro de Pessoas**
    - Acesse a seção `Pessoas` e cadastre os indivíduos que interagirão com o sistema. Este é o cadastro base que será utilizado para criar Clientes e Funcionários.


2.  **Definição de Papéis (Cliente e Funcionário)**
    - Após cadastrar uma pessoa, acesse `Clientes` ou `Funcionários` para associar a pessoa a um desses papéis. O campo de busca com autocomplete permite encontrar a pessoa cadastrada facilmente.


3.  **Cadastro de Serviços**
    - Na seção `Serviços`, defina os serviços que o salão oferece (ex: "Corte de Cabelo", "Manicure"), especificando seus respectivos valores e durações.


4.  **Criação dos Horários de Atendimento**
    - Para definir a grade de horários do salão, você tem duas opções:
        - **Automática (Recomendado):** Execute o comando `python manage.py gerador_de_horario`. Ele criará automaticamente todos os horários de trabalho para os próximos 6 meses.
        - **Manual:** Cadastre datas e horas específicas na seção `Datas e horários`.
    - *Nota: O script de geração automática pode ser facilmente ajustado para se adequar a diferentes regras de negócio da empresa.*


5.  **Criação das Vagas de Atendimento**
    - Esta é a etapa que define a agenda. Em `Vagas de Atendimento`, você conecta um `Funcionário` a uma `Data e Horário` e aos `Serviços` que ele pode realizar naquele momento. Isso cria um espaço de atendimento disponível para agendamento.


6.  **Realização do Agendamento**
    - Finalmente, na seção `Agendamentos`, selecione um `Cliente` e uma `Vaga de Atendimento`. O sistema foi otimizado para mostrar apenas as vagas que ainda estão livres, utilizando um campo de busca inteligente para facilitar a marcação do serviço e evitar conflitos de horário.
    

## Usuários e Níveis de Acesso

O script `popular_banco` cria automaticamente perfis de usuário com permissões pré-definidas para facilitar os testes.

* **Dono**
    -   **Usuário:** `Dono`
    -   **Senha:** `teste1234`
    -   **Acesso:** Perfil de administrador com amplos poderes. Possui permissão para gerenciar a maioria dos módulos (Clientes, Serviços, Agendamentos). 
  

* **Recepcionista**
    -   **Usuários:** `recepcionista_1`, `recepcionista_2`, etc.
    -   **Senha:** `teste1234`
    -   **Acesso:** Perfil operacional com permissão total para criar, visualizar, editar e deletar registros em todos os módulos do sistema. É o perfil destinado ao gerenciamento do dia a dia da agenda.


* **Funcionário**
    -   **Usuários:** `funcionario_1`, `funcionario_2`, etc.
    -   **Senha:** `teste1234`
    -   **Acesso:** Perfil com acesso de **apenas leitura** (view-only). Pode visualizar os dados do sistema, como sua própria agenda e serviços, mas não pode criar, editar ou apagar registros.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.