from flask import Flask, render_template, request, jsonify
import json,boto3
from datetime import date, timedelta
app = Flask(__name__)

jd_file = 'jobDefinitions_v2.json'
markerFilePath = 'marker.json'

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/home")
def mainPage():
    return render_template("page.html")

@app.route("/jobStatus/", methods=["POST"])
def runJob():
    env = request.form.get("env_name")
    job = request.form.get("job_name")
    client = boto3.client('lambda')
    with open(jd_file) as json_file:
        data = json.load(json_file)
        sfname = [j["stepFunctionName"] for j in data["jobs"] if j["name"]==job][0].replace("${environment}",env)
        jobname = [j["starterLambdaName"] for j in data["jobs"] if j["name"]==job][0].replace("${environment}",env)
    response = client.invoke(FunctionName=jobname)
    stepfunction_arn = "arn:aws:states:eu-west-1:650967531325:stateMachine:" + sfname
    url = "https://eu-west-1.console.aws.amazon.com/states/home?region=eu-west-1#/statemachines/view/"+stepfunction_arn
    status = "Success" if response['ResponseMetadata']['HTTPStatusCode']==200 else "Failed"
    jobinfo = {"job" : jobname, "env" : env, "url" : url, "status": status}
    return render_template("jobstatus.html", **jobinfo)

@app.route("/lastExecution/", methods=["POST"])
def lastExecution():
    env = request.form.get("env_name")
    job = request.form.get("job_name")
    client = boto3.client('stepfunctions')
    with open(jd_file) as json_file:
        data = json.load(json_file)
        sfname = [j["stepFunctionName"] for j in data["jobs"] if j["name"]==job][0].replace("${environment}",env)
        jobname = [j["starterLambdaName"] for j in data["jobs"] if j["name"]==job][0].replace("${environment}",env)
    stepfunction_arn = "arn:aws:states:eu-west-1:650967531325:stateMachine:" + sfname
    url = "https://eu-west-1.console.aws.amazon.com/states/home?region=eu-west-1#/statemachines/view/"+stepfunction_arn
    response = client.list_executions(stateMachineArn=stepfunction_arn)
    jobinfo = {"job" : jobname, "env" : env, "url" : url, "status": response['executions'][0]['status']}
    return render_template("jobstatus.html", **jobinfo)

@app.route('/createMarker', methods=["POST"])
def createMarker():
    env = request.form.get("env_name")
    job = request.form.get("job_name")
    s3 = boto3.resource('s3')
    localdate = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    with open(jd_file) as json_file:
        data = json.load(json_file)
        marker = [j["markerPath"] for j in data["jobs"] if j["name"]==job][0].replace("${environment}",env).replace("${date}", localdate)
        jobname = [j["starterLambdaName"] for j in data["jobs"] if j["name"]==job][0].replace("${environment}",env)
    s3bucket = marker.split("/")[2]
    destination = '/'.join(marker.split("/")[3:])
    s3.meta.client.upload_file(markerFilePath, s3bucket, destination)
    return "Markers Created in %s bucket at the following path %s" % (s3bucket, destination)

@app.route("/livesearch",methods=["POST","GET"])
def livesearch():
    searchbox = request.form.get("text")
    output = []
    with open(jd_file) as json_file:
        data = json.load(json_file)
        output = [{"name" : job['name']} for job in data["jobs"] if searchbox.lower() in job["name"].lower()]
    return jsonify(output)
