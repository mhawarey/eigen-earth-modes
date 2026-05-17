# Eigen Earth Modes

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Interactive visualizer of Earth's free oscillations (normal modes) — both **spheroidal** (`nSl`) and **toroidal** (`nTl`) — with reference periods compiled from PREM and Masters & Widmer (AGU 1995).

A desktop Tkinter GUI that renders the surface displacement pattern of any selected mode on a 3-D sphere, animates the oscillation in real time, and reports the period, frequency, nodal-line count, and physical interpretation.

## Features

- **27 reference modes** including the famous "football mode" ₀S₂ (T ≈ 53.9 min) and radial mode ₀S₀.
- Spheroidal and toroidal modes side-by-side.
- Adjustable azimuthal order *m* with live re-rendering.
- Smooth oscillation animation via Matplotlib `FuncAnimation`.
- Zero external services, fully offline, single-file app.

## Why this matters

Earth's free oscillations are the planet's fingerprint in elastodynamics. Excited by great earthquakes (M ≥ 7.5) and the 2004 Sumatra event in particular, these modes constrain the radial density and elastic structure of the Earth, the existence of a solid inner core, and even attenuation in the mantle. Yet hands-on visualization tools for them remain scarce outside specialist seismology packages. This app gives anyone a tactile feel for spherical-harmonic geometry on a real geophysical object.

## Quick start

```bash
pip install -r requirements.txt
python eigen_earth_modes.py
```

## References

- Dziewonski, A. M. & Anderson, D. L. (1981). *Preliminary reference Earth model.* Physics of the Earth and Planetary Interiors, 25(4), 297–356.
- Masters, T. G. & Widmer, R. (1995). *Free oscillations: Frequencies and attenuations.* In Global Earth Physics: A Handbook of Physical Constants, AGU.
- Lay, T. & Wallace, T. C. (1995). *Modern Global Seismology.* Academic Press.

## Author

**Dr. Mosab Hawarey**
>
PhD, Geodetic & Photogrammetric Engineering (ITU) | MSc, Geomatics (Purdue) | MBA (Wales) | BSc, MSc (METU)

- GitHub: https://github.com/mhawarey
- Personal: https://hawarey.org/mosab
- ORCID: https://orcid.org/0000-0001-7846-951X

## License

MIT License
