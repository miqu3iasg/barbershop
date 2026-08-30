# Feedback e dúvidas

Este documento é para registrar **dúvidas**, **problemas encontrados** e
**sugestões** sobre o projeto — qualquer coisa que não seja "uma tarefa
pronta para fazer" (isso vai em `docs/TODO.md`) e sim "algo que precisa de
discussão ou de uma decisão antes de virar tarefa".

Use isso sempre que:
- Não entender por que algo foi feito de um jeito.
- Achar um bug e não tiver certeza se é bug ou comportamento esperado.
- Tiver uma ideia de melhoria mas não tiver certeza se faz sentido para o
  escopo do projeto.
- Travar em alguma parte da instalação/execução que o `README.md` não
  cobriu.

## Como usar

1. Adicione uma linha nova na tabela abaixo, preenchendo todas as
   colunas que conseguir.
2. Se for algo urgente que está travando o seu trabalho, avisa no grupo
   também — não deixa só aqui esperando alguém ler.
3. Quem responder/resolver atualiza a coluna **Status** e escreve a
   resposta na coluna **Resposta / decisão**. Não apaga a pergunta
   original, só adiciona a resposta ao lado — isso vira um histórico útil
   para quem entrar no projeto depois.
4. Status possíveis: `Aberto`, `Em análise`, `Resolvido`, `Não vamos fazer`
   (com o motivo escrito na resposta).

## Registro

| Data | Autor | Categoria | Descrição | Status | Resposta / decisão |
|---|---|---|---|---|---|
| 2026-08-30 | Claude | Exemplo | Como devo nomear um novo endpoint de relatório, tipo "quantos cortes um barbeiro fez no mês"? Fica em `appointment_controller.py` como uma `@action` ou merece um controller próprio `report_controller.py`? | Aberto | — |
| 2026-08-30 | Claude | Exemplo (bug) | Ao gerar a migration inicial, descobrimos que Django sempre importa `from django.db import migrations, models`, o que quebra se o app se chamar `models` e alguma migration precisar referenciar uma função customizada de dentro do próprio pacote `models`. | Resolvido | Movemos a validação de CPF de `validators=[...]` no campo para o método `Client.clean()`, que não é serializado em migration. Ver `models/client.py`. Se for adicionar um novo `validators=[...]` customizado em qualquer campo, cuidado com esse mesmo problema — prefira `clean()`. |

<!--
Exemplo de categorias que fazem sentido usar na coluna "Categoria":
Dúvida de arquitetura · Dúvida de código · Bug · Sugestão · Dúvida de setup/instalação · Dúvida de escopo (o que entra ou não no projeto)
-->
