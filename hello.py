from flask import Flask, render_template, request, jsonify
import json,boto3
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/home")
def mainPage():
    return render_template("page.html")

@app.route("/jobStatus/", methods=["POST"])
def jobStatus():
    env = request.form.get("env_name")
    job = request.form.get("job_name")
    client = boto3.client('lambda')
    with open('jobDefinitions.json') as json_file:
        data = json.load(json_file)
        jname = [j["starterLambdaName"] for j in data["jobs"] if j["name"]==job][0]
    response = client.get_function_configuration(FunctionName=jname.replace("${environment}",env))['Environment']['Variables']['H24_STEPFUNCTION_ARN']
    url = "https://eu-west-1.console.aws.amazon.com/states/home?region=eu-west-1#/statemachines/view/"+response
    return "Check Job Status here ==> "+ url

@app.route("/livesearch",methods=["POST","GET"])
def livesearch():
    searchbox = request.form.get("text")
    output = []
    with open('jobDefinitions.json') as json_file:
        data = json.load(json_file)
        output = [{"name" : job['name']} for job in data["jobs"] if job["name"].startswith(searchbox)]
    return jsonify(output)
