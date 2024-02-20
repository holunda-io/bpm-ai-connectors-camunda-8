from flask import Flask, request, jsonify, Response

app = Flask(__name__)


@app.route('/createOutputVariables', methods=['POST'])
def create_output_variables():
    data = request.get_json()
    return jsonify({'result': data['context']['result']}), 200


@app.route('/examineErrorExpression', methods=['POST'])
def examine_error_expression():
    return Response(status=204)


app.run(host='localhost', port=8080)
