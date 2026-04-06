# Estação Meteorológica IoT

Sistema de monitoramento meteorológico com ESP32, broker MQTT, API REST Flask e banco de dados SQLite.

---

## Decisões de Arquitetura

No arquivo da ponderada pede:

```
Arduino → Porta Serial USB → Script Python (serial) → API Flask → SQLite → Interface Web
```

O meu projeto segue uma arquitetura um pouco diferente, substituindo a comunicação serial por MQTT:

```
ESP32 (WiFi) → Broker MQTT (test.mosquitto.org) → leitor.py (subscriber) → API Flask → SQLite → Interface Web
```

### O que mudou e por quê

| Elemento | Especificação | Este projeto | Motivo |
|---|---|---|---|
| Hardware | Arduino Uno | ESP32 | ESP32 possui WiFi nativo, eliminando a necessidade de cabo USB para transferência de dados |
| Protocolo | Serial USB | MQTT (TCP/IP) | MQTT é o protocolo padrão de IoT; permite que o dispositivo envie dados sem estar fisicamente conectado ao servidor |
| Broker | — | `test.mosquitto.org` (público) | Broker público para desenvolvimento, sem necessidade de infraestrutura adicional |
| Leitor serial | `serial_reader.py` via `pyserial` | `leitor.py` via `paho-mqtt` | Substitui a leitura serial por assinatura no tópico MQTT `estacao/dados` |
| Arquivo `.ino` | `estacao.ino` (Arduino) | `codigo.ino` (ESP32) | Sketch adaptado para ESP32 com suporte a WiFi e PubSubClient |
| Simulação | Opcional no Arduino ou Python | Embutida no ESP32 (`modoSimulacao = true`) | O próprio ESP32 gera dados simulados realistas quando os sensores físicos não estão montados |

### Sobre o ESP32 e MQTT

O leitor MQTT (`leitor.py`) conecta ao broker público `test.mosquitto.org` pela internet. Para que dados entrem no sistema, o ESP32 precisa estar **ligado e conectado ao WiFi** — ele não precisa estar fisicamente conectado ao computador via USB. Sem o ESP32 publicando mensagens no tópico, o leitor ficará aguardando e nenhum dado será inserido no banco.

---

## Estrutura do Projeto

```
ponderada comp/
├── src/
│   ├── app.py              # Aplicação Flask principal
│   ├── database.py         # Funções de acesso ao SQLite (CRUD)
│   ├── leitor.py           # Subscriber MQTT → POST para a API Flask
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/main.js      # Gráfico (Chart.js), DELETE e PUT via fetch
│   └── templates/
│       ├── base.html
│       ├── index.html      # Dashboard com gráfico e últimas 10 leituras
│       ├── historico.html  # Tabela completa com editar/excluir
│       └── editar.html     # Formulário de edição pré-preenchido
├── arduino/
│   └── codigo.ino          # Sketch do ESP32 (WiFi + MQTT + DHT11 + simulação)
├── schema.sql              # Script DDL do banco de dados
├── dados.db                # Banco SQLite com leituras de exemplo
├── requirements.txt
└── README.md
```

---

## Requisitos

- Python 3.10 ou superior
- ESP32 com acesso à internet (WiFi)
- Arduino IDE 2.x (para gravar o sketch no ESP32)
- Sensor DHT11 ligado ao pino 4 do ESP32 — **opcional** (veja modo simulação abaixo)

---

## Instalação

### 1. Clone o repositório e crie o ambiente virtual

```bash
git clone <url-do-repositorio>
cd "ponderada comp"

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure o ESP32

Abra `arduino/codigo.ino` na Arduino IDE e ajuste as credenciais de rede:

```cpp
const char* ssid     = "seu_wifi";
const char* password = "sua_senha";
```

**Modo simulação** (sem sensor físico): a variável `modoSimulacao` já está definida como `true`. O ESP32 irá gerar valores aleatórios realistas de temperatura (20–35 °C) e umidade (40–80 %) sem precisar do DHT11 conectado.

```cpp
bool modoSimulacao = true;  // troque para false se o DHT11 estiver montado
```

Grave o sketch no ESP32 e confirme no Monitor Serial que ele se conecta ao WiFi e ao broker.

---

## Execução

Abra **dois terminais** com o ambiente virtual ativado.

### Terminal 1 — Servidor Flask

```bash
cd src
python app.py
```

O servidor sobe em `http://localhost:5000`.

### Terminal 2 — Leitor MQTT

```bash
cd src
python leitor.py
```

O leitor conecta ao broker `test.mosquitto.org`, assina o tópico `estacao/dados` e encaminha cada mensagem recebida via POST para a API Flask. Com o ESP32 ligado e publicando, os dados aparecem automaticamente no banco e na interface.

> **Nota:** inicie o Flask antes do leitor para evitar erros de conexão na primeira mensagem.

---

## Interface Web

| Página | URL | Descrição |
|---|---|---|
| Dashboard | `http://localhost:5000/` | Gráfico de linha (temperatura e umidade) + últimas 10 leituras em cards |
| Histórico | `http://localhost:5000/historico` | Tabela completa com botões de editar e excluir |
| Edição | `http://localhost:5000/editar/<id>` | Formulário pré-preenchido; salva via PUT |

---

## Rotas da API REST

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Painel principal (HTML) |
| `GET` | `/leituras` | Histórico completo — HTML por padrão, JSON com `?formato=json` |
| `GET` | `/leituras/<id>` | Detalhe de uma leitura específica (JSON) |
| `GET` | `/historico` | Alias para `/leituras` (HTML) |
| `GET` | `/editar/<id>` | Formulário de edição (HTML) |
| `POST` | `/leituras` | Insere nova leitura (JSON) |
| `PUT` | `/leituras/<id>` | Atualiza uma leitura (JSON) |
| `DELETE` | `/leituras/<id>` | Remove uma leitura |
| `GET` | `/api/estatisticas` | Média, mín e máx de temperatura, umidade e pressão (JSON) |
| `GET` | `/api/leituras/recentes` | Últimas 20 leituras em JSON (usado pelo gráfico) |

### Exemplo — inserir leitura manualmente

```bash
curl -X POST http://localhost:5000/leituras \
  -H "Content-Type: application/json" \
  -d '{"temperatura": 24.5, "umidade": 62.0, "pressao": 1013.2}'
```

Resposta esperada (`201 Created`):
```json
{"id": 1, "status": "criado"}
```

### Exemplo — atualizar leitura

```bash
curl -X PUT http://localhost:5000/leituras/1 \
  -H "Content-Type: application/json" \
  -d '{"temperatura": 25.0, "umidade": 60.0}'
```

### Exemplo — excluir leitura

```bash
curl -X DELETE http://localhost:5000/leituras/1
```

---

## Banco de Dados

Arquivo: `dados.db` (SQLite, criado automaticamente na raiz do projeto).

```sql
CREATE TABLE IF NOT EXISTS leituras (
    id          INTEGER  PRIMARY KEY AUTOINCREMENT,
    temperatura REAL     NOT NULL,
    umidade     REAL     NOT NULL,
    pressao     REAL,
    localizacao TEXT     DEFAULT 'Lab',
    timestamp   DATETIME DEFAULT (datetime('now', 'localtime'))
);
```

O banco já acompanha o repositório com ao menos 30 leituras de exemplo em `dados.db`.

## Dependências

```
Flask==3.1.3
paho-mqtt==2.1.0
requests==2.33.1
pyserial==3.5
```
