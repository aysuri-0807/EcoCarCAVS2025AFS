#include "controller.h"
#include <iostream>
#include <algorithm> //for std::min 
#include <cmath> //for pow function 

// Constructor
CaccController::CaccController() {
    // If you want to save any variables in memory (e.g. your constants for a PID controller),
    // you will need to add them to the cpp/include/controller.h file and set their values here
    x = 10;
    egoYPos = 0.0; //Track the Ego cars vertical position (on the road) 
}

// Function that is called every timestep
// It calculates the torque and break commands and passes them back to BESEE
void CaccController::controllerStep(
        // torqueCommand_nm and brakeCommand_mps2 are passed by reference so they are basically the return values of your function
        // See: https://www.geeksforgeeks.org/cpp-functions-pass-by-reference/
        double &torqueCommand_nm,
        double &brakeCommand_mps2,

        // The target speed you are aiming to reach (assuming no lead vehicle)
        double setSpeed, 
        // Your current speed
        double egoSpeed_mps, 
        // If there is a vehicle in front
        bool leadExists,
        // x, x velocity, y, y velocity of the lead vehicle (all 0 if there is no lead)
        double leadXPos,
        double leadXVel,
        double leadYPos,
        double leadYVel
    
    )


{
    
    double interval; 
    double gapError; 
    interval = 0.01; 
    egoYPos += egoSpeed_mps * interval; //Integration of speed to get distance covered in the time segment, append this and store to track position of car 

    if (leadExists) { //Check for lead 
    double leadSpeed_mph = leadYVel * 2.23694; //Conversion mps -> mph 
    double minSafeDistance_m = 2.8 * pow(leadSpeed_mph, 0.45) + 8.0; //Theoretical safe distance 

    double actualGap_m = leadYPos - egoYPos; //Current distance 
    gapError = actualGap_m - minSafeDistance_m; 

    //Smoothing - we do not accelerate or decelerate if the gap error is  +/-5% 
    double acceptableErr = 0.05 * minSafeDistance_m; 

    if (std::abs(gapError) <= acceptableErr){ //If the gapError (regardless of pos or neg) is within 5% of the desired value, negate gapError 
        gapError = 0; 
    }

    double prop_gain = 500; //Smallest unit of torque gain, torque changes in increments of this
    double torque = prop_gain * gapError; //if less than 0, gap is too close; decelerate, more than 0, gap is too far, accelerate 
 
    if (torque >= 0) {
    torqueCommand_nm = std::min(torque, 5000.0); // max torque limit
    brakeCommand_mps2 = 0;
} else {
    torqueCommand_nm = 0;
    brakeCommand_mps2 = std::min(-torque / 3000.0, 10.0); // convert to braking
}
}

else { //If no lead car is detected; rather than do nothing, egocar will simply move forward 
    torqueCommand_nm = 5000; 
    brakeCommand_mps2 = 0; 
}

}