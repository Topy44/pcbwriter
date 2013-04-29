#ifndef PCBWRITER_PINS_H
#define PCBWRITER_PINS_H

// DEBUG0_OUT: PB0
#define DEBUG0_OUT_PORT GPIOB
#define DEBUG0_OUT_PIN  GPIO0

// DEBUG1_OUT: PB1
#define DEBUG1_OUT_PORT GPIOB
#define DEBUG1_OUT_PIN  GPIO1

/*  Stepper:
    PD0: ORANGE
    PD1: BROWN
    PD2: YELLOW
    PD3: BLACK
 */

#define STEPPER_PORT GPIOD
#define STEPPER_ORANGE_PIN GPIO0
#define STEPPER_BROWN_PIN GPIO1
#define STEPPER_YELLOW_PIN GPIO2
#define STEPPER_BLACK_PIN GPIO3

#endif