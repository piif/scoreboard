// PIF_TOOL_CHAIN_OPTION: EXTRA_LIBS := ArduinoTools

/**
 * first try to dialog with scoreboard Grunenwald, similar to this one :
 * http://www.casalsport.com/afficheur-grunenwald-gd2150p_78353-10-100-1-p.r.htm
 *
 * make use of my serialInput lib : see https://github.com/piif/ArduinoTools/tree/master/serialInput
 */

#ifdef PIF_TOOL_CHAIN
	#include <Arduino.h>
	#include "serialInput/serialInput.h"
#else
	// other includes with short pathes
	#include "serialInput.h"
#endif

#ifndef DEFAULT_BAUDRATE
	#define DEFAULT_BAUDRATE 115200
#endif

#define DATA_OUT 2
#define CLOCK_OUT 3

int Time = 0,
	VisitorGoal = 0,
	LocalGoal = 0,
	VisitorFault = 0,
	LocalFault = 0,
	Buzzer = 0;

// top, top right, bottom right, bottom, bottom left, top left, middle, nc1, nc2, nc3
byte segments[] = {
	//...mLlbrRt
	0b0000111111, // 0
	0b0000000110, // 1
	0b0001011011, // 2
	0b0001001111, // 3
	0b0001100110, // 4
	0b0001101101, // 5
	0b0001111101, // 6
	0b0000000111, // 7
	0b0001111111, // 8
	0b0001101111, // 9
};

struct _bitBuffer {
	word BVu;
	word BVd;
	word FV;
	word BLu;
	word BLd;
	word FL;
	word Md;
	word Mu;
	word Sd;
	word Su;
	word Bz;
} bitBuffer;

word *buffer = (word *)&bitBuffer;

void updateData() {
	int t = Time;
	bitBuffer.Su = segments[t % 10];
	t /= 10;
	bitBuffer.Sd = segments[t % 10];
	t /= 10;
	bitBuffer.Mu = segments[t % 10];
	t /= 10;
	bitBuffer.Md = segments[t % 10];

	bitBuffer.FV = segments[VisitorFault];
	bitBuffer.FL = segments[LocalFault];

	bitBuffer.BVu = segments[VisitorGoal % 10];
	bitBuffer.BVd = segments[VisitorGoal / 10];
	bitBuffer.BLu = segments[LocalGoal % 10];
	bitBuffer.BLd = segments[LocalGoal / 10];

	bitBuffer.Bz = Buzzer ? 0b1000000000 : 0;
}

void sendData() {
	for(byte i = 0; i < 11; i++) {
		for(word mask = 0b1000000000; mask > 0; mask >>=1) {
			digitalWrite(DATA_OUT, buffer[i] & mask ? LOW : HIGH);
			digitalWrite(CLOCK_OUT, HIGH);
			delayMicroseconds(30);
			digitalWrite(CLOCK_OUT, LOW);
			delayMicroseconds(40);
		}
	}
}

void help() {
	Serial.println("t [0000 .. 9999] set time");
	Serial.println("v [00 .. 99] set goal for visitor");
	Serial.println("l [00 .. 99] set goal for local");
	Serial.println("V [0 .. 9] set fault for visitor");
	Serial.println("L [0 .. 9] set fault for local");
	Serial.println("z [1,0] set buzzer on/off");
	Serial.println("state :");
	Serial.print(" Time : "); Serial.println(Time);
	Serial.print(" Visitor : "); Serial.print(VisitorGoal); Serial.print(" / "); Serial.println(VisitorFault);
	Serial.print(" Local   : "); Serial.print(LocalGoal);   Serial.print(" / "); Serial.println(LocalFault);
	Serial.print(" Buffer : ");
	for(byte i = 0; i < 11; i++) {
		Serial.print("   "); Serial.println(buffer[i], BIN);
	}
}

InputItem list[] = {
	{ 't', 'i', (void *)&Time },
	{ 'v', 'i', (void *)&VisitorGoal },
	{ 'l', 'i', (void *)&LocalGoal },
	{ 'V', 'i', (void *)&VisitorFault },
	{ 'L', 'i', (void *)&LocalFault },
	{ 'z', 'i', (void *)&Buzzer },
	{ '?', 'f', (void *)help }
};

void setup(void) {
	Serial.begin(DEFAULT_BAUDRATE);
	pinMode(DATA_OUT, OUTPUT);
	pinMode(CLOCK_OUT, OUTPUT);

	registerInput(sizeof(list), list);
	updateData();
	help();
}

void loop() {
	handleInput();
	updateData();
	sendData();
	delay(100);
}
