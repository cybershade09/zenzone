from flask import Flask, jsonify
import requests

app = Flask(__name__)

def get_quote():
    url = "https://zenquotes.io/api/random"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()[0]['q'] + " - " + response.json()[0]['a']
    return "Error fetching quote"

@app.route('/quote', methods=['GET'])
def quote():
    return jsonify({"quote": get_quote()})

if __name__ == '__main__':
    app.run(port=80)