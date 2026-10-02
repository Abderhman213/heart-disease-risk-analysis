-- overview
SELECT COUNT(*) patients, ROUND(AVG(disease)*100,1) prevalence_pct, ROUND(AVG(age),1) avg_age, ROUND(AVG(chol),0) avg_chol FROM patients;

-- by_site
SELECT site, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients GROUP BY site ORDER BY prevalence_pct DESC;

-- by_sex
SELECT sex_l, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients GROUP BY sex_l;

-- by_age
SELECT age_group, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients GROUP BY age_group ORDER BY age_group;

-- by_cp
SELECT cp_l, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients GROUP BY cp_l ORDER BY prevalence_pct DESC;

-- by_exang
SELECT exang_l, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients WHERE exang_l IS NOT NULL GROUP BY exang_l;

-- by_chol
SELECT chol_cat, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients WHERE chol_cat!='nan' GROUP BY chol_cat;

-- by_bp
SELECT bp_cat, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients WHERE bp_cat!='nan' GROUP BY bp_cat;

-- by_hr
SELECT hr_cat, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients WHERE hr_cat!='nan' GROUP BY hr_cat;

-- severity
SELECT num severity, COUNT(*) n FROM patients GROUP BY num ORDER BY num;

-- sex_x_age
SELECT age_group, sex_l, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients GROUP BY age_group, sex_l ORDER BY age_group, sex_l;