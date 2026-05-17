"""
Eigen Earth Modes — Interactive visualizer of Earth's free oscillations.

Computes and visualizes spheroidal (nSl) and toroidal (nTl) normal modes
of a spherical, non-rotating, elastic, isotropic Earth model using a
simplified PREM-like radial structure. Mode periods come from a curated
reference table (Dziewonski & Anderson, 1981; Masters & Widmer, 1995).
Surface displacement patterns use vector spherical harmonics.

Author: Dr. Mosab Hawarey (@DrHawarey)
License: MIT
"""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from scipy.special import sph_harm, lpmv


# Reference mode periods (seconds) for a PREM-like Earth.
# Source: Masters & Widmer, "Free Oscillations: Frequencies and Attenuations"
# in Global Earth Physics: A Handbook of Physical Constants (AGU, 1995).
# Format: (n, l, type) -> period in seconds
REFERENCE_MODES = {
    # Spheroidal modes (radial order n, angular degree l)
    (0, 2, "S"): 3233.25,   # "Football mode" — longest period
    (0, 3, "S"): 2134.13,
    (0, 4, "S"): 1545.60,
    (0, 5, "S"): 1190.20,
    (0, 6, "S"): 963.30,
    (0, 7, "S"): 811.65,
    (0, 8, "S"): 707.85,
    (0, 9, "S"): 633.95,
    (0, 10, "S"): 579.30,
    (0, 0, "S"): 1227.52,   # Radial "breathing" mode
    (1, 2, "S"): 1470.85,
    (1, 3, "S"): 1064.30,
    (1, 4, "S"): 851.20,
    (2, 1, "S"): 1075.50,
    # Toroidal modes (no radial component)
    (0, 2, "T"): 2636.40,
    (0, 3, "T"): 1703.20,
    (0, 4, "T"): 1305.85,
    (0, 5, "T"): 1075.95,
    (0, 6, "T"): 924.95,
    (0, 7, "T"): 818.10,
    (0, 8, "T"): 736.90,
    (0, 9, "T"): 672.80,
    (0, 10, "T"): 620.40,
    (1, 2, "T"): 757.80,
    (1, 3, "T"): 695.20,
    (1, 4, "T"): 635.40,
}


def mode_label(n: int, l: int, kind: str) -> str:
    return f"{n}{kind}{l}"


def displacement_field(l: int, m: int, kind: str, theta: np.ndarray, phi: np.ndarray, phase: float):
    """
    Compute surface displacement amplitude pattern.

    For visualization on a sphere we use real spherical harmonics Y_l^m
    modulated by cos(phase). For spheroidal modes we render the radial
    displacement; for toroidal modes we render the tangential curl pattern.
    """
    Y = sph_harm(m, l, phi, theta)
    real_Y = Y.real * math.cos(phase) - Y.imag * math.sin(phase)
    if kind == "S":
        # Radial displacement pattern (scalar field on sphere)
        return real_Y
    else:
        # Toroidal: use the curl pattern of Y_l^m which produces purely
        # tangential motion. For visualization we display |∇Y|^2-like
        # intensity which highlights the nodal lines characteristic of
        # toroidal oscillation.
        dY_dtheta = (lpmv(m, l, np.cos(theta + 1e-6)) - lpmv(m, l, np.cos(theta - 1e-6))) / 2e-6
        amp = dY_dtheta * math.cos(phase)
        return amp * np.cos(m * phi)


class EigenEarthApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Eigen Earth Modes — Free Oscillation Visualizer")
        self.root.geometry("1200x780")

        self.anim = None
        self._build_ui()
        self._populate_modes()
        self._update_plot()

    def _build_ui(self) -> None:
        left = ttk.Frame(self.root, padding=10)
        left.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left, text="Earth's Free Oscillations", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(left, text="Select a normal mode:", font=("Segoe UI", 10)).pack(anchor="w", pady=(8, 2))

        self.mode_var = tk.StringVar()
        self.mode_box = ttk.Combobox(left, textvariable=self.mode_var, width=22, state="readonly")
        self.mode_box.pack(anchor="w")
        self.mode_box.bind("<<ComboboxSelected>>", lambda e: self._update_plot())

        ttk.Label(left, text="Azimuthal order m:", font=("Segoe UI", 10)).pack(anchor="w", pady=(12, 2))
        self.m_var = tk.IntVar(value=0)
        self.m_spin = ttk.Spinbox(left, from_=-10, to=10, textvariable=self.m_var, width=8,
                                   command=self._update_plot)
        self.m_spin.pack(anchor="w")

        self.animate_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(left, text="Animate", variable=self.animate_var,
                        command=self._update_plot).pack(anchor="w", pady=(12, 2))

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, pady=12)

        self.info = tk.Text(left, width=34, height=18, wrap="word",
                            font=("Consolas", 9), relief="flat",
                            background=self.root.cget("bg"))
        self.info.pack(anchor="w")

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, pady=12)
        ttk.Label(left, text="Dr. Mosab Hawarey • MIT License",
                  font=("Segoe UI", 8), foreground="#777").pack(anchor="w")

        right = ttk.Frame(self.root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig = plt.Figure(figsize=(9, 7), dpi=100)
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _populate_modes(self) -> None:
        labels = []
        self._lookup: dict[str, tuple[int, int, str]] = {}
        for (n, l, kind), period in sorted(REFERENCE_MODES.items(), key=lambda x: -x[1]):
            label = f"{mode_label(n, l, kind)}  (T = {period:.1f} s)"
            labels.append(label)
            self._lookup[label] = (n, l, kind)
        self.mode_box["values"] = labels
        self.mode_box.current(0)

    def _selected_mode(self) -> tuple[int, int, str, float]:
        key = self.mode_var.get()
        n, l, kind = self._lookup[key]
        return n, l, kind, REFERENCE_MODES[(n, l, kind)]

    def _update_plot(self) -> None:
        if self.anim is not None:
            self.anim.event_source.stop()
            self.anim = None

        n, l, kind, period = self._selected_mode()
        m = max(-l, min(l, int(self.m_var.get())))

        theta = np.linspace(0, np.pi, 90)
        phi = np.linspace(0, 2 * np.pi, 180)
        theta_grid, phi_grid = np.meshgrid(theta, phi, indexing="ij")

        self.ax.clear()
        self.ax.set_box_aspect((1, 1, 1))
        self.ax.set_axis_off()
        self.ax.set_title(f"Mode {mode_label(n, l, kind)}   m = {m}   "
                          f"T = {period:.2f} s   f = {1/period*1000:.3f} mHz")

        x = np.sin(theta_grid) * np.cos(phi_grid)
        y = np.sin(theta_grid) * np.sin(phi_grid)
        z = np.cos(theta_grid)

        amp = displacement_field(l, m, kind, theta_grid, phi_grid, phase=0.0)
        norm = np.max(np.abs(amp)) + 1e-12
        colors = plt.cm.RdBu_r(0.5 + 0.5 * amp / norm)
        self._surface = self.ax.plot_surface(x, y, z, facecolors=colors,
                                              rstride=1, cstride=1,
                                              linewidth=0, antialiased=False)

        # Info text
        self.info.delete("1.0", tk.END)
        self.info.insert(tk.END,
                         f"Mode:     {mode_label(n, l, kind)}\n"
                         f"Type:     {'Spheroidal' if kind == 'S' else 'Toroidal'}\n"
                         f"n (radial):    {n}\n"
                         f"l (angular):   {l}\n"
                         f"m (azimuthal): {m}\n"
                         f"Period:   {period:.2f} s\n"
                         f"Frequency:{1/period*1000:.4f} mHz\n\n"
                         f"Nodal lines (zeros of Y_l^m):\n"
                         f"  latitudinal: {l - abs(m)}\n"
                         f"  longitudinal:{abs(m)}\n\n"
                         f"Reference periods compiled from\n"
                         f"PREM (Dziewonski & Anderson 1981)\n"
                         f"and Masters & Widmer (AGU 1995).\n")

        if self.animate_var.get():
            self._start_animation(theta_grid, phi_grid, x, y, z, l, m, kind, norm)
        else:
            self.canvas.draw_idle()

    def _start_animation(self, theta_grid, phi_grid, x, y, z, l, m, kind, norm):
        def update(frame):
            phase = 2 * math.pi * frame / 60.0
            amp = displacement_field(l, m, kind, theta_grid, phi_grid, phase=phase)
            colors = plt.cm.RdBu_r(0.5 + 0.5 * amp / norm)
            self.ax.clear()
            self.ax.set_box_aspect((1, 1, 1))
            self.ax.set_axis_off()
            n_label = self.mode_var.get()
            self.ax.set_title(n_label)
            self.ax.plot_surface(x, y, z, facecolors=colors,
                                 rstride=1, cstride=1,
                                 linewidth=0, antialiased=False)
            return ()

        self.anim = FuncAnimation(self.fig, update, frames=60, interval=80, blit=False)
        self.canvas.draw_idle()


def main() -> None:
    try:
        root = tk.Tk()
        EigenEarthApp(root)
        root.mainloop()
    except Exception as exc:
        messagebox.showerror("Eigen Earth Modes", f"Fatal error:\n{exc}")
        raise


if __name__ == "__main__":
    main()
