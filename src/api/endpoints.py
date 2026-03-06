from flask import jsonify
import re

@app.route('/regex-test', methods=['POST'])
def regex_test():
    data = request.get_json()
    pattern = data['pattern']
    text = data['text']
    matches = re.findall(pattern, text)
    return jsonify({'matches': matches})