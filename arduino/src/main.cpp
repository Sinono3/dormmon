#include <Arduino.h>

/*
This script measures the noise level each iteration and
calculates the average of the last averageSize readings.

If the calculated average reaches the given threshold, "ALERT" is printed.
*/

const int soundPin = A0;
const int digitalSound = 4;
const int noiseThreshold = 22;

// throttle: gives number of iterations skipped before average calculation and serial print
const int delayNum = 500;

// calculation limiter: gives the number of readings to average over
const int averageSize = 500;

int sounds[averageSize] = {}; // stores the last noise measurements

void setup() {
	Serial.begin(9600);
	pinMode(LED_BUILTIN, OUTPUT);
	pinMode(soundPin, INPUT);
	pinMode(digitalSound, INPUT);
}

// calculates average noise level
double avg(const int sounds[], int count) {
	double sum = 0;
	for (int j = 0; j < count; ++j) {
		sum += (double)sounds[j];
	}
	return sum / (double)count;
}

int index = 0;
void loop() {
	int digitalSoundIn = digitalRead(digitalSound);
	// int analogSoundIn = analogRead(soundPin);
	
	// sounds[index] = analogSoundIn;

	// // increment index but never higher than size of sounds[]
	// index = (index + 1) % averageSize;

	// if (index % delayNum == 0) {
	// 	double averageNoise = avg(sounds, averageSize);

	// 	// interesting for coding, unnecessary for regular operation
	// 	Serial.print((double)analogSoundIn, 3);
	// 	Serial.print(",");
	// 	Serial.print(digitalSoundIn, 3);
	// 	Serial.println();

	// 	// if the average is higher than the treshold, an alert is printed
	// 	if (averageNoise >
	// 		noiseThreshold) { //exchange averageNoise with analogSoundIn to use the current reading instead of average
	// 		digitalWrite(LED_BUILTIN, HIGH);
	// 		// Serial.print("ALERT! "); // trigger for rpi to show alert popup
	// 		// Serial.print("averageNoise");
	// 	} else {
	// 		digitalWrite(LED_BUILTIN, LOW);
	// 		// Serial.println("No Alert"); // trigger for rpi to close alert popup
	// 	}
	// }
	if (digitalSoundIn) {
		Serial.print("ALERT! "); // trigger for rpi to show alert popup
		delay(4000);

	} else {
		Serial.println("No Alert"); // trigger for rpi to close alert popup
	}
}
