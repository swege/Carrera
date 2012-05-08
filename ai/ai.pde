/*
    This program is used to control the speed of the car for the individual
    track sections. Currently the values / the speed is hardcoded and they
    need to be adjusted manually for each track.
*/
int car_pin = 11;
int power_release = 12;
unsigned long time = 0;

// the speed of the car when it enters the light barrier
// Sensor number:    0     1     2     3     4     5     6     7     8     9    10    11
int VALUES1[12] = {   1,  175,    1,  200,    1,  120,   70,  120,  120,  120,  120,  255};
// time in ms to keep that speed
int DELAY[12] =   {  45,   45,   75,   50,   80,  200,  100,  999,  999,  999,  999,  200};
// new speed for the car when the time from above is over
int VALUES2[12] = { 160,  140,  140,  150,  140,  110,  120,  120,  120,  120,  120,  180};

int START_VALUE = 120;


void setup() {
    int j;
    for (int i=0; i<12; i++) {
        j = i + 22;
        pinMode(j, INPUT);
        // connect pull up resistor
        digitalWrite(j, HIGH);
    }
    pinMode(11, OUTPUT);
    digitalWrite(11, HIGH);
    pinMode(power_release, INPUT);
}

void loop() {
    int last_sensor = -1;
    int value = START_VALUE;
    bool sensor;
    int j;
    int i = 0;
    while (true) {
        // check the start signal of the UE9
        while (!digitalRead(power_release)) {
            // power the track off
            analogWrite(car_pin, 255);
        }
        // only update the pwm signal if the value actually changed, should take
        // some load off the arduino
        // break
        if (value == 0) {
            analogWrite(car_pin, 255 - value);
            //delay(1);
            //analogWrite(10, 255);
        } else {
            //analogWrite(10, 0);
            //delay(1);
            analogWrite(car_pin, 255 - value);
        }
        for(int i=0; i<12; i++) {
            j = i + 22;
            sensor = digitalRead(j);
            if (sensor == LOW) {
                value = VALUES1[i];
                time = millis();
                last_sensor = i;
            }
            if (last_sensor != -1 && millis() - time > DELAY[last_sensor]) {
                value = VALUES2[last_sensor];
            }
        }
    }
}
