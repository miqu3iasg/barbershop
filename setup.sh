#!/usr/bin/env bash
#
# setup.sh sobe o projeto Sistema de Gestão de Barbearia do zero.
#
# O que este script faz:
#   1. Confere se Docker e Docker Compose estão instalados (e dá instruções
#      de instalação por sistema operacional se não estiverem).
#   2. Confere se existe um Python 3.10+ para rodar a CLI.
#   3. Cria o arquivo .env a partir do .env.example, se ainda não existir.
#   4. Sobe o banco de dados + API via Docker Compose.
#   5. Espera a API responder antes de terminar.
#   6. Cria (opcionalmente) um virtualenv com as dependências, para a CLI
#      rodar e para o editor/IDE reconhecer os pacotes.
#
# Uso:
#   ./setup.sh                 # roda tudo
#   ./setup.sh --skip-docker   # pula a parte de subir os containers
#                              # (use se o Docker já estiver rodando via outro processo)
#   ./setup.sh --no-venv       # não cria o virtualenv da CLI
#
set -uo pipefail

COLOR_RESET="\033[0m"
COLOR_BOLD="\033[1m"
COLOR_GREEN="\033[32m"
COLOR_YELLOW="\033[33m"
COLOR_RED="\033[31m"
COLOR_CYAN="\033[36m"

info()    { printf "%b\n" "${COLOR_CYAN}ℹ ${1}${COLOR_RESET}"; }
success() { printf "%b\n" "${COLOR_GREEN}✓ ${1}${COLOR_RESET}"; }
warn()    { printf "%b\n" "${COLOR_YELLOW}⚠ ${1}${COLOR_RESET}"; }
fail()    { printf "%b\n" "${COLOR_RED}✗ ${1}${COLOR_RESET}"; }
step()    { printf "\n%b\n" "${COLOR_BOLD}── ${1} ──────────────────────────${COLOR_RESET}"; }

SKIP_DOCKER=false
NO_VENV=false
for arg in "$@"; do
    case "$arg" in
        --skip-docker) SKIP_DOCKER=true ;;
        --no-venv) NO_VENV=true ;;
        -h|--help)
            echo "Uso: ./setup.sh [--skip-docker] [--no-venv]"
            exit 0
            ;;
        *)
            warn "Argumento desconhecido: $arg (ignorando)"
            ;;
    esac
done

printf "\n%b\n" "${COLOR_BOLD}${COLOR_CYAN}╔════════════════════════════════════════════════════════╗${COLOR_RESET}"
printf "%b\n"   "${COLOR_BOLD}${COLOR_CYAN}║   Setup — Sistema de Gestão de Barbearia                ║${COLOR_RESET}"
printf "%b\n\n" "${COLOR_BOLD}${COLOR_CYAN}╚════════════════════════════════════════════════════════╝${COLOR_RESET}"

OS_NAME="desconhecido"
case "$(uname -s)" in
    Linux*)  OS_NAME="linux" ;;
    Darwin*) OS_NAME="macos" ;;
    CYGWIN*|MINGW*|MSYS*) OS_NAME="windows" ;;
esac
info "Sistema detectado: ${OS_NAME}"

check_docker() {
    step "Verificando Docker"

    if ! command -v docker >/dev/null 2>&1; then
        fail "Docker não encontrado."
        print_docker_install_instructions
        return 1
    fi

    if ! docker info >/dev/null 2>&1; then
        fail "O Docker está instalado, mas não parece estar rodando."
        case "$OS_NAME" in
            macos|windows)
                warn "Abra o aplicativo Docker Desktop e espere o ícone ficar verde, depois rode este script de novo."
                ;;
            linux)
                warn "Tente: sudo systemctl start docker"
                warn "Se o erro for de permissão, rode: sudo usermod -aG docker \$USER — depois faça logout/login."
                ;;
        esac
        return 1
    fi

    if ! docker compose version >/dev/null 2>&1; then
        fail "Docker encontrado, mas o plugin 'docker compose' não está disponível."
        print_docker_install_instructions
        return 1
    fi

    success "Docker $(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1) e Docker Compose $(docker compose version --short 2>/dev/null) encontrados."
    return 0
}

print_docker_install_instructions() {
    echo ""
    warn "Este projeto PRECISA de Docker para rodar o banco de dados e a API."
    echo ""
    case "$OS_NAME" in
        macos)
            echo "  1. Baixe o Docker Desktop em: https://www.docker.com/products/docker-desktop/"
            echo "  2. Instale normalmente (arraste para a pasta Applications)."
            echo "  3. Abra o Docker Desktop uma vez e espere o ícone da baleia ficar estável."
            echo "  4. Rode este script de novo: ./setup.sh"
            ;;
        windows)
            echo "  1. Baixe o Docker Desktop em: https://www.docker.com/products/docker-desktop/"
            echo "  2. Durante a instalação, mantenha a opção 'WSL 2' marcada, se disponível."
            echo "  3. Reinicie o computador se for pedido."
            echo "  4. Abra o Docker Desktop uma vez e espere o ícone ficar estável."
            echo "  5. Rode este script de novo dentro do WSL ou Git Bash: ./setup.sh"
            ;;
        linux)
            echo "  Instalação rápida (Ubuntu/Debian):"
            echo "    curl -fsSL https://get.docker.com | sh"
            echo "    sudo usermod -aG docker \$USER"
            echo "  Depois disso, feche e abra o terminal (ou faça logout/login) e rode: ./setup.sh"
            echo ""
            echo "  Para outras distros, veja: https://docs.docker.com/engine/install/"
            ;;
        *)
            echo "  Veja as instruções oficiais em: https://docs.docker.com/get-docker/"
            ;;
    esac
    echo ""
}

check_python() {
    step "Verificando Python"

    local python_bin=""
    for candidate in python3 python; do
        if command -v "$candidate" >/dev/null 2>&1; then
            python_bin="$candidate"
            break
        fi
    done

    if [ -z "$python_bin" ]; then
        fail "Python não encontrado."
        warn "Instale o Python 3.10 ou superior:"
        case "$OS_NAME" in
            macos)  warn "  brew install python@3.12   (ou baixe em https://www.python.org/downloads/)" ;;
            linux)  warn "  sudo apt install python3 python3-venv python3-pip" ;;
            windows) warn "  Baixe em https://www.python.org/downloads/ e marque 'Add Python to PATH' na instalação." ;;
            *) warn "  Baixe em https://www.python.org/downloads/" ;;
        esac
        return 1
    fi

    local version
    version=$("$python_bin" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    local major minor
    major=$(echo "$version" | cut -d. -f1)
    minor=$(echo "$version" | cut -d. -f2)

    if [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -lt 10 ]; }; then
        warn "Encontrado Python ${version}, mas este projeto precisa de 3.10+."
        warn "A CLI pode não funcionar corretamente com essa versão."
        return 1
    fi

    success "Python ${version} encontrado (${python_bin})."
    PYTHON_BIN="$python_bin"
    return 0
}

setup_env_file() {
    step "Configurando variáveis de ambiente"

    if [ -f .env ]; then
        info "Arquivo .env já existe — mantendo o que já está configurado."
        return 0
    fi

    if [ ! -f .env.example ]; then
        fail ".env.example não encontrado. Você está rodando este script na raiz do projeto?"
        return 1
    fi

    cp .env.example .env
    success "Arquivo .env criado a partir de .env.example."
    warn "Os valores padrão são só para desenvolvimento local. Se for expor a API além do seu computador, troque DJANGO_SECRET_KEY e POSTGRES_PASSWORD antes."
    return 0
}

start_containers() {
    step "Subindo o banco de dados e a API (Docker Compose)"

    if ! docker compose up --build -d; then
        fail "Falha ao subir os containers. Veja o erro acima."
        return 1
    fi

    success "Containers no ar."
    return 0
}

wait_for_api() {
    step "Aguardando a API ficar disponível"

    local max_attempts=30
    local attempt=1

    while [ "$attempt" -le "$max_attempts" ]; do
        if curl --silent --fail --output /dev/null "http://localhost:8000/api/docs/" 2>/dev/null; then
            success "API respondendo em http://localhost:8000"
            return 0
        fi
        printf "."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo ""
    warn "A API não respondeu depois de $((max_attempts * 2))s. Isso pode ser normal se o build ainda estiver rodando."
    warn "Confira os logs com: docker compose logs -f api"
    return 1
}

setup_venv() {
    step "Preparando o ambiente da CLI (virtualenv)"

    if [ -z "${PYTHON_BIN:-}" ]; then
        warn "Python não foi encontrado corretamente — pulando criação do virtualenv."
        warn "Instale o Python e rode manualmente: pip install -r requirements.txt"
        return 1
    fi

    if [ -d ".venv" ]; then
        info "Virtualenv .venv já existe — reaproveitando."
    else
        "$PYTHON_BIN" -m venv .venv
        success "Virtualenv criado em .venv/"
    fi

    # shellcheck disable=SC1091
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    elif [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
    fi

    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    success "Dependências instaladas no virtualenv."
    return 0
}

DOCKER_OK=true
if [ "$SKIP_DOCKER" = false ]; then
    if ! check_docker; then
        DOCKER_OK=false
    fi
else
    info "Pulando verificação do Docker (--skip-docker)."
fi

PYTHON_OK=true
if ! check_python; then
    PYTHON_OK=false
fi

if [ "$DOCKER_OK" = false ]; then
    echo ""
    fail "Não é possível continuar sem Docker. Instale seguindo as instruções acima e rode ./setup.sh de novo."
    exit 1
fi

setup_env_file || exit 1

if [ "$SKIP_DOCKER" = false ]; then
    start_containers || exit 1
    wait_for_api || true   # não trava o script por causa disso, só avisa
fi

if [ "$NO_VENV" = false ] && [ "$PYTHON_OK" = true ]; then
    setup_venv || true
fi

step "Tudo pronto"
echo ""
success "Backend:  http://localhost:8000"
success "Swagger:  http://localhost:8000/api/docs/"
echo ""
info "Para rodar a CLI em outro terminal:"
if [ "$NO_VENV" = false ] && [ "$PYTHON_OK" = true ]; then
    echo "    source .venv/bin/activate   (Windows: .venv\\Scripts\\activate)"
fi
echo "    python cli.py"
echo ""
info "Para parar os containers depois: docker compose down"
info "Dúvidas ou problemas? Registre em docs/FEEDBACK.md"
echo ""
