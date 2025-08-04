# %% [markdown]
# # Loop Maneuver Simulation
#
# This Jupytext-compatible script simulates the **4 Gz** vertical loop maneuver for a healthy pilot.
# Open it as a notebook in JupyterLab/VS Code or run it as plain Python.
#
# **Contents**
# 1. Parameter setup
# 2. Derived calculations
# 3. Gz vs time visualization
# 4. Altitude vs time visualization
# 5. Interactive widget to explore different entry speeds / load factors

# %%
import numpy as np
import matplotlib.pyplot as plt

# Enable inline plotting when executed inside a notebook
try:
    get_ipython
    %matplotlib inline  # type: ignore
except NameError:
    pass

# %%
# --- Parameters ---

g = 9.81                      # gravitational acceleration [m/s²]
v_entry = 150.0               # entry speed [m/s] (~300 kts)
N_bottom = 4.0                # target maximum positive Gz at the bottom
num_points = 500              # resolution of the simulation

# %%
# --- Derived quantities ---

R = v_entry**2 / ((N_bottom - 1) * g)   # loop radius for given entry speed & max G
theta = np.linspace(0, 2*np.pi, num_points)  # angle (0°=bottom, 180°=top)

# Assuming constant air-speed along the loop (simplification)
n_z = v_entry**2 / (g * R) + np.cos(theta)   # load factor formula n = v²/(gR) + cosθ

time = R * theta / v_entry                  # time axis (s): s = R·θ, t = s / v
altitude = R * (1 - np.cos(theta))           # relative altitude along the loop

# %%
# --- Gz vs Time ---

plt.figure(figsize=(10, 5))
plt.plot(time, n_z, label="Gz (load factor)")
plt.axhline(1, color="gray", linestyle="--", lw=1)
plt.title("Gz vs Time for 4 G Vertical Loop")
plt.xlabel("Time [s]")
plt.ylabel("Load factor n (Gz)")
plt.legend()
plt.grid(True)
plt.show()

# %%
# --- Altitude vs Time ---

plt.figure(figsize=(10, 5))
plt.plot(time, altitude, color="tab:orange")
plt.title("Relative Altitude along the Loop")
plt.xlabel("Time [s]")
plt.ylabel("Altitude change [m]")
plt.grid(True)
plt.show()

# %%
# --- Interactive exploration (requires ipywidgets) ---

try:
    import ipywidgets as widgets
    from IPython.display import display
except ImportError:
    widgets = None


def plot_loop(v_entry=150.0, N_bottom=4.0):
    """Re-plot loop metrics for user-selected parameters."""
    R = v_entry**2 / ((N_bottom - 1) * g)
    theta = np.linspace(0, 2 * np.pi, num_points)
    n_z = v_entry**2 / (g * R) + np.cos(theta)
    time = R * theta / v_entry
    altitude = R * (1 - np.cos(theta))

    plt.figure(figsize=(9, 4))

    plt.subplot(1, 2, 1)
    plt.plot(time, n_z)
    plt.title("Gz vs Time")
    plt.xlabel("t [s]")
    plt.ylabel("n (G)")
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(time, altitude, color="tab:orange")
    plt.title("Relative Altitude")
    plt.xlabel("t [s]")
    plt.ylabel("Δh [m]")
    plt.grid(True)

    plt.tight_layout()
    plt.show()


if widgets is not None:
    ui = widgets.VBox([
        widgets.FloatSlider(value=150, min=50, max=300, step=10, description="Entry speed [m/s]"),
        widgets.FloatSlider(value=4, min=2, max=9, step=0.5, description="Max G")
    ])
    out = widgets.interactive_output(plot_loop, {"v_entry": ui.children[0], "N_bottom": ui.children[1]})
    display(ui, out)
else:
    print("ipywidgets not installed – interactive controls disabled.")