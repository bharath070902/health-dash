import pandas as pd
from datetime import datetime

patients_df = pd.read_csv("./output/csv/patients.csv")
conditions_df = pd.read_csv("./output/csv/conditions.csv")
medications_df = pd.read_csv("./output/csv/medications.csv")
encounters_df = pd.read_csv("./output/csv/encounters.csv")
organizations_df = pd.read_csv("./output/csv/organizations.csv")
immunizations_df = pd.read_csv("./output/csv/immunizations.csv")

patients_df["BIRTHDATE"] = pd.to_datetime(patients_df["BIRTHDATE"], errors="coerce")
patients_df["AGE"] = pd.to_datetime('today').year - patients_df['BIRTHDATE'].dt.year
encounters_df["START"] = pd.to_datetime(encounters_df["START"], errors="coerce")
medications_df["START"] = pd.to_datetime(medications_df["START"], errors="coerce").dt.tz_localize(None)
organizations_df["NAME"] = organizations_df["NAME"].str.replace(r"\s+", " ", regex=True)



def format_time_ago(td):
    td = pd.Timestamp(datetime.now()) - td
    seconds = td.total_seconds()
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours ago"
    else:
        return f"{int(seconds // 86400)} days ago"

def get_organizations():
    organizations = organizations_df["NAME"].unique().tolist()

    return organizations


def get_dashboard(organization):
    organization_id = organizations_df.loc[organizations_df["NAME"] == organization, "Id"].iloc[0]

    filtered_encounters = encounters_df[encounters_df["ORGANIZATION"] == organization_id]
    patient_ids = filtered_encounters["PATIENT"].unique()
    filtered_patients = patients_df[patients_df["Id"].isin(patient_ids)]
    total_encounters = filtered_encounters.shape[0]

    total_patients = len(patient_ids)

    filtered_conditions = conditions_df[conditions_df["PATIENT"].isin(patient_ids)]
    disorder_conditions = filtered_conditions[filtered_conditions["DESCRIPTION"].str.endswith("(disorder)", na=False)]

    most_common_condition = (
        disorder_conditions["DESCRIPTION"].value_counts().idxmax()
        if not filtered_conditions.empty
        else "No Data"
    )

    filtered_patients["AGE"] = pd.to_datetime('today').year - filtered_patients["BIRTHDATE"].dt.year
    average_age = filtered_patients["AGE"].mean()

    filtered_medications = medications_df[medications_df["PATIENT"].isin(patient_ids)]
    most_prescribed_medication = (
        filtered_medications["DESCRIPTION"].value_counts().idxmax()
        if not filtered_medications.empty
        else "No Data"
    )

    return {
        "total_patients": total_patients,
        "most_common_condition": most_common_condition.replace(" (disorder)", ""),
        "average_age": round(average_age, 2) if not pd.isna(average_age) else "No Data",
        "most_prescribed_medication": most_prescribed_medication,
        "total_encounters": total_encounters
    }

def get_patient_demographics(organization, age_filter=None, gender_filter=None, condition_filter=None):
    # print(age_filter, gender_filter, condition_filter)
    organization_id = organizations_df.loc[organizations_df["NAME"] == organization, "Id"].iloc[0]
    filtered_encounters = encounters_df[encounters_df["ORGANIZATION"] == organization_id]
    patient_ids = filtered_encounters["PATIENT"].unique()
    filtered_patients = patients_df[patients_df["Id"].isin(patient_ids)]


    if gender_filter and gender_filter != "All":
        genders = {
            "Male": "M", "Female": "F"
        }
        filtered_patients = filtered_patients[filtered_patients["GENDER"] == genders[gender_filter]]


    if age_filter and age_filter != "All Ages":
        age_ranges = {
            "0-18": (0, 18),
            "19-35": (19, 35),
            "36-50": (36, 50),
            "51 ": (51, 100)
        }
        age_min, age_max = age_ranges[age_filter]
        filtered_patients = filtered_patients[(filtered_patients["AGE"] >= age_min) & (filtered_patients["AGE"] <= age_max)]


    if condition_filter and condition_filter != "Loading..." and condition_filter != "All Conditions":
        filtered_conditions = conditions_df[conditions_df["PATIENT"].isin(patient_ids)]
        condition_patients = filtered_conditions[filtered_conditions["DESCRIPTION"] == condition_filter]["PATIENT"].unique()
        filtered_patients = filtered_patients[filtered_patients["Id"].isin(condition_patients)]


    gender_distribution = filtered_patients["GENDER"].value_counts().to_dict()

    age_groups = pd.cut(filtered_patients["AGE"], bins=[0, 18, 35, 50, 65, 100],
                        labels=["0-18", "19-35", "36-50", "51-65", "65+"], include_lowest=True)
    age_distribution = age_groups.value_counts().to_dict()

    top_conditions = (
        conditions_df["DESCRIPTION"]
        .value_counts()
        .head(10)
        .index.tolist()
    )

    return {
        "gender_distribution": gender_distribution,
        "age_distribution": age_distribution,
        "top_conditions": top_conditions
    }

def get_treatments(organization,  time_filter=None, medication_filter=None):
    organization_id = organizations_df.loc[organizations_df["NAME"] == organization, "Id"].iloc[0]
    filtered_encounters = encounters_df[encounters_df["ORGANIZATION"] == organization_id]
    encounter_ids = filtered_encounters["Id"].unique()
    filtered_medications = medications_df[medications_df["ENCOUNTER"].isin(encounter_ids)]

    if time_filter and time_filter != "All Time":
        date_ranges = {
            "Last 30 Days": pd.Timestamp.today() - pd.Timedelta(days=30),
            "Last 6 Months": pd.Timestamp.today() - pd.DateOffset(months=6),
            "Last Year": pd.Timestamp.today() - pd.DateOffset(years=1)
        }
        filtered_medications = filtered_medications[filtered_medications["START"] >= date_ranges[time_filter]]

    if medication_filter and medication_filter != "All Medications":
        filtered_medications = filtered_medications[filtered_medications["DESCRIPTION"] == medication_filter]

    top_medications = (
        filtered_medications["DESCRIPTION"]
        .value_counts()
        .head(10)
        .to_dict()
    )

    total_prescriptions = filtered_medications.shape[0]

    active_treatments = filtered_medications[filtered_medications["STOP"].isna()].shape[0]

    unique_medications = filtered_medications["DESCRIPTION"].nunique()

    return {
        "top_medications": top_medications,
        "total_prescriptions": total_prescriptions,
        "active_treatments": active_treatments,
        "unique_medications": unique_medications,

    }

def get_trends(organization, region_filter=None, time_filter=None):
    # print("here", region_filter, time_filter)
    print("(", organization.replace(" ", "."), ")")
    organization_id = organizations_df.loc[organizations_df["NAME"] == organization, "Id"].iloc[0]
    print("==================", organization_id)
    filtered_encounters = encounters_df[encounters_df["ORGANIZATION"] == organization_id]
    patient_ids = filtered_encounters["PATIENT"].unique()
    filtered_patients = patients_df[patients_df["Id"].isin(patient_ids)]
    filtered_encounters = filtered_encounters.merge(filtered_patients[["Id", "STATE"]], left_on="PATIENT", right_on="Id", how="left").rename(columns={"Id_x": "Encounter_ID", "Id_y": "Patient_ID"})
    filtered_encounters["START"] = filtered_encounters["START"].dt.tz_localize(None)

    # print(filtered_encounters.head(10))

    deceased_patients = filtered_patients[filtered_patients["DEATHDATE"].notna()]["Id"].unique()
    chronic_conditions = conditions_df[conditions_df["PATIENT"].isin(deceased_patients)]
    chronic_conditions["START"] = pd.to_datetime(chronic_conditions["START"], errors="coerce")
    chronic_conditions["START"] = chronic_conditions["START"].dt.tz_localize(None)

    if region_filter and region_filter != "All Regions":
        filtered_encounters = filtered_encounters[filtered_encounters["STATE"] == region_filter]

    if time_filter and time_filter != "All Time":
        date_ranges = {
            "Last 12 Months": pd.Timestamp.today() - pd.DateOffset(months=12),
            "Last 6 Months": pd.Timestamp.today() - pd.DateOffset(months=6),
            "Last 3 Months": pd.Timestamp.today() - pd.DateOffset(months=3)
        }
        filtered_encounters = filtered_encounters[filtered_encounters["START"] >= date_ranges[time_filter]]
        chronic_conditions = chronic_conditions[chronic_conditions["START"] >= date_ranges[time_filter]]

    encounter_ids = filtered_encounters["Encounter_ID"].unique()
    filtered_immunizations = immunizations_df[immunizations_df["ENCOUNTER"].isin(encounter_ids)]

    # print(filtered_immunizations.head(5))

    immunization_distribution = (
        filtered_immunizations.merge(filtered_encounters[["Encounter_ID", "STATE"]], left_on="ENCOUNTER", right_on="Encounter_ID", how="left")
        .groupby("STATE")["ENCOUNTER"]
        .count()
        .to_dict()
    )

    top_chronic_conditions = (
        chronic_conditions["DESCRIPTION"]
        .value_counts()
        .head(5)
        .to_dict()
    )

    return {
        "immunization_distribution": immunization_distribution,
        "top_chronic_conditions": top_chronic_conditions
    }


def predict_readmission_risk(organization, patient_filter=None, time_filter=None):
    """
    Predicts the risk of patient readmission based on historical data.
    Returns risk scores and contributing factors.
    """
    organization_id = organizations_df.loc[organizations_df["NAME"] == organization, "Id"].iloc[0]
    filtered_encounters = encounters_df[encounters_df["ORGANIZATION"] == organization_id]

    # Get unique patients with their encounter data
    patient_ids = filtered_encounters["PATIENT"].unique()
    patient_encounters = {}

    # Apply time filter if provided
    if time_filter and time_filter != "All Time":
        date_ranges = {
            "Last 30 Days": pd.Timestamp.today() - pd.Timedelta(days=30),
            "Last 6 Months": pd.Timestamp.today() - pd.DateOffset(months=6),
            "Last Year": pd.Timestamp.today() - pd.DateOffset(years=1)
        }
        filtered_encounters = filtered_encounters[filtered_encounters["START"] >= date_ranges[time_filter]]

    # Count encounters per patient to identify frequent visitors
    for patient_id in patient_ids:
        patient_encounters[patient_id] = filtered_encounters[filtered_encounters["PATIENT"] == patient_id].shape[0]

    # Get patient demographics and conditions
    filtered_patients = patients_df[patients_df["Id"].isin(patient_ids)]
    filtered_conditions = conditions_df[conditions_df["PATIENT"].isin(patient_ids)]
    filtered_medications = medications_df[medications_df["PATIENT"].isin(patient_ids)]

    # Calculate readmission risk factors
    risk_factors = {}
    high_risk_patients = []
    medium_risk_patients = []
    low_risk_patients = []

    for patient_id, encounter_count in patient_encounters.items():
        # Get patient age
        patient_age = filtered_patients.loc[filtered_patients["Id"] == patient_id, "AGE"].iloc[0]

        # Get patient conditions
        patient_conditions = filtered_conditions[filtered_conditions["PATIENT"] == patient_id]["DESCRIPTION"].tolist()
        chronic_condition_count = sum(1 for condition in patient_conditions if "disorder" in condition.lower())

        # Get patient medications
        patient_medications = filtered_medications[filtered_medications["PATIENT"] == patient_id]["DESCRIPTION"].nunique()

        # Calculate risk score (simplified algorithm)
        risk_score = 0
        risk_factors[patient_id] = []

        # Factor 1: Frequent visits
        if encounter_count >= 5:
            risk_score += 30
            risk_factors[patient_id].append("Frequent hospital visits")
        elif encounter_count >= 3:
            risk_score += 15
            risk_factors[patient_id].append("Multiple hospital visits")

        # Factor 2: Age risk
        if patient_age >= 65:
            risk_score += 25
            risk_factors[patient_id].append("Elderly patient")
        elif patient_age <= 10:
            risk_score += 15
            risk_factors[patient_id].append("Young patient")

        # Factor 3: Chronic conditions
        if chronic_condition_count >= 3:
            risk_score += 25
            risk_factors[patient_id].append("Multiple chronic conditions")
        elif chronic_condition_count >= 1:
            risk_score += 10
            risk_factors[patient_id].append("Has chronic condition")

        # Factor 4: Multiple medications
        if patient_medications >= 5:
            risk_score += 20
            risk_factors[patient_id].append("Complex medication regimen")
        elif patient_medications >= 3:
            risk_score += 10
            risk_factors[patient_id].append("Multiple medications")

        # Categorize patients by risk
        patient_name = filtered_patients.loc[filtered_patients["Id"] == patient_id, "FIRST"].iloc[0] + " " + \
                      filtered_patients.loc[filtered_patients["Id"] == patient_id, "LAST"].iloc[0]

        patient_data = {
            "id": patient_id,
            "name": patient_name,
            "age": int(patient_age),
            "risk_score": risk_score,
            "risk_factors": risk_factors[patient_id]
        }

        if risk_score >= 60:
            high_risk_patients.append(patient_data)
        elif risk_score >= 30:
            medium_risk_patients.append(patient_data)
        else:
            low_risk_patients.append(patient_data)

    # Sort patients by risk score
    high_risk_patients = sorted(high_risk_patients, key=lambda x: x["risk_score"], reverse=True)[:10]
    medium_risk_patients = sorted(medium_risk_patients, key=lambda x: x["risk_score"], reverse=True)[:10]
    low_risk_patients = sorted(low_risk_patients, key=lambda x: x["risk_score"], reverse=True)[:10]

    # Calculate overall statistics
    total_patients = len(patient_ids)
    high_risk_percentage = round(len(high_risk_patients) / total_patients * 100, 1) if total_patients > 0 else 0
    medium_risk_percentage = round(len(medium_risk_patients) / total_patients * 100, 1) if total_patients > 0 else 0
    low_risk_percentage = round(len(low_risk_patients) / total_patients * 100, 1) if total_patients > 0 else 0

    # Identify most common risk factors
    all_factors = [factor for patient_id in risk_factors for factor in risk_factors[patient_id]]
    factor_counts = {}
    for factor in all_factors:
        if factor in factor_counts:
            factor_counts[factor] += 1
        else:
            factor_counts[factor] = 1

    top_risk_factors = dict(sorted(factor_counts.items(), key=lambda item: item[1], reverse=True)[:5])

    return {
        "high_risk_patients": high_risk_patients,
        "medium_risk_patients": medium_risk_patients,
        "low_risk_patients": low_risk_patients,
        "risk_distribution": {
            "high_risk": high_risk_percentage,
            "medium_risk": medium_risk_percentage,
            "low_risk": low_risk_percentage
        },
        "top_risk_factors": top_risk_factors
    }


organization_id = "HOLLYWOOD CROSS MEDICAL CLINIC"
# dashboard_data = get_dashboard(organization_id)
# print(dashboard_data)
# print(get_trends(organization_id))