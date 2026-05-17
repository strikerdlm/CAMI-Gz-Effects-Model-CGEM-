# Suggested Reviewers — BSPC submission

The five candidates below are active researchers in conformal prediction, surrogate emulation of mechanistic / physiological models, biosignal machine learning, and uncertainty quantification for biomedical signals. Each has at least one peer-reviewed paper in the last five years on a directly relevant methodological topic, holds a verifiable institutional email at an academic or government research institution, has no co-authorship with Diego Malpica (ORCID 0000-0002-2257-4940) in the past three years on a Tavily/Semantic Scholar pass, and is not affiliated with the Colombian Aerospace Force, Aerocivil, any Colombian aerospace institution, or any institution in Bogotá. None of the five appears on the current *Biomedical Signal Processing and Control* editorial board (verified against the live ScienceDirect roster, May 2026).

## 1. Marcos Matabuena, PhD

- **Affiliation:** Department of Digital Health & Statistical AI, Mohamed bin Zayed University of Artificial Intelligence (MBZUAI), Abu Dhabi, United Arab Emirates (formerly Department of Biostatistics, Harvard T.H. Chan School of Public Health)
- **Institutional email:** marcos.matabuena@mbzuai.ac.ae
- **ORCID:** https://orcid.org/0000-0003-3841-4447
- **Expertise rationale:** Matabuena is the senior author of the closest published precedent to the present manuscript — Portela, Banga & Matabuena, "Conformal prediction for uncertainty quantification in dynamic biological systems," *PLOS Computational Biology* 21(5):e1013098 (2025), https://doi.org/10.1371/journal.pcbi.1013098 — which applies split-conformal calibration on top of a mechanistic ODE biological model, exactly the architectural pattern used here for the FAA CAMI G-Effects model. His broader programme on conformal and kNN predictive uncertainty quantification in metric spaces, and on high-frequency biosignals from wearables and continuous glucose monitors, gives him direct technical command of both the Mondrian/CQR machinery and the biosignal application domain.

## 2. Vignesh Gopakumar, PhD

- **Affiliation:** UCL Centre for Artificial Intelligence, Department of Computer Science, University College London, London, United Kingdom; and UK Atomic Energy Authority, Culham, United Kingdom
- **Institutional email:** v.gopakumar@ucl.ac.uk
- **ORCID:** https://orcid.org/0000-0001-9181-7593
- **Expertise rationale:** Gopakumar leads the conformal prediction work on uncertainty quantification for data-driven surrogate models — Gopakumar et al., "Uncertainty quantification of surrogate models using conformal prediction," *Machine Learning: Science and Technology* (2024/2025), https://doi.org/10.1088/2632-2153/ae2e7b — which benchmarks conformalized quantile regression, absolute-residual, and standard-deviation nonconformity scores on emulators of stiff numerical systems and explicitly tests coverage under distribution shift. The methodological overlap with the present manuscript's CQR-based surrogate of a Fortran ODE solver, evaluated under maneuver-stratified out-of-distribution regimes, is essentially one-to-one.

## 3. Henrik Boström, PhD

- **Affiliation:** Division of Software and Computer Systems, School of Electrical Engineering and Computer Science, KTH Royal Institute of Technology, Stockholm, Sweden
- **Institutional email:** bostromh@kth.se
- **ORCID:** https://orcid.org/0000-0001-8382-0300
- **Expertise rationale:** Boström is a primary methodological reference for Mondrian conformal prediction and the maintainer of `crepes`, the Python conformal-prediction library that implements standard, normalized, and Mondrian conformal regressors and classifiers — Boström, "Conformal Prediction in Python with crepes," *Proceedings of the 13th Symposium on Conformal and Probabilistic Prediction with Applications (COPA 2024)*, PMLR vol. 230. His decade of work on per-stratum (Mondrian) calibration of nonconformity scores is directly relevant to the manuscript's stratification of conformal residuals by maneuver category.

## 4. Tapabrata Rohan Chakraborty, PhD

- **Affiliation:** Principal Research Fellow, Department of Computer Science (UCL Cancer Institute / Transparent and Reliable AI Lab), University College London, London, United Kingdom; and Theme Lead, Frontier AI Assurance, The Alan Turing Institute, London, United Kingdom
- **Institutional email:** t.chakraborty@ucl.ac.uk
- **ORCID:** https://orcid.org/0000-0002-7156-6049
- **Expertise rationale:** Chakraborty's TRAIL group at UCL and the Alan Turing Institute works specifically on the marginal-vs-individualised coverage problem in conformal prediction and on conformal uncertainty quantification for clinical and biomedical signals — e.g., Chakraborti & Dey, "Conformal Prediction for Reliable Image Super-Resolution," *Proceedings of the 14th Symposium on Conformal and Probabilistic Prediction with Applications (COPA 2025)*, PMLR vol. 266. His broader portfolio on conformal calibration for personalised healthcare and biomedical imaging aligns directly with the manuscript's abstention layer over a Mahalanobis OOD score.

## 5. Gareth J. Conduit, PhD

- **Affiliation:** Department of Physics (Theory of Condensed Matter Group, Lennard-Jones Centre), Royal Society University Research Fellow, University of Cambridge, Cambridge, United Kingdom
- **Institutional email:** gjc29@cam.ac.uk
- **ORCID:** https://orcid.org/0000-0002-7378-0432
- **Expertise rationale:** Conduit is the senior author of Strickland et al., "Degrees of uncertainty: conformal deep learning for non-invasive core body temperature prediction in extreme environments," *Communications Engineering* (2025), https://doi.org/10.1038/s44172-025-00548-6, which couples a conformal predictor to a deep regression model on physiological and environmental inputs to produce calibrated prediction intervals for a safety-critical biosignal under heat stress. The methodological fit with the present manuscript's distribution-free conformal layer over a mechanistic physiological model is direct, and his broader work on machine-learning surrogates for high-dimensional scientific systems supports review of the surrogate-emulation architecture.
