# Rebuild this dashboard in Power BI

Source file: `data/heart_clean.csv` (920 rows). Get Data → Text/CSV → Transform Data → check types, then Close & Apply.

## DAX measures
```
Patients        = COUNTROWS(heart_clean)
Disease Cases   = CALCULATE([Patients], heart_clean[disease] = 1)
Disease Rate %  = DIVIDE([Disease Cases], [Patients])
Avg Age         = AVERAGE(heart_clean[age])
Male Share %    = DIVIDE(CALCULATE([Patients], heart_clean[sex_l]="Male"), [Patients])
Avg Cholesterol = AVERAGE(heart_clean[chol])
Avg Max HR      = AVERAGE(heart_clean[thalach])
```
## Layout (16:9, dark navy slicer panel on the left, gradient banner on top)
| Visual | Fields |
|---|---|
| 6 KPI cards | measures above |
| Donut | Legend: disease label, Values: Patients |
| Clustered column | Axis: age_group, Legend: sex_l, Values: Disease Rate % |
| Column | Axis: num, Values: Patients |
| Bar | Axis: cp_l, Values: Disease Rate % (sort desc) |
| Line | Axis: hr_cat, Values: Disease Rate % |
| Column | Axis: exang_l, Values: Disease Rate % |
| Scatter | X: age, Y: thalach, Legend: disease |
| Bar | Axis: site, Values: Disease Rate % |
| Slicers | site, sex_l |

## Theme
Red `#EF4444` (disease), Teal `#14B8A6` (healthy), Violet `#7C3AED`, Pink `#EC4899`, Navy `#0F172A`, background `#F1F5F9`.
Rounded white cards: Format → Effects → Visual border → Rounded corners 16px, Shadow on.
Set Disease Rate % to Percentage with 1 decimal. Add the data caveat as a text box (hospital referral differences, 172 zero-cholesterol values treated as missing).
