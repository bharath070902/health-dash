document.addEventListener("DOMContentLoaded", function () {
    const sections = {
        "Dashboard": document.getElementById("dashboard"),
        "Demographics": document.getElementById("demographics"),
        "Treatments & Medications": document.getElementById("treatments"),
        "Public Health Trends": document.getElementById("trends"),
        "Readmission Predictions": document.getElementById("predictions")
    };

    // console.log(document.getElementById("treatments"));

    function showSection(sectionName) {
        console.log(sectionName);
        Object.values(sections).forEach(section => section.style.display = "none");
        sections[sectionName].style.display = "block";
    }

    document.querySelectorAll(".nav-link").forEach(navItem => {
        navItem.addEventListener("click", function () {
            document.querySelectorAll(".nav-link").forEach(link => link.classList.remove("active"));
            this.classList.add("active");
            showSection(this.textContent.trim());
        });
    });

    document.getElementById("ageFilter").addEventListener("change", loadDemographics);
    document.getElementById("genderFilter").addEventListener("change", loadDemographics);
    document.getElementById("conditionFilter").addEventListener("change", loadDemographics);

    document.getElementById("time-filter").addEventListener("change", loadTreatments);
    document.getElementById("medication-filter").addEventListener("change", loadTreatments);

    document.getElementById("trends-time-filter").addEventListener("change", loadTrends);
    document.getElementById("regions-filter").addEventListener("change", loadTrends);
    document.getElementById("prediction-time-filter").addEventListener("change", loadPredictions);

    showSection("Dashboard");

    loadDashboard();
    loadDemographics();
    loadConditionsFilter();
    loadTreatments();
    loadMedicationsFilter();
    loadTrends();
    loadRegionsFilter();
    loadPredictions();
});

async function loadPredictions() {
    try {
        const timeFilter = document.getElementById("prediction-time-filter").value;

        const response = await fetch(`/api/predictions?time=${timeFilter}`);
        const data = await response.json();

        // Update risk distribution chart
        updateRiskDistributionChart(data.risk_distribution);

        // Update risk factors chart
        updateRiskFactorsChart(data.top_risk_factors);

        // Update high risk patients table
        const highRiskTable = document.getElementById("high-risk-patients-table");
        highRiskTable.innerHTML = "";

        data.high_risk_patients.forEach(patient => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${patient.name}</td>
                <td>${patient.age}</td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="progress flex-grow-1" style="height: 6px;">
                            <div class="progress-bar bg-danger" style="width: ${patient.risk_score}%;"></div>
                        </div>
                        <span class="ms-2">${patient.risk_score}</span>
                    </div>
                </td>
                <td>${patient.risk_factors.join(", ")}</td>
            `;
            highRiskTable.appendChild(row);
        });

        // Update medium risk patients table
        const mediumRiskTable = document.getElementById("medium-risk-patients-table");
        mediumRiskTable.innerHTML = "";

        data.medium_risk_patients.forEach(patient => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${patient.name}</td>
                <td>${patient.age}</td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="progress flex-grow-1" style="height: 6px;">
                            <div class="progress-bar bg-warning" style="width: ${patient.risk_score}%;"></div>
                        </div>
                        <span class="ms-2">${patient.risk_score}</span>
                    </div>
                </td>
                <td>${patient.risk_factors.join(", ")}</td>
            `;
            mediumRiskTable.appendChild(row);
        });

    } catch (error) {
        console.error("Error fetching prediction data:", error);
    }
}

function updateRiskDistributionChart(riskData) {
    const ctx = document.getElementById('risk-distribution-chart').getContext('2d');

    // Check if chart already exists and destroy it
    if (window.riskDistributionChart) {
        window.riskDistributionChart.destroy();
    }

    window.riskDistributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['High Risk', 'Medium Risk', 'Low Risk'],
            datasets: [{
                data: [riskData.high_risk, riskData.medium_risk, riskData.low_risk],
                backgroundColor: ['#dc3545', '#ffc107', '#28a745'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            layout: {
                padding: 10
            }
        }
    });
}

function updateRiskFactorsChart(factorsData) {
    const ctx = document.getElementById('risk-factors-chart').getContext('2d');

    // Check if chart already exists and destroy it
    if (window.riskFactorsChart) {
        window.riskFactorsChart.destroy();
    }

    const labels = Object.keys(factorsData);
    const data = Object.values(factorsData);

    window.riskFactorsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Patients',
                data: data,
                backgroundColor: '#4e73df',
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            },
            layout: {
                padding: 10
            }
        }
    });
}

async function loadConditionsFilter() {
    try {
        const response = await fetch(`/api/demographics`);
        const data = await response.json();
        // console.log(data);

        let conditionFilterElement = document.getElementById("conditionFilter");
        conditionFilterElement.innerHTML = '<option selected>All Conditions</option>';
        data.top_conditions.forEach(condition => {
            let option = document.createElement("option");
            option.textContent = condition;
            option.value = condition;
            conditionFilterElement.appendChild(option);
        });
    } catch (error) {
        console.error("Error fetching dashboard data:", error);
    }
}

async function loadMedicationsFilter() {
    try {
        const response = await fetch(`/api/treatments`);
        const data = await response.json();

        // console.log(data.top_medications);

        let medicationFilterElement = document.getElementById("medication-filter");
        medicationFilterElement.innerHTML = '<option selected>All Medications</option>';
        Object.keys(data.top_medications).forEach(med => {
            let option = document.createElement("option");
            option.textContent = med;
            option.value = med;
            medicationFilterElement.appendChild(option);
        });
    } catch (error) {
        console.error("Error fetching dashboard data:", error);
    }
}

async function loadRegionsFilter() {
    try {
        const response = await fetch(`/api/trends`);
        const data = await response.json();


        console.log(data.immunization_distribution);

        let regionsFilterElement = document.getElementById("regions-filter");
        regionsFilterElement.innerHTML = '<option selected>All Regions</option>';
        Object.keys(data.immunization_distribution).forEach(region => {
            let option = document.createElement("option");
            option.textContent = region;
            option.value = region;
            regionsFilterElement.appendChild(option);
        });
    } catch (error) {
        console.error("Error fetching dashboard data:", error);
    }
}

async function loadDashboard() {
    try {
        const response = await fetch("/api/dashboard");
        const data = await response.json();

        document.getElementById("total-patients").innerText = data.total_patients;
        document.getElementById("most-common-condition").innerText = data.most_common_condition;
        document.getElementById("average-age").innerText = data.average_age + " years";
        document.getElementById("total-encounters").innerText = data.total_encounters;
        document.getElementById("most-prescribed-medication").innerText = data.most_prescribed_medication;
        // console.log(data);
    } catch (error) {
        console.error("Error fetching dashboard data:", error);
    }
}

async function loadDemographics() {
    try {
        const ageFilter = document.getElementById("ageFilter").value;
        const genderFilter = document.getElementById("genderFilter").value;
        const conditionFilter = document.getElementById("conditionFilter").value;

        const response = await fetch(`/api/demographics?age=${ageFilter}&gender=${genderFilter}&condition=${conditionFilter}`);
        const data = await response.json();
        updateDemographicsCharts(data);

        // console.log(data);
    } catch (error) {
        console.error("Error fetching dashboard data:", error);
    }
}

async function loadTreatments() {
    try {
        const timeFilter = document.getElementById("time-filter").value;
        const medicationFilter = document.getElementById("medication-filter").value;

        const response = await fetch(`/api/treatments?time=${timeFilter}&medication=${medicationFilter}`);
        const data = await response.json();

        document.getElementById("total-prescriptions").innerText = data.total_prescriptions;
        document.getElementById("active-treatments").innerText = data.active_treatments;
        document.getElementById("unique-medications").innerText = data.unique_medications;

        updateMedicationChart(data.top_medications);
    } catch (error) {
        console.error("Error fetching treatments data:", error);
    }
}

async function loadTrends() {
    try {
        const timeFilter = document.getElementById("trends-time-filter").value;
        const regionFilter = document.getElementById("regions-filter").value;

        console.log(timeFilter, regionFilter)

        const response = await fetch(`/api/trends?time=${timeFilter}&region=${regionFilter}`);
        const data = await response.json();

        console.log(data);

        updateTrendsCharts(data.immunization_distribution, data.top_chronic_conditions);
    } catch (error) {
        console.error("Error fetching treatments data:", error);
    }
}

function updateDemographicsCharts(data) {
    function generateChart(ctx, data, label) {
        return new Chart(ctx, {
            type: "pie",
            data: {
                labels: Object.keys(data),
                datasets: [{
                    data: Object.values(data),
                    backgroundColor: ["#007bff", "#dc3545", "#ffc107", "#28a745", "#17a2b8"]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        });
    }

    if (window.ageChartInstance) window.ageChartInstance.destroy();
    if (window.genderChartInstance) window.genderChartInstance.destroy();

    window.ageChartInstance = generateChart(document.getElementById("ageChart"), data.age_distribution, "Age Distribution");
    window.genderChartInstance = generateChart(document.getElementById("genderChart"), data.gender_distribution, "Gender Distribution");
}

function updateMedicationChart(medications) {
    const ctx = document.getElementById("medications-chart").getContext("2d");

    if (window.medicationsChartInstance) {
        window.medicationsChartInstance.destroy();
    }

    window.medicationsChartInstance = new Chart(ctx, {
        type: "pie",
        data: {
            labels: Object.keys(medications),
            datasets: [{
                data: Object.values(medications),
                backgroundColor: ["#007bff", "#dc3545", "#ffc107", "#28a745", "#17a2b8", "#6610f2", "#fd7e14", "#20c997", "#6c757d", "#e83e8c"]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    });
}

function updateTrendsCharts(immunization_distribution, top_chronic_conditions) {
    function generateBarChart(ctx, data, label) {
        console.log(data);
        return new Chart(ctx, {
            type: "bar",
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: label,
                    data: Object.values(data),
                    backgroundColor: ["#007bff", "#dc3545", "#ffc107", "#28a745", "#17a2b8"]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    if (window.immunizationChartInstance) window.immunizationChartInstance.destroy();
    if (window.chronicConditionsChartInstance) window.chronicConditionsChartInstance.destroy();

    window.immunizationChartInstance = generateBarChart(
        document.getElementById("vaccination-chart"),
        immunization_distribution,
        "Immunizations per Region"
    );

    window.chronicConditionsChartInstance = generateBarChart(
        document.getElementById("conditions-chart"),
        top_chronic_conditions,
        "Top Chronic Conditions"
    );
}