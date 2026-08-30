# Sistema de Gestão de Barbearia

Um projeto único e integrado: uma API Django (com PostgreSQL, Docker e
documentação Swagger) e uma **CLI de terminal** que fala com essa API por
HTTP. Não são "dois projetos" — é uma única árvore de pastas, seguindo a
mesma arquitetura em camadas de ponta a ponta, onde o terminal é
literalmente a camada de **View** do MVC, só que conversando com o
**Controller** pela rede em vez de em memória.

> Código (nomes de classes, funções, comentários, docstrings) está em
> **inglês**. Tudo que o usuário vê no terminal — prompts, mensagens de
> erro/sucesso — está em **português**. Este README também.

## Estrutura de pastas

```
barbershop/
├── manage.py            # entrypoint do backend Django
├── cli.py                # entrypoint da CLI de terminal
├── docker-compose.yml    # sobe Postgres + API
├── requirements.txt      # UM único requirements para o projeto inteiro
│
├── config/               # settings do Django + settings da CLI, lado a lado
│   ├── settings.py
│   ├── urls.py
│   ├── exception_handler.py
│   └── cli_settings.py
│
├── models/               # Django app: as entidades de domínio (1 arquivo por entidade)
│   ├── client.py
│   ├── barber.py
│   ├── working_hours.py
│   ├── service.py
│   ├── appointment.py       # aggregate root, com as regras de negócio
│   └── appointment_item.py
│
├── repositories/         # acesso a dados (ORM), 1 arquivo por agregado
├── services/              # orquestração da aplicação (application layer)
├── controllers/            # DRF ViewSets — os "Controllers" HTTP
├── serializers/              # validação de forma dos dados de entrada/saída HTTP
├── exceptions/                 # exceções de domínio (backend) e de API (CLI)
│
├── views/                       # a "View" do terminal: menus, prompts, feedback
├── utils/
│   ├── client/                    # infraestrutura: HTTP client (requests) + fachada da API
│   ├── formatters.py                # banners, tabelas, cores, mensagens
│   └── validators.py                 # validação client-side (CPF, e-mail, telefone...)
│
└── static/                         # arquivos estáticos do Django
```

Por que essa organização e não "api/" + "cli/" como duas pastas separadas:
o backend e o terminal são dois **processos** diferentes (um é servidor
Django, o outro é um cliente HTTP), mas são **um projeto só**. Colocá-los
em pastas irmãs no mesmo nível ("api" vs "cli") fazia parecer dois módulos
desconectados. Agora `models`, `repositories`, `services`, `controllers` e
`exceptions` formam o backend; `views` e `utils/client` formam a
apresentação (o terminal); e tudo compartilha o mesmo `requirements.txt`,
a mesma pasta `exceptions/` e a mesma convenção de código.

## Modelagem de domínio

Cada entidade tem seu próprio arquivo em `models/`, e as **regras de
negócio moram nos próprios models**, não espalhadas em serviços genéricos:

- **`Client`** valida seu próprio CPF (dígitos verificadores, não só
  formato) em `Client.clean()` / `Client.validate_document()`, e sabe se
  desativar (`client.deactivate()`).
- **`Service`** sabe calcular seu preço/duração para N unidades
  (`service.price_for(quantity)`).
- **`WorkingHours`** sabe dizer se um intervalo de horário cabe dentro do
  expediente (`working_hours.covers(start, end)`).
- **`Barber`** sabe dizer se está qualificado para um serviço
  (`barber.is_qualified_for(service)`) e buscar seu expediente de um dia
  (`barber.working_hours_for(week_day)`).
- **`Appointment`** é o aggregate root: `appointment.schedule(services)`
  calcula o horário de término, valida o expediente do barbeiro e checa
  conflito de agenda — tudo dentro do próprio método do model, levantando
  exceções de domínio (`SchedulingConflictError`,
  `OutsideWorkingHoursError` etc.) quando alguma regra é violada.
  `appointment.cancel()` e `appointment.confirm()` implementam a máquina de
  estados do agendamento.
- **`AppointmentItem`** guarda um **snapshot** do preço/duração do serviço
  no momento do agendamento (`AppointmentItem.build_for(...)`), para que
  uma mudança futura de preço não altere agendamentos já feitos.

Os **repositories** (`repositories/`) são deliberadamente finos: só sabem
buscar, salvar e orquestrar a transação — nunca reimplementam uma regra que
já existe no model. Os **services** (`services/`) resolvem IDs em objetos
de domínio e chamam o repository certo — a camada de "caso de uso".

## Rodando o projeto

### 1. Subir a API + banco

```bash
cp .env.example .env
docker compose up --build
```

- Documentação Swagger: **http://localhost:8000/api/docs/**
- Redoc: `http://localhost:8000/api/redoc/`
- Schema OpenAPI: `http://localhost:8000/api/schema/`

As migrations já estão versionadas em `models/migrations/`; o
`entrypoint.sh` aplica elas automaticamente ao subir o container.

### 2. Rodar a CLI de terminal

Em outro terminal, com Python 3.10+:

```bash
pip install -r requirements.txt
python cli.py
```

Por padrão aponta para `http://localhost:8000/api/v1`. Para apontar para
outro endereço, defina `BARBERSHOP_API_URL` antes de rodar.

### Roteiro sugerido para testar

1. Cadastre um serviço (ex: "Corte", 30 min, R$ 45).
2. Cadastre um barbeiro e defina o expediente dele (menu Barbeiros →
   opção 3).
3. Cadastre um cliente.
4. Marque um agendamento — a CLI te guia em 4 passos (cliente, barbeiro,
   serviços, horário), mostra um resumo antes de confirmar, e ao final
   mostra a duração e o valor total já calculados pelo backend.
5. Tente marcar outro agendamento no mesmo horário para o mesmo barbeiro,
   ou fora do expediente dele — a CLI vai mostrar o erro de negócio vindo
   direto da API.
6. Ligue o "modo dev" (opção 5 do menu principal) para ver a requisição e
   a resposta HTTP cruas de cada ação — bom para apresentação.

## Duas camadas de validação

- **Terminal (`utils/validators.py`):** valida CPF, e-mail, telefone e
  datas *antes* de qualquer requisição sair, com retry automático — o
  usuário nunca vê um erro genérico, a CLI pede de novo até o dado ser
  válido (veja `utils/prompts.py`).
- **Backend:** os `serializers/` validam a forma dos dados HTTP; as regras
  de negócio de verdade (conflito de agenda, expediente, CPF com dígito
  verificador) vivem nos `models/` e são a fonte da verdade — a CLI nunca
  deveria ser o único lugar onde uma regra é aplicada.

## Próximos passos possíveis (fora do escopo atual)

- Autenticação (JWT) e permissões por tipo de usuário.
- Testes automatizados (pytest) para os métodos de domínio dos models.
- Paginação client-side na CLI para listagens muito grandes.
