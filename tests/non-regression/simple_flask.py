from flask import Flask, jsonify
from OpenHosta import emulate
from OpenHosta import DefaultModel
from OpenHosta import reload_dotenv

app = Flask(__name__)

@app.route("/ask/<question>")
def home(question="Introduce yourself and say hello")->str:
    """
    A simple Flask application that returns an answer to the question.
    """
    return emulate()

@app.route("/reload_config")
def reload_config():
    reload_dotenv()
    return jsonify({"status": "dotenv reloaded"})

@app.route("/")
def root():
    params = DefaultModel.api_parameters.copy()
    params.update({"model": DefaultModel.model_name})
    params.update({"base_url": DefaultModel.base_url})
    return jsonify(params)

def produce_a_joke_about(topic)->str:
    """
    Produce a joke about the given topic.
    """
    return emulate()

@app.route("/joke/<topic>")
def joke(topic):
    """
    A simple Flask application that returns a joke about the topic.
    """
    return produce_a_joke_about(topic)

# To run: flask --app simple_flask run --reload

if __name__ == '__main__':
    app.run(debug=True)

