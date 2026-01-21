from flask import Flask, request, jsonify, render_template 
from services.predictor import predict_transaction 
from services.data_service import save_transaction
from services.metrics_service import (
    get_kpis,
    fraud_vs_non_fraud,
    fraud_by_network,
    fraud_by_transaction_type,
    transactions_over_time,
)


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        input_data = request.get_json()

        if not input_data:
            return jsonify({"error": "No input data provided"}), 400

        # 1️⃣ Run ML prediction
        result = predict_transaction(input_data)

        # 2️⃣ Save to CSV
        save_transaction(input_data, result)

        # 3️⃣ Return result
        return jsonify(result)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/dashboard-data", methods=["GET"])
def dashboard_data():
    try:
        data = {
            "kpis": get_kpis(),
            "fraud_vs_non_fraud": fraud_vs_non_fraud(),
            "fraud_by_network": fraud_by_network(),
            "fraud_by_transaction_type": fraud_by_transaction_type(),
            "transactions_over_time": transactions_over_time(freq="D"),
        }

        return jsonify(data)

    except Exception as e:
        print("❌ Dashboard error:", e)
        return jsonify({"error": "Failed to load dashboard data"}), 500

    

if __name__ == "__main__":
    app.run(debug=True)