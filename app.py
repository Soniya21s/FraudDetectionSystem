from flask import Flask, request, jsonify, render_template 
from services.predictor import predict_transaction 

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
        # 1️⃣ Get JSON input
        input_data = request.get_json()

        if not input_data:
            return jsonify({"error": "No input data provided"}), 400

        # 2️⃣ Call ML pipeline
        result = predict_transaction(input_data)

        # 3️⃣ Return result
        return jsonify(result)

    except ValueError as e:
        # Input validation / feature issues
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        # Unexpected errors
        return jsonify({"error": "Internal server error"}), 500
    

if __name__ == "__main__":
    app.run(debug=True)






