 # AI-ENHANCED-FLIGHT-DECISION-SUPPORT-SEOUL-TOKYO-
This is NOT SUPPOSE TO FLY AT ALL because the maximum flight distance of Cessna 172 is 1,185 km. But it's just a code to show the ai trying to find the best path, except for all that.


# AI-Cessna-172
## AI Decision Support: Seoul to Tokyo Flight Simulator

An advanced AI copilot simulating a **1,147 km** flight from Seoul to Tokyo in a **Cessna 172**, using **neural networks**, **real-time data**, a **GUI**, and **weight dynamics**.  
**Note**: This is purely for demonstration – the actual maximum range of a typical Cessna 172 is around **1,185 km** – but this project illustrates AI-based pathfinding and safety checks.

---

## Key Features

1. **Seoul-Tokyo Route**  
   - Simulates a **1,147 km** flight distance, continuously tracked.
   - Aviation constraints include a **1,185 km** approximate maximum range.

2. **Weight & CG Dynamics**  
   - Adjusts performance based on pilot and cargo weights.
   - Computes center of gravity (CG) for stability considerations.

3. **Neural Network Inference**  
   - Small **Keras** model classifies “critical” vs. “non-critical” states.
   - Demonstrates how AI can augment pilot decision-making.

4. **Real-Time Data**  
   - Simulated ADS-B feed for altitude, wind, and engine variations.
   - Updates occur every half second to mimic real-time conditions.

5. **Pilot GUI**  
   - **Tkinter** interface displays altitude, speed, fuel status, and AI recommendations.
   - Shows top advisory messages (e.g., “Storm! Divert?” or “Low Fuel!”).

---

## Installation

1. **Clone this repository**:
   
   ```bash
   git clone https://github.com/imnotwcked/AI-ENHANCED-FLIGHT-DECISION-SUPPORT-SEOUL-TOKYO-
   cd AI-ENHANCED-FLIGHT-DECISION-SUPPORT-SEOUL-TOKYO-
2. 2. Install dependencies:
   ```bash
   pip install -r requirements.txt

## Usage

1. Run the simulation:
   
   ```bash
   python ai_decision_support.py
   
2. Provide weight details (example):
    Pilot weight (lbs): 145
    Cargo weight (lbs): 50
   
3. Watch the GUI
    The flight updates every half second.
    Recommendations appear for issues like low fuel, near-stall speed, or severe weather.

## Experimental Results
Flight Duration: ~5 hours at ~230 km/h (depending on final speed/fuel usage).

Completion:
    Tokyo reached (~5,000 simulation steps), or
    Fuel runs out → forced landing scenario.
    
Real-Time Updates: The GUI refreshes every 0.5 seconds

## CODE EXPLANATION

`flight_decision_support.py` is divided into:

1. **Global Constants**  
   - Placeholder values for physics, distances (e.g., `AIR_DENSITY`, `FUEL_BURN_RATE`, etc.)

2. **`FlightState` Dataclass**  
   - Stores key flight variables like altitude, airspeed, fuel, weather severity, and distance remaining.

3. **`AIDecisionSupport` Class**  
   - **Builds/Trains a Minimal Neural Network** (toy data) for “critical vs. non-critical” classification.  
   - **Runs Flight Simulation Logic**: Periodically updates altitude, speed, fuel usage, and weather conditions.  
   - **Condition Checks**: Combines neural network output with a rule-based weighting system to generate recommendations.  
   - **Tkinter GUI**: Displays real-time flight parameters and AI suggestions.

4. **`main()` Function**  
   - Prompts the user for pilot/cargo weight.  
   - Instantiates `AIDecisionSupport` and runs the simulation loop.  
