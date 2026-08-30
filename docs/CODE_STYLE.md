# Padrão de código

Este documento define como escrever código neste projeto. Não é sugestão —
é o que será cobrado em revisão. O objetivo não é burocracia: é garantir
que qualquer pessoa do grupo consiga abrir um arquivo que não escreveu e
entender onde mexer sem perguntar para quem escreveu.

## 1. Idioma

- **Código** (nomes de classes, funções, variáveis, comentários,
  docstrings): **inglês**, sempre.
- **Interação com o usuário** (tudo que é `print()` ou `input()` mostrado
  no terminal): **português**, sempre.

```python
# ERRADO — código em português
class Cliente:
    def cadastrar_cliente(self, nome, telefone):
        ...

# ERRADO — texto do usuário em inglês
print_success("Client registered successfully!")

# CERTO
class Client:
    def register_client(self, name, phone):
        ...

print_success(f"Cliente '{client['name']}' cadastrado com sucesso!")
```

Isso não é estética: código em inglês é o padrão de qualquer vaga/empresa
que vocês vão encontrar depois da faculdade, e misturar os dois idiomas no
mesmo arquivo deixa a leitura mais lenta para todo mundo.

## 2. Onde cada coisa vai (as camadas)

Cada pasta tem uma responsabilidade única. Antes de escrever uma linha,
pergunte "isso é regra de negócio, acesso a dado, orquestração, ou
apresentação?" e vá para a pasta certa.

| Pasta | Responsabilidade | NÃO deve conter |
|---|---|---|
| `models/` | Entidades + regras de negócio (a fonte da verdade) | Chamadas HTTP, formatação de resposta |
| `repositories/` | Ler/salvar no banco via ORM | Regra de negócio, validação de negócio |
| `services/` | Resolver IDs em objetos e orquestrar repositories | Query direta ao ORM, regra de negócio duplicada |
| `controllers/` | Traduzir HTTP ↔ services | Regra de negócio, acesso direto ao banco |
| `serializers/` | Validar **forma** dos dados (tipo, obrigatoriedade) | Regra de negócio (isso é validação de **conteúdo**, não forma) |
| `views/` | Menus, prompts e formatação no terminal | Lógica de negócio, chamada HTTP direta (`requests.get(...)`) |
| `utils/client/` | Fazer a chamada HTTP de verdade | Regra de negócio, formatação visual |

### Exemplo real: onde vai a regra "não pode agendar em horário ocupado"?

```python
# ERRADO — regra de negócio dentro do controller
class AppointmentViewSet(viewsets.ModelViewSet):
    def create(self, request):
        conflitos = Appointment.objects.filter(
            barber_id=request.data["barber_id"],
            start_at__lt=end_at, end_at__gt=start_at,
        )
        if conflitos.exists():
            return Response({"detail": "conflito"}, status=400)
        ...

# ERRADO — regra de negócio dentro do repository
class AppointmentRepository:
    def create(self, client, barber, start_at, services):
        if Appointment.objects.filter(barber=barber, ...).exists():
            raise Exception("conflito")
        ...

# CERTO — a regra vive no model, que é o dono do conceito "Appointment"
class Appointment(models.Model):
    def schedule(self, services):
        ...
        self._ensure_no_conflicts()

    def _ensure_no_conflicts(self):
        conflicts = Appointment.objects.for_barber(self.barber).overlapping(self.start_at, self.end_at)
        if conflicts.exists():
            raise SchedulingConflictError("This barber already has an appointment at this time.")
```

Regra geral: **se dois lugares diferentes do código puderem "esquecer" de
aplicar a regra, ela está no lugar errado.** Colocando no model, é
impossível criar um `Appointment` sem passar por `schedule()`.

## 3. Um arquivo por entidade/classe principal

Nunca coloque duas classes de domínio no mesmo arquivo só porque estão
relacionadas.

```python
# ERRADO — barber.py
class Barber(models.Model):
    ...

class WorkingHours(models.Model):  # devia estar em working_hours.py
    ...

class WeekDay(models.IntegerChoices):  # devia estar em working_hours.py também
    ...
```

```python
# CERTO
# barber.py
class Barber(models.Model):
    ...

# working_hours.py
class WeekDay(models.IntegerChoices):
    ...

class WorkingHours(models.Model):
    ...
```

O nome do arquivo é sempre o nome da entidade em `snake_case`:
`appointment_item.py` → `class AppointmentItem`.

## 4. Nomenclatura

- Classes: `PascalCase` (`AppointmentRepository`, `SchedulingConflictError`).
- Funções, métodos e variáveis: `snake_case` (`schedule_appointment`,
  `client_id`).
- Constantes: `UPPER_SNAKE_CASE` (`NON_BLOCKING_STATUSES`).
- Arquivos: `snake_case.py`, no singular quando representam uma entidade
  (`client.py`, não `clients.py`).
- Um repository/service/controller/serializer segue sempre o padrão
  `<entidade>_<camada>.py` → `barber_repository.py`, `barber_service.py`,
  `barber_controller.py`, `barber_serializer.py`.

```python
# ERRADO
def GetAllClients(self): ...
CLIENT_repo = ClientRepository()
class client_service: ...

# CERTO
def list_clients(self): ...
client_repository = ClientRepository()
class ClientService: ...
```

## 5. Exceções

Nunca use `Exception` genérica para erro de negócio. Toda violação de
regra de negócio deve ser uma subclasse de `DomainError`
(`exceptions/domain_exceptions.py`); toda falha de comunicação HTTP na CLI
é uma subclasse de `ApiError` (`exceptions/api_exceptions.py`).

```python
# ERRADO
if conflicts.exists():
    raise Exception("Deu ruim no agendamento")

# CERTO
if conflicts.exists():
    raise SchedulingConflictError("This barber already has an appointment at this time.")
```

Se a regra que você está implementando não tem uma exceção que a
represente ainda, crie uma nova em `exceptions/domain_exceptions.py`
— não reaproveite uma exceção existente com um significado diferente do
que o nome dela diz.

## 6. Type hints e docstrings

- Toda função/método público (sem `_` na frente) deve ter type hints nos
  parâmetros e no retorno.
- Docstring de módulo (o comentário `"""..."""` no topo do arquivo)
  explica **por que** o arquivo existe, não só o que ele faz.
- Comentários dentro do código explicam **por que**, nunca **o que** (o
  código já diz o que faz).

```python
# ERRADO — comentário inútil, só repete o código
# soma os precos dos itens
total = sum(item.unit_price * item.quantity for item in items)

# CERTO — comentário explica uma decisão não óbvia
# Usamos o preço salvo no item (snapshot), não o preço atual do Service,
# para que uma alteração de preço não afete agendamentos já feitos.
total = sum(item.unit_price * item.quantity for item in items)
```

```python
# ERRADO — sem type hints
def register_client(self, name, document_number, phone, email):
    ...

# CERTO
def register_client(self, name: str, document_number: str, phone: str, email: str) -> Client:
    ...
```

## 7. Imports

Ordem: biblioteca padrão → bibliotecas de terceiros → módulos do projeto,
com uma linha em branco entre cada grupo. Sempre import absoluto a partir
da raiz do projeto (`from models.models import Client`), nunca import
relativo saindo da própria camada.

```python
# CERTO
import re
from datetime import timedelta

from django.db import models
from rest_framework import serializers

from exceptions.domain_exceptions import SchedulingConflictError
from models.models import Appointment
```

## 8. Strings e formatação

- Use f-strings, nunca `%` ou `.format()`.
- Nunca duplique uma mensagem de erro/sucesso em mais de um lugar — se
  duas views mostram a mesma mensagem, extraia para uma função em
  `utils/formatters.py`.

```python
# ERRADO
print("Cliente %s cadastrado" % client["name"])
print_error("Erro: {}".format(str(exc)))

# CERTO
print_success(f"Cliente '{client['name']}' cadastrado com sucesso!")
print_error(str(exc))
```

## 9. Checklist ao criar um novo recurso

Sempre que adicionar uma entidade nova (ex: "Product" para venda de
produtos), estes são os arquivos que precisam existir/ser atualizados, na
ordem. Pule um passo e o recurso fica pela metade:

1. `models/<entidade>.py` — a classe do model, com as regras de negócio
   dela como métodos.
2. `models/models.py` — adicionar o import/export da nova classe.
3. `models/admin.py` — registrar no admin (`@admin.register(...)`).
4. Gerar a migration: `python manage.py makemigrations models`.
5. `repositories/<entidade>_repository.py` — CRUD básico.
6. `services/<entidade>_service.py` — casos de uso que orquestram o
   repository.
7. `serializers/<entidade>_serializer.py` — forma dos dados HTTP.
8. `controllers/<entidade>_controller.py` — o ViewSet.
9. `config/urls.py` — registrar o novo router (`router.register(...)`).
10. `utils/client/api_client.py` — adicionar os métodos que a CLI vai usar
    para falar com os novos endpoints.
11. `views/<entidade>_view.py` — o menu/formulário no terminal.
12. `views/main_menu.py` e `cli.py` — registrar a nova view no menu
    principal e na injeção de dependência.

Se você mexeu em uma regra de negócio existente (não criou uma entidade
nova), o mínimo a revisar é: **o model** (onde a regra vive),
**o repository** (se a query mudou), **o serializer** (se um campo novo
precisa aparecer na resposta) e **a view da CLI** (se o formulário
precisa de um campo novo).

## 10. Testes (quando existirem)

Ainda não há suite de testes no projeto (veja `docs/TODO.md`). Quando
forem escritos, a convenção é: um arquivo de teste por módulo, espelhando
o caminho do arquivo testado (`models/appointment.py` →
`tests/models/test_appointment.py`), usando `pytest`, e testando
principalmente os métodos de domínio (`schedule`, `cancel`, `confirm`) com
casos de sucesso e de cada exceção de domínio que eles podem lançar.
