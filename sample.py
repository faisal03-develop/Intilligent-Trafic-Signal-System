# import pandas as pd
# import matplotlib.pyplot as plt
#
# # data = [100,101,102];
# # series = pd.Series(data,index=[1,2,3])
# # print(series)
# #
# # #Data Frame: Tabular form of Data Tables.
# #
# # data = {
# #     "Name": ['Faisal','MatArmStrong'],
# #     "Age": [22,27]
# # }
# # df  = pd.DataFrame(data,index=[1,2])
# #
# # #Add new column
# # df["Job"] = ['FrontEnd','Enterpeneur']
# #
# # #Add new row
# # new_row = pd.DataFrame([{"Name":"Sandy", "Age": 23, "Job":"BackEnd"}],index=[3])
# #
# # df = pd.concat([df,new_row])
# #
# # print(df)
#
#
# # Importing Data from the CSV File:
#
# # read_json --For reading JSON
# # read_csv --For reading CSV
#
# df = pd.read_csv('dataset.csv')
#
# # print(df)
# # print(df.to_string())
# # print(df.loc["Charizard",["Height","Weight"]])
# # print(df.to_string())
# # print(df[df["Name"] == "Charizard"][["Height", "Weight"]])
# # print(df.iloc[0:11:2,0:4])
#
# # pokemon = input("Enter the name of the PokeMon: ")
# # try:
# #     print(df[df["Name"]==pokemon])
# # except KeyError:
# #     print(f"{pokemon} does not Exist")
#
# df = df.plot()
# plt.show
#
# username = str(input("Enter your username: "));
#
# if(len(username)<12 and username.isalpha()):
#     print(f"Your UUSERNAME: {username} is valid")
# else:
#     print(f"Your UUSERNAME: {username} is not valid")



import random
import time
import copy
from enum import Enum
from collections import deque

# ================== ENUMS ==================
class LightState(Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class VehicleType(Enum):
    CAR = "CAR"
    BIKE = "BIKE"
    BUS = "BUS"
    EMERGENCY = "EMERGENCY"


DIRECTIONS = ["N", "E", "S", "W"]  # Clockwise order

# ================== VEHICLE ==================
class Vehicle:
    def __init__(self, vid, vtype, direction, arrival_time):
        self.id = vid
        self.type = vtype
        self.direction = direction
        self.arrival_time = arrival_time

    def is_emergency(self):
        return self.type == VehicleType.EMERGENCY


# ================== LANE QUEUE ==================
class LaneQueue:
    def __init__(self):
        self.queue = deque()

    def add_vehicle(self, v):
        self.queue.append(v)

    def pop_vehicle(self):
        return self.queue.popleft()

    def peek(self):
        return self.queue[0] if self.queue else None

    def __len__(self):
        return len(self.queue)


# ================== TRAFFIC SIGNAL ==================
class TrafficSignal:
    def __init__(self):
        self.state = {d: LightState.RED for d in DIRECTIONS}
        self.current_index = 0
        self.current_green = DIRECTIONS[self.current_index]

        self.timer = 0
        self.green_duration = 5
        self.yellow_duration = 2

        self.state[self.current_green] = LightState.GREEN

    def emergency_override(self, direction):
        for d in DIRECTIONS:
            self.state[d] = LightState.RED
        self.state[direction] = LightState.GREEN
        self.current_green = direction
        self.timer = 0

    def update_cycle(self):
        self.timer += 1

        if self.timer <= self.green_duration:
            for d in DIRECTIONS:
                self.state[d] = LightState.RED
            self.state[self.current_green] = LightState.GREEN

        elif self.timer <= self.green_duration + self.yellow_duration:
            self.state[self.current_green] = LightState.YELLOW

        else:
            # Move to next direction
            self.timer = 0
            self.current_index = (self.current_index + 1) % len(DIRECTIONS)
            self.current_green = DIRECTIONS[self.current_index]

            for d in DIRECTIONS:
                self.state[d] = LightState.RED
            self.state[self.current_green] = LightState.GREEN


# ================== STATISTICS ==================
class TrafficStats:
    def __init__(self):
        self.total_wait = 0
        self.exited = 0

    def log_exit(self, vehicle, time_tick):
        self.exited += 1
        self.total_wait += (time_tick - vehicle.arrival_time)

    def average_wait(self):
        return 0 if self.exited == 0 else self.total_wait / self.exited


# ================== INTERSECTION ==================
class Intersection:
    def __init__(self):
        self.lanes = {d: LaneQueue() for d in DIRECTIONS}
        self.signal = TrafficSignal()
        self.stats = TrafficStats()

    def spawn_vehicle(self, vid, time_tick):
        direction = random.choice(DIRECTIONS)
        vtype = random.choices(
            [VehicleType.CAR, VehicleType.BIKE, VehicleType.BUS, VehicleType.EMERGENCY],
            weights=[70, 20, 8, 2]
        )[0]
        self.lanes[direction].add_vehicle(Vehicle(vid, vtype, direction, time_tick))

    def handle_emergency(self):
        for d in DIRECTIONS:
            v = self.lanes[d].peek()
            if v and v.is_emergency():
                self.signal.emergency_override(d)
                return True
        return False

    def move_vehicles(self, time_tick):
        green_dir = self.signal.current_green

        if self.signal.state[green_dir] == LightState.GREEN:
            lane = self.lanes[green_dir]

            if len(lane) > 0:
                front = lane.peek()

                # 🚫 Prevent same-tick exit
                if front.arrival_time == time_tick:
                    return

                v = lane.pop_vehicle()
                self.stats.log_exit(v, time_tick)


# ================== SIMULATION CONTROLLER ==================
class SimulationController:
    def __init__(self):
        self.intersection = Intersection()
        self.history = []
        self.time = 0
        self.vehicle_id = 1
        self.running = False

    def save_state(self):
        self.history.append(copy.deepcopy(self.intersection))

    def undo(self):
        if self.history:
            self.intersection = self.history.pop()
            print("Undo successful")
        else:
            print("Nothing to undo")

    def reset(self):
        self.__init__()
        print("Simulation reset")

    def step(self):
        self.save_state()
        self.time += 1

        emergency = self.intersection.handle_emergency()
        if not emergency:
            self.intersection.signal.update_cycle()

        # Move only ONE vehicle from ONE green lane
        self.intersection.move_vehicles(self.time)

        # Spawn vehicle last
        if random.random() < 0.7:
            self.intersection.spawn_vehicle(self.vehicle_id, self.time)
            self.vehicle_id += 1

        self.print_status()

    def start(self, steps=20):
        self.running = True
        for _ in range(steps):
            if not self.running:
                break
            self.step()
            time.sleep(0.3)

    def pause(self):
        self.running = False
        print("Simulation paused")

    def print_status(self):
        print(f"\n⏱ Time: {self.time}")
        print("🚦 Signal States:",
              {d: self.intersection.signal.state[d].value for d in DIRECTIONS})
        print("🚗 Lane Queues:",
              {d: len(self.intersection.lanes[d]) for d in DIRECTIONS})
        print(f"📊 Avg Waiting Time: {self.intersection.stats.average_wait():.2f}")
        print(f"✅ Total Exited Vehicles: {self.intersection.stats.exited}")


# ================== MAIN ==================
if __name__ == "__main__":
    sim = SimulationController()

    while True:
        print("\n--- Intelligent Traffic Simulation (ONE GREEN ONLY) ---")
        print("1) Start 20 steps")
        print("2) Step once")
        print("3) Pause")
        print("4) Reset")
        print("5) Undo last step")
        print("6) Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            sim.start()
        elif choice == "2":
            sim.step()
        elif choice == "3":
            sim.pause()
        elif choice == "4":
            sim.reset()
        elif choice == "5":
            sim.undo()
        elif choice == "6":
            break
        else:
            print("Invalid choice")
