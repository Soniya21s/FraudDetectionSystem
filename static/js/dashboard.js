document.addEventListener("DOMContentLoaded", function () {

    async function loadDashboardData() {
        try {
            const response = await fetch("/dashboard-data");
            const data = await response.json();

            if (!response.ok) {
                console.error("Failed to load dashboard data");
                return;
            }

            updateKPIs(data.kpis);
            renderFraudPie(data.fraud_vs_non_fraud);
            renderFraudByNetwork(data.fraud_by_network);
            renderTransactionsOverTime(data.transactions_over_time);
            renderFraudByType(data.fraud_by_transaction_type);

        } catch (error) {
            console.error("Dashboard error:", error);
        }
    }

    /* ==============================
       KPI CARDS
    ================================ */

    function updateKPIs(kpis) {
        document.getElementById("kpi-total").innerText = kpis.total_transactions;
        document.getElementById("kpi-fraud").innerText = kpis.fraud_transactions;
        document.getElementById("kpi-rate").innerText = kpis.fraud_rate + "%";
    }

    /* ==============================
       FRAUD VS NON-FRAUD (PIE)
    ================================ */

    function renderFraudPie(data) {
        new Chart(document.getElementById("fraudPieChart"), {
            type: "doughnut",
            data: {
                labels: ["Fraud", "Non-Fraud"],
                datasets: [{
                    data: [data.fraud, data.non_fraud],
                    backgroundColor: ["#EF4444", "#22C55E"]
                }]
            }
        });
    }

    /* ==============================
       FRAUD BY NETWORK (BAR)
    ================================ */

    function renderFraudByNetwork(data) {
        new Chart(document.getElementById("fraudNetworkChart"), {
            type: "bar",
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: "Fraud Count",
                    data: Object.values(data),
                    backgroundColor: "#2563EB"
                }]
            },
            options: {
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    /* ==============================
       TRANSACTIONS OVER TIME (LINE)
    ================================ */

    function renderTransactionsOverTime(data) {
        new Chart(document.getElementById("transactionsTimeChart"), {
            type: "line",
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: "Transactions",
                    data: Object.values(data),
                    borderColor: "#2563EB",
                    fill: false,
                    tension: 0.3
                }]
            }
        });
    }

    /* ==============================
       FRAUD BY TRANSACTION TYPE (BAR)
    ================================ */

    function renderFraudByType(data) {
        new Chart(document.getElementById("fraudTypeChart"), {
            type: "bar",
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: "Fraud Count",
                    data: Object.values(data),
                    backgroundColor: "#0F172A"
                }]
            },
            options: {
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // Initial load
    loadDashboardData();
});