## Variables Currently Modeled by CGEM:

### **Primary Physiological Parameters:**
- Sex (male/female with different physiological profiles)
- Height and anthropometric scaling
- Resting and maximum blood pressure (systolic/diastolic)
- Heart rate response time constants
- Cardiovascular fitness levels (high/average/low resistance)
- Cerebral blood flow parameters
- Seat tilt angle effects

### **Countermeasures Modeled:**
- Anti-G suits (pressure, coverage percentage)
- Anti-G straining maneuvers (AGSM effectiveness)
- Positive pressure breathing gear (PBG)
- Muscle tensing/gripping effects
- Combined countermeasure interactions

### **Limited Modeling of:**
- **Dehydration** - through cardiovascular parameter changes
- **Mild hyperthermia** - through blood pressure effects
- **Medications** - basic cardiac response delays (e.g., beta-blockers)
- **Fatigue** - reduced AGSM effectiveness only

---

## Critical Variables NOT Fully Modeled by CGEM:

### **1. Sleep & Circadian Factors (HIGH PRIORITY)**
- **Sleep duration and quality** - insufficient sleep significantly reduces G-tolerance
- **Sleep debt/accumulated fatigue** - multiple days of poor sleep compound effects
- **Time of day/circadian rhythm** - G-tolerance varies throughout 24-hour cycle
- **Shift work effects** - irregular sleep patterns from flight schedules

### **2. Autonomic Nervous System (HIGH PRIORITY)**
- **Heart Rate Variability (HRV)** - strong predictor of G-tolerance, reflects stress/recovery
- **Stress levels** - acute and chronic stress reduce performance
- **Autonomic balance** - sympathetic vs parasympathetic activity

### **3. Metabolic & Biochemical (HIGH PRIORITY)**
- **Blood glucose levels** - hypoglycemia significantly reduces G-tolerance
- **Hydration status** - detailed fluid balance vs simple dehydration modeling
- **Electrolyte balance** - sodium, potassium levels affect cardiovascular function
- **Hormonal status** - cortisol, adrenaline, thyroid hormones

### **4. Respiratory Factors (MEDIUM-HIGH PRIORITY)**
- **Hyperventilation** - reduces G-tolerance by ~0.6G
- **CO2 levels** - arterial carbon dioxide affects tolerance
- **Breathing patterns** - controlled breathing can improve HRV and tolerance
- **Oxygen saturation** - hypoxia reduces tolerance significantly

### **5. Environmental Stressors (MEDIUM PRIORITY)**
- **Core body temperature** - 1°C rise reduces tolerance by 30-40%
- **Ambient temperature extremes** - cockpit heat/cold stress
- **Noise exposure** - chronic noise affects stress and sleep
- **Vibration exposure** - additional physiological stress
- **Altitude/hypoxia** - reduces tolerance by ~0.5G at 10,000ft equivalent

### **6. Cognitive & Psychological (MEDIUM PRIORITY)**
- **Mental workload** - high cognitive demands reduce tolerance
- **Attention/focus state** - concentration affects muscle tension and breathing
- **Anxiety levels** - acute anxiety can impair performance
- **Motivation/arousal** - optimal performance requires proper arousal level

### **7. Physical Condition (MEDIUM PRIORITY)**
- **Recent illness/infection** - active infections reduce tolerance
- **Training recency** - "G lay-off" after 2-4 weeks significantly reduces tolerance
- **Physical fitness specificity** - isometric vs aerobic training have different effects
- **Muscle fatigue state** - pre-existing fatigue affects AGSM performance

### **8. Substance Effects (MEDIUM PRIORITY)**
- **Alcohol consumption** - specific dose-response relationships (110ml whisky = -0.1 to -0.4G)
- **Caffeine** - can affect HRV and stress response
- **Nicotine** - affects cardiovascular function
- **Prescription medications** - beyond simple cardiac delays

### **9. Unusual Physiological States (LOWER PRIORITY)**
- **Stomach distension** - full stomach can increase tolerance by 0.6-1.3G
- **Motion sickness susceptibility** - affects tolerance
- **Vestibular function** - inner ear health impacts G-tolerance
- **Individual genetic variations** - inherent physiological differences

### **10. Operational Factors (LOWER PRIORITY)**
- **G-transition effects** - complex push-pull maneuver sequences
- **Mission duration** - cumulative fatigue during long flights
- **Pre-flight preparation time** - rushed vs prepared states
- **Post-flight recovery** - effects on subsequent missions

---

## **Highest Priority Missing Variables for Implementation:**

1. **Sleep Quality/Duration Monitoring** - Single biggest performance factor
2. **Heart Rate Variability** - Real-time autonomic status indicator  
3. **Blood Glucose Levels** - Significant, measurable impact
4. **Core Body Temperature** - Large quantifiable effect
5. **Stress/Cortisol Levels** - Affects multiple physiological systems
6. **Training Recency** - "G lay-off" has major operational implications

### Variables for survey

Based on the research findings and your existing Colombian Aerospace Forces variables, here's a comprehensive survey list for pilot G-tolerance prediction and model enhancement:

**Pilot Demographics & Experience:**
- Identification number
- Age
- Sex
- Height (cm)
- Weight (kg)
- Military unit
- Current aircraft type
- Total flight hours (all aircraft)
- Current flight hours in current aircraft
- Hours flown in the last two weeks
- Hours flown in the last month
- Years of military flight experience
- Number of different aircraft types flown
- Days since last G-exposure flight
- Average G-exposures per month in current role

**G-Force Experience History:**
- How many episodes of grey out has had in the past year
- How many episodes of blackout has had in the past year
- How many episodes of GLOC has had in the past year
- Most recent grey out episode (days ago)
- Most recent blackout episode (days ago)
- Most recent GLOC episode (days ago)
- Highest G-force experienced in career
- Typical maximum G-force in current aircraft operations

**Sleep & Fatigue Assessment:**
- Average sleep hours per night over past week
- Sleep quality rating (1-10) over past week
- Number of nights with <6 hours sleep in past week
- Time of last sleep before current flight
- Hours of sleep before current flight
- Number of duty days without adequate rest in past month
- Frequency of shift changes per month
- Time zone changes in past two weeks

**Physical Health & Fitness:**
- Current resting heart rate (if known)
- Current blood pressure (if known/recent medical)
- Exercise frequency per week
- Primary exercise type (aerobic/strength/mixed)
- Hours of physical exercise per week
- Body fat percentage (if known)
- Any cardiovascular medications (Y/N)
- Any blood pressure medications (Y/N)
- Current illness or infection (Y/N)
- Days since last illness

**Physiological Status (Day of Survey):**
- Hours since last meal
- Hours since last caffeine consumption
- Cups of coffee/caffeine drinks in past 24 hours
- Glasses of water consumed today
- Alcohol consumption in past 24 hours (units)
- Alcohol consumption in past week (units)
- Current stress level (1-10 scale)
- Energy level right now (1-10 scale)
- Current body temperature (if measurable)
- Any medication taken in past 24 hours

**Environmental & Operational Factors:**
- Altitude of current base operations
- Average cockpit temperature during flights (hot/comfortable/cold)
- Noise exposure hours per week (high engine/equipment noise)
- Vibration exposure hours per week
- Mission type frequency (combat/training/transport percentages)
- G-suit availability and usage frequency
- Anti-G training recency (weeks since last training)
- Breathing technique training level (none/basic/advanced)

**Lifestyle & Behavioral Factors:**
- Smoking status (never/former/current)
- If current smoker: cigarettes per day
- Dietary pattern (regular meals/irregular/skip meals)
- Hydration habits (excellent/good/fair/poor)
- Supplement usage (vitamins, performance enhancers)
- Mental stress sources (family/financial/work scale 1-10)
- Relaxation/meditation practices (frequency)
- Time off from flying duties in past month

**Performance & Symptoms:**
- Self-rated G-tolerance compared to peers (much lower/lower/average/higher/much higher)
- Typical warning signs before grey out (vision/dizziness/other)
- Recovery time after high-G maneuvers (seconds)
- Frequency of post-flight fatigue (never/rarely/sometimes/often/always)
- Frequency of headaches after high-G flights
- Any vision changes noted after G-exposure
- Concentration difficulties after high-G flights
- Physical symptoms during high-G (nausea/muscle fatigue/breathing difficulty)

**Training & Countermeasures:**
- Anti-G straining maneuver proficiency (1-10 self-rating)
- Breathing control technique proficiency (1-10 self-rating)
- G-suit fit quality (poor/adequate/excellent)
- Frequency of G-suit use when available
- Muscle tensing/gripping techniques used
- Pre-flight preparation routine consistency
- Physical conditioning focus (general/G-specific/none)

**Psychological Factors:**
- Confidence level during high-G maneuvers (1-10)
- Anxiety level before high-G flights (1-10)
- Motivation level for current duties (1-10)
- Job satisfaction rating (1-10)
- Mental workload during typical flights (1-10)
- Attention/focus ability during high-G (1-10)
- Risk tolerance personality (conservative/moderate/aggressive)