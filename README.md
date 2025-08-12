# CGEM-based G-LOC Modeling and Visualization Suite

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)](https://en.wikipedia.org/wiki/Cross-platform)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Status](https://img.shields.io/badge/Status-Research-blueviolet)](https://en.wikipedia.org/wiki/Research)

A modern, researcher-friendly toolkit for modeling G-induced loss of consciousness (G-LOC) and visualizing aerospace physiology using the FAA’s CGEM foundations. This repository brings together computational models, simulations, and interactive visualizations to support training, safety analysis, and research in aerospace medicine.

Developed by **Dr. Diego Malpica**.

### Highlights
- **Physiology-aware modeling**: CGEM-based computations for greyout, blackout, and G-LOC risk.
- **Interactive visualizations**: Streamlit dashboards for scenarios, thresholds, timelines, and maneuver profiles.
- **Reproducible workflows**: Notebooks and scripts for demos and experiments.
- **Extensible**: Modular code to customize models, parameters, and data pipelines.

---

## Quick Start

1) Set up the environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2) Launch the interactive visualization app
```bash
streamlit run enhanced_app.py
```

3) Run the aerobatic profiles demo (optional)
```bash
python demo_example.py
```

4) Explore notebooks
- Open `aerobatic_profiles_demo.ipynb` or `aerobatic_maneuvers_simulation.ipynb` in your favorite environment.

---

## Features
- Risk timelines and threshold overlays for greyout, blackout, and G-LOC.
- Maneuver libraries and sample inputs for scenario exploration.
- Exportable figures for training and reporting.
- Example inputs in `Aerobatics_sample_inputs/` and data files for model runs.

---

## Acknowledgments
This work is built upon and inspired by foundational research conducted within the **Federal Aviation Administration (FAA)** Office of Aerospace Medicine and decades of operational physiology experience. We gratefully acknowledge the contributions of the **U.S. Military** community—aviators, aircrew, and allied professionals—who served both as scientists and as research participants in the studies underpinning this modeling approach. Their service and commitment to safety and science made this work possible.

Special recognition is due to the FAA researchers and collaborators whose efforts developed, validated, and documented the CGEM approach and related physiology insights.

---

## How to Cite
If you use this repository in academic or technical work, please cite the foundational FAA report:

Malpica, D. (Developer). (2025). CGEM-based G-LOC Modeling and Visualization Suite [Computer software].

And include the original research reference (APA format):

Copeland, K., & Whinnery, J. E. (2023). Cerebral blood flow-based computer modeling of Gz-induced effects (DOT/FAA/AM-23/6). Office of Aerospace Medicine, Federal Aviation Administration, Washington, DC.

---

## Disclaimer
- This toolkit is intended for research, education, and training support. It does not substitute for operational aeromedical guidance or certification processes.
- This project is not an official product of the FAA or the U.S. Department of Defense. All views expressed are those of the contributors.

---

## Repository Guide
- `enhanced_app.py`: Streamlit UI for interactive modeling and visualization
- `app.py`, `demo_example.py`: Additional demos and app entry points
- `src/`: Core model code (e.g., CGEM implementation and related utilities)
- `Aerobatics_sample_inputs/`: Example input profiles for scenarios
- `docs/`: Guides and related documents
- `notebooks/`: Research and demo notebooks

---

## Contact
Questions, collaborations, or feedback are welcome.

- Lead developer: **Dr. Diego Malpica**
- Please open an issue or pull request to start the conversation.
