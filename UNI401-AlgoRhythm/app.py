from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

# KONEKSI KE MONGODB ATLAS
uri = "mongodb+srv://dwibagusd:YI7oMb8ttI4XsTk4@darrr.zeiv7.mongodb.net/?retryWrites=true&w=majority&appName=Darrr"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['MyData']
collection = db['DataTest']

# ENDPOINT UNTUK MENERIMA DATA DARI ESP32
@app.route('/data', methods=['POST'])
def receive_data():
    try:
        data = request.json  # Terima data dalam format JSON
        collection.insert_one(data)  # Simpan ke MongoDB
        return jsonify({"message": "Data berhasil disimpan", "status": "success"}), 201
    except Exception as e:
        return jsonify({"message": "Gagal menyimpan data", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
