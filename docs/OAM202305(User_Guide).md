

DOT/FAA/AM-23/5
Office of Aerospace Medicine
Washington, DC 20591

# CGEM User's Guide

Kyle Copeland

Civil Aerospace Medical Institute
Federal Aviation Administration
Oklahoma City, OK 73125

21 May 2021

Final Report

---


# NOTICE

This document is disseminated under the sponsorship of the U.S. Department of Transportation in the interest of information exchange. The United States Government assumes no liability for the contents thereof.

----

This publication and all Office of Aerospace Medicine technical reports are available in full-text from the Civil Aerospace Medical Institute's publications Web site: (www.faa.gov/go/oamtechreports)

ii


---


# Technical Report Documentation Page

<table>
<tr>
<td>1. Report No.<br>DOT/FAA/AM-23/5</td>
<td>2. Government Accession No.</td>
<td>3. Recipient's Catalog No.</td>
</tr>
<tr>
<td>4. Title and Subtitle<br>CGEM User's Guide</td>
<td colspan="2">5. Report Date<br>May 2021<br>6. Performing Organization Code</td>
</tr>
<tr>
<td>7. Author(s)<br>Copeland, K.</td>
<td colspan="2">8. Performing Organization Report No.</td>
</tr>
<tr>
<td>9. Performing Organization Name and Address<br>Civil Aerospace Medical Institute FAA<br>P.O. Box 25082<br>Oklahoma City, OK 73125</td>
<td colspan="2">10. Work Unit No. (TRAIS)<br><br>11. Contract or Grant No.</td>
</tr>
<tr>
<td>12. Sponsoring Agency name and Address<br>Office of Aerospace<br>Medicine Federal Aviation<br>Administration 800<br>Independence Ave., S.W.<br>Washington, DC 20591</td>
<td colspan="2">13. Type of Report and Period Covered<br>Technical Report<br><br><br>14. Sponsoring Agency Code</td>
</tr>
<tr>
<td colspan="3">15. Supplemental Notes<br>Author ORCID: Copeland (0000-0002-8480-3614)<br>Technical report DOI: https://doi.org/10.21949/1524438</td>
</tr>
<tr>
<td colspan="3">16. Abstract<br>This report is a guide to the use of the Civil Aerospace Medical Institute (CAMI) G Effects Model (CGEM) software. The software models effects of extreme Gz accelerations, including visual symptoms, G-LOC, and return to consciousness following G-LOC. The software accommodates Gz acceleration profiles experienced by most civilian and military pilots and also reproduces historical centrifuge experiments. Effects such as dehydration and fatigue are readily accommodated through changes in physiological parameters. Future planned developments include extending the model to include monitoring additional brain centers, anti-G equipment failure, an improved lung function model, direct inclusion of a library of acceleration profiles for standard maneuvers used in aerobatics, and a more user-friendly means of inputting effects of pilot dehydration and fatigue beyond adjusting the current input parameters.</td>
</tr>
<tr>
<td>17. Key Words<br>G-LOC, blackout, aerobatics, peripheral light loss, G tolerance, acceleration</td>
<td colspan="2">18. Distribution Statement<br>Document is available to the public through the Internet from the FAA and the National Transportation Library:<br>http://www.faa.gov/go/oamtec<br>hreports/<br>https://ntl.bts.gov/ntl</td>
</tr>
<tr>
<td>19. Security Classif. (of this report)<br>Unclassified</td>
<td>20. Security Classif. (of this page)<br>Unclassified</td>
<td>21. No. of Pages<br>29</td>
<td>22. Price</td>
</tr>
</table>

Form DOT F 1700.7 (8-72) Reproduction of completed page authorized

iii


---


iv

# ACKNOWLEDGEMENTS

This work is in partial fulfillment of Project 2017-AAM-631-NUM-10123 sponsored by the FAA's Office of Aerospace Medicine.

The CGEM software development began in 2012, with a conversation with Gen (ret.) James Whinnery, M.D., Ph.D., who was then manager of the Aeromedical Research Division (AMRD) at CAMI and a well-known expert with a long history of the study of G-induced loss of consciousness (G-LOC) and return to consciousness. The initial model was a simple two-parameter fit to G-LOC-related data he had collected over many years. The program would not exist without his explanation of the physiology of G-LOC. Thanks are also due to Estrella Forster, Ph.D., also a former Manager of the Aeromedical Research Division at CAMI, who encouraged the continued development of the model after Dr. Whinnery's retirement; and to Paul Rogers, Ph.D., and William Hathaway of the Numerical Sciences Research Team at CAMI, who were willing to discuss the mathematics and coding of the model in its early stages and had some enthusiasm for its possible applications to aerobatic flight evaluation.

Thanks to all those who helped with editing this manuscript, particularly Stacey Zinke-McKee, Manager of the Protections and Survival Laboratory, and Dr. Anthony Tvaryanas, current manager of AMRD.

---



v

# TABLE OF CONTENTS

**LIST OF ABBREVIATIONS** ..................................................................................................................... vi

**EXECUTIVE SUMMARY** ........................................................................................................................ vii

**INTRODUCTION** ........................................................................................................................................ 1
- Civil Aerospace Medical Institute G Effects Model Software.................................................................. 1
- Background ............................................................................................................................................... 1

**DESCRIPTION**............................................................................................................................................. 3
- Design ....................................................................................................................................................... 3
- User Inputs................................................................................................................................................ 6
  - Control and parameters ......................................................................................................................... 6
  - Simulation options ................................................................................................................................ 6
  - The simulation series ............................................................................................................................ 9
  - Custom internal simulation ................................................................................................................... 9
  - Custom simulation driven by data in an external file ........................................................................... 9
- System Requirements and Installation .................................................................................................... 10
- Output Files............................................................................................................................................. 11

**CONCLUDING REMARKS** ...................................................................................................................... 11
- Contact Information ................................................................................................................................ 11

**REFERENCES** ........................................................................................................................................... 12

**APPENDICES** ............................................................................................................................................ 14
- Appendix A: Sample Contents of File gloc_inp.dat ............................................................................... 14
- Appendix B: Sample Custom Gz Exposure Profile File Contents: File Contents .................................. 17
- Appendix C. Sample Output: Vertical Eight Maneuver ......................................................................... 19
- Appendix D. Sample Internal Centrifuge Experimental Profile Output File .......................................... 21

---


# LIST OF ABBREVIATIONS

AGS       Anti-G suit

AGSM      Anti-G straining maneuver

CAMI      Civil Aerospace Medical Institute

CGEM      CAMI G effects model

G-LOC     G induced loss of consciousness

ITP       Intrathoracic pressure

PBG       Pressure breathing gear

vi


---


# EXECUTIVE SUMMARY

This report is a guide to the use of the Civil Aerospace Medical Institute (CAMI) G Effects Model (CGEM) software. The software models effects of extreme Gz accelerations, including visual symptoms, G-LOC, and return to consciousness following G-LOC. The software accommodates Gz acceleration profiles experienced by most civilian and military pilots and also reproduces historical centrifuge experiments. Effects such as dehydration and fatigue are readily accommodated through changes in physiological parameters. Future planned developments include extending the model to include monitoring additional brain centers, anti-G equipment failure, an improved lung function model, direct inclusion of a library of acceleration profiles for standard maneuvers used in aerobatics, and a more user-friendly means of inputting effects of pilot dehydration and fatigue beyond adjusting the current input parameters.

vii


---


# CGEM User's Guide

## INTRODUCTION

### Civil Aerospace Medical Institute G Effects Model Software

There is ongoing interest in G force effects in both civil and military aviation, particularly its possible role in certain aerobatic accidents. To assist in investigations of these kinds of accidents and provide a tool useful to reduce risk of G force related accidents, a software-implemented model of G force-induced loss of consciousness (G-LOC), return to useful consciousness, and visual symptoms, the Civil Aerospace Medical Institute (CAMI) G Effects Model (CGEM), was developed. Model results compare well with experimental centrifuge data from US Navy and US Air Force pilots, as well as other published data (Copeland & Whinnery, 2023).

### Background

Aerobatic and combat aircraft maneuvers can include large accelerations called G forces, so named because they feel like changes in gravity. When these accelerations are along the up-down axis from the pilot or other exposed individual's perspective, they are more specifically referred to as G<sub>z</sub> (z indicating direction) forces. Persons exposed to these forces can experience visual symptoms, including blackout, or may even become unconscious, a condition referred to as G-LOC. When it occurs, G-LOC can last for only a few seconds or last longer than 30 seconds, depending on the conditions that prompted it (Whinnery & Forster 2015). There is considerable natural variation in G tolerance. It can occur in untrained healthy individuals at exposures as low as positive 2 G<sub>z</sub> (i.e., acceleration equivalent to double the normal force of gravity at the Earth's surface; Figure 1, p. 2) (Bureau of Air Safety Investigation [BASI], 1988). There has been a great deal of research on the topic. Some reviews include Mohler (1972), Kirkham et al. (1982), BASI (1988), and Buick (1989). A situation inducing a pilot's loss of consciousness while in flight could result in the loss of control of the aircraft. At a minimum, there will be a loss of pilot situational awareness if the pilot is fortunate enough to wake up before a mishap event occurs (e.g., see McMahon & Newman, 2016).

In very high positive G<sub>z</sub> onset situations, there are no warning symptoms sufficiently prior to onset of G-LOC to allow an affected person to prevent it. If onset is sufficiently slow, several warning signs precede G-LOC: a loss of peripheral vision (i.e., grayout), the loss of all vision (i.e., blackout), and finally, increasing levels of cognitive difficulty. These effects are due to lack of adequate circulation of fresh blood to the eye and brain and can be alleviated if G<sub>z</sub> is reduced or G<sub>z</sub> tolerance is somehow rapidly increased (e.g., by activating a pressure suit or performing a straining maneuver). Some factors known to reduce G-LOC resistance include hypotension, hypoglycemia, illness, dehydration, exposure to alcohol, and fatigue. Resistance can be improved from the naïve state by frequent exposure, the practice of certain exercises, and mechanical aides.

1


---


# Figure 1

## In-flight G force components, Gx, Gy, and Gz.

[Diagram showing a seated human figure in profile with directional arrows indicating G-force components. The figure shows:
- -Gz arrow pointing upward from the head
- +Gz arrow pointing downward toward the feet
- -Gx and +Gx arrows pointing left and right respectively at chest level
- -Gy and +Gy arrows pointing backward and forward respectively at chest level

Text boxes in the diagram read:
"TERMINOLOGY FOR ACCELERATION FORCES ON THE BODY"

"VECTOR DIRECTION NAMED FOR THE DIRECTION THE HEART MOVES RELATIVE TO THE SKELETON UNDER THE IMPOSED ACCELERATION"]

For each component, the arrow indicates the direction of pull of the force felt by the body (Mohler, 1972).

Negative Gz is considered more dangerous than positive Gz because blood is forced into the head instead of being pulled out. During negative Gz exposure, the body attempts to counter the pooling by slowing the heart rate and by vasodilation to lower intracranial pressure and restore normal blood flow in the head. At the lowest levels, unpleasant symptoms such as nausea have been reported. At more negative Gz levels, a visual symptom called redout, a phenomenon similar to grayout, but the visual field becomes red, occurs. Physiologically, redout remains poorly understood. Redout is followed by G-LOC and can be accompanied by retinal hemorrhages. Exposure to negative Gz reduces tolerance to positive Gz until recovery (BASI, 1998). Countermeasures for positive Gz exposures are not effective for negative Gz.

2


---


Both military and civilian pilots can perform significant aerobatic maneuvers, e.g., during agricultural (e.g., crop dusting) and entertainment (e.g., air show) flights. Military maneuvers tend to avoid negative Gz. While they do endure the extreme Gz of military flight, civilian pilots do not as deliberately avoid negative Gz, rarely use anti-G equipment (civilian aircraft are seldom equipped to accommodate it), and sometimes experience unsustainably high negative Gz for short periods as part of their routines. A civilian pilot is also more likely to be older and use non-disqualifying medications with cardiovascular effects that could reduce his or her resistance.

CGEM was developed with these considerations in mind. The remainder of this report describes the design and use of the CGEM software.

# DESCRIPTION

## Design

The software can model persons (pilots, experimental participants, etc.) of different sexes and cardiovascular conditions and allows the inclusion of estimated effects of drugs and conditions known to affect circulation capacities, heart rate changes, and/or vascular system response to stress. Strategies such as anti-G suits (AGS), positive pressure breathing gear (PBG), anti-G straining maneuvers (AGSM), and other muscle-tensing effects are allowed as user-definable options. Any Gz exposure profile may be entered and simulated at millisecond resolution, enabling modeling any aerobatic maneuver, series of maneuvers, or centrifuge experiment.

The four reserve bank balances are tracked. The balance of each bank is based on the amount of oxygen brought by fully oxygenated blood at the minimum flow rate needed to maintain a particular state of metabolic operation based on experimental data. Each bank has a maximum allowed balance equal to the balance maintained during the normal resting state. Two banks balances are used to track brain function: one for G-LOC (a consciousness bank) and one for brain tissue death (the life bank). Two additional banks follow the state of the retina: the first is for tracking the start of visual symptoms (such as grayout or redout and peripheral light loss), and the second is for blackout.

Regarding the brain function-related banks, the blood flow is used to refill the life bank and/or keep it full, with any extra flow being used to refill and maintain the consciousness bank. The two retinal banks are essentially separate measures of the balance of the retinal bank level at the outermost and most central regions. The basic assertions and assumptions used in the model are:

* The brain contains the body's centers of consciousness (Långsjö et al., 2012).
* Cells normally hold a reserve of oxygen and other needed resources creating an incapacitation buffer if supply is suddenly interrupted (Burton, 2000; Moore et al., 1993; Whinnery et al., 2014). This buffer can last 5 to 15 seconds, but the most common consciousness buffer times are relatively brief. For example, Rossen et al. (1943), in a study of 111 young adult men, found that cellular reserves will maintain consciousness for 5 to 11 seconds if the flow is stopped by cervical compression, but the distribution is peaked towards the lower end, with an average of 7.1 seconds and median of 6.5 (± 0.5) seconds.

3


---


While adjustable by the user, the default values for minimum, mean, and maximum reserves are set at 5, 7.1, and 15 seconds, respectively.

* As a known limiting factor, blood oxygenation deficit is used as a proxy for blood usefulness to tissues. It is known that oxygen is needed by cells and that hyperoxygenation is of limited benefit in resisting G-LOC (Besch et al., 1994; Tripp et al., 2009).

* Cells do housekeeping. The size of the buffer and the time to return to full function depend on the cells' anaerobic fitness if the flow is completely stopped (Besch et al., 1994; Ryoo et al., 2004). The model assumes cells' life and full function (for vision or consciousness) reserve banks must be fully refilled before cell normal function resumes.

* For brain cells, a full life reserve bank will keep the cells alive without any impairment after revival for a further 180 seconds after unconsciousness if blood flow is not restored. This is somewhat arbitrary since the normal function can be restored after more prolonged periods, but damage is increasingly common at times longer than 3 minutes (Walters, 1998).

* Retinal cells are assumed to be practically immortal; the life bank is not tracked. This is because normal eye function is restored after much longer periods of oxygen deprivation than brain tissue can survive, and there are no reports of lingering blackout after return to consciousness in pilots.

* Assuming full oxygenation, a cerebral blood flow rate of about 18 to 20 dL/minute is needed to maintain consciousness indefinitely (Walters, 1998).

* Assuming full oxygenation, about 20% (set to 9 dL/minute in this model) of the normal cerebral blood flow rate is needed to maintain cell function (Clarke and Sokoloff, 1989).

* Oxygenation of blood can be reduced by high positive and negative Gz due to lost lung capacity (Eiken & Grönkvist, 2013).

* Negative Gz is similar enough with respect to G-LOC that it can be modeled as positive Gz with respect to effects (Kirkham et al., 1982).

* Unlike positive Gz exposure, which increases heart rate, negative Gz exposure can reduce heart rate and delay the heart rate response to positive Gz (Civil Aviation Safety Authority Australia, 2001). In the model, this delay is the lesser time of negative Gz exposure or 5 seconds. Heart-level arterial pressures and heart rate-related blood pressure increases are returned to normal whenever Gz falls below 1.4 G.

* Countermeasures for +Gz effects are not effective at increasing negative Gz tolerance.

* Cerebral blood flow is modeled as a function of mean arterial pressure and vascular resistance (Walters, 1998).

* Normal intracranial pressure is 9 mmHg (range, 5 to 13 mmHg) (Walters, 1998).

* Normal intraocular pressure is 22 mmHg (Tipton, 1983).

* Under normal conditions, the mean arterial blood pressure change with height above the heart is -0.7335 mmHg/cm.

* Once G-LOC has occurred, the brain must restore its cellular reserves before resuming useful consciousness.

4


---


• All organ distance measurements in a relaxed person under normal gravity are scaled using sex and height from the International Commission on Radiation Protection and Measurements (ICRP) Publication 110 anthropomorphic phantoms (ICRP, 2009). These phantoms are digitized computed tomography scans of adults.

• If the person is not fully erect (i.e., the seat is not vertical), relative vertical distances are adjusted only below the level of the cortical cervical spine. To allow continued good visibility from the cockpit, the head is assumed to remain vertical.

• There are multiple centers of the brain involved in consciousness (Långsjö et al., 2012). For modeling cerebral blood flow, the center of consciousness in the brain was selected to be located halfway between the base of the brain and the center of mass of the eye.

• Grayout, peripheral light loss, and blackout occur because of inadequate flow at the retina (i.e., retinal ischemia). Intraocular pressure must be overcome by local arterial pressure to prevent visual symptoms (Whinnery & Forster, 2015).

The resource flow model uses flow rates (F) at sites above the heart based on locally available perfusion pressures (P<sub>P</sub>), vascular resistance (R), and fractional blood oxygenation (O) (Eq. 1),

$$F = O * (P_P) / R,$$                                                                      (1)

where the perfusion pressure is calculated from Gz, the heart level mean arterial pressure (P<sub>H</sub>), the change in elevation from the heart to the site (H), intraocular or intracranial pressure (P<sub>I</sub>), and the change in arterial pressure per unit change in elevation (dP/dH, at -0.7333 mmHg/cm) as (Eq. 2),

$$P_P = P_H + H * dP/dH * G - P_I.$$                                                          (2)

The vascular resistance is allowed to range between a normal value of 1.6 and a minimum of 0.4 mmHg/dL/minute as the body attempts to autonomically maintain normal flow (or more) at the center-of-consciousness level.

P<sub>H</sub> is set to resting level and allowed to ramp up to maximum levels as a function of time after Gz exceeds 1.4 G as described by Eq. 3,

$$P_H = P_{H\_rest} + P_{H\_increase} * (1.0 - exp(-t/B))$$                                        (3)

where P<sub>H_increase</sub> is the difference between the maximum allowed value of P<sub>H</sub> for the person and the resting value, and B is a time constant resulting in the maximum value of P<sub>H</sub> in 14 to 20 seconds for most persons (Tipton, 1983). Once the Gz stress drops below 1.4 G, the P<sub>H</sub> is immediately returned to resting levels. For negative Gz, this change in P<sub>H</sub> is not used because the response mechanisms sometimes suppress heart rate and attempt to drop pressure. Interestingly, a recent study by Rice et al. (2016) did not observe changes significantly below normal levels in practicing aerobatic pilots. To model the push-pull effect (i.e., instances with Gz changing from negative to positive, such during aerobatic maneuvers), time spent at negative Gz of up to 5 seconds is introduced as a delay to response in correcting P<sub>H</sub> for positive Gz stress. While some delay is allowed, consistent with Rice et al.'s findings, heart level blood pressure is not allowed to drop below the normal baseline.

5


---


The AGS effects are modeled in two ways: rise in intrathoracic pressure (ITP) and an elevation of the heart (Buick, 1989; Burton, 2000). The net effect of the suit inflation is assumed to be 3 to 6 mmHg/psi at heart level depending on body coverage of the suit (6 mmHg/psi at >70% coverage, 3 mmHg/psi at <35% coverage, and linear interpolation for coverage in between). The heart is also forced upwards by inflation by 6 mmHg/psi. A realistic limit of suit inflation is 10 to 12 mmHg/psi.

An AGSM can be incorporated with or without an anti-G suit. The maximum effectiveness is limited to an increase in ITP of 130 mmHg, while the assumed rise in heart level mean arterial pressure per mmHg of ITP is 0.75 mmHg at heart level (Buick et al., 1991). The increase in ITP from an anti-G suit, if present, is compared to the AGSM increase in ITP. The higher value is used.

Straining muscles, even something as simple as tightly gripping an object, can increase arterial pressure if done for long enough (50 mmHg in about 30 seconds) (Quarry & Spodick, 1974). The user can directly specify the level of this effect. The pressure increase may be used throughout a simulation, or the pressure can increase linearly from a user-defined level to a user-defined maximum in 30 seconds. The total increase is limited to 60 mmHg. If AGSM is also used, then the greater of the two pressure increases is used in the model.

Users can designate a maximum pressure for PBG. This gear significantly increases +Gz resistance without AGSM and reduces the strain of breathing while performing AGSM, increasing the time pilots can sustain high +Gz exposures before significant muscle fatigue occurs (Eiken et al., 2007). Studies indicate maximal effectiveness at 60 mmHg with 1:1 conversion to heart level mean arterial pressure. Thus, in CGEM, PBG ITP is limited to 60 mmHg regardless of user-entered values above this level.

## User Inputs

### Control and parameters

The program has no internal menus. Operation is entirely controlled by the input file gloc_inp.dat (see Appendix 1 for a sample version of this file) and files indicated therein. This file holds all basic information to be used by the program that the user can alter. These variables include sex, height, resting and maximal blood pressures, heart-related blood pressure increase time constant, maximal Gz exposure profile information, anti-G countermeasures, seat tilt, a time shift for pharmacological or other heart-driven blood pressure responses to stress, and designated input and output filenames. The meaning of each line is explained in Table 1 (p. 7 and following).

### Simulation options

The user can choose any of three simulation options: a series of simulations with acceleration profiles similar to historical centrifuge experiments, a single simulation of a centrifuge experiment, or a flight-like simulation, where all aspects of the acceleration profile are defined by the user in an external file.

6


---



# Table 1
## Parameters in file gloc_inp.dat

<table>
<thead>
<tr>
<th>Line</th>
<th>Parameter</th>
<th>Units</th>
<th>Allowed Values (Recommended)</th>
<th>Explanation</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>G0 (G<sub>0</sub>)</td>
<td>g</td>
<td>Any (0-1.4)</td>
<td>Local gravity field in g, typically =1</td>
</tr>
<tr>
<td>2</td>
<td>Gmax (G<sub>max</sub>)</td>
<td>g</td>
<td>Up to 15</td>
<td>Maximum Gz allowed during an internally defined centrifuge experiment simulation</td>
</tr>
<tr>
<td>3</td>
<td>fnorm</td>
<td>dl/min</td>
<td>Any (45-54)</td>
<td>Normal blood flow rate through brain</td>
</tr>
<tr>
<td>4</td>
<td>fmax</td>
<td>dl/min</td>
<td>Any (110)</td>
<td>Maximum blood flow rate through brain</td>
</tr>
<tr>
<td>5</td>
<td>Fcon</td>
<td>dl/min</td>
<td>Any (17-20)</td>
<td>Blood flow needed through brain to maintain consciousness</td>
</tr>
<tr>
<td>6</td>
<td>Flife</td>
<td>dl/min</td>
<td>Any (8-10)</td>
<td>Blood flow needed through brain to maintain brain cell life</td>
</tr>
<tr>
<td>7</td>
<td>Gtm</td>
<td>---</td>
<td>Any (1.0)</td>
<td>G tolerance time multiplier for the studied population. In normal use, this parameter = 1.0. Its purpose is to help investigate individual differences among otherwise physiologically similar persons in a population.</td>
</tr>
<tr>
<td>8</td>
<td>Beta</td>
<td>seconds</td>
<td>Any (2-3)</td>
<td>Time constant in seconds for heart rate response function. This should be about 1/7 the time to ramp up to full response. A value of 2-3 seconds seems typical (15-20 seconds to reach max effect).</td>
</tr>
<tr>
<td>9</td>
<td>BSP</td>
<td>mmHg</td>
<td>Any (100-130)</td>
<td>Baseline resting systolic blood pressure</td>
</tr>
<tr>
<td>10</td>
<td>BDP</td>
<td>mmHg</td>
<td>Any (60-90)</td>
<td>Baseline resting diastolic blood pressure</td>
</tr>
<tr>
<td>11</td>
<td>MSP</td>
<td>mmHg</td>
<td>Any (131-213)</td>
<td>Maximum exercising systolic blood pressure</td>
</tr>
<tr>
<td>12</td>
<td>MDP</td>
<td>mmHg</td>
<td>Any (59-98)</td>
<td>Maximum exercising diastolic blood pressure</td>
</tr>
<tr>
<td>13</td>
<td>conbank</td>
<td>seconds</td>
<td>Any (5-15)</td>
<td>Seconds of consciousness if oxygen flow stops. This is experimentally shown to range from 5 to 15 seconds from rapid decompression and choke collar reports.</td>
</tr>
<tr>
<td>14</td>
<td>lifebank</td>
<td>seconds</td>
<td>Any (180)</td>
<td>Seconds of life of brain cells if blood flow stops after conbank is exhausted. A typically accepted value is about 180 seconds (3 minutes), after which brain damage is considered increasingly likely. This period is large enough that it does not affect time to G-LOC.</td>
</tr>
<tr>
<td>15</td>
<td>gmaxtime</td>
<td>seconds</td>
<td>Any</td>
<td>Seconds to hold acceleration at Gmax during centrifuge experiment simulations. Set parameters 15, 16, and 17 to >0.0; otherwise, a set of simulations at predetermined dG/dt steps will be done based on values of parameters 16 and 17. If parameter 16 is 0.0 then a set of return to consciousness simulations will be done. If parameter 17 is 0.0 a set of G-LOC induction simulations will be run. If both are 0.0 then a set of 27 simulations up to G-LOC and back to consciousness at the opposite dG/dt steps after time gmaxtime will be run.</td>
</tr>
</tbody>
</table>

7


---



<table>
<thead>
<tr>
<th>Line</th>
<th>Parameter</th>
<th>Units</th>
<th>Allowed Values (Recommended)</th>
<th>Explanation</th>
</tr>
</thead>
<tbody>
<tr>
<td>16</td>
<td>Rampup (R<sub>up</sub>)</td>
<td>g/second</td>
<td>Any</td>
<td>Positive rate of change in Gz (g/s) towards G-LOC used for centrifuge experiment simulations</td>
</tr>
<tr>
<td>17</td>
<td>Rampdown (R<sub>down</sub>)</td>
<td>g/second</td>
<td>Any</td>
<td>Negative rate of change in Gz (g/s) after gmaxtime used for centrifuge experiment simulations</td>
</tr>
<tr>
<td>18</td>
<td>sex</td>
<td>---</td>
<td>0 or 1</td>
<td>Selects the sex of the phantom to use for distance scaling: 1=male, 0=female.</td>
</tr>
<tr>
<td>19</td>
<td>Howtall</td>
<td>cm</td>
<td>Any (162.6-195.6)</td>
<td>Height of person in cm (e.g., U.S. fighter pilot range is 162.6-195.6 cm) used to calculate the heart-eye and other vertical distances.</td>
</tr>
<tr>
<td>20</td>
<td>Smpsi</td>
<td>psi</td>
<td>Any (0-15)</td>
<td>Maximum pressure in psi of anti-G suit. The net effect is added Gz tolerance by increase of internal pressures at heart level and from slightly raising the physical location of the heart in the chest cavity. The pressure is linearly increased from 0 psi at 1 G to the indicated value at 9 G. Values above and below recommended limits are treated as upper and lower recommended values.</td>
</tr>
<tr>
<td>21</td>
<td>Sbc</td>
<td>---</td>
<td>Any (0-0.7)</td>
<td>Suit body coverage: more coverage can double effectiveness but is less comfortable. Standard military coverage is 30-35% and can be up to 85%. Values above and below recommended limits are treated as upper and lower recommended values.</td>
</tr>
<tr>
<td>22</td>
<td>Agsm</td>
<td>---</td>
<td>0-1</td>
<td>Effectiveness of the anti-G straining maneuver: uses a decimal value from 0 (completely ineffective) to 1.0 (optimal). Optimal effectiveness will increase intrathoracic pressure by as much as about 130 mmHg.</td>
</tr>
<tr>
<td>23</td>
<td>Pbg</td>
<td>mmHg</td>
<td>Any (≤ 60)</td>
<td>Pressurized breathing gear: This raises pressure in the chest cavity to assist breathing under high G. Maximum useful pressure is limited to 60 mmHg. The pressure is ramped as G increases from 0 mmHg at 1 G to the indicated value at 9 G.</td>
</tr>
<tr>
<td>24</td>
<td>otherstrain</td>
<td>mmHg</td>
<td>Any (≤ 60)</td>
<td>In the absence of AGSM, other muscle strains, such as tightly gripping an object, will increase mean arterial pressure at heart level by as much as 60 mmHg. Even just a single tight grip can increase this pressure by 15 mmHg, while 0 indicates fully relaxed. This value is applied at the start of the test (e.g., a pre-tensed person). A value above 60 will be treated as 60.</td>
</tr>
<tr>
<td>25</td>
<td>O_strain_limit</td>
<td>mmHg</td>
<td>Any (≤ 60)</td>
<td>The maximum allowed rise in heart level arterial pressure from gripping or other muscle tensing. It takes about 30 seconds in a simulation to increase from the value of parameter 24 to this value. A value above 60 will be treated as 60.</td>
</tr>
</tbody>
</table>

8


---



<table>
<thead>
<tr>
<th>Line</th>
<th>Parameter</th>
<th>Units</th>
<th>Allowed Values (Recommended)</th>
<th>Explanation</th>
</tr>
</thead>
<tbody>
<tr>
<td>26</td>
<td>seattilt</td>
<td>degrees</td>
<td>0-90 (0-35)</td>
<td>Angle in degrees the seat is tilted from vertical, if any. It is used to correct heart-brain distance (e.g., 0-10° for typical, 30° for an F-16) and include the effect of lung self-crushing from effective weight at large inclinations under high Gz. Note: some unmodeled physiological effects are likely to be significant at angles greater than 35°.</td>
</tr>
<tr>
<td>27</td>
<td>DrugDelay</td>
<td>seconds</td>
<td>Any (0-3)</td>
<td>Time delay in heart response to stress from pharmaceuticals (e.g., metoprolol can delay initial ramp by a few seconds)</td>
</tr>
<tr>
<td>28</td>
<td>outname</td>
<td>---</td>
<td>Any (12-character max.)</td>
<td>Name of output file if parameter 30=0</td>
</tr>
<tr>
<td>29</td>
<td>who</td>
<td>---</td>
<td>0, 1, 2, 3, 4, 5, or 6</td>
<td>Source of the physiology information: 0=physiology specified by other parameters in this file; 1-6 indicate use of physiologies from Table 2 (p.10)</td>
</tr>
<tr>
<td>30</td>
<td>gfile</td>
<td>---</td>
<td>0 or 1</td>
<td>Gz profile source: 0=use a built-in centrifuge experiment plan sequence, 1=use acceleration changes from the file named in parameter 31</td>
</tr>
<tr>
<td>31</td>
<td>egpname</td>
<td>---</td>
<td>Any (12-character max.)</td>
<td>Name of file with dGz/dt profile data</td>
</tr>
<tr>
<td>32</td>
<td>egpoutname</td>
<td>---</td>
<td>Any (12-character max.)</td>
<td>Name of file with dGz/dt profile output</td>
</tr>
</tbody>
</table>

*Note.* G-LOC = G-induced loss of consciousness.

**The simulation series**

If R<sub>up</sub> and R<sub>down</sub> (Table 1, parameters 16 and 17) are both zero, the program will simulate a series of centrifuge experiments such as those reported by Whinnery et al. (2014). These are symmetric simulations where acceleration starts at G<sub>0</sub> (Table 1, parameter 1); the acceleration increases until G-LOC, held for 1 second, then decreases back to G<sub>0</sub> at the same rate. The rate of change of Gz in the first simulation is 0.01 G/sec. In succeeding simulations, the rate is increased in 0.01 G/s steps up to 0.1 G/s; then the cycle repeats in 0.1-Gz steps until the rate is 1 G/s, at which point the rate increases by 1 G/s for each simulation up to G<sub>max</sub> (Table 1, parameter 2) or if G<sub>max</sub> is not an integer, the nearest integer value below G<sub>max</sub>. The output is written to screen and to the output file named by the user as the internal simulation profile output file (Table 1, parameter 28).

**Custom internal simulation**

If R<sub>up</sub> and R<sub>down</sub> have non-zero values, a single simulation of a centrifuge experiment will be run using the parameters from Table 1. The output is written to screen and to the output file named by the user as the internal simulation profile output file (Table 1, parameter 28).

**Custom simulation driven by data in an external file**

Using the user-designated custom simulation profile input file (Table 1, parameter 31) allows the user to define a custom Gz profile. The program can simulate any Gz exposure profile at up to millisecond specificity, but the file must be formatted appropriately (an example is provided in Appendix 2). The first line must be an integer indicating the number of following data lines to use.

9


---



The following lines must have the rate of change in Gz followed by an integer value for the number of milliseconds to use that rate of change (i.e., dGz/dt, t). The software is precompiled to use up to 1000 acceleration changes. The output is written to the screen and the user-designated custom simulation profile output file (Table 1, parameter 32).

There are six different standard person physiologies built into the model. The parameter values of standard persons are listed in Table 2. If none of the standard persons are selected, the parameter values the user specifies in file gloc_inp.dat are used.

**Table 2**

*Parameters specifying physiological attributes used for CGEM standard persons.*

<table>
<thead>
<tr>
<th>Parameter (units)</th>
<th>High Resistance</th>
<th>Average Resistance</th>
<th>Low Resistance</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="4"><strong>Males</strong></td>
</tr>
<tr>
<td>Physiology</td>
<td>1</td>
<td>2</td>
<td>3</td>
</tr>
<tr>
<td>Normal flow (dL/min)</td>
<td>54</td>
<td>49.5</td>
<td>45</td>
</tr>
<tr>
<td>Flow needed for consciousness (dL/min)</td>
<td>18</td>
<td>19</td>
<td>20</td>
</tr>
<tr>
<td>Flow for life support (dL/min)</td>
<td>8</td>
<td>9</td>
<td>10</td>
</tr>
<tr>
<td>Beta (sec)</td>
<td>2</td>
<td>2.5</td>
<td>3</td>
</tr>
<tr>
<td>Bank of consciousness (seconds)</td>
<td>15</td>
<td>7.1</td>
<td>5</td>
</tr>
<tr>
<td>Bank of life (seconds)</td>
<td>180</td>
<td>180</td>
<td>180</td>
</tr>
<tr>
<td>Height<sup>A</sup> (cm)</td>
<td>162.5</td>
<td>179</td>
<td>195.6</td>
</tr>
<tr>
<td>Resting systolic BP<sup>B</sup> (mmHg)</td>
<td>130</td>
<td>120</td>
<td>100</td>
</tr>
<tr>
<td>Resting diastolic BP<sup>B</sup> (mmHg)</td>
<td>90</td>
<td>80</td>
<td>60</td>
</tr>
<tr>
<td>Maximally active systolic BP<sup>C</sup> (mmHg)</td>
<td>213</td>
<td>177</td>
<td>147</td>
</tr>
<tr>
<td>Maximally active diastolic BP<sup>C</sup> (mmHg)</td>
<td>98</td>
<td>88</td>
<td>59</td>
</tr>
<tr>
<td colspan="4"><strong>Females</strong></td>
</tr>
<tr>
<td>Physiology</td>
<td>4</td>
<td>5</td>
<td>6</td>
</tr>
<tr>
<td>Normal flow (dL/min)</td>
<td>54</td>
<td>49.5</td>
<td>45</td>
</tr>
<tr>
<td>Flow needed for consciousness (dL/min)</td>
<td>18</td>
<td>19</td>
<td>20</td>
</tr>
<tr>
<td>Flow for life support (dL/min)</td>
<td>8</td>
<td>9</td>
<td>10</td>
</tr>
<tr>
<td>Beta (sec)</td>
<td>2</td>
<td>2.5</td>
<td>3</td>
</tr>
<tr>
<td>Bank of consciousness (seconds)</td>
<td>15</td>
<td>7.1</td>
<td>5</td>
</tr>
<tr>
<td>Bank of life (seconds)</td>
<td>180</td>
<td>180</td>
<td>180</td>
</tr>
<tr>
<td>Height (cm)</td>
<td>162.5</td>
<td>179</td>
<td>195.6</td>
</tr>
<tr>
<td>Resting systolic BP<sup>B</sup> (mmHg)</td>
<td>130</td>
<td>120</td>
<td>100</td>
</tr>
<tr>
<td>Resting diastolic BP<sup>B</sup> (mmHg)</td>
<td>90</td>
<td>80</td>
<td>60</td>
</tr>
<tr>
<td>Maximally active systolic BP<sup>C</sup> (mmHg)</td>
<td>187</td>
<td>157</td>
<td>131</td>
</tr>
<tr>
<td>Maximally active diastolic BP<sup>C</sup> (mmHg)</td>
<td>93</td>
<td>76</td>
<td>60</td>
</tr>
</tbody>
</table>

<sup>A</sup> Allowed size range of fighter pilots in U.S. military, not population anatomical data.
<sup>B</sup> This is the "healthy" range, persons with resting BP outside of this range would normally be treated for hypertension or hypotension.
<sup>C</sup> FRIEND cohort (Sabbahi et al., 2018) 95<sup>th</sup>, 50<sup>th</sup> and 5<sup>th</sup> percentile values for young adult males and females (ages 20-39).

*Note: BP = blood pressure; CGEM = Civil Aerospace Medical Institute G Effects Model (CGEM).*

## System Requirements and Installation

A compiled version is available for Intel processors running 64-bit Windows and Linux. The executable uses about 700 kB of disk space. The output file size is extremely variable and depends

10


---


on the acceleration profile used; for development examples, sizes ranged from a few kB to several hundred kB.

**Output Files**

The program produces output files based on the user's choices. Output files begin with a summary of physiological and simulation-related information, followed by a large table. If an acceleration profile from an external file is used, the output table shows person status throughout the simulation each second and the millisecond time of the change of state whenever there is a change state for physical abilities (consciousness, blackout, or vision). An example file is shown in Appendix C. The output table is slightly different for standard simulations of centrifuge experiments. A sample of this file is shown in Appendix D. In this case, the Gz profile results are summarized by times and G levels of the tracked effects: time to G-LOC, time to return to consciousness from absolute incapacitation, time at the onset of visual symptoms, time at blackout, G onset rate, G at the return to consciousness, G at unconsciousness, G at blackout, and G at the beginning of visual symptoms. The final column is the lowest balance in the life bank.

## CONCLUDING REMARKS

This report describes the general function and use of new software for modeling G effects in persons such as pilots and centrifuge experiment participants. The software includes enough flexibility to model any practical acceleration profiles for most civilian and military pilots and reproduce historical centrifuge experiments. Effects such as dehydration and fatigue are readily accommodated through changes in physiological parameters. However, there is considerable room for improvement. Some possible extensions would be the inclusion of anti-G equipment failure, an improved lung function model to account for tilt towards supine or prone positions, direct inclusion of profiles for standard maneuvers used in aerobatics, and effects of pilot dehydration and fatigue beyond adjusting the current input parameters.

**Contact Information**

User feedback is always welcome. Questions, suggestions, and comments should be sent to:

U.S. Department of Transportation  
Federal Aviation Administration  
Office of Aerospace Medicine  
Health Safety Information Team, AAM-631  
Civil Aerospace Medical Institute  
Oklahoma City, OK 73169  
Fax: 405-954-1010  
E-mail: 9-AMC-AAM600-SPECIMENS@faa.gov

11


---


# REFERENCES

Besch, E.L., Werchan, P.M., Wiegman, J.F., Nesthus, T.E., Shahed, A.R. (1994 Apr). Effect of hypoxia and hyperoxia on human +Gz duration tolerance. *Journal of Applied Physiology (1985)*, 76(4), 1693–700, doi:10.1152/jappl.1994.76.4.1693.

Buick, F. (1989). +Gz Protection in the Future – Review of Scientific Literature (Report DCIEM No 89-RR-47). Defence and Civil Institute of Environmental Medicine.

Buick, F., Hartley, J., & Pecaric, M. (1991). Maximum intra-thoracic pressure with PBG and AGSM. In AGARD (Eds.), *High altitude and high acceleration protection for military aircrew*. Neuille-sur-Seine, France:NATO-AGARD; AGARD-CP-516, Oct 7.1–7.9.

Burton R. R. (2000). Mathematical models for predicting G-level tolerances. *Aviation, Space, and Environmental Medicine*, 71(5), 506–513.

Bureau of Air Safety Investigation. (1988). The Possibility of G-Induced Loss of Consciousness (G-LOC) during Aerobatics in Light Aircraft (Research Report 872-1017). Department of Transport and Communications.

Civil Aviation Safety Authority Australia. (2001). Guidelines for Aerobatics (AC91-075(0)).

Clarke, D. D., & Sokoloff, L. (1989). Circulation and energy metabolism of the brain. In G. Siegel, B. V. Agrano, R. W. Albers, P. V. Molino (Eds.), *Basic Neurochemistry* (pp. 565–90). Raven Press.

Copeland, K. & Whinnery J. E. (2023). Cerebral Blood Flow Based Computer Modeling of Gz-Induced Effects (Report No. DOT/FAA/AM-23/6). U.S. Department of Transportation. Federal Aviation Administration. Office of Aviation Medicine. https://doi.org/10.21949/1524446

Eiken, O., & Grönkvist, M. (2013). Signs and symptoms during supra-tolerance +G(z) exposures, with reference to G-garment failure. *Aviation, Space, and Environmental Medicine*, 84(3), 196–205. https://doi.org/10.3357/asem.3436.2013.

Eiken, O., Kölegärd, R., Bergsten, E., & Grönkvist, M. (2007). G protection: interaction of straining maneuvers and positive pressure breathing. *Aviation, Space, and Environmental Medicine*, 78(4), 392–398.

International Commission on Radiological Protection. (2009). Adult reference computational phantoms. ICRP Publication 110, *Annals of the ICRP*, 39, 2.

Långsjö, J. W., Alkire, M. T., Kaskinoro, K., Hayama, H., Maksimow, A., Kaisti, K. K., Aalto, S., Aantaa, R., Jääskeläinen, S. K., Revonsuo, A., & Scheinin, H. (2012). Returning from oblivion: imaging the neural core of consciousness. *The Journal of Neuroscience: The Official Journal of the Society for Neuroscience*, 32(14), 4935–4943. https://doi.org/10.1523/JNEUROSCI.4962-11.2012

Kirkham W. R, Wicks, S. M., & Lowrey, D. L. (1982). G Incapacitation in Aerobatic Pilots: An Aerobatic Hazard (Report No. FAA-AM-82-13). U.S. Department of Transportation. Federal Aviation Administration. Office of Aviation Medicine.

McMahon, T.W., & Newman D.G. (2016). G-induced visual symptoms in a military helicopter pilot. *Military Medicine*, 181(11/12), e1696-e1699.

12


---


Mohler, S. R. (1972). G Effects on the Pilot during Aerobatics (Report number FAA-AM-72-28). U.S. Department of Transportation. Federal Aviation Administration. Office of Aviation Medicine.

Moore, T. W., Jaron, D., Hrebien, L., & Bender, D. (1993). A mathematical model of G time-tolerance. Aviation, Space, and Environmental Medicine, 64(10), 947–951.

Quarry, V. M., & Spodick, D. H. (1974). Cardiac responses to isometric exercise: comparative effects with different postures and levels of exertion. Circulation, 49(5), 905–920. https://doi.org/10.1161/01.cir.49.5.905

Rice, G. M., Snider, D., Moore, J. L., Lavan, J. T., Folga, R., & VanBrunt, T. B. (2016). Evidence for -Gz Adaptation Observed with Wearable Biosensors During High Performance Jet Flight. Aerospace Medicine and Human Performance, 87(12), 996–1003. https://doi.org/10.3357/AMHP.4609.2016

Rossen, R., Kabat, H., Anderson, J. P. (1943). Acute arrest of cerebral circulation in man. Archives of Neurology and Psychiatry, 50(5), 510–28. https://doi.org/10.1001/archneurpsyc.1943.02290230022002

Ryoo, H. C., Sun, H. H., Shender, B. S., & Hrebien, L. (2004). Consciousness monitoring using near-infrared spectroscopy (NIRS) during high +Gz exposures. Medical Engineering & Physics, 26(9), 745–753. https://doi.org/10.1016/j.medengphy.2004.07.003

Sabbahi, A., Arena, R., Kaminsky, L. A., Myers, J., & Phillips, S. A. (2018). Peak Blood Pressure Responses During Maximum Cardiopulmonary Exercise Testing: Reference Standards From FRIEND (Fitness Registry and the Importance of Exercise: A National Database). Hypertension (Dallas, Tex. : 1979), 71(2), 229–236. https://doi.org/10.1161/HYPERTENSIONAHA.117.10116

Tripp, L. D., Warm, J. S., Matthews, G., Chiu, P. Y., & Bracken, R. B. (2009). On tracking the course of cerebral oxygen saturation and pilot performance during gravity-induced loss of consciousness. Human Factors, 51(6), 775–784. https://doi.org/10.1177/0018720809359631

Tipton, D. A. (1983). The Effects of Gx, Gy, and Gz Forces on Cone Mesopic Vision (AFAMRL-TR-83-047). Air Force Aerospace Medical Research Laboratory.

Walters, F. J. M. (1998). Intracranial pressure and cerebral blood flow. Update in Anaethesia, 8, 18–23.

Whinnery, T., & Forster, E. M. (2015). Neurologic state transitions in the eye and brain: kinetics of loss and recovery of vision and consciousness. Visual Neuroscience, 32, E008. https://doi.org/10.1017/S095252381500005X

Whinnery, T., Forster, E. M., & Rogers, P. B. (2014). The +Gz recovery of consciousness curve. Extreme Physiology & Medicine, 3, 9. https://doi.org/10.1186/2046-7648-3-9

13


---


# APPENDICES

## Appendix A: Sample Contents of File gloc_inp.dat

The example gloc.inp file contents that follow (courier font text) instruct the CGEM program to:

* Limit anti-g suit inflation to 8.8 psi (Line 20)
* Use a 70% coverage anti-g suit (Line 21)
* Limit anti-g straining maneuver (AGSM) effectiveness to 0% (Line 22)
* Limit pressure breathing gear to 60 mmHg (Line 23)
* Apply 0.0 mmHg for pre-simulation muscle tensing (Line 24)
* Limit the non-AGSM muscle tensing effect to 0.0 mmHg throughout the simulation (Line 25)
* Apply a 10 degree seat tilt (Line 26)
* Apply 0 seconds of heart response delay to changing Gz (Line 27)
* Use predefined subject physiology 2 (Line 29)
* Run a simulation described in an external file (line 30)
* Read file rapidtol.txt for simulation input data (Line 31)
* Write simulation output to file rapidtol.0 (line 32)

```
1.0, "Starting Gz"
13.0, "Max. allowed Gz"
49.5, "normal flow rate through brain dl/min"
110.0, "max flow rate through the brain"
19.0, "flow needed to maintain consciousness "
9.0, "flow needed to maintain life"
1.0, "g-tolerance multiplier relative to normal"
3.0, "heart action ramp-up time constant"
120., "Starting Systolic BP"
80., "Starting Diastolic BP"
177., "Max Systolic BP"
80., "Max Diastolic BP"
7.1, "starting seconds of consciousness after flow stops"
180.0, "starting seconds of cell life after flow stops"
1.0, "time to hold gmax in ramp-up experiment"
0.0, "dGzdt for ramp-up"
0.0, "dGzdt for ramp-down"
0, "subject sex"
```

14


---


```
179.0, "subject height in cm"
8.8, "anti-g suit max pressure in PSI(max ~12)"
0.70, "anti-g suit fractional body coverage (.0 to .7)"
0.0, "anti-g strain man effectiveness (0 none to 1 full)"
60.0, "Pressure breathing gear max mmHg (up to 60)"
0.0, "Other pre-test strain, 0 if relaxed, max 60 mmHg"
0.0, "non-agsm tensing limit during test (0.-60. mmHg) "
10.0, "seat tilt from vertical in degrees"
0.0, "seconds delay in heart response due to pharma"
test2019.dat
2, "subject data source (0=above, 1-6 are pre-defined)"
1, "0/1 use a internal/custom experimental profile"
rapidtol.txt
rapidtol.0
```

# COMMENTS
# The above physiology parameter choices are for midrange g tolerance
# Parameters are:
1. G0 - local gravity field in g, typically =1
2. Gmax - maximum Gz for an internally defined experiment
3. fnorm - normal blood flow rate through brain in dl/min (45-54)
4. fmax - maximum blood flow rate through brain (about 110)
5. fcon - blood flow needed through brain to maintain consciousness (17-20)
6. flife - blood flow needed through brain to maintain brain cell life (8-10)
7. gtm - g tolerance time multiplier for studied population, usually = 1.0, but can be as great as 1.53 using breathing techniques
8. beta - time constant in seconds for heart rate response function (This should be about 1/7 the time to ramp up to full response.) 2-3 seem typical (15-20 seconds to reach max effect)
9. BSP - baseline systolic blood pressure (typically 110-140)
10. BDP - baseline diastolic blood pressure (typically 60-90)
11. MSP - maximum exercising systolic blood pressure (range 130-234)
12. MDP - maximum exercising diastolic blood pressure (range 56-100)
13. conbank - seconds of consciousness if oxygen flow stops. This is experimentally shown to range from 5 to 15 seconds from rapid decompression and choke collar reports, 10 seems a reasonable midrange
14. lifebank - seconds of life of brain life if blood flow stops minus conbank

15


---


(typically accepted value is about 3 minutes). 180 sec is large enough that it does not effect time to GLOC or RTC times

15. **gmaxtime** seconds held at Gmax
(To simulate a particular experiment set 11, 12, and 13 to >0.0, otherwise a set of simulations at predetermined dG/dt steps will be done based on values of 12 and 13.
If 12 is 0.0 then a set of return to con sims will be done. If 13 is 0.0 a set of GLOC induction sims will be run. If both are 0.0 then a set of 30 sims up to GLOC and back to consciousness at the opposite dGdt after time gmaxtime will be run.)

16. **rampup** positive rate of change in Gz (g/s) towards GLOC

17. **rampdown** negative rate of change in Gz after gmaxtime in g/s

18. **male/female** 1=male, 0=female, selects which phantom to scale distances from

19. **howtall** height of subject in cm (U.S. fighter pilot range is 162.6-195.6 cm) used to calculate the heart-brain vertical distance, which is a slightly less than the heart-eye vertical distance.

20. **smpsi** max pressure in PSI of anti-G suit, net effect is added g tolerance by increase of internal pressures at heart level and from slightly raising the physical location of the heart in the chest cavity.
The pressure is ramped to the indicated value at 9 G.

21. **sbc** suit body coverage (more coverage can double effectiveness, but less comfortable. standard military is 30-35%, can be up to 85%

22. **agsm** Effectiveness of the anti-G straining maneuver, 0. to 1. optimal effectiveness will increase intra-thoracic pressure by as much as about 130 mmHg.

23. **pbg** Pressurized breathing gear raises pressure in the chest cavity to assist breathing under high G. Max useful pressure is about 60 mmHg.
The pressure is ramped to the indicated value at 9 G.

24. **otherstrain** In the absence of AGSM, other muscle strains, such as tightly gripping an object, will increase mean arterial pressure at heart level by as much as 60 mmHg. Even just a single tight grip can increase HLAP by 15 mmHg. Use 0 for relaxed.
This value is applied at the start of the test (e.g., a pre-tensed subject).

25. **O_strain_limit** The rise in arterial pressure from gripping or other muscle tensing takes about 30 seconds to reach full effect. This value is the upper limit.

26. **seattilt** Angle of seat tilted from vertical, if any, used to correct heart-brain distance. (e.g., 0-10 deg. for typical, 30 deg. for an F-16)
Lungs self-crushing from effective weight at large inclinations is also an issue to

16


---



consider.

27. **DrugDelay** - Time delay in heart response to stress from pharma (e.g., metprolol can delay initial ramp by a few seconds).

28. **outname** - Name of output file (12 character max)

29. **who** - Allows a standard pilot physiology instead of the one defined by parameters above
    0=use parameters, 1=high-resistance male, 2= average male, 3=low-resistance male,
    4=high-resistance female, 5=average female, 6=low-resistance female

30. **gfile** - 0=use built in experiment plan sequence, 1=use experimental plan from file
    egpname

31. **egpname** - name of file (12 character max) with experimental dGz/dt profile data

32. **egpoutname** - name of file (12 character max) with experimental dGz/dt profile output

## Appendix B: Sample Custom Gz Exposure Profile File Contents: File Contents

This example input file (courier font text) models an outside-inside vertical eight aerobatic maneuver using data from Mohler (1972). The first line indicates the number of lines below it to be read. The second and following lines each indicate a period of constant rate of change in acceleration, also called "jerk," in units of Gz per second: the first number is a real number specifying jerk, while the second is an integer specifying the duration of the jerk in milliseconds.

```
32
0., 1000
-3.2, 1000
-0.1, 3000
0.0, 2000
0.3, 1000
0.5, 1000
0.3, 1000
1.0, 1000
0.3, 2000
0.2, 1000
```

17


---



<table>
<tr><td>0.1</td><td>2000</td></tr>
<tr><td>-0.1</td><td>2000</td></tr>
<tr><td>-0.7</td><td>2000</td></tr>
<tr><td>-2.0</td><td>1000</td></tr>
<tr><td>-0.6</td><td>2000</td></tr>
<tr><td>0.8</td><td>1000</td></tr>
<tr><td>7.8</td><td>1000</td></tr>
<tr><td>0.6</td><td>1000</td></tr>
<tr><td>0.8</td><td>1000</td></tr>
<tr><td>0.2</td><td>1000</td></tr>
<tr><td>-1.1</td><td>1000</td></tr>
<tr><td>-0.9</td><td>1000</td></tr>
<tr><td>-0.6</td><td>1000</td></tr>
<tr><td>-0.3</td><td>1000</td></tr>
<tr><td>-0.5</td><td>1000</td></tr>
<tr><td>-0.2</td><td>1000</td></tr>
<tr><td>0.1</td><td>1000</td></tr>
<tr><td>-1.7</td><td>1000</td></tr>
<tr><td>-0.3</td><td>1000</td></tr>
<tr><td>-0.1</td><td>1000</td></tr>
<tr><td>-0.2</td><td>2000</td></tr>
<tr><td>-0.3</td><td>2000</td></tr>
</table>

18


---


# Appendix C. Sample Output: Vertical Eight Maneuver

The sample output file below (in courier font text) is the output from running the outside-inside vertical eight maneuver acceleration profile on person 2 (average male). The first part of the report describes person-related information; the second part is a report on states of the various flow rates and banks during the trial. The twelve columns are time in seconds, G level, effective G level for physical effects, consciousness bank balance in seconds of normal flow, flow at consciousness level, flow through the top of the eye (beginning of peripheral light loss), flow available to the central level of the eye (blackout), blackout bank balance in seconds of normal flow, and the current states of consciousness, visual symptom onset, and full blackout. For the state indicators, odd numbers indicate impairment, while even numbers indicate resumed function. The occasion large numbers in the time column indicate times of state changes in milliseconds. Data are for the end of the second.

```
Subject Parameters:
Brain-heart dist, G0, min flow, no-flow awake(sec)
  30.37330       1.000000           19.00000                    7.100000
max G,          F0,    max flow, Eye-heart dist
  13.40000       49.50000           123.7500                    33.01761
Subject height, male, no-flow alive(sec)
  179.0000                      1  180.0000
Units for distances are cm
Units for flows are dl/min
Units for acceleration are G
Units for times are seconds
Flow needed to avoid eventual death                       9.000000    s
USING these BPs        120.0000          80.00000                    177.0000   80.00000
Heart response time constant (ms):      2500.000
-------------------- Results -------------------
```

<table>
<thead>
<tr>
<th>Time</th>
<th>G</th>
<th>Geff</th>
<th>C_bank</th>
<th>F_Con</th>
<th>F_vis</th>
<th>F_BO</th>
<th>BO_Bank</th>
<th>HMAP</th>
<th>C</th>
<th>V</th>
<th>B</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>1.000</td>
<td>1.000</td>
<td>7.100</td>
<td>42.951</td>
<td>33.505</td>
<td>40.488</td>
<td>5.040</td>
<td>100.011</td>
<td>0</td>
<td>0</td>
<td>0</td>
</tr>
<tr>
<td>2</td>
<td>-2.197</td>
<td>2.197</td>
<td>7.100</td>
<td>43.810</td>
<td>24.186</td>
<td>37.288</td>
<td>5.040</td>
<td>100.000</td>
<td>0</td>
<td>0</td>
<td>0</td>
</tr>
<tr>
<td>3</td>
<td>-2.300</td>
<td>2.300</td>
<td>7.100</td>
<td>43.695</td>
<td>22.641</td>
<td>36.596</td>
<td>5.040</td>
<td>100.000</td>
<td>0</td>
<td>0</td>
<td>0</td>
</tr>
<tr>
<td>4</td>
<td>-2.400</td>
<td>2.400</td>
<td>7.100</td>
<td>44.161</td>
<td>21.255</td>
<td>36.333</td>
<td>5.040</td>
<td>100.000</td>
<td>0</td>
<td>0</td>
<td>0</td>
</tr>
<tr>
<td>5</td>
<td>-2.500</td>
<td>2.500</td>
<td>7.100</td>
<td>44.140</td>
<td>19.412</td>
<td>35.579</td>
<td>5.040</td>
<td>100.000</td>
<td>0</td>
<td>0</td>
<td>0</td>
</tr>
<tr>
<td>6</td>
<td>-2.500</td>
<td>2.500</td>
<td>7.100</td>
<td>44.137</td>
<td>19.409</td>
<td>35.576</td>
<td>5.040</td>
<td>100.000</td>
<td>0</td>
<td>0</td>
<td>0</td>
</tr>
<tr>
<td>7</td>
<td>-2.500</td>
<td>2.500</td>
<td>7.100</td>
<td>44.137</td>
<td>19.409</td>
<td>35.576</td>
<td>5.040</td>
<td>100.000</td>
<td>0</td>
<td>0</td>
<td>0</td>
</tr>
<tr>
<td>8</td>
<td>-2.200</td>
<td>2.200</td>
<td>7.100</td>
<td>43.734</td>
<td>24.100</td>
<td>37.206</td>
<td>5.040</td>
<td>100.000</td>
<td>0</td>
<td>0</td>
<td>0</td>
</tr>
<tr>
<td>9</td>
<td>-1.700</td>
<td>1.700</td>
<td>7.100</td>
<td>43.900</td>
<td>29.608</td>
<td>39.522</td>
<td>5.040</td>
<td>100.000</td>
<td>0</td>
<td>0</td>
<td>0</td>
</tr>
<tr>
<td>10</td>
<td>-1.400</td>
<td>1.400</td>
<td>7.100</td>
<td>43.656</td>
<td>31.715</td>
<td>40.214</td>
<td>5.040</td>
<td>100.000</td>
<td>0</td>
<td>0</td>
<td>0</td>
</tr>
<tr>
<td>11</td>
<td>-0.401</td>
<td>0.401</td>
<td>7.100</td>
<td>49.500</td>
<td>43.015</td>
<td>49.500</td>
<td>5.040</td>
<td>100.000</td>
<td>0</td>
<td>0</td>
<td>0</td>
</tr>
<tr>
<td>12</td>
<td>-0.100</td>
<td>0.100</td>
<td>7.100</td>
<td>49.500</td>
<td>47.787</td>
<td>49.500</td>
<td>5.040</td>
<td>100.000</td>
<td>0</td>
<td>0</td>
<td>0</td>
</tr>
</tbody>
</table>

19


---



<table>
<tr><td>13</td><td>0.200</td><td>0.200</td><td>7.100</td><td>49.500</td><td>46.202</td><td>49.500</td><td>5.040</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>14</td><td>0.400</td><td>0.400</td><td>7.100</td><td>49.500</td><td>43.026</td><td>49.500</td><td>5.040</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>15</td><td>0.500</td><td>0.500</td><td>7.100</td><td>49.500</td><td>41.438</td><td>48.055</td><td>5.040</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>16</td><td>0.600</td><td>0.600</td><td>7.100</td><td>48.518</td><td>39.851</td><td>46.541</td><td>5.040</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>17</td><td>0.500</td><td>0.500</td><td>7.100</td><td>49.500</td><td>41.435</td><td>48.052</td><td>5.040</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>18</td><td>0.400</td><td>0.400</td><td>7.100</td><td>49.500</td><td>43.021</td><td>49.500</td><td>5.040</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>19</td><td>-0.299</td><td>0.299</td><td>7.100</td><td>49.500</td><td>44.629</td><td>49.500</td><td>5.040</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>20</td><td>-0.999</td><td>0.999</td><td>7.100</td><td>42.964</td><td>33.520</td><td>40.503</td><td>5.040</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>21</td><td>-2.998</td><td>2.998</td><td>7.100</td><td>44.024</td><td>5.237</td><td>29.815</td><td>5.040</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>22</td><td>-3.599</td><td>3.599</td><td>7.100</td><td>27.031</td><td>0.000</td><td>4.578</td><td>4.780</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>23</td><td>-4.199</td><td>4.199</td><td>6.489</td><td>0.000</td><td>0.000</td><td>0.000</td><td>3.780</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>24</td><td>-3.401</td><td>3.401</td><td>6.328</td><td>38.088</td><td>0.000</td><td>16.598</td><td>2.840</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>25</td><td>4.392</td><td>4.392</td><td>7.016</td><td>0.000</td><td>0.000</td><td>0.000</td><td>4.406</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>26</td><td>4.999</td><td>4.999</td><td>6.016</td><td>0.000</td><td>0.000</td><td>0.000</td><td>3.406</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>27</td><td>5.799</td><td>5.799</td><td>5.016</td><td>0.000</td><td>0.000</td><td>0.000</td><td>2.406</td><td>100.000</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>27509</td><td>5.902</td><td>5.902</td><td>4.506</td><td>0.000</td><td>0.000</td><td>0.000</td><td>1.896</td><td>100.000</td><td>0</td><td>1</td><td>0</td></tr>
<tr><td>28</td><td>6.000</td><td>6.000</td><td>4.016</td><td>0.000</td><td>0.000</td><td>0.000</td><td>1.406</td><td>100.000</td><td>0</td><td>1</td><td>0</td></tr>
<tr><td>29</td><td>4.901</td><td>4.901</td><td>3.016</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.406</td><td>100.000</td><td>0</td><td>1</td><td>0</td></tr>
<tr><td>29406</td><td>4.535</td><td>4.535</td><td>2.609</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>100.000</td><td>0</td><td>1</td><td>1</td></tr>
<tr><td>30</td><td>4.001</td><td>4.001</td><td>2.016</td><td>4.660</td><td>0.000</td><td>0.000</td><td>0.000</td><td>100.000</td><td>0</td><td>1</td><td>1</td></tr>
<tr><td>31</td><td>3.401</td><td>3.401</td><td>2.135</td><td>38.101</td><td>0.000</td><td>16.611</td><td>0.000</td><td>100.000</td><td>0</td><td>1</td><td>1</td></tr>
<tr><td>32</td><td>3.100</td><td>3.100</td><td>4.541</td><td>43.858</td><td>0.554</td><td>27.831</td><td>0.963</td><td>100.000</td><td>0</td><td>1</td><td>1</td></tr>
<tr><td>33</td><td>2.601</td><td>2.601</td><td>7.042</td><td>44.084</td><td>17.290</td><td>34.692</td><td>3.510</td><td>100.000</td><td>0</td><td>1</td><td>1</td></tr>
<tr><td>33478</td><td>2.504</td><td>2.504</td><td>7.100</td><td>44.006</td><td>19.260</td><td>35.434</td><td>5.040</td><td>100.000</td><td>0</td><td>1</td><td>2</td></tr>
<tr><td>34</td><td>2.400</td><td>2.400</td><td>7.100</td><td>44.149</td><td>21.240</td><td>36.319</td><td>5.040</td><td>100.000</td><td>0</td><td>1</td><td>2</td></tr>
<tr><td>35</td><td>2.500</td><td>2.500</td><td>7.100</td><td>44.134</td><td>19.406</td><td>35.574</td><td>5.040</td><td>100.000</td><td>0</td><td>1</td><td>2</td></tr>
<tr><td>36</td><td>0.802</td><td>0.802</td><td>7.100</td><td>45.713</td><td>36.654</td><td>43.492</td><td>5.040</td><td>100.000</td><td>0</td><td>1</td><td>2</td></tr>
<tr><td>36712</td><td>0.586</td><td>0.586</td><td>7.100</td><td>48.711</td><td>40.070</td><td>46.750</td><td>5.040</td><td>100.000</td><td>0</td><td>2</td><td>2</td></tr>
<tr><td>37</td><td>0.500</td><td>0.500</td><td>7.100</td><td>49.500</td><td>41.437</td><td>48.054</td><td>5.040</td><td>100.000</td><td>0</td><td>2</td><td>2</td></tr>
<tr><td>38</td><td>0.400</td><td>0.400</td><td>7.100</td><td>49.500</td><td>43.027</td><td>49.500</td><td>5.040</td><td>100.000</td><td>0</td><td>2</td><td>2</td></tr>
<tr><td>39</td><td>0.200</td><td>0.200</td><td>7.100</td><td>49.500</td><td>46.199</td><td>49.500</td><td>5.040</td><td>100.000</td><td>0</td><td>2</td><td>2</td></tr>
<tr><td>40</td><td>0.000</td><td>0.000</td><td>7.100</td><td>49.500</td><td>49.373</td><td>49.500</td><td>5.040</td><td>100.000</td><td>0</td><td>2</td><td>2</td></tr>
<tr><td>41</td><td>-0.300</td><td>0.300</td><td>7.100</td><td>49.500</td><td>44.617</td><td>49.500</td><td>5.040</td><td>100.000</td><td>0</td><td>2</td><td>2</td></tr>
<tr><td>42</td><td>-0.600</td><td>0.600</td><td>7.100</td><td>48.524</td><td>39.857</td><td>46.547</td><td>5.040</td><td>100.000</td><td>0</td><td>2</td><td>2</td></tr>
</table>

20


---



# Appendix D. Sample Internal Centrifuge Experimental Profile Output File

For the simulation of centrifuge experiments using internal Gz profiles, the standard output format is similar to the custom output but more compact. The Gz profile results are summarized by times and G levels of the tracked effects: time to G-LOC, time to return to consciousness from absolute incapacitation, time at the onset of visual symptoms, time at blackout, G onset rate, G at the return to consciousness, G at unconsciousness, G at blackout, and G at the beginning of visual symptoms. The final column is the lowest balance in the life bank. The sample below (in courier font text) is for an average resistance female pilot subjected to the series of 27 different experimental profiles of constant change in acceleration described in subsection "The simulation series" on p. 15.

```
Parameters:
 Brain-heart dist, G0, min flow, no-flow awake(s)
   27.59683          1.000000             19.00000             7.100000
 max G,            F0,    max flow, Eye-heart dist
   11.00000          49.50000             110.0000             32.51156
 Subject height, sex, time@Gmax, no-flow alive(s)
   191.0000                    0 female  1.000000            180.0000
 Units for distances are cm
 Units for flows are dl/min
 Units for acceleration are G
 Units for times are seconds
 Max suit presure  0.0000000E+00 psi
 Flow needed to avoid eventual death       9.000000           s
 Heart response time constant (ms):      3000.000
 Rampdown rate for thus run:  0.0000000E+00
```

<table>
<thead>
<tr>
<th>T-GLOC</th>
<th>T-RECON</th>
<th>T-GREY</th>
<th>T-BLACK</th>
<th>dGz/dt</th>
<th>Gz@C</th>
<th>Gz@U</th>
<th>Gz@B</th>
<th>Gz@G</th>
<th>minLife</th>
</tr>
</thead>
<tbody>
<tr>
<td>648.804</td>
<td>47.503</td>
<td>413.567</td>
<td>498.794</td>
<td>0.010</td>
<td>7.013</td>
<td>7.488</td>
<td>5.988</td>
<td>5.136</td>
<td>155.509</td>
</tr>
<tr>
<td>328.347</td>
<td>40.300</td>
<td>212.221</td>
<td>254.431</td>
<td>0.020</td>
<td>6.761</td>
<td>7.567</td>
<td>6.089</td>
<td>5.244</td>
<td>157.158</td>
</tr>
<tr>
<td>221.265</td>
<td>37.577</td>
<td>144.221</td>
<td>172.137</td>
<td>0.030</td>
<td>6.511</td>
<td>7.638</td>
<td>6.164</td>
<td>5.327</td>
<td>157.835</td>
</tr>
<tr>
<td>167.724</td>
<td>35.495</td>
<td>109.878</td>
<td>130.661</td>
<td>0.040</td>
<td>6.289</td>
<td>7.709</td>
<td>6.226</td>
<td>5.395</td>
<td>157.995</td>
</tr>
<tr>
<td>135.599</td>
<td>33.841</td>
<td>89.094</td>
<td>105.608</td>
<td>0.050</td>
<td>6.088</td>
<td>7.780</td>
<td>6.280</td>
<td>5.455</td>
<td>157.875</td>
</tr>
<tr>
<td>114.183</td>
<td>32.411</td>
<td>75.134</td>
<td>88.847</td>
<td>0.060</td>
<td>5.906</td>
<td>7.851</td>
<td>6.331</td>
<td>5.508</td>
<td>157.850</td>
</tr>
<tr>
<td>98.885</td>
<td>31.126</td>
<td>65.121</td>
<td>76.875</td>
<td>0.070</td>
<td>5.743</td>
<td>7.922</td>
<td>6.381</td>
<td>5.558</td>
<td>158.008</td>
</tr>
<tr>
<td>87.412</td>
<td>29.989</td>
<td>57.611</td>
<td>67.895</td>
<td>0.080</td>
<td>5.594</td>
<td>7.993</td>
<td>6.432</td>
<td>5.609</td>
<td>158.216</td>
</tr>
<tr>
<td>78.488</td>
<td>28.978</td>
<td>51.770</td>
<td>60.911</td>
<td>0.090</td>
<td>5.456</td>
<td>8.064</td>
<td>6.482</td>
<td>5.659</td>
<td>158.446</td>
</tr>
<tr>
<td>71.350</td>
<td>28.077</td>
<td>47.097</td>
<td>55.324</td>
<td>0.100</td>
<td>5.327</td>
<td>8.135</td>
<td>6.532</td>
<td>5.710</td>
<td>158.676</td>
</tr>
<tr>
<td>39.225</td>
<td>22.579</td>
<td>22.810</td>
<td>28.354</td>
<td>0.200</td>
<td>4.329</td>
<td>8.845</td>
<td>6.671</td>
<td>5.562</td>
<td>160.485</td>
</tr>
<tr>
<td>25.754</td>
<td>17.309</td>
<td>15.394</td>
<td>18.745</td>
<td>0.300</td>
<td>3.533</td>
<td>8.726</td>
<td>6.623</td>
<td>5.618</td>
<td>163.818</td>
</tr>
</tbody>
</table>

21


---



<table>
<tr>
<td>20.011</td>
<td>15.317</td>
<td>12.229</td>
<td>14.677</td>
<td>0.400</td>
<td>2.878</td>
<td>9.004</td>
<td>6.871</td>
<td>5.892</td>
<td>164.737</td>
</tr>
<tr>
<td>16.932</td>
<td>14.350</td>
<td>10.471</td>
<td>12.415</td>
<td>0.500</td>
<td>2.291</td>
<td>9.466</td>
<td>7.207</td>
<td>6.235</td>
<td>165.092</td>
</tr>
<tr>
<td>15.005</td>
<td>13.801</td>
<td>9.358</td>
<td>10.972</td>
<td>0.600</td>
<td>1.723</td>
<td>10.003</td>
<td>7.583</td>
<td>6.615</td>
<td>165.256</td>
</tr>
<tr>
<td>13.685</td>
<td>13.458</td>
<td>8.598</td>
<td>9.974</td>
<td>0.700</td>
<td>1.159</td>
<td>10.580</td>
<td>7.982</td>
<td>7.019</td>
<td>165.339</td>
</tr>
<tr>
<td>12.724</td>
<td>12.990</td>
<td>8.050</td>
<td>9.246</td>
<td>0.800</td>
<td>1.000</td>
<td>11.000</td>
<td>8.397</td>
<td>7.440</td>
<td>165.581</td>
</tr>
<tr>
<td>11.996</td>
<td>12.106</td>
<td>7.639</td>
<td>8.695</td>
<td>0.900</td>
<td>1.000</td>
<td>11.000</td>
<td>8.826</td>
<td>7.875</td>
<td>166.191</td>
</tr>
<tr>
<td>11.426</td>
<td>11.387</td>
<td>7.321</td>
<td>8.265</td>
<td>1.000</td>
<td>1.000</td>
<td>11.000</td>
<td>9.265</td>
<td>8.321</td>
<td>166.688</td>
</tr>
<tr>
<td>9.034</td>
<td>8.008</td>
<td>6.036</td>
<td>6.478</td>
<td>2.000</td>
<td>1.000</td>
<td>11.000</td>
<td>11.000</td>
<td>11.000</td>
<td>169.061</td>
</tr>
<tr>
<td>8.325</td>
<td>6.805</td>
<td>5.670</td>
<td>5.953</td>
<td>3.000</td>
<td>1.000</td>
<td>11.000</td>
<td>11.000</td>
<td>11.000</td>
<td>169.918</td>
</tr>
<tr>
<td>7.992</td>
<td>6.181</td>
<td>5.499</td>
<td>5.707</td>
<td>4.000</td>
<td>1.000</td>
<td>11.000</td>
<td>11.000</td>
<td>11.000</td>
<td>170.367</td>
</tr>
<tr>
<td>7.800</td>
<td>5.794</td>
<td>5.401</td>
<td>5.565</td>
<td>5.000</td>
<td>1.000</td>
<td>11.000</td>
<td>11.000</td>
<td>11.000</td>
<td>170.646</td>
</tr>
<tr>
<td>7.676</td>
<td>5.534</td>
<td>5.338</td>
<td>5.472</td>
<td>6.000</td>
<td>1.000</td>
<td>11.000</td>
<td>11.000</td>
<td>11.000</td>
<td>170.834</td>
</tr>
<tr>
<td>7.589</td>
<td>5.344</td>
<td>5.293</td>
<td>5.408</td>
<td>7.000</td>
<td>1.000</td>
<td>11.000</td>
<td>11.000</td>
<td>11.000</td>
<td>170.971</td>
</tr>
<tr>
<td>7.525</td>
<td>5.199</td>
<td>5.260</td>
<td>5.360</td>
<td>8.000</td>
<td>1.000</td>
<td>11.000</td>
<td>11.000</td>
<td>11.000</td>
<td>171.076</td>
</tr>
<tr>
<td>7.476</td>
<td>5.086</td>
<td>5.235</td>
<td>5.323</td>
<td>9.000</td>
<td>1.000</td>
<td>11.000</td>
<td>11.000</td>
<td>11.000</td>
<td>171.157</td>
</tr>
</table>

22
