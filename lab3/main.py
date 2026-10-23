from config import Config
from simulation import Simulation
from visualization import run_animation


if __name__ == "__main__":
    run_animation(Simulation(Config()))
