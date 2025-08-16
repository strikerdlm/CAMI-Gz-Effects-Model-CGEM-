

DOT/FAA/AM-23/6
Office of Aerospace Medicine
Washington, DC 20591

[Federal Aviation Administration logo]

# Cerebral Blood Flow Based Computer Modeling of Gz-Induced Effects

Kyle Copeland  
James E. Whinnery

Civil Aerospace Medical Institute (CAMI)  
Federal Aviation Administration  
Oklahoma City, OK 73169

January 2023


---


# NOTICE

This document is disseminated under the sponsorship of the U.S. Department of Transportation in the interest of information exchange. The United States Government assumes no liability for the contents thereof.

----

This publication and all Office of Aerospace Medicine technical reports are available in full-text from the Civil Aerospace Medical Institute's publications website (www.faa.gov/go/oamtechreports) and at the National Transportation Library's Repository & Open Science Access Portal (https://rosap.ntl.bts.gov/)

---



# Technical Report Documentation Page

<table>
<tr>
<td>1. Report No.<br>DOT/FAA/AM-23/6</td>
<td>2. Government Accession No.</td>
<td>3. Recipient's Catalog No.</td>
</tr>
<tr>
<td>4. Title and Subtitle<br>Cerebral Blood Flow Based Computer Modeling of Gz-Induced Effects</td>
<td colspan="2">5. Report Date<br>January 24, 2023</td>
</tr>
<tr>
<td colspan="3">6. Performing Organization Code</td>
</tr>
<tr>
<td>7. Author(s)<br>K. Copeland; J. E. Whinnery (Ret.)</td>
<td colspan="2">8. Performing Organization Report No.<br>DOT/FAA/AM-23/6</td>
</tr>
<tr>
<td>9. Performing Organization Name and Address<br>Civil Aerospace Medical Institute (CAMI)<br>Federal Aviation Administration<br>Oklahoma City, OK 73169</td>
<td colspan="2">10. Work Unit No. (TRAIS) NA?<br><br>11. Contract or Grant No.<br>NA</td>
</tr>
<tr>
<td>12. Sponsoring Agency Name and Address<br>Office of Aerospace Medicine<br>Federal Aviation Administration<br>800 Independence Ave., S.W.<br>Washington, DC 20591</td>
<td colspan="2">13. Type of Report and Period Covered<br>Technical Report<br><br>14. Sponsoring Agency Code</td>
</tr>
<tr>
<td colspan="3">15. Supplementary Notes<br>This report contains the accepted-for-publication version of a manuscript that will appear with the same authors and title in a future issue of the journal Aerospace Medicine and Human Performance. All additional content, such as this form, was added to meet Office of Aviation Medicine report publishing requirements.<br>Author ORCIDs: K. Copeland (0000-0002-8480-3614), Whinnery (NA)<br>Technical report DOI: https://doi.org/10.21949/1524446</td>
</tr>
<tr>
<td colspan="3">16. Abstract<br><br>Introduction: There is continued interest in acceleration (G) effects in civil aviation, as G-induced loss of consciousness (G-LOC), impaired consciousness, and visual effects play a role in aerobatic, agricultural, and military aviation accidents. Methods: A software model (the Civil Aerospace Medical Institute G-Effects Model [CGEM]) based on physical and physiological variables related to inflight tissue resupply, using oxygen flow as a proxy for supply availability, was developed to evaluate risk of G-LOC and related phenomena in aeronauts. Aeronauts were modeled using several parameters, including sex, cardiovascular fitness, and other common modifiers such as G-suits, positive pressure breathing gear, anti-G straining and other muscle-tensing. The software was validated by comparison with experimental data from the peer-reviewed literature. Results: CGEM predicted physiological effects of Gz exposure accurately, particularly for rapid onset rates. Predicted times to G-LOC and absolute incapacitation periods were consistently within one standard deviation of pooled results obtained during centrifuge experiments using USN and USAF pilots. Predictions of G tolerance based on visual effects onset also compared well with published data, as did evaluation of symptoms expected during a difficult aerobatic maneuver. Discussion: CGEM is a new tool for civil and military aviation. Rather than providing a simple G tolerance number, through proper selection of parameters flight surgeons, pilots, and accident investigators can gain insight into changes in risk from factors such fatigue, medications, dehydration, and anti-G countermeasures used.</td>
</tr>
<tr>
<td>17. Key Word<br>acceleration, aerobatics, G-LOC, G-tolerance, modeling</td>
<td colspan="2">18. Distribution Statement<br>Document is available to the public through the National Transportation Library: https://ntl.bts.gov/ntl</td>
</tr>
<tr>
<td>19. Security Classif. (of this report)<br>Unclassified</td>
<td>20. Security Classif. (of this page)<br>Unclassified</td>
<td>21. No. of Pages<br>18</td>
<td>22. Price<br>NA</td>
</tr>
</table>

Form DOT F 1700.7 (8-72)        Reproduction of completed page authorized


---


# Acknowledgements

The authors thank Richard Greenhaw, Ph.D., Research Mathematician at CAMI, for providing guidance on statistical methods. Thanks also are due to former Aerospace Medical Research Division Manager at CAMI, Estrella Forster, Ph.D., for encouraging the development of the model and to Paul Rogers, Ph.D. for discussions regarding the software design and early draft manuscript contents. Finally, thanks to those at CAMI who provided thorough reviews, in particular Susan Jay, Ph.D., Team Lead, Human Physiology Research Team, Stacey Zinke-McKee, Manager of the Protection and Survival Laboratory, and Anthony Tvaryanas, M.D., Ph.D., Aerospace Medical Research Division Manager.

The work described in this report was funded by the FAA Office of Aerospace Medicine and was performed at the FAA Civil Aerospace Medical Institute as Aerospace Medical Research Task 2017-AAM-631-NUM-10123. The FAA has chosen not to patent the software and will release it to the public through the National Transportation Library with the following DOIs: Software User's Guide doi.org/10.21949/1524438; Software doi.org/10.21949/1524439. The authors have no conflicts of interest to declare.

ii


---


# Table of Contents

Acknowledgements......................................................................................................................... ii

Table of Contents........................................................................................................................... iii

List of Abbreviations ..................................................................................................................... iv

Abstract/Executive Summary…...................................................................................................... 1

Introduction..................................................................................................................................... 2

Methods……………....................................................................................................................... 3

Results............................................................................................................................................. 5

Discussion..................................................................................................................................... 10

References..................................................................................................................................... 11

iii


---


# List of Abbreviations

<table>
<thead>
<tr>
<th>Term</th>
<th>Definition</th>
</tr>
</thead>
<tbody>
<tr>
<td>AGSM</td>
<td>anti-G straining maneuver</td>
</tr>
<tr>
<td>CAMI</td>
<td>Civil Aerospace Medical Institute</td>
</tr>
<tr>
<td>CGEM</td>
<td>CAMI G-Effects Model</td>
</tr>
<tr>
<td>G-LOC</td>
<td>G force-induced loss of consciousness</td>
</tr>
<tr>
<td>ITP</td>
<td>intrathoracic pressure</td>
</tr>
<tr>
<td>PBG</td>
<td>positive pressure breathing gear</td>
</tr>
<tr>
<td>USAF</td>
<td>United States Air Force</td>
</tr>
<tr>
<td>USN</td>
<td>United States Navy</td>
</tr>
</tbody>
</table>

iv


---


# Abstract/Executive Summary

**Introduction:** There is continued interest in acceleration (G) effects in civil aviation, as G-induced loss of consciousness (G-LOC), impaired consciousness, and visual effects play a role in aerobatic, agricultural, and military aviation accidents. **Methods:** A software model (the Civil Aerospace Medical Institute G-Effects Model [CGEM]) based on physical and physiological variables related to inflight tissue resupply, using oxygen flow as a proxy for supply availability, was developed to evaluate risk of G-LOC and related phenomena in aeronauts. Aeronauts were modeled using several parameters, including sex, cardiovascular fitness, and other common modifiers such as G-suits, positive pressure breathing gear, anti-G straining and other muscle-tensing. The software was validated by comparison with experimental data from the peer-reviewed literature. **Results:** CGEM predicted physiological effects of Gz exposure accurately, particularly for rapid onset rates. Predicted times to G-LOC and absolute incapacitation periods were consistently within one standard deviation of pooled results obtained during centrifuge experiments using USN and USAF pilots. Predictions of G tolerance based on visual effects onset also compared well with published data, as did evaluation of symptoms expected during a difficult aerobatic maneuver. **Discussion:** CGEM is a new tool for civil and military aviation. Rather than providing a simple G tolerance number, through proper selection of parameters flight surgeons, pilots, and accident investigators can gain insight into changes in risk from factors such fatigue, medications, dehydration, and anti-G countermeasures used.

1


---


# Introduction

Aircraft maneuvers involving large accelerations (called G forces, because they feel like changes in gravity from the pilot's perspective) can result in pilot unconsciousness, a condition commonly referred to as G force-induced loss of consciousness (G-LOC). Typically, total incapacitation from G-LOC lasts for several seconds, although it can last longer than 30 seconds.<sup>13</sup> G-LOC is thought to result from inadequate flow of resources such as oxygen (i.e., hypoxia) at the consciousness maintaining centers of the brain.<sup>10</sup> It occurs in untrained healthy individuals at exposures as low as +2 Gz (i.e., upward acceleration equivalent to double the normal force of gravity at the Earth's surface).

In very high positive Gz onset situations, there are no reported precursor symptoms to G-LOC. With sufficiently slow onset of positive Gz, there are precursor symptoms: loss of peripheral vision called *gray out*, then loss of all vision referred to as *black out*. These symptoms can be alleviated if positive Gz is reduced or resistance to G-LOC, called *G-tolerance*, is increased. There may also be a measureable reduction in cognitive function called *A-LOC*. Factors known to reduce G-tolerance include hypotension, hypoglycemia, illness, dehydration, exposure to alcohol, and fatigue. G-tolerance can be improved from the naïve state by frequent exposure to high Gz, practice of anti-G straining maneuver (AGSM) exercises, and protective equipment such as a well-fitted G-suit.

Exposure to negative Gz for more than a few seconds is considered more dangerous than exposure to positive Gz. Negative Gz exposure induces a slowing of the heart rate and peripheral vasodilation in an attempt to lower intracranial pressure and restore proper cerebral blood flow as blood and spinal fluid begin to pool in the head. Symptoms include nausea and a visual symptom called *red-out* followed by G-LOC. Exposure to negative Gz also can reduce tolerance to positive Gz maneuvering (i.e., the "push-pull effect"). There are no known effective countermeasures to negative Gz exposure. Thus, combat maneuvers avoid large or prolonged negative Gz exposures. More lengthy reviews of Gz effects can be found in Kirkam et al.<sup>8</sup> and many other sources.

An aging population of civilian pilots perform aerobatic maneuvers during agricultural (e.g., crop dusting) and entertainment (e.g., air show) flights. These pilots typically do not wear protective equipment such as a G-suit, sometimes experience unsustainably high negative Gz for short periods as part of their routines, and may take non-disqualifying cardiovascular medications that could alter G-tolerance. While the military has developed computer models such as Burton's<sup>2</sup> for estimating G-tolerance and some symptoms, such software is not readily available as a civilian research tool. Thus, new software for estimating times of onset and recovery for G-induced effects based on pilot physiology, deployed countermeasures, and flight maneuvers was developed at the Federal Aviation Administration's Civil Aerospace Medical Institute (CAMI) in Oklahoma City, OK, as a safety tool for flight surgeons, pilots, and accident investigators. The remainder of this report describes the CAMI G-Effects Model software, hereafter called *CGEM*, and its validation.

2


---


## Methods

### Procedures

CGEM calculates Gz effects based on resource flow and use in affected organs. Blood flow and oxygenation levels serve as a proxy for general resource movement. The resource flow model uses flow rates (F) at sites above the heart based on local perfusion pressures (P<sub>P</sub>), vascular resistance, and fractional blood oxygenation (O) (limited to 100%)<sup>10</sup> (Eq. 1),

$$F = O * (P_P) / R,$$
(1)

where P<sub>P</sub> is calculated from Gz, the heart level mean arterial pressure (P<sub>H</sub>), the change in elevation from the heart to the site (H), intraocular or intracranial pressure (P<sub>I</sub>), and the change in arterial pressure per unit change in elevation (dP/dH, at -0.7333 mmHg/cm) with (Eq. 2),

$$P_P = P_H + H * dP/dH * G - P_I.$$
(2)

Vascular resistance is allowed to vary between a normal value of 1.6 mmHg/dl/min and a minimum of 0.4 mmHg/dl/min as the body attempts to autonomically maintain normal blood flow (or more) at the center-of-consciousness level. P<sub>H</sub> is set to resting level and allowed to ramp up to maximum levels as a function of time after Gz exceeds 1.4 G as described by equation 3,

$$P_H = P_{H\_rest} + P_{H\_increase} * (1.0 - exp(- t/B))$$
(3)

where P<sub>H_increase</sub> is the difference between the maximum allowed valued of P<sub>H</sub> for the participant and the resting value, and B is a time constant resulting in maximum value of P<sub>H</sub> in 14-20 seconds for most participants.<sup>11</sup> Once the Gz drops below 1.4 G, P<sub>H</sub> immediately returns to resting levels. This change in P<sub>H</sub> is not used for negative Gz since response mechanisms can suppress heart rate and attempt to decrease pressure. To model the push-pull effect, time spent in negative Gz up to 5 seconds is introduced as a delay in response in correcting P<sub>H</sub> for following positive Gz stress. Heart level blood pressure is not allowed to drop below the normal baseline.

Based on the user-indicated Gz exposure, participant physiology (a pre-defined high, low, or average resistance male or female within the range for normal humans, or completely user-defined), and other parameters, CGEM manipulates and monitors cell resource reserve banks. Two banks track the resource level of the consciousness center of the brain: a consciousness bank and a brain tissue death bank (life bank). Two additional banks track retinal state: a bank for onset of visual symptoms such as gray (or red) out and peripheral light loss and a bank for retinal black

3


---


out. The balance of each bank is based on the amount of fully oxygenated blood at the minimum flow rate needed to maintain that state of operation based on experimental data. Each bank has a maximum allowed balance equal to the balance maintained during the normal resting state. In the consciousness related banks, blood flow refills the life bank and keeps it full, with extra flow used to refill and maintain the consciousness bank. The two retinal banks are separate measures of the balance of the retinal bank at the peripheral and most central visual regions.

## Subjects

Basic assertions and assumptions about modeled aeronauts, experimental participants, etc., include:

* All organ distance measurements in relaxed participants under normal gravity are scaled to anthropomorphic phantoms.<sup>6</sup>

* The center of consciousness in the brain is located halfway between the base of the brain and the center of mass of the eye.

* Cells normally have a reserve of oxygen and other needed resources which acts as an incapacitation buffer if resupply is suddenly interrupted.<sup>2,14</sup>

* Blood oxygenation deficit is an indicator of blood usefulness to tissues.

* The reserve bank must be fully refilled before function resumes.

* Non-functioning cells survive at least 180 seconds in a reversible state of reduced resource use.<sup>12</sup>

* Assuming full oxygenation, a cerebral blood flow rate of 18-20 dl/min will maintain consciousness.<sup>12</sup>

* Assuming full oxygenation, 20% (9 dl/min in CGEM) of normal cerebral blood flow will maintain cell life.<sup>12</sup>

* Blood oxygenation can be reduced by high positive and negative Gz due to lost lung capacity (from lung and surrounding tissue deformation).

* Negative Gz is similar enough with respect to G-LOC that it can be treated the same as positive Gz with respect to the modeled physiological effects.<sup>8</sup>

* Countermeasures for +Gz effects are not effective for increasing negative Gz tolerance.

* Each experiment or flight simulation begins with exposure at +1 Gz, equivalent to level flight or sitting in a centrifuge.

* Cerebral blood flow is a function of mean arterial pressure and vascular resistance.<sup>12</sup>

* Normal intracranial pressure is 9 mmHg (natural range is 5-13 mmHg).<sup>12</sup>

* Normal intraocular pressure is 22 mmHg (natural range is extremely variable).<sup>11</sup>

4


---


• When the seat back is not vertical, relative vertical distances are adjusted only below the level of the cortical cervical spine.

• Hyperthermia and dehydration affect G-tolerance through changes in cardiovascular function.<sup>5</sup>

Protective G-suit effects are modeled in two ways: a rise in intrathoracic pressure (ITP) and an elevation of the heart. The net effect of G-suit inflation is assumed to be up to 6 mmHg/psi at heart level depending on body coverage of the suit (6 mmHg/psi at >70% coverage, 3 mmHg/psi at 35% coverage, and a linear interpolation for other values). When the G-suit is inflated, the heart elevation rises by 6mm/psi. Inflation is limited to 12 psi.

An anti-G straining maneuver (AGSM) may be used with or without a G-suit. The maximum effectiveness of an AGSM is limited to an ITP increase of 130 mmHg, while the assumed rise in P<sub>H</sub> per mmHg of ITP is 0.75 mmHg.<sup>1</sup> If ITP increases from both AGSM and G-suit are present, CGEM uses the higher of the two values.

Even prolonged tight gripping an object can increase arterial pressure. The user may specify non-AGSM straining either as constant pressure used throughout a simulation or as a linearly increasing pressure from a user-defined level to a user-defined maximum, limited to 60 mmHg, in 30 seconds. If an AGSM is also specified, CGEM uses the greater of the two pressure increases.

Users may designate a maximum pressure for positive pressure breathing gear (PBG) up to 60 mmHg ITP. This gear significantly increases +Gz resistance without AGSM and increases the time a pilot can sustain AGSM during high +Gz exposures before significant muscle fatigue occurs.

## Statistical Analysis

Non-linear regressions and associated confidence and prediction intervals used for validation of the results were calculated using Sigmaplot14 (Systat Software, Inc.). Values of R<sup>2</sup> for regressions and CGEM results were calculated using the method preferred by Kåvlseth for non-linear models.<sup>7</sup>

## Results

As expected, effects on G tolerance differed for rapid and gradual onset rates and varied greatly with parameter values. For instance, CGEM predicted G tolerances of 7.1 G and 7.5 G, respectively, for an average resistance male participant while performing an AGSM. Adding a brief cardiac response delay of 3 seconds (e.g., from a beta blocking blood pressure control medication) lowered the rapid onset tolerance to 6.0 G with no effect on gradual onset tolerance. The effect of mild dehydration or mild hyperthermia on blood pressure lowered rapid and gradual onset G-tolerances in each case by 0.1 G. Combining the effects of mild dehydration with mild hyperthermia lowered G-tolerances a bit more: to 6.8 G and 7.2 G, respectively. Allowing fatigue to reduce AGSM effectiveness by 50% dramatically lowered G-tolerance to 5.8 G and 6.1 G, respectively, while adding fatigue to mild dehydration and mild hyperthermia lowered G-tolerances to 5.5 G and 5.8 G, respectively.

5


---


To investigate validity, experimental G-exposure profiles from published studies were modeled and resulting calculated G effects were compared with the experimental data. Studies used in the validation included those with and without countermeasures. Several aerobatic maneuvers were also programmed based on Gz profiles measured in flight.<sup>8</sup> For these, model-generated expected symptoms for the six different standard participants were compared with anecdotal pilot experiences.

Figure 1 shows CGEM results as well as pooled experimental G-LOC data of Figure 2 of Whinnery and Forster.<sup>13</sup> The data set is of 729 initially relaxed predominantly male USN and USAF participants. CGEM results are shown for the three different resistance standard male participants with no anti-G countermeasures, an experimental acceleration limit of 9.4 G, and a 10° posterior seat tilt. The average resistance male participant is consistently within a standard deviation of the pooled results and CGEM reproduces the range of participant responses extremely well.

CGEM results for duration of absolute incapacitation (time needed to return to consciousness after G-LOC) were verified using the data of Whinnery et al.<sup>14</sup> For these experiments, participants were accelerated to unconsciousness, held for 1 second at the Gz at which unconsciousness occurred and then decelerated using the negative of the acceleration rate to unconsciousness. CGEM results are shown with the experimental data in Figure 2. Data are from Table 2 of the reference and represent pooled results from 715 predominantly male participants. CGEM results are shown for the three different resistance standard male participants with no anti-G countermeasures, an experimental acceleration limit of 9.4 G, and a 10° posterior seat tilt. CGEM reproduces the experimental data extremely well.

Cochran et al.<sup>3</sup> studied peripheral light loss, gray out, black out, and unconsciousness following rapid G-onsets to plateaus in steps of 0.5 Gz (n=1000). Once the beginning of visual symptoms was found for each participant, the experimenters used 0.3 Gz steps to develop response curves for each participant and averaged the curves. Experimenters noted participants were not completely relaxed in that they were instructed to use joysticks to signal visual symptoms and found that results varied widely among participants. The participant 50<sup>th</sup> percentile results for these endpoints were 3.9, 4.8, and 5.3 Gz, respectively. The participant means were 4.1 (standard deviation [sd] 0.7), 4.7 (sd 0.8), and 5.4 (sd 0.9) Gz. CGEM results calculated using the average resistance male and applying a 15 mmHg maximum increase due to muscle tension after 30 seconds (to approximate the slightly unrelaxed state reported by the experimenters) are 4.0 Gz for the onset of visual symptoms, 4.9 Gz for black out, and 5.4 Gz for unconsciousness, in excellent agreement (much less than 1 sd) with the data.

6


---



<table>
<thead>
<tr>
<th>Acceleration onset rate (G/s)</th>
<th>USAF + USN pooled data - Time to loss of consciousness (s)</th>
<th>CGEM low resistance male (s)</th>
<th>CGEM average resistance male (s)</th>
<th>CGEM high resistance male (s)</th>
</tr>
</thead>
<tbody>
<tr>
<td>0.05</td>
<td>95 ± 5</td>
<td>95</td>
<td>90</td>
<td>85</td>
</tr>
<tr>
<td>0.1</td>
<td>85 ± 10</td>
<td>75</td>
<td>70</td>
<td>65</td>
</tr>
<tr>
<td>0.2</td>
<td>70 ± 15</td>
<td>45</td>
<td>40</td>
<td>35</td>
</tr>
<tr>
<td>0.5</td>
<td>20 ± 5</td>
<td>18</td>
<td>15</td>
<td>12</td>
</tr>
<tr>
<td>1.0</td>
<td>12 ± 3</td>
<td>10</td>
<td>8</td>
<td>6</td>
</tr>
<tr>
<td>2.0</td>
<td>9 ± 2</td>
<td>7</td>
<td>6</td>
<td>4</td>
</tr>
<tr>
<td>5.0</td>
<td>8 ± 3</td>
<td>5</td>
<td>4</td>
<td>3</td>
</tr>
<tr>
<td>10.0</td>
<td>9 ± 4</td>
<td>4</td>
<td>3</td>
<td>2</td>
</tr>
</tbody>
</table>

**Figure 1.** Time to loss of consciousness induction relative to acceleration onset rate in relaxed participants. Data are pooled experimental results from Whinnery and Forster.<sup>13</sup> Error bars shown are standard deviations. The three CGEM curves are for high, low, and average resistance physiology standard male participants, with no anti-G countermeasures.

7


---



<table>
<thead>
<tr>
<th>Acceleration offset rate (G/s)</th>
<th>Whinnery et al., 2014 (Duration of absolute incapacitation)</th>
<th>CGEM low resistance male</th>
<th>CGEM average resistance male</th>
<th>CGEM high resistance male</th>
</tr>
</thead>
<tbody>
<tr>
<td>0.2</td>
<td>13.6</td>
<td>19.8</td>
<td>13.6</td>
<td>10.8</td>
</tr>
<tr>
<td>0.4</td>
<td>12.5</td>
<td>13.2</td>
<td>10.4</td>
<td>10.6</td>
</tr>
<tr>
<td>0.6</td>
<td>10.3</td>
<td>11.8</td>
<td>9.8</td>
<td>10.4</td>
</tr>
<tr>
<td>0.8</td>
<td>8.6</td>
<td>10.8</td>
<td>9.4</td>
<td>10.2</td>
</tr>
<tr>
<td>1.0</td>
<td>7.7</td>
<td>10.0</td>
<td>9.0</td>
<td>10.0</td>
</tr>
<tr>
<td>1.2</td>
<td></td>
<td>9.4</td>
<td>8.7</td>
<td>9.8</td>
</tr>
<tr>
<td>1.4</td>
<td></td>
<td>8.9</td>
<td>8.4</td>
<td>9.6</td>
</tr>
<tr>
<td>1.6</td>
<td></td>
<td>8.5</td>
<td>8.1</td>
<td>9.4</td>
</tr>
<tr>
<td>1.8</td>
<td></td>
<td>8.1</td>
<td>7.8</td>
<td>9.2</td>
</tr>
<tr>
<td>2.0</td>
<td></td>
<td>7.8</td>
<td>7.6</td>
<td>9.0</td>
</tr>
</tbody>
</table>

**Figure 2.** Duration of absolute incapacitation in relaxed participants. Data are pooled experimental results from Whinnery et al.<sup>14</sup> Error bars shown are standard deviations. The third point, with the largest error bars, is the average for the whole data set (n=715). The three CGEM curves are for high, low, and average resistance physiology standard male participants, with no anti-G countermeasures.

Burton summarized the results of several anti-G countermeasures experiments as part of the verification of his pressure-based model.<sup>2</sup> Burton's summarized experimental data and CGEM results calculated using variables listed in Burton's summary are shown in Table 1. The CGEM participant is the average resistance male in a 12° posterior seat tilt and height adjusted to match the 350 mm heart-eye distance used by Burton. The rapid onset tolerance endpoint is 0.1 Gz below the point of black out within 15 seconds after ramp-up at 10 Gz/s. The experiments

8


---



**Table I.** Measured<sup>*</sup> and calculated<sup>†</sup> effectiveness of common anti-G countermeasures, assuming a 12° seat tilt.

<table>
<thead>
<tr>
<th>Countermeasure</th>
<th colspan="2">Gradual onset tolerance, +Gz</th>
<th colspan="2">Rapid onset tolerance, +Gz</th>
</tr>
<tr>
<th></th>
<th>Measured</th>
<th>CGEM</th>
<th>Measured</th>
<th>CGEM</th>
</tr>
</thead>
<tbody>
<tr>
<td>Gripping<sup>‡</sup></td>
<td>5.6</td>
<td>4.8</td>
<td>4.5</td>
<td>4.0</td>
</tr>
<tr>
<td>G-suit<sup>§</sup></td>
<td>4.7, 5.7, 5.9, 6.9</td>
<td>5.3, 5.6, 5.7, 5.9</td>
<td>4.7, 5.0, 5.9</td>
<td>5.2, 5.3, 5.5</td>
</tr>
<tr>
<td>G-suit<sup>¶</sup></td>
<td>6.7</td>
<td>6.8</td>
<td>5.6</td>
<td>6.8</td>
</tr>
<tr>
<td>G-suit<sup>**</sup> + gripping <sup>‡</sup></td>
<td>6.2</td>
<td>6.3</td>
<td>5.4</td>
<td>5.1</td>
</tr>
<tr>
<td>AGSM</td>
<td>---</td>
<td>7.2</td>
<td>---</td>
<td>6.8</td>
</tr>
<tr>
<td>G-suit<sup>††</sup> + AGSM</td>
<td>---</td>
<td>9.2, 9.5</td>
<td>9.0, 10.7</td>
<td>8.6, 8.9</td>
</tr>
<tr>
<td>G-suit<sup>‡‡</sup> + PBG</td>
<td>---</td>
<td>8.7, 10.2</td>
<td>7.8, 8.8</td>
<td>8.5, 9.9</td>
</tr>
<tr>
<td>G-suit<sup>§§</sup> + AGSM +PBG</td>
<td>---</td>
<td>10.6</td>
<td>11.0</td>
<td>10.4</td>
</tr>
</tbody>
</table>

<sup>*</sup> Data are as summarized by Burton.<sup>2</sup>

<sup>†</sup> Calculations are for average resistance male participant with height altered to match data source by requiring a 350 mm heart-eye distance when standing.

<sup>‡</sup> CGEM tensing effect set at 15 mmHg from pre-exposure tensing sustained during onset.<sup>2</sup>

<sup>§</sup> For gradual onset, inflations were limited to 4.1, 5.6, 6.0, and 7.5 psi, respectively. For rapid onset, suit inflations used were 4.1, 4.5, and 5.9 psi, respectively.

<sup>¶</sup> Larger coverage suit, >50%, 5.3 psi.

<sup>**</sup> For gradual onset suit inflated to 5.1 psi, for rapid onset inflation limited to 6.3 psi.

<sup>††</sup> Suit inflations of 10 and 12 psi.

<sup>‡‡</sup> Gradual onset suit inflation of 10.7 psi and rapid onset suit inflation of 9.5 psi, each with suits of 30% and 70% coverage.

<sup>§§</sup> Suit inflation 12 psi.

summarized by Burton did not use exactly matching criteria (e.g., plateau times vary from 10 s to 15 s and G-tolerance measures are not completely consistent), so direct comparisons of experimental data variables and CGEM selected variables are not appropriate. Another significant uncertainty in some CGEM calculations was how much arterial pressure to add from gripping. While muscle tension from gripping has little influence on rapid onset G-tolerance, gradual onset G-tolerances can shift considerably. For instance, Burton's model used a constant 15 mmHg, while up to 50 mmHg is easily possible according to Quarry and Spodic.<sup>2,9</sup> GCEM results reported in Table I use Burton's value of 15 mmHg. Using Quarry and Spodic's value of 50 mmHg, CGEM calculates a gradual onset gripping-only G-tolerance of 5.9 G, a gradual onset gripping-with-suit G-tolerance of 7.5 G, a rapid onset gripping-only G-tolerance of 4.4 G, and a rapid onset gripping-with-suit G-tolerance of 5.7 G.

Eiken et al.<sup>4</sup> examined anti-G countermeasures in a systematic fashion to evaluate component relative effectiveness. They examined G-suits, AGSM, and PBG, relative to relaxed conditions in experienced Swedish Gripen fighter pilots (n=10). G-exposure was limited to 9 Gz and full peripheral light loss was used as the indication of maximum tolerance. Table II summarizes the Eiken et al.<sup>4</sup> experimental results along with corresponding CGEM calculations for average resistance male participant physiology, adjusted to use the experiment reported average participant

9


---



<table>
<thead>
<tr>
<th colspan="4">Table II. Comparison of CGEM calculations with Eiken et al.<sup>4</sup> experimental findings.</th>
</tr>
<tr>
<th rowspan="2">Countermeasure</th>
<th colspan="3">Measured tolerance, +Gz</th>
<th rowspan="2">GCEM model tolerance, +Gz*</th>
</tr>
<tr>
<th>Mean</th>
<th>Range</th>
<th>S.D.</th>
</tr>
</thead>
<tbody>
<tr>
<td>None</td>
<td>3.4</td>
<td>2.8-4.3</td>
<td>0.5</td>
<td>4.2</td>
</tr>
<tr>
<td>G-suit<sup>†</sup></td>
<td>6.5</td>
<td>4.5-9.0+</td>
<td>1.2</td>
<td>6.5</td>
</tr>
<tr>
<td>G-suit+PBG<sup>‡</sup></td>
<td>8.0</td>
<td>6.5-9.0+</td>
<td>0.8</td>
<td>8.4</td>
</tr>
<tr>
<td>G-suit+AGSM<sup>§</sup></td>
<td>8.9</td>
<td>8.5-9.0+</td>
<td>0.2</td>
<td>9.0+</td>
</tr>
<tr>
<td>G-suit+AGSM+PBG</td>
<td>9.0+</td>
<td>8.5-9.0+</td>
<td>0.1</td>
<td>9.0+</td>
</tr>
</tbody>
</table>

\* Average of G calculated for beginning of visual symptoms and black out was used as an estimate of complete peripheral light loss. Average resistance participant physiology used except for height of 181 cm, matching the experimental cohort.

<sup>†</sup> G-suit (max. of 10 psi at 9 G)

<sup>‡</sup> Pressure breathing gear (ramped to 50 mmHg at 9 G)

<sup>§</sup> Anti-G straining maneuver (calculations assume 130 mmHg increase in ITP)

height of 181 cm. CGEM calculations are within the range of reported for the experimental data and close to the mean values. The only point more than 1 sd from the experimental mean value is the datum for no countermeasures.

Kirkham et al.<sup>8</sup> report measurements of G-forces during demonstration aerobatic flights by an expert pilot, as well as pilot reports on symptoms during maneuvers. The most physiologically challenging maneuver is an outside-inside vertical eight maneuver. Pilots report the 7-9 o'clock portion (29-32 s into the maneuver) of the inside loop as the most likely to result in G-LOC. This portion occurs a few seconds after the time of peak Gz and immediately follows a rapid shift from large negative to large positive Gz. CGEM calculations indicate male and female average resistance pilots experience black out 29.4 s and 30.0 s into the maneuver, respectively, and come close to G-LOC while low resistance pilots experience black out at 27.0 s and 27.1 s, respectively, then G-LOC at 27.5 s and 28.3 s, respectively, when Gz is near its maximum.

## Discussion

CGEM reproduces a wide range of experimental results for participants with and without using anti-G countermeasures with very high accuracy. Calculations for all experimental endpoints modeled are within the experimental range of participant responses and are almost always within one standard deviation of pooled experimental results, indicating the simple cell function assumptions used in CGEM are adequate for this kind of modeling. The underestimation of the time to loss of consciousness when compared with the data at very low onset rates suggests a completely relaxed participant may not be an accurate assumption. At low onset rates vascular pressure increases from muscle tension such as gripping controls may increase time to G-LOC. For example, CGEM predicts G-LOC in 54 s for an initially relaxed average-resistance male participant exposed to the gradual onset rate of 0.080 G/s. If, after passing 1.4 Gz, initially relaxed participants are allowed to increase the non-AGSM related muscle strain effect to a realistic physical maximum of 60 mmHg in 30 s, calculated time to G-LOC increases to 80 s, a gain of 26 s.

10


---


Results for duration of absolute incapacitation are consistent with experimental results and the assertion that prolonged loss of blood flow results in longer times to recovery made by Ryoo et al.<sup>10</sup>

Flow tracking allows CGEM to incorporate factors such as dehydration and medications that can influence heart rate and blood pressure, factors that are neither present nor applicable to curve-fitting models such as that of Whinnery et al.<sup>14</sup>

Possible future additions to CGEM include countermeasure equipment failure, an improved lung function model to account for larger seat tilt angles towards supine or prone positions, profiles for standard aerobatic maneuvers, changes in physiology with age, and the effects of dehydration and fatigue on pilot performance beyond adjusting the current input parameters. Finally, brain tissue deformation is currently unaccounted for by the model, and blood flow in different brain function centers could be tracked, improving insight into observed functional impairment associated with A-LOC and following G-LOC.

# References

1. Buick F, Hartley J, Pecaric M. Maximum intra-thoracic pressure with PBG and AGSM. In: AGARD, eds. High altitude and high acceleration protection for military aircrew. Neuille-sur-Seine, France: NATO-AGARD; 1991. Report No: AGARD-CP-516, Oct 7.1–7.9.

2. Burton RR. Mathematical models for predicting G-level tolerances. Aviat, Space, and Environ Med. 2000; 71:506–513.

3. Cochran LB, Gard PW, Norsworthy ME. Variations in human G tolerance to positive acceleration. Pensacola, FL: U.S. Naval School of Aviation Medicine; 1954. Report No: NM 001 059.02.10.

4. Eiken O, Ölgård R, Bergsten E, Grönkvist M. G protection: interaction of straining maneuvers and positive pressure breathing. Aviat, Space, and Environ Med. 2007; 78:392–398.

5. González-Alonso J, Mora-Rodriguez R, Below PR, Coyle EF. Dehydration markedly impairs cardiovascular function in hyperthermic endurance athletes during exercise. J App Physiol. 1997; 82(4), 1229–36.

6. International Commission on Radiological Protection. Adult reference computational phantoms. ICRP Publication 110. Ann ICRP. 2009; 39(2).

7. Kåvlseth TO. Note on the R2 measure of goodness of fit for nonlinear models. Bulletin of the Psychonomic Society, 1983; 21(1), 79–80.

8. Kirkam WR, Wicks SM, Lowrey DL. G incapacitation in aerobatic pilots: an aerobatic hazard. Springfield, VA, USA: National Technical Information Service; 1982. Report No: FAA-AM-82-13.

11


---


9. Quarry VM, Spodic DH. Cardiac responses to isometric exercise: comparative effects of different postures and different levels of exertion. Circulation. 1974; 49:905–920.

10. Ryoo HC, Sun HH, Shender BS, Hrebien L. Consciousness monitoring using near-infrared spectroscopy (NIRS) during high +Gz exposures. Med and Eng Phys. 2004; 26:745–753.

11. Tipton DA. The Effects of Gx, Gy, and Gz forces on cone mesopic vision. Springfield, VA, USA: National Technical Information Service; 1983. Report No: AFAMRL-TR-83-047.

12. Walters FJM. Intracranial pressure and cerebral blood flow. Update in Anaesthesia. 1998; 8:18–23.

13. Whinnery T, Forster EM. The +Gz-induced loss of consciousness curve. Extreme Physiol and Med. 2013; 2:19.

14. Whinnery T, Forster EM, Rogers PB. The +Gz recovery of consciousness curve. Extreme Physiol and Med. 2014; 3:9.

12
