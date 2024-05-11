import io
from flask import Flask, request, jsonify, send_file
from pydantic import ValidationError

from user_settings import firestore_integration
from user_settings.request_models import UserSettings
from cv_processor import process_cv

app = Flask(__name__)


@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part provided'}), 400
    if 'chatId' not in request.args:
        return jsonify({'error': 'Chat ID not provided'}), 400

    chat_id = request.args.get('chatId')
    file = request.files['file']

    if file:
        ranges_count = firestore_integration.get_user_settings(chat_id)[
            firestore_integration.probability_ranges_count_field_name]
        file_data = file.read()
        processed_file, general_probability = process_cv(file_data, ranges_count)
        processed_file_bytes = processed_file.getvalue()

        response = send_file(io.BytesIO(processed_file_bytes),
                             mimetype='application/pdf',
                             as_attachment=True,
                             download_name='processed_file.pdf')
        response.headers['Ranges-Count'] = ranges_count
        response.headers['General-Probability'] = general_probability
        return response, 200
    else:
        return jsonify({'error': 'No file part provided'}), 400


@app.route('/settings', methods=['POST'])
def save_user_settings():
    try:
        user_settings = UserSettings.parse_raw(request.data)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    firestore_integration.save_user_settings(user_settings)
    return jsonify({"status": "OK"}), 201


if __name__ == "__main__":
    app.run(debug=True)
