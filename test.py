from services.predictor import predict_transaction

sample_input = {
    "transaction type": "P2P",
    "transaction_status": "SUCCESS",
    "merchant_category": "Grocery",
    "amount": 3000,
    "sender_age": 25,
    "receiver_age": 18,
    "sender_state": "Delhi",
    "sender_bank": "HDFC",
    "receiver_bank": "SBI",
    "device_type": "Android",
    "network_type": "wifi",
    "hour_of_day": 22,
    "day_of_week": "Monday",
    "is_weekend": 0,
}

predict_transaction(sample_input)