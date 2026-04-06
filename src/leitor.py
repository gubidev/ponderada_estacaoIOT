import json
import requests
import time
import paho.mqtt.client as mqtt

# Configurações
BROKER = "test.mosquitto.org"
PORTA = 1883
TOPICO = "estacao/dados"  # Um tópico único para não misturar com outros
URL_FLASK = "http://localhost:5000/leituras"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Conectado ao broker MQTT ({BROKER})!")
        client.subscribe(TOPICO)
        print(f"Escutando o tópico: {TOPICO}...")
    else:
        print(f"Falha ao conectar. Código: {rc}")

def on_message(client, userdata, msg):
    try:
        # Pega a mensagem do broker e converte de bytes para string
        payload = msg.payload.decode('utf-8')
        dados = json.loads(payload)
        
        # Envia os dados via POST para a sua própria API Flask
        resposta = requests.post(URL_FLASK, json=dados)
        
        if resposta.status_code == 201:
            print(f"Salvo no Banco: {dados}")
        else:
            print(f"Erro ao salvar na API: {resposta.text}")
            
    except json.JSONDecodeError:
        print(f"Erro: O payload recebido não é um JSON válido -> {payload}")
    except requests.exceptions.ConnectionError:
        print("Erro: O servidor Flask parece estar desligado!")

# Configuração e inicialização do Cliente MQTT
print("Iniciando Leitor MQTT...")
cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1) #Versao 1 para nao dar erro, não sei o pq tava dando erro, mas resolveu
cliente.on_connect = on_connect
cliente.on_message = on_message

try:
    cliente.connect(BROKER, PORTA, 60)
    # Loop infinito para manter a conexão ativa e escutando
    cliente.loop_forever()
except KeyboardInterrupt:
    print("\nEncerrando leitor...")
    cliente.disconnect()
except Exception as e:
    print(f"Erro na conexão: {e}")