document.addEventListener("DOMContentLoaded", function () {
	const form = document.getElementById("prediction-form");

	form.addEventListener("submit", async function (e) {
		e.preventDefault();

		const formData = new FormData(form);

		const payload = {
			"transaction type": formData.get("transaction_type") || "",
			"transaction_status": formData.get("transaction_status"),
			"amount": Number(formData.get("amount")),
			"merchant_category": formData.get("merchant_category"),
			"sender_age": Number(formData.get("sender_age")),
			"receiver_age": Number(formData.get("receiver_age")),
			"sender_state": formData.get("sender_state"),
			"sender_bank": formData.get("sender_bank"),
			"receiver_bank": formData.get("receiver_bank"),
			"device_type": formData.get("device_type"),
			"network_type": formData.get("network_type"),
			"hour_of_day": Number(formData.get("hour_of_day")),
			"day_of_week": formData.get("day_of_week"),
			"is_weekend": formData.get("is_weekend") === "on" ? 1 : 0,
		};

		const resultCard = document.getElementById("result-card");
		const resultText = document.getElementById("result-text");

		try {
			const resp = await fetch("/predict", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(payload),
			});

			const json = await resp.json();

			if (!resp.ok) {
				resultText.textContent = json.error || "Prediction failed";
				resultCard.style.display = "block";
				return;
			}

			resultText.innerHTML = `Decision: <strong>${json.decision}</strong> — Probability: ${json.fraud_probability}`;
			resultCard.style.display = "block";
		} catch (err) {
			resultText.textContent = "Failed to contact server.";
			resultCard.style.display = "block";
		}
	});
});