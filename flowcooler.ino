// Versão funcional usar para teste com leitura de 2 pressão, 2 termopar_1 Vazão
// Versão final para essa etapa e phyton ok
//Receber valor serial de set e dividir por 10
// Esse funcionou melhor e todos sensores 30/08/24
#include <PID_v1.h>
#include "max6675.h"

const int zeroCrossPin = 18;  // Pino para detecção de zero
const int triacPin = 9;       // Pino para controle do triac via PWM
const int flowSensorPin = 21;  // Pino do sensor de fluxo

volatile bool zeroCrossDetected = false;
unsigned long halfCycle = 5250; // Meio ciclo de 60 Hz em microssegundos (8,3 ms)

// Duty Clycle de trabalho do motor
int dutyCyclePWM = 0;

double Setpoint, Input, Output;
double Kp = 5.0 , Ki = 2.5 , Kd = 0;
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

float flowRate;
unsigned long tempo_anterior = 0;
long int frequencia[200];
float medFreq = 0;
int idx = 0;

// Dados para interpolação
const float freqs[] = {0.0, 18.78, 37.6, 56.34, 75.12, 93.9, 112.7, 131.46, 150.2, 169.02, 187.8, 206.58, 225.3};
const float flowRates[] = {0.0, 2.5, 5.0, 7.7, 10.0, 12.5, 15.0, 17.5, 20.0, 22.5, 25.0, 27.5, 30.0 };
const int numPoints = sizeof(freqs) / sizeof(freqs[0]);

volatile int pulseCount = 0;
unsigned long previousMillisFlow = 0;
const unsigned long intervalFlow = 200; // Intervalo em milissegundos

int thermoDO1 = 4, thermoCS1 = 3, thermoCLK1 = 2;
int thermoDO2 = 5, thermoCS2 = 6, thermoCLK2 = 7;
MAX6675 thermocouple1(thermoCLK1, thermoCS1, thermoDO1);
MAX6675 thermocouple2(thermoCLK2, thermoCS2, thermoDO2);

// Variáveis de calibração
float fatorCorrecao1 = 1.0;  // Inicialmente, sem correção
float offset1 = -1.2;        // Offset ajustado para o Termopar 1

float fatorCorrecao2 = 1.0;  // Inicialmente, sem correção
float offset2 = -1.2;        // Offset ajustado para o Termopar 2

int press1 = A1, press2 = A2;
float pressure1 = 0.0, pressure2 = 0.0;
float lastFlowRate = -1, lastPressure1 = -1, lastPressure2 = -1, lastFreq = -1;

void setup() {
  pinMode(zeroCrossPin, INPUT);
  pinMode(triacPin, OUTPUT);
  pinMode(flowSensorPin, INPUT);

  attachInterrupt(digitalPinToInterrupt(zeroCrossPin), zeroCrossInterrupt, FALLING);
  attachInterrupt(digitalPinToInterrupt(flowSensorPin), countPulse, RISING);
    
  pinMode(thermoDO1, INPUT);
  pinMode(thermoCS1, OUTPUT);
  pinMode(thermoCLK1, OUTPUT);

  pinMode(thermoDO2, INPUT);
  pinMode(thermoCS2, OUTPUT);
  pinMode(thermoCLK2, OUTPUT);

  Serial.begin(9600);
  Serial.println("Ajuste Motor");

  myPID.SetMode(AUTOMATIC);
  myPID.SetOutputLimits(0, 255);  // Define o limite da saída do PID
  Setpoint = 0;

  // Configuração de baixo do Timer 5 do Atmel 2560
  cli();
  TCCR5A = 0;              
  TCCR5B = (1 << WGM52) | (1 << CS51);  // Modo CTC com prescaler de 8
  unsigned int aux = ( 2 * 4000 ) - 1;
  OCR5AH = (aux >> 8) & 0xFF; 
  OCR5AL = aux & 0xFF;     
  TIMSK5 = (1 << OCIE5A);
  sei();
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillisFlow >= intervalFlow) 
  {
    previousMillisFlow = currentMillis;

    // Controle de Fluxo pelo PID
    medFreq = 0;
    for( int i = 0; i < (sizeof(frequencia)/ 4); i ++ ) {
      medFreq += frequencia[i];
    }    
    flowRate = getFlowRate( medFreq / (sizeof(frequencia)/ 4) );
    Input = flowRate;  // Atualiza o input do PID com o valor do fluxo
    
    // Calcula o novo valor de saída com base no PID
    myPID.Compute();   
    
    // Mapeia a saída do PID para o ciclo de trabalho
    dutyCyclePWM = map(Output, 0, 255, 0, 100);  

    // Aquisição dos dados de Temperatura e pressão
    int val1 = analogRead(press1);
    int val2 = analogRead(press2);
    
    pressure1 = ((val1 / 1023.0) * 10.0) / 1.03;
    pressure2 = ((val2 / 1023.0) * 10.0) / 1.03;

    // Ajuste os valores lidos dos termopares
    float leituraTermopar1 = thermocouple1.readCelsius() * fatorCorrecao1 + offset1;
    float leituraTermopar2 = thermocouple2.readCelsius() * fatorCorrecao2 + offset2;
    
    Serial.print( leituraTermopar1 );
    Serial.print(";");
    Serial.print( leituraTermopar2 );
    Serial.print(";");
    Serial.print( pressure1 );
    Serial.print(";");
    Serial.print( pressure2 );
    Serial.print(";");
    Serial.println( flowRate );
    }
  
    if (Serial.available()) {
      String command = Serial.readStringUntil('\n');
      processCommand(command);
    }
}

void countPulse() {
  pulseCount++;
  unsigned long tempo_atual = millis(); 
  unsigned long deltaT = tempo_atual - tempo_anterior;
  frequencia[idx] = 1000.0 / deltaT;
  if( frequencia[idx] <= 4 ) {
    for( int i = 0; i < (sizeof(frequencia)/ 4); i ++ ) {
      frequencia[i] = 0;
    } 
  }
  
  tempo_anterior = tempo_atual;
  if( idx < (sizeof(frequencia)/ 4) ) {
       idx ++;
  }
  else idx = 0;
}

float getFlowRate(float frequencia) {
  if (frequencia < freqs[0]) return flowRates[0];
  if (frequencia > freqs[sizeof(freqs)/sizeof(freqs[0]) - 1]) return flowRates[sizeof(flowRates)/sizeof(flowRates[0]) - 1];

  for (int i = 0; i < sizeof(freqs)/sizeof(freqs[0]) - 1; i++) {
    if (frequencia >= freqs[i] && frequencia <= freqs[i + 1]) {
      float x0 = freqs[i];
      float x1 = freqs[i + 1];
      float y0 = flowRates[i];
      float y1 = flowRates[i + 1];

      return y0 + (frequencia - x0) * (y1 - y0) / (x1 - x0);
    }
  }
  return 0.0;
}

void zeroCrossInterrupt() {
  if (dutyCyclePWM != 0) {
    digitalWrite(triacPin, LOW);
    unsigned int periodo_us = (108 - dutyCyclePWM) * halfCycle / 100;
    unsigned int aux = ( 2 * periodo_us ) - 1;
    OCR5AH = (aux >> 8) & 0xFF; 
    OCR5AL = aux & 0xFF;
    TCNT5H = 0; // Zera o Timer5  
    TCNT5L = 0;
    zeroCrossDetected = true;
  }
}

ISR(TIMER5_COMPA_vect) {
  if ( zeroCrossDetected == true )
  {
    digitalWrite(triacPin, HIGH);
    delayMicroseconds(100);
    digitalWrite(triacPin, LOW);
    zeroCrossDetected = false;
  }
}

void processCommand(String command) {
  command.trim();

  if (command.startsWith("set ")) {
    // Converta o valor para float para lidar com decimais
    float value = command.substring(4).toFloat();
    // Divida o valor por 10
    float adjustedValue = value / 10;
    // Verifique se o valor ajustado está no intervalo permitido
    if (adjustedValue >= 0 && adjustedValue <= 30) {
      Setpoint = adjustedValue;
      Serial.print("Setpoint ajustado para: ");
      Serial.print("; ");
      Serial.print(Setpoint, 1); // Mostra 1 casa decimal
      Serial.print("; ");
      Serial.print(Setpoint, 1); // Mostra 1 casa decimal
      Serial.print("; ");
      Serial.print(Setpoint, 1); // Mostra 1 casa decimal
      Serial.print("; ");
      Serial.println(Setpoint, 1); // Mostra 1 casa decimal
 
    } else {
      Serial.print("Erro: Valor ajustado deve estar entre 0 e 30.");
      Serial.print("; ");
      Serial.print("E");
      Serial.print("; ");
      Serial.print("E");
      Serial.print("; ");
      Serial.print("E");
      Serial.print("; ");
      Serial.println("E");
    }
  } else if (command.equals("emergency")) {
    Serial.println("Comando de emergência recebido.");
    Setpoint = 0;
  } else {
    Serial.print("Comando não reconhecido.");
      Serial.print("; ");
      Serial.print("E");
      Serial.print("; ");
      Serial.print("E");
      Serial.print("; ");
      Serial.print("E"); 
      Serial.print("; ");
      Serial.println("E");
  }
}
