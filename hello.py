from flask import Flask, render_template, request, jsonify
import json,boto3
app = Flask(__name__)

jd_file = 'jobDefinitions_v2.json'

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
#    response = client.get_function_configuration(FunctionName=jname.replace("${environment}",env))['Environment']['Variables']['H24_STEPFUNCTION_ARN']
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

@app.route("/livesearch",methods=["POST","GET"])
def livesearch():
    searchbox = request.form.get("text")
    output = []
    with open(jd_file) as json_file:
        data = json.load(json_file)
        output = [{"name" : job['name']} for job in data["jobs"] if job["name"].startswith(searchbox)]
    return jsonify(output)
