import time
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import tkinter as tk
from dataclasses import dataclass
from typing import List, Tuple
import logging
import threading

AIR_DENSITY = 1.225           # kg/m^3 (not heavily used in this simplified example)
WING_AREA = 174               # ft^2 (placeholder for lift calculation)
LIFT_COEFFICIENT = 1.2
GRAVITY = 32.174              # ft/s^2
DISTANCE_SEOUL_TOKYO = 1147   # km
CRUISE_SPEED = 230            # km/h
MAX_RANGE = 1185              # km
FUEL_CAPACITY = 56            # gallons
FUEL_BURN_RATE = 8.4          # gallons/hour (derived from range)
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


@dataclass
class FlightState:
    """
    Stores flight parameters for the Seoul-Tokyo route.
    All values are rough placeholders for demonstration.
    """
    altitude: float         # feet
    airspeed: float         # knots
    fuel: float             # gallons
    heading: float          # degrees (0-359)
    vertical_speed: float   # feet/min
    weather_severity: int   # 0=clear, 1=turbulent, 2=storm
    engine_rpm: float       # rpm
    wind_speed: float       # knots
    total_weight: float     # lbs
    cg_position: float      # inches aft of datum
    distance_remaining: float  # km to destination

class AIDecisionSupport:
    """
    AI copilot for a conceptual Seoul→Tokyo flight.
    - Uses a minimal neural net for 'critical vs. non-critical' flight states.
    - Combines rule-based logic (weights dict) with a single-output MLP.
    - Displays real-time recommendations via Tkinter.
    """

    def __init__(self, pilot_weight: float, cargo_weight: float):
        """Initialize plane specs, flight state, neural net, and GUI."""
        # Basic aircraft specs (simplified)
        self.base_weight = 1670         # lbs (empty weight, placeholder)
        self.total_weight = self.base_weight + pilot_weight + cargo_weight
        self.max_gross_weight = 2550    # lbs
        self.max_altitude = 14000       # feet
        self.max_fuel = FUEL_CAPACITY   # gallons
        self.max_rpm = 2700             # redline rpm
        self.min_safe_altitude = 1000   # feet

        # CG calculation (extremely simplified)
        self.cg_position = (pilot_weight * 37 + cargo_weight * 80) / (
            pilot_weight + cargo_weight + self.base_weight
        )
        self.cg_limits = (35.0, 47.3)   # typical single-engine limits

        # Weight-adjusted performance
        self.weight_factor = self.total_weight / self.base_weight
        self.stall_speed = 48 * (self.total_weight / 2450) ** 0.5  # pseudo formula
        self.max_speed = 124   # knots
        self.max_climb_rate = 721 / self.weight_factor  # ft/min

        # Initial flight state
        self.state = FlightState(
            altitude=5000,
            airspeed=124,    # knots
            fuel=self.max_fuel,
            heading=90,      # East
            vertical_speed=0,
            weather_severity=0,
            engine_rpm=2400,
            wind_speed=0,
            total_weight=self.total_weight,
            cg_position=self.cg_position,
            distance_remaining=DISTANCE_SEOUL_TOKYO
        )

        # Train minimal neural net
        self.model = self._train_neural_network()

        # Weighted rule-based approach for recommendations
        self.weights = {
            "low_altitude": 0.9, "low_fuel": 0.8, "speed_risk": 0.7,
            "weather": 0.6,     "stability": 0.5, "engine": 0.4,
            "weight": 0.3,      "cg": 0.2,        "distance": 0.1
        }
        self.stable_count = 0  # track stable flight periods

        # Set up Tkinter GUI
        self.root = tk.Tk()
        self.root.title("AI Decision Support - Seoul to Tokyo")
        self.status_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.status_label.pack(pady=10)
        self.recommend_label = tk.Label(self.root, text="AI Recommendations:\n",
                                        font=("Arial", 10), justify="left")
        self.recommend_label.pack(pady=10)
        self.running = True  # control simulation loop

    def _train_neural_network(self) -> Sequential:
        """
        Train a minimal neural network (binary output: 0=non-critical, 1=critical).
        Using only a few lines of data to illustrate concept.
        """
        X = np.array([
            [5000, 124, 40,   0, 0, 2400,  0, 1670, 37, 1147],   # Start
            [800,   50,  5, -500, 2, 2200, 20, 2550, 45,  500],   # Critical
            [12000,150, 20, 200, 1, 2500, 15, 2000, 40,  800],   # Moderate
            [3000,  60,  0,   0, 0, 2300,  5, 1800, 38,    0]     # End
        ])
        y = np.array([[0], [1], [0], [1]])  # toy labels

        model = Sequential([
            Dense(16, activation='relu', input_shape=(10,)),
            Dense(8, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        model.fit(X, y, epochs=50, verbose=0)
        logging.info("Neural network trained with minimal flight data.")
        return model

    def simulate_adsb_data(self) -> None:
        """
        Simulate real-time data changes (wind speed, weather severity).
        For demonstration, randomize wind speed if weather is non-clear.
        """
        # Slight randomization of airspeed & engine RPM
        self.state.airspeed += random.uniform(-3, 3)
        self.state.engine_rpm += random.uniform(-50, 50)

        # If weather is severe, create wind events
        if self.state.weather_severity > 0:
            self.state.wind_speed = random.uniform(0, 30)
        else:
            self.state.wind_speed = 0

        # Occasionally change weather severity
        if random.random() < 0.15:
            self.state.weather_severity = random.randint(0, 2)

    def update_state(self) -> None:
        """
        Core flight logic: updates altitude, airspeed, distance, fuel, etc.
        Simulates extremely simplified flight physics for demonstration.
        """
        # Convert from knots to ft/s
        speed_fts = self.state.airspeed * 1.68781
        # Calculate naive lift
        lift = 0.5 * AIR_DENSITY * (speed_fts**2) * WING_AREA * LIFT_COEFFICIENT * 0.0689476
        excess_lift = lift - self.state.total_weight

        # RPM factor: if engine_rpm is high, produce more climb
        rpm_factor = (self.state.engine_rpm - 2400) / 2400

        # vertical_speed in ft/min
        self.state.vertical_speed = (
            excess_lift / self.state.total_weight * 1000
            + rpm_factor * 500
            - random.uniform(50, 100)
        ) * self.weight_factor

        # Update altitude in feet
        self.state.altitude += self.state.vertical_speed / 60

        # Wind effect on airspeed & heading
        wind_effect = self.state.wind_speed * random.uniform(-0.1, 0.1)
        self.state.airspeed += wind_effect
        self.state.heading = (self.state.heading + wind_effect * 0.5) % 360

        # Fuel consumption
        # We'll assume a short step, so we approximate usage:
        fuel_consumption = FUEL_BURN_RATE * 0.00833 * self.weight_factor
        self.state.fuel -= fuel_consumption

        # Distance covered (1 knot = 1.852 km/h)
        speed_kmh = self.state.airspeed * 1.852
        self.state.distance_remaining -= speed_kmh * 0.00833

        # Possibly update random "ADS-B" style data
        self.simulate_adsb_data()
        self._constrain_parameters()

    def _constrain_parameters(self) -> None:
        """
        Clamp or limit key parameters to within 'safe' or plausible bounds.
        """
        self.state.airspeed = max(self.stall_speed, min(self.max_speed, self.state.airspeed))
        self.state.fuel = max(0, min(self.max_fuel, self.state.fuel))
        self.state.altitude = max(0, min(self.max_altitude, self.state.altitude))
        self.state.engine_rpm = max(1000, min(self.max_rpm, self.state.engine_rpm))
        self.state.vertical_speed = max(-self.max_climb_rate, min(self.max_climb_rate, self.state.vertical_speed))
        self.state.distance_remaining = max(0, self.state.distance_remaining)

    def evaluate_conditions(self) -> List[Tuple[float, str]]:
        """
        Generate recommendations from rule-based logic + neural net classification.
        Returns a sorted list of (priority, message).
        """
        # Prepare features for MLP
        features = np.array([[
            self.state.altitude, self.state.airspeed, self.state.fuel,
            self.state.vertical_speed, self.state.weather_severity,
            self.state.engine_rpm, self.state.wind_speed,
            self.state.total_weight, self.state.cg_position,
            self.state.distance_remaining
        ]])
        # Prediction: 0 => safe, 1 => critical
        criticality = self.model.predict(features, verbose=0)[0][0]

        # Start collecting recommendations
        recommendations = []
        if criticality > 0.8:
            recommendations.append((1.0, "CRITICAL: Immediate action required!"))

        # Rule-based checks:
        if self.state.altitude < self.min_safe_altitude:
            recommendations.append((self.weights["low_altitude"], "LOW ALT: Climb immediately!"))
        if self.state.fuel < 5:
            recommendations.append((self.weights["low_fuel"], "FUEL CRITICAL: Divert to nearest airport!"))
        elif self.state.fuel < 10:
            recommendations.append((self.weights["low_fuel"] * 0.7, "Fuel low: Plan landing soon."))

        if self.state.airspeed < self.stall_speed + 10:
            recommendations.append((self.weights["speed_risk"], "NEAR STALL: Increase power!"))
        elif self.state.airspeed > self.max_speed - 20:
            recommendations.append((self.weights["speed_risk"] * 0.8, "High speed: Reduce throttle!"))

        if self.state.weather_severity == 1:
            recommendations.append((self.weights["weather"], "TURBULENCE: Maintain stable flight."))
        elif self.state.weather_severity == 2:
            recommendations.append((self.weights["weather"] * 1.2, "STORM: Consider changing route."))

        if abs(self.state.vertical_speed) > (self.max_climb_rate * 0.7):
            recommendations.append((self.weights["stability"], "High VS: Adjust pitch or power."))

        if self.state.engine_rpm > 2600:
            recommendations.append((self.weights["engine"], "High RPM: Reduce throttle to avoid damage."))

        if self.state.total_weight > self.max_gross_weight:
            recommendations.append((self.weights["weight"], "OVER MAX WEIGHT: Performance severely impacted."))

        if not (self.cg_limits[0] <= self.state.cg_position <= self.cg_limits[1]):
            recommendations.append((self.weights["cg"], "CG OUT OF LIMITS: Unsafe load distribution!"))

        if self.state.distance_remaining < 50:
            recommendations.append((self.weights["distance"], "APPROACHING destination: Prepare landing."))

        # Sort by priority in descending order
        return sorted(recommendations, key=lambda x: x[0], reverse=True)

    def update_gui(self):
        """
        Refresh the GUI labels (status + recommendations).
        """
        # Summarize flight status
        status_text = (
            f"ALT: {self.state.altitude:.0f} ft | SPD: {self.state.airspeed:.1f} kt\n"
            f"FUEL: {self.state.fuel:.1f} gal | VS: {self.state.vertical_speed:.0f} fpm\n"
            f"RPM: {self.state.engine_rpm:.0f} | WIND: {self.state.wind_speed:.1f} kt\n"
            f"WEATHER: {['Clear','Turbulent','Storm'][self.state.weather_severity]}\n"
            f"WEIGHT: {self.state.total_weight:.0f} lbs | CG: {self.state.cg_position:.1f} in\n"
            f"REMAINING: {self.state.distance_remaining:.0f} km to Tokyo"
        )
        self.status_label.config(text=status_text)

        # Evaluate conditions -> recommendations
        recs = self.evaluate_conditions()
        rec_text = "AI Recommendations:\n"
        if recs:
            # Display top 3 suggestions
            for priority, msg in recs[:3]:
                rec_text += f"[{priority:.2f}] {msg}\n"
        else:
            rec_text += "Conditions nominal."
            self.stable_count += 1

        self.recommend_label.config(text=rec_text)

    def run_assistance(self):
        """
        Start a background thread for flight updates and run the Tkinter mainloop.
        """
        def simulation_loop():
            while self.running:
                self.update_state()
                self.update_gui()

                # Termination checks
                if self.state.fuel <= 0:
                    self.recommend_label.config(text="NO FUEL: Emergency landing required!")
                    self.running = False
                elif self.state.distance_remaining <= 0:
                    self.recommend_label.config(text="ARRIVED AT DESTINATION: Prepare to land.")
                    self.running = False
                elif self.stable_count >= 10:
                    self.recommend_label.config(text="STABLE FLIGHT ACHIEVED.")
                    self.running = False

                time.sleep(0.5)

        # Launch simulation in a separate thread to keep GUI responsive
        threading.Thread(target=simulation_loop, daemon=True).start()
        self.root.mainloop()

def main():
    """
    Run the AI Decision Support Simulation for a "Seoul→Tokyo" flight.
    Prompt user for pilot/cargo weight, then start the GUI + simulation loop.
    """
    logging.info("Flight Simulation: Seoul→Tokyo")

    try:
        pilot_weight = float(input("Enter pilot weight (lbs): "))
        cargo_weight = float(input("Enter cargo weight (lbs): "))
        if not (0 < pilot_weight <= 500 and 0 <= cargo_weight <= 500):
            raise ValueError("Weights must be between 0 and 500 lbs.")

        ai = AIDecisionSupport(pilot_weight, cargo_weight)
        logging.info("Starting AI Decision Support Simulation...")
        ai.run_assistance()

    except ValueError as ve:
        logging.error(f"Input error: {ve}")
    except Exception as ex:
        logging.error(f"Execution failed: {ex}")

if __name__ == "__main__":
    main()
