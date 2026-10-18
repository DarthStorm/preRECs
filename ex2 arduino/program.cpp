// sources:
// https://github.com/curiores/ArduinoTutorials/blob/main/encoderControl/part3/part3.ino
// https://www.youtube.com/watch?v=dTGITLnYAY0

// i assume you got the memo
// (from my previous exercise)
// and have read my repo
// :3 

// -- READ ME --
// USER SETTINGS
// since tinkercad is different from irl arduino,
// motor movements will likely be inaccurate
// fortunately, i have predicted this problem

float scale_factor = 1;

// if the motor is not doing consistent 360s anymore,
// but is doing consistent spins,
// set the scale factor to a low number (maybe 0.5)
// and slowly increase it until you are getting consistent 360s
// cant test in workshop rn sorry :(

// setting number 2: either 90, 180 or 360 
// to get corresponding degree spins
// you can also try anything

int degrees = 360;

// code below

#include <util/atomic.h>

// Encoder pins
// yellow
const int ENCA = 2;
// purple
const int ENCB = 3;


// Motor driver pins
// 11 behaves like a PWM, can treat as one
const int PWM = 11;
const int IN2 = 10;
const int IN1 = 9;

bool stopped = false;


int degrees_to_counts(int deg){
  return 460.0 * deg / 360 * scale_factor;
}


int target = degrees_to_counts(degrees);
int slow_threshhold = 40; // when motor gets close
int error = 5; // if motor gets in error range it will stop

volatile long pulseCount = 0;




void readEncoder() {
  // triggered when A activates
  bool a = digitalRead(ENCA);
  bool b = digitalRead(ENCB);

  // a will always be 1
  // so if a == b then previously it was 01 -> 11
  // and if a != b then it was 00 -> 10
  // diff directions, take one as positive
  if (a == b) {
    pulseCount++;
  } else {
    pulseCount--;
  }
}




void setup() {
  Serial.begin(9600);

  // Encoder inputs
  // pullup removes noise
  pinMode(ENCA, INPUT_PULLUP);
  pinMode(ENCB, INPUT_PULLUP);

  // Motor outputs
  pinMode(PWM, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  // when A is activated run readEncoder
  attachInterrupt(
    digitalPinToInterrupt(ENCA),
    readEncoder, // up there
    CHANGE
  );

  // Run motor in one direction
  // digitalWrite(IN1, HIGH);
  // digitalWrite(IN2, LOW);
  // analogWrite(PWM, 100);
}

void printPosition() {
  // print cd
  static unsigned long lastPrint = 0;

  if (millis() - lastPrint >= 500) {
    long count;
	
    // magic
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
      count = pulseCount;
    }

    Serial.print("Encoder position: ");
    Serial.println(count);

    lastPrint = millis();
  }
}

// sets motor to spin in direction `dir` with pwm `pwmVal`
// pwm, in1 and in2 are inputs
// `dir` is either -1, 0, or 1
// stole from someone elses github
void setMotor(int dir, int pwmVal, int pwm, int in1, int in2){
  analogWrite(pwm,pwmVal);
  if(dir == 1){
    digitalWrite(in1,HIGH);
    digitalWrite(in2,LOW);
  }
  else if(dir == -1){
    digitalWrite(in1,LOW);
    digitalWrite(in2,HIGH);
  }
  else{
    digitalWrite(in1,LOW);
    digitalWrite(in2,LOW);
  }
}

int sign(int x) {
  if (x == 0) {return 0;}
  else if (x < 0) {return -1;}
  else if (x > 0) {return 1;}
}

void motorLoop(int target){
  // pid goes here
  // pid globals:
  static long prevT = micros();
  static float eprev = 0;
  static float eintegral = 0;
  
  float kp = 1;
  float kd = 0; // derivative
  float ki = 0; // integral
  
  // get deltatime
  long currT = micros();
  float delta = (static_cast<float>(currT) - prevT) / 1.0e6; // in seconds
  prevT = currT;
  
  int e = target - pulseCount; // swap if not working
  
  // get derivative, approx from limit definition
  float dedt = (e - eprev) / delta;
  eintegral += e * delta;
  
  // control signal
  float u = kp*e + kd*dedt + ki*eintegral;
  
  float power = fabs(u);
  if (power > 255) {power = 255;}
  
  int dir = sign(u);
  
  // send it! (to the motor)
  setMotor(dir, power, PWM, IN1, IN2);
  
  // for later
  eprev = e;
}


void loop() {
  
  // dynamically set target here to move motor to specified position as well!
  motorLoop(target); // leave. this. in.
}
