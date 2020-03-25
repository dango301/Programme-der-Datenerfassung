
int durs[] = {480, 400, 320, 240, 160, 80}; // Light Up Durations
int del = 1, // intervall for data collection in ms
    warmup = 40, // measured time before LED is switched on
    cooldown = 80, // Time for which LED remains off in between
    T = 80, // multiplier for measured time after LED is switched off
    amount = 15; // repitions of each in durs


void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(8, OUTPUT);
  Serial.println("DATA_START");
  Serial.println();


  //executed measurements
  for (int i = 0; i < 6; i++) {
    for (int j = 0; j < amount; j++) {
     test(durs[i]);
     delay(2500); // Pause, sodass sich Lichtwerte zwischen Messungswiederholungen zurücksetzen können
    }
  }

  Serial.print("DATA_END"); //end of program:
}

void loop() {
}


void exportData(int T[], int D[], int LEN, float DUR) {
  Serial.println("MEASUREMENT_DURATION: " + String(DUR));
  for (int i = 0; i < LEN; i++)
    Serial.println(String(T[i]) + ":" + String(D[i]));
  Serial.println("MEASUREMENT_END");
  Serial.println();
}

void test(float dur) {

  const long int start = millis() + warmup; // start is set in future so LED lights up at t=0
  const int len = ceil((warmup + 2 * (dur + T) + cooldown) / del);
  int t[len],
      d[len],
      index = 0,
      cT = millis() - start;


  while (cT < 0) {
    t[index] = cT;
    d[index++] = analogRead(A0);
    delay(del);
    cT = millis() - start;
  }


  digitalWrite(LED_BUILTIN, HIGH);
  digitalWrite(8, HIGH);

  while (cT <= dur) {
    t[index] = cT;
    d[index++] = analogRead(A0);
    delay(del);
    cT = millis() - start;
  }


  digitalWrite(LED_BUILTIN, LOW);
  digitalWrite(8, LOW);

  while (cT <= dur + T) {
    t[index] = cT;
    d[index++] = analogRead(A0);
    delay(del);
    cT = millis() - start;
  }


  digitalWrite(LED_BUILTIN, HIGH);
  digitalWrite(8, HIGH);

  while (cT <= 2 * dur + T) {
  t[index] = cT;
    d[index++] = analogRead(A0);
    delay(del);
    cT = millis() - start;
  }


  digitalWrite(LED_BUILTIN, LOW);
  digitalWrite(8, LOW);

  while (cT <= 2 * dur + 2 * T) {
  t[index] = cT;
    d[index++] = analogRead(A0);
    delay(del);
    cT = millis() - start;
  }


  exportData(t, d, index, dur);
}
