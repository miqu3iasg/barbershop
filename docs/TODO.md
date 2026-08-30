# TODO — o que falta no projeto

Lista de tarefas pendentes. Cada tarefa tem quatro
blocos aninhados: **Onde** (path exato dos arquivos), **O que fazer**,
**Como fazer** (passo a passo, marque cada passo conforme for concluindo)
e **Módulos afetados** (o que mais precisa mudar quando você mexer naquele
arquivo — não pule essa parte, ou a tarefa fica pela metade).

Antes de pegar uma tarefa, avise no grupo quem está fazendo o quê, pra não
duplicar trabalho. Terminou? Marque o checkbox principal da tarefa e avise
no grupo. Encontrou algo que não sabia que existia, não entendeu o porquê
de algo, ou travou em algum passo? Registre em `docs/FEEDBACK.md`, esse
documento aqui é só para tarefas já claras.

---

## 🔴 Prioridade alta 

- [ ] **1. Mostrar barbeiros disponíveis com o dia/horário de expediente ao marcar um agendamento**
  - **Onde:**
    - `views/appointment_view.py` (método `_create`)
    - `utils/client/api_client.py`
    - `controllers/barber_controller.py`
    - `serializers/barber_serializer.py`
  - **O que fazer:**
    - Hoje, no passo 2 do wizard de agendamento (`print_step(2, 4, ...)`),
      a CLI só mostra `ID` e `Nome` do barbeiro
      (`print_table(["ID", "Nome"], ...)`). O usuário não tem como saber
      em quais dias da semana aquele barbeiro atende sem sair do fluxo e
      ir manualmente no menu Barbeiros → Definir horário de trabalho só
      para consultar.
    - O objetivo é que a própria tela de "selecione o barbeiro" já mostre
      os dias/horários de expediente de cada um, para o usuário escolher
      com informação suficiente, sem precisar sair do fluxo.
  - **Como fazer:**
    - [ ] Confirmar que `BarberSerializer` já devolve `working_hours`
      aninhado (ele devolve — veja `serializers/barber_serializer.py`,
      campo `working_hours = WorkingHoursSerializer(many=True, ...)`).
      Ou seja, o backend já manda esse dado, só falta a CLI usar.
    - [ ] Em `utils/client/api_client.py`, conferir que `list_barbers()`
      já retorna esse campo (ele retorna, é o mesmo endpoint
      `GET /barbers/`) — não precisa criar endpoint novo.
    - [ ] Em `views/appointment_view.py`, no passo 2 (seleção de
      barbeiro), montar as linhas da tabela juntando o nome do barbeiro
      com um resumo legível do expediente dele. Por exemplo, para cada
      barbeiro, formatar `working_hours` em algo como
      `"Seg-Sex 08:00-18:00, Sáb 08:00-12:00"` (agrupando dias
      consecutivos com o mesmo horário deixa mais bonito, mas se for
      complexo demais, começe listando um dia por linha mesmo).
    - [ ] Adicionar uma função auxiliar de formatação em
      `utils/formatters.py` (algo como `format_working_hours(hours_list)`)
      para não deixar essa lógica de string dentro da view.
    - [ ] Atualizar a tabela exibida para
      `print_table(["ID", "Nome", "Expediente"], ...)`.
    - [ ] Se um barbeiro não tiver nenhum expediente cadastrado ainda,
      mostrar algo como `"(sem expediente definido)"` em vez de deixar a
      coluna vazia — isso também avisa o usuário que aquele barbeiro
      provavelmente vai falhar na validação de disponibilidade.
  - **Módulos afetados:**
    - `views/appointment_view.py` — mudança principal.
    - `utils/formatters.py` — nova função de formatação de expediente,
      reaproveitável também em `views/barber_view.py` (ele já lista o
      expediente de um barbeiro individual em outro formato, ver se vale
      a pena usar a mesma função lá para não duplicar lógica de formato).
    - Nenhuma mudança no backend é necessária — o dado já existe na API.

---

- [ ] **2. Implementar as transições de status que faltam no Appointment**
  - **Onde:**
    - `models/appointment.py`
    - `repositories/appointment_repository.py`
    - `services/appointment_service.py`
    - `controllers/appointment_controller.py`
    - `utils/client/api_client.py`
    - `views/appointment_view.py`
  - **O que fazer:**
    - Hoje `Appointment` só sabe ir de `SCHEDULED` → `CONFIRMED`
      (`confirm()`) e de qualquer status não-final → `CANCELLED`
      (`cancel()`). Os status `IN_PROGRESS`, `COMPLETED` e `NO_SHOW`
      existem em `AppointmentStatus` mas nunca são alcançáveis.
  - **Como fazer:**
    - [ ] Em `models/appointment.py`, defina por escrito a máquina de
      estados antes de codar (ex: só pode `start()` quem está
      `CONFIRMED`; só pode `complete()` quem está `IN_PROGRESS`;
      `mark_as_no_show()` só a partir de `SCHEDULED` ou `CONFIRMED`).
    - [ ] Implemente `start()`, `complete()` e `mark_as_no_show()`
      seguindo exatamente o mesmo padrão de `confirm()`/`cancel()`:
      validar a transição atual e levantar `InvalidStatusTransitionError`
      (de `exceptions/domain_exceptions.py`) se não for permitida.
    - [ ] Em `repositories/appointment_repository.py`, adicione `start()`,
      `complete()`, `mark_as_no_show()` espelhando `cancel()`/`confirm()`
      (mesmo padrão de `@transaction.atomic` + `save(update_fields=...)`).
    - [ ] Em `services/appointment_service.py`, adicione os métodos de
      aplicação correspondentes, buscando o appointment por ID igual
      `cancel_appointment`/`confirm_appointment` já fazem.
    - [ ] Em `controllers/appointment_controller.py`, adicione as
      `@action` (`start`, `complete`, `no-show`), documentadas com
      `@extend_schema`, seguindo o padrão de `cancel`/`confirm`.
    - [ ] Em `utils/client/api_client.py`, adicione os métodos HTTP
      correspondentes (`start_appointment`, `complete_appointment`,
      `mark_appointment_as_no_show`).
    - [ ] Em `views/appointment_view.py`, adicione as opções no menu de
      Agendamentos e os respectivos métodos privados
      (`_start`, `_complete`, `_mark_as_no_show`), seguindo o padrão de
      `_cancel`/`_confirm` (sempre com `prompt_confirm` antes).
  - **Módulos afetados:**
    - Todos os listados acima em "Onde" — essa é uma tarefa que atravessa
      as 4 camadas do backend mais a CLI.

---

- [ ] **3. Deixar o barbeiro escolher especialidades no cadastro**
  - **Onde:**
    - `views/barber_view.py` (método `_create`)
  - **O que fazer:**
    - Hoje o cadastro de barbeiro sempre manda `"specialties": []` fixo
      para a API. Todo barbeiro cadastrado pela CLI nasce "generalista" e
      nunca é possível vinculá-lo a serviços específicos pelo terminal —
      mesmo o backend já suportando isso
      (`models/barber.py` → `Barber.is_qualified_for()`).
  - **Como fazer:**
    - [ ] Em `views/barber_view.py`, dentro de `_create`, antes de montar
      o payload, listar os serviços ativos
      (`self.api.list_services(is_active=True)`) com `print_table`,
      igual já é feito em `appointment_view.py`.
    - [ ] Perguntar com `prompt_text` os IDs separados por vírgula (pode
      deixar vazio para "generalista", igual ao comportamento atual).
    - [ ] Trocar `"specialties": []` pela lista de IDs escolhida.
  - **Módulos afetados:**
    - Nenhum além do próprio `views/barber_view.py` — o backend já aceita
      `specialties` no payload (`controllers/barber_controller.py`).

---

- [ ] **4. Permitir editar e desativar clientes, barbeiros e serviços pela CLI**
  - **Onde:**
    - `services/barber_service.py`, `services/service_catalog_service.py`
      (o `services/client_service.py` já tem `deactivate_client`)
    - `controllers/client_controller.py`, `controllers/barber_controller.py`,
      `controllers/service_controller.py`
    - `utils/client/api_client.py`
    - `views/client_view.py`, `views/barber_view.py`, `views/service_view.py`
  - **O que fazer:**
    - Hoje só existe "listar" e "cadastrar" nesses três menus. Não dá
      para desativar um cliente/barbeiro/serviço pelo terminal, mesmo os
      models já tendo o método pronto (`Client.deactivate()`,
      `Barber.deactivate()` — falta o equivalente em `Service`).
  - **Como fazer:**
    - [ ] Adicionar `Service.deactivate()` em `models/service.py`
      (não existe ainda — só `Client` e `Barber` têm hoje).
    - [ ] Adicionar um método `deactivate` em
      `services/barber_service.py` e `services/service_catalog_service.py`
      chamando o repository, no mesmo padrão de `ClientService.deactivate_client`.
    - [ ] Em cada `controllers/<entidade>_controller.py`, adicionar uma
      `@action` `desativar`/`deactivate` (`detail=True, methods=["post"]`),
      seguindo o padrão de `set_working_hours` em `barber_controller.py`.
    - [ ] Em `utils/client/api_client.py`, adicionar
      `deactivate_client(client_id)`, `deactivate_barber(barber_id)`,
      `deactivate_service(service_id)`.
    - [ ] Em cada `views/<entidade>_view.py`, adicionar a opção
      "Desativar" no menu, sempre com `prompt_confirm` antes (é uma ação
      que tira o registro de circulação, então merece confirmação).
  - **Módulos afetados:**
    - `models/service.py`, `services/`, `controllers/`,
      `utils/client/api_client.py` e `views/` das três entidades — é uma
      tarefa que se repete três vezes, quase igual, então dá para dividir
      entre três pessoas do grupo (uma entidade cada) sem conflito de
      arquivo.

---

- [ ] **5. Testes unitários — obrigatório, no mínimo um teste por módulo**
  - **Onde:** criar a pasta `tests/` na raiz, espelhando a estrutura do
    projeto.
  - **O que fazer:**
    - O projeto inteiro hoje só foi validado manualmente. Isso é
      arriscado — qualquer alteração pode quebrar uma regra de negócio
      sem ninguém perceber até rodar na CLI na mão. **Todo módulo
      abaixo precisa de pelo menos um teste antes do projeto ser
      considerado "pronto"**, mesmo que simples.
  - **Como fazer (configuração, uma vez só):**
    - [ ] Adicionar `pytest` e `pytest-django` ao `requirements.txt`.
    - [ ] Criar `pytest.ini` na raiz com
      `DJANGO_SETTINGS_MODULE = config.settings` e
      `python_files = test_*.py`.
    - [ ] Seguir a convenção de `docs/CODE_STYLE.md` seção 10: arquivo de
      teste espelha o caminho do arquivo testado
      (`models/appointment.py` → `tests/models/test_appointment.py`).
  - **Checklist de módulos que precisam de teste (marque conforme for
    cobrindo):**
    - **`models/` (o mais importante — é onde vive a regra de negócio):**
      - [ ] `tests/models/test_client.py` — CPF válido, CPF inválido
        (dígito verificador errado), `deactivate()`.
      - [ ] `tests/models/test_barber.py` — `is_qualified_for()` com e
        sem especialidades cadastradas, `working_hours_for()`.
      - [ ] `tests/models/test_working_hours.py` — `covers()` com
        horário dentro, fora, e na borda do expediente.
      - [ ] `tests/models/test_service.py` — `price_for()` e
        `duration_for()` com quantidade > 1.
      - [ ] `tests/models/test_appointment.py` — o mais crítico:
        `schedule()` com sucesso, com conflito
        (`SchedulingConflictError`), fora do expediente
        (`OutsideWorkingHoursError`), sem serviço selecionado
        (`EmptyServiceListError`), no passado (`PastSchedulingError`);
        e `confirm()`/`cancel()` com transição válida e inválida.
      - [ ] `tests/models/test_appointment_item.py` — `build_for()` gera
        o snapshot correto de preço/duração.
    - **`repositories/`:**
      - [ ] `tests/repositories/test_client_repository.py` — `create()`
        persiste e `full_clean()` recusa CPF inválido.
      - [ ] `tests/repositories/test_barber_repository.py` — `create()`
        com `specialty_ids`, `set_working_hours()`.
      - [ ] `tests/repositories/test_service_repository.py` — `active()`
        filtra corretamente.
      - [ ] `tests/repositories/test_appointment_repository.py` —
        `schedule()` cria o `Appointment` + os `AppointmentItem` juntos
        na mesma transação.
    - **`services/`:**
      - [ ] `tests/services/test_client_service.py`
      - [ ] `tests/services/test_barber_service.py`
      - [ ] `tests/services/test_service_catalog_service.py`
      - [ ] `tests/services/test_appointment_service.py` — incluindo o
        caso de `ResourceNotFoundError` quando `client_id`/`barber_id`
        não existe.
    - **`controllers/` (teste de integração via `APIClient` do DRF):**
      - [ ] `tests/controllers/test_client_controller.py`
      - [ ] `tests/controllers/test_barber_controller.py`
      - [ ] `tests/controllers/test_service_controller.py`
      - [ ] `tests/controllers/test_appointment_controller.py` —
        incluindo que um `SchedulingConflictError` do domínio vira
        `HTTP 400` (testa o `config/exception_handler.py` também).
    - **CLI (`utils/`):**
      - [ ] `tests/utils/test_validators.py` — `is_valid_cpf`,
        `is_valid_email`, `is_valid_phone` com casos válidos e
        inválidos.
      - [ ] `tests/utils/test_http_client.py` — usando `requests-mock`
        ou similar, testar que um `404` vira `ResourceNotFoundError` e
        um `400` vira `ValidationApiError`.
  - **Módulos afetados:**
    - `requirements.txt` (novas dependências: `pytest`,
      `pytest-django`, e `requests-mock` para os testes de HTTP).
    - `docs/CODE_STYLE.md` — atualizar a seção 10 removendo o aviso de
      "ainda não existem testes" assim que o primeiro for escrito.

---

## 🟡 Prioridade média

- [ ] **6. Listagem de agendamentos sem filtro na CLI**
  - **Onde:** `views/appointment_view.py` (método `_list`)
  - **O que fazer:**
    - `AppointmentService.list_appointments(**filters)` e
      `api.list_appointments(status=None)` já aceitam filtro por status,
      mas a CLI sempre chama sem filtro nenhum. Numa barbearia com muitos
      agendamentos isso vira uma lista enorme e inútil.
  - **Como fazer:**
    - [ ] Em `_list`, antes de chamar `self.api.list_appointments()`,
      perguntar com `prompt_choice` se o usuário quer filtrar por status
      (mostrar as opções: Todos, Agendado, Confirmado, Cancelado etc. —
      hardcode a lista de strings na própria view; não importe o backend
      na CLI, ela é desacoplada de propósito).
    - [ ] Passar o valor escolhido para
      `self.api.list_appointments(status=...)`.
  - **Módulos afetados:**
    - Nenhum — o backend já suporta isso via
      `filterset_fields = ["status", "barber", "client"]` em
      `controllers/appointment_controller.py`.

---

- [ ] **7. Sem paginação de verdade na CLI**
  - **Onde:** `utils/client/api_client.py` (método `_results`)
  - **O que fazer:**
    - O DRF pagina as listagens em 20 por página
      (`config/settings.py` → `PAGE_SIZE`), mas `ApiClient._results()`
      sempre pega só `data["results"]` da primeira página e ignora
      `next`/`previous`. Com mais de 20 registros, a CLI simplesmente
      não mostra o resto.
  - **Como fazer:**
    - [ ] Decidir a abordagem: (a) a CLI busca todas as páginas
      automaticamente seguindo `data["next"]` até acabar, ou (b) a CLI
      mostra "Página 1 de N" e pergunta se quer ver a próxima. Comecem
      pela (a), é mais simples.
    - [ ] Ajustar `_results` para, se `data["next"]` não for `None`,
      fazer outra chamada HTTP para essa URL e concatenar os resultados.
  - **Módulos afetados:**
    - Nenhum outro arquivo muda — é uma mudança isolada em
      `utils/client/api_client.py`.

---

- [ ] **8. Pequenas funcionalidades que faltam em módulos já existentes**

  Estas são tarefas menores — não criam camada nova nenhuma, só usam
  capacidade que a API já tem e a CLI ainda não expõe. Boas para quem
  quer uma tarefa mais rápida.

  - [ ] **8.1 Exibir o CPF formatado ao consultar um cliente**
    - **Onde:** `serializers/client_serializer.py`, `views/client_view.py` (método `_show`)
    - **O que fazer:**
      - `models/client.py` já tem a property `formatted_document`
        (`"xxx.xxx.xxx-xx"`), mas ela nunca é exposta pela API nem usada
        na CLI — hoje `_show` mostra o CPF cru (`document_number`).
    - **Como fazer:**
      - [ ] Adicionar um campo `formatted_document =
        serializers.CharField(read_only=True)` em `ClientSerializer`
        (o DRF já resolve automaticamente via a property do model, sem
        precisar de `SerializerMethodField`).
      - [ ] Em `views/client_view.py` → `_show`, trocar
        `client["document_number"]` por `client["formatted_document"]`
        no resumo exibido.
    - **Módulos afetados:** nenhum outro.

  - [ ] **8.2 Filtrar agendamentos por cliente ou barbeiro na CLI**
    - **Onde:** `utils/client/api_client.py` (método `list_appointments`), `views/appointment_view.py`
    - **O que fazer:**
      - O backend já aceita `?client=<id>` e `?barber=<id>` (mesmo
        `filterset_fields` da tarefa 6), mas `list_appointments` só
        aceita `status`. Seria útil, por exemplo, ver rapidamente todos
        os agendamentos de um cliente específico.
    - **Como fazer:**
      - [ ] Adicionar os parâmetros `client_id=None` e `barber_id=None`
        em `ApiClient.list_appointments`, incluindo no dicionário
        `params` só os que não forem `None`.
      - [ ] Na tela de listagem da CLI, oferecer filtro adicional por
        cliente/barbeiro (pode reaproveitar o mesmo prompt da tarefa 6).
    - **Módulos afetados:** nenhum outro.

  - [ ] **8.3 Buscar cliente por nome, CPF ou e-mail na listagem**
    - **Onde:** `utils/client/api_client.py` (método `list_clients`), `views/client_view.py` (método `_list`)
    - **O que fazer:**
      - `ClientViewSet.search_fields = ["name", "document_number",
        "email"]` já existe no backend (busca via `?search=termo`), mas
        a CLI nunca usa. Útil quando a base de clientes crescer.
    - **Como fazer:**
      - [ ] Adicionar um parâmetro `search=None` em
        `ApiClient.list_clients`, mapeando para `?search=` na
        requisição.
      - [ ] Em `views/client_view.py` → `_list`, perguntar (opcional, com
        `prompt_text(..., optional=True)`) se o usuário quer buscar por
        um termo antes de listar.
    - **Módulos afetados:** nenhum outro. O mesmo padrão pode ser
      repetido depois para barbeiros e serviços, que também têm
      `search_fields` no backend.

  - [ ] **8.4 Permitir ordenar as listagens**
    - **Onde:** `utils/client/api_client.py`, `views/client_view.py`, `views/service_view.py`
    - **O que fazer:**
      - `ordering_fields` já existe em `ClientViewSet` (`name`,
        `created_at`) e `ServiceViewSet` (`name`, `price`,
        `duration_minutes`), mas a CLI nunca passa `?ordering=`.
    - **Como fazer:**
      - [ ] Adicionar parâmetro `ordering=None` nos métodos de listagem
        relevantes de `ApiClient`.
      - [ ] Nas views, oferecer uma opção simples tipo "ordenar por
        preço" / "ordenar por nome" antes de listar serviços.
    - **Módulos afetados:** nenhum outro.

  - [ ] **8.5 Ver a agenda do dia atual rapidamente**
    - **Onde:** `views/appointment_view.py`
    - **O que fazer:**
      - Hoje para ver "o que tem hoje" o usuário precisa listar todos os
        agendamentos e procurar visualmente. Adicionar uma opção rápida
        de menu "Ver agenda de hoje".
    - **Como fazer:**
      - [ ] Adicionar a opção no menu de Agendamentos.
      - [ ] Buscar todos os agendamentos
        (`self.api.list_appointments()`) e filtrar no lado da CLI
        (Python puro, sem mudar o backend) os que têm `start_at` na data
        de hoje, usando `datetime.now().date()`.
      - [ ] Exibir com `print_table`, ordenado por horário.
    - **Módulos afetados:** nenhum outro — filtro feito inteiramente no
      cliente, sem precisar de endpoint novo.

---

Qualquer dúvida sobre uma tarefa específica, ou se achar que falta contexto
em algum passo, registre em `docs/FEEDBACK.md` em vez de adivinhar.
