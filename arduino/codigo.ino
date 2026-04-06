#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

// CONFIGURAÇÕES DE REDE E MQTT

const char* ssid = "nome";
const char* password = "senha wifi";
const char* mqtt_server = "test.mosquitto.org"; 
const char* topico_dados = "estacao/dados"; // Mesmo tópico do script Python

WiFiClient espClient;
PubSubClient client(espClient);

// CONFIGURAÇÕES DOS SENSORES

#define DHTPIN 4      // Pino do DHT11 no ESP32
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Coloque como 'true' para simular os dados, ou 'false' se tiver os sensores montados
bool modoSimulacao = true; 
unsigned long tempoAnterior = 0;
const long intervaloEnvio = 5000; // Envia a cada 5 segundos

void setup_wifi() {
  delay(10);
  Serial.println("\nConectando ao WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentando conexão MQTT...");
    String clientId = "ESP32_Estacao_G3_";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("Conectado ao broker!");
    } else {
      Serial.print("Falha, erro=");
      Serial.print(client.state());
      Serial.println(" Tentando de novo em 5s...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  
  if (modoSimulacao) {
    randomSeed(analogRead(0));
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long tempoAtual = millis();
  
  // Condicional de tempo (não trava o ESP32 como o delay)
  if (tempoAtual - tempoAnterior >= intervaloEnvio) {
    tempoAnterior = tempoAtual;

    float temp, umid;

    if (modoSimulacao) {
      temp = random(200, 350) / 10.0; // Gera temperatura entre 20.0 e 35.0
      umid = random(400, 800) / 10.0; // Gera umidade entre 40.0 e 80.0
    } else {
      temp = dht.readTemperature();
      umid = dht.readHumidity();
    }

    if (!isnan(temp) && !isnan(umid)) {
      // Monta o JSON em uma String
      String payload = "{";
      payload += "\"temperatura\":" + String(temp, 1) + ",";
      payload += "\"umidade\":" + String(umid, 1) + ",";
      payload += "\"pressao\": 1013.2"; // Fixo por enquanto, adicione o BMP180 aqui se quiser
      payload += "}";

      // Publica no broker
      client.publish(topico_dados, payload.c_str());
      
      Serial.print("Enviado para MQTT: ");
      Serial.println(payload);
    } else {
      Serial.println("Erro ao ler os sensores!");
    }
  }
}