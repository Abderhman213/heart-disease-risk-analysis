"""Heart Disease Risk Analysis - UCI (Cleveland, Hungary, Switzerland, VA Long Beach). 920 patients."""
import pandas as pd, numpy as np, sqlite3, json
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold, train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, roc_curve, confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

cols = ["age","sex","cp","trestbps","chol","fbs","restecg","thalach","exang","oldpeak","slope","ca","thal","num"]
sites = {"cleveland":"Cleveland (USA)","hungarian":"Hungary","switzerland":"Switzerland","va":"VA Long Beach (USA)"}
frames=[]
for k,v in sites.items():
    d = pd.read_csv(f"raw/processed.{k}.data", header=None, names=cols, na_values="?")
    d["site"]=v; frames.append(d)
raw = pd.concat(frames, ignore_index=True)
raw.to_csv("data/heart_raw_combined.csv", index=False)

df = raw.copy()
quality = {"rows":len(df), "missing_by_col":df.isna().sum().to_dict(), "duplicates":int(df.duplicated().sum())}
# Cleaning: chol==0 and trestbps==0 are impossible -> NaN
quality["chol_zero"]=int((df.chol==0).sum()); quality["bp_zero"]=int((df.trestbps==0).sum())
df.loc[df.chol==0,"chol"]=np.nan; df.loc[df.trestbps==0,"trestbps"]=np.nan
df["disease"]=(df.num>0).astype(int)
df["sex_l"]=df.sex.map({1:"Male",0:"Female"})
df["cp_l"]=df.cp.map({1:"Typical angina",2:"Atypical angina",3:"Non-anginal pain",4:"Asymptomatic"})
df["exang_l"]=df.exang.map({1:"Yes",0:"No"})
df["age_group"]=pd.cut(df.age,[0,39,49,59,69,120],labels=["<40","40-49","50-59","60-69","70+"])
df["chol_cat"]=pd.cut(df.chol,[0,200,240,1000],labels=["Desirable (<200)","Borderline (200-239)","High (240+)"])
df["bp_cat"]=pd.cut(df.trestbps,[0,120,140,300],labels=["Normal (<120)","Elevated (120-139)","High (140+)"])
df["hr_cat"]=pd.cut(df.thalach,[0,120,150,250],labels=["<120","120-149","150+"])
df.to_csv("data/heart_clean.csv", index=False)

# SQL layer
con = sqlite3.connect("data/heart.db"); df.astype({"age_group":str,"chol_cat":str,"bp_cat":str,"hr_cat":str}).to_sql("patients",con,if_exists="replace",index=False)
Q = {
"overview":"SELECT COUNT(*) patients, ROUND(AVG(disease)*100,1) prevalence_pct, ROUND(AVG(age),1) avg_age, ROUND(AVG(chol),0) avg_chol FROM patients",
"by_site":"SELECT site, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients GROUP BY site ORDER BY prevalence_pct DESC",
"by_sex":"SELECT sex_l, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients GROUP BY sex_l",
"by_age":"SELECT age_group, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients GROUP BY age_group ORDER BY age_group",
"by_cp":"SELECT cp_l, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients GROUP BY cp_l ORDER BY prevalence_pct DESC",
"by_exang":"SELECT exang_l, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients WHERE exang_l IS NOT NULL GROUP BY exang_l",
"by_chol":"SELECT chol_cat, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients WHERE chol_cat!='nan' GROUP BY chol_cat",
"by_bp":"SELECT bp_cat, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients WHERE bp_cat!='nan' GROUP BY bp_cat",
"by_hr":"SELECT hr_cat, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients WHERE hr_cat!='nan' GROUP BY hr_cat",
"severity":"SELECT num severity, COUNT(*) n FROM patients GROUP BY num ORDER BY num",
"sex_x_age":"SELECT age_group, sex_l, COUNT(*) n, ROUND(AVG(disease)*100,1) prevalence_pct FROM patients GROUP BY age_group, sex_l ORDER BY age_group, sex_l",
}
res = {k: pd.read_sql(q,con).to_dict("records") for k,q in Q.items()}
open("src/queries.sql","w").write("\n\n".join(f"-- {k}\n{q};" for k,q in Q.items()))

# Stats tests
st={}
for c in ["age","trestbps","chol","thalach","oldpeak"]:
    a=df[df.disease==1][c].dropna(); b=df[df.disease==0][c].dropna()
    t,p=stats.mannwhitneyu(a,b); st[c]={"mean_disease":round(a.mean(),1),"mean_healthy":round(b.mean(),1),"p":float(p)}
for c in ["sex","cp","exang","fbs"]:
    ct=pd.crosstab(df[c],df.disease); chi,p,_,_=stats.chi2_contingency(ct); st[c]={"chi2":round(chi,1),"p":float(p)}
# Odds ratio male vs female
ct=pd.crosstab(df.sex,df.disease); orr=(ct.loc[1,1]*ct.loc[0,0])/(ct.loc[1,0]*ct.loc[0,1])
st["sex_odds_ratio"]=round(float(orr),2)

# Modeling
feat=["age","sex","cp","trestbps","chol","fbs","restecg","thalach","exang","oldpeak"]
X=df[feat]; y=df.disease
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.25,random_state=42,stratify=y)
lr=make_pipeline(SimpleImputer(strategy="median"),StandardScaler(),LogisticRegression(max_iter=1000))
rf=make_pipeline(SimpleImputer(strategy="median"),RandomForestClassifier(n_estimators=400,random_state=42,min_samples_leaf=3))
cv=StratifiedKFold(5,shuffle=True,random_state=42)
model={}
for n,m in [("Logistic Regression",lr),("Random Forest",rf)]:
    cvauc=cross_val_score(m,X,y,cv=cv,scoring="roc_auc"); m.fit(Xtr,ytr); pr=m.predict_proba(Xte)[:,1]
    fpr,tpr,_=roc_curve(yte,pr)
    model[n]={"cv_auc":round(cvauc.mean(),3),"test_auc":round(roc_auc_score(yte,pr),3),"test_acc":round(accuracy_score(yte,pr>0.5),3),
              "roc":[[round(a,3),round(b,3)] for a,b in zip(fpr[::max(1,len(fpr)//40)],tpr[::max(1,len(tpr)//40)])],
              "cm":confusion_matrix(yte,pr>0.5).tolist()}
rf.fit(X,y); imp=rf[-1].feature_importances_
names={"age":"Age","sex":"Sex","cp":"Chest pain type","trestbps":"Resting BP","chol":"Cholesterol","fbs":"Fasting sugar","restecg":"Rest ECG","thalach":"Max heart rate","exang":"Exercise angina","oldpeak":"ST depression"}
model["importance"]=sorted([{"feature":names[f],"value":round(float(v),3)} for f,v in zip(feat,imp)],key=lambda x:-x["value"])

# scatter sample for dashboard
sc=df[["age","thalach","disease","sex_l"]].dropna().round(0).to_dict("records")
out={"quality":quality,"sql":res,"stats":st,"model":model,"scatter":sc,
     "kpi":{"patients":len(df),"prevalence":round(df.disease.mean()*100,1),"avg_age":round(df.age.mean(),1),"male_pct":round((df.sex==1).mean()*100,1),
            "avg_chol":round(df.chol.mean()),"avg_hr":round(df.thalach.mean())}}
json.dump(out,open("outputs/results.json","w"),indent=1,default=str)
print(json.dumps({k:v for k,v in out.items() if k not in("scatter",)},indent=1,default=str)[:6000])
