from flask import Flask, render_template, url_for, flash, redirect
import requests
from forms import RegistrationForm, LoginForm, DeviceForm, ConnectDevice, ChooseDevice, BridgePublisher, BridgeService, \
    TerminateTopic, TerminateService
from components import Rabbitmq
import json
import amqp_protocol

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
global api_url
api_url = "http://127.0.0.1:8080"
global rabbitmq
rabbitmq = Rabbitmq()
rabbitmq.host = "localhost"
rabbitmq.port = "5672"
rabbitmq.vhost = "/"


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        data = {"fullname": form.fullname.data, "username": form.username.data
            , "password": form.password.data}
        url = "{}/{}".format(api_url, "users")
        r = requests.post(url, json=data)
        result = r.json()["result"]
        if result == "Done":
            flash(result, 'success')
        else:
            flash(result, "danger")
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/registerdevice", methods=['GET', 'POST'])
def register_device():
    form = DeviceForm()
    if form.validate_on_submit():
        data = {"name": form.name.data, "role": form.role.data
            , "password": form.password.data, "ip": form.ip.data}
        url = "{}/{}".format(api_url, "devices")
        r = requests.post(url, json=data)
        result = r.json()["result"]
        if result == "Done":
            flash(result, 'success')
        else:
            flash(result, "danger")
        return redirect(url_for('home'))
    return render_template('device_register.html', title='DeviceRegister', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        rabbitmq.username = username
        rabbitmq.password = password
        try:
            rabbitmq.connect()
            return redirect(url_for('login_home', username=username))
        except Exception as e:
            flash(e, "danger")
    return render_template('login.html', title='Login', form=form)


@app.route("/user/<string:username>", methods=['GET', 'POST'])
def login_home(username):
    pass
    return render_template('login_home.html', title='loginhome', username=username)


@app.route("/user/<string:username>/monitor/devices", methods=['GET', 'POST'])
def monitor_devices(username):
    form = ChooseDevice()
    if form.validate_on_submit():
        device_name = form.devicename.data
        rabbitmq.sync_device_stats(device_name)
        data = rabbitmq.get_stats_data()
        memory = data["memory"]["used"]
        pass
        return render_template("monitor_device.html", title="monitordevices", data=data, name=device_name,
                               username=username)
    return render_template("device_list.html", title="devicelist", form=form, username=username)


@app.route("/user/<string:username>/monitor/ros", methods=['GET', 'POST'])
def monitor_ros(username):
    form = ChooseDevice()
    if form.validate_on_submit():
        devicename = form.devicename.data
        rabbitmq.sync_ros_services(devicename)
        rabbitmq.sync_ros_topics(devicename)
        rabbitmq.sync_ros_nodes(devicename)
        topics = rabbitmq.get_topics()["topics"]
        services = rabbitmq.get_services()["services"]
        nodes = rabbitmq.get_nodes()["nodes"]
        return render_template("monitor_ros.html", topics=topics, services=services, nodes=nodes, username=username)
    return render_template("device_list.html", title="monitorros", form=form, username=username)


@app.route("/user/<string:username>/connectdevice", methods=['GET', 'POST'])
def connect_device(username):
    form = ConnectDevice()
    if form.validate_on_submit():
        data = {
            "username": username,
            "device_name": form.devicename.data,
            "password": form.password.data}
        url = "{}/{}".format(api_url, "users/register_device")
        r = requests.post(url, json=data)
        result = r.json()["result"]
        if result != "Done":
            flash(result, 'danger')
            return redirect(url_for("connect_device", username=username))
        url2 = "{}/{}".format(api_url, "devices/connect/{}".format(form.devicename.data))
        r2 = requests.post(url2)
        connect = r2.json()["result"]
        flash(connect, "success")

    return render_template('connect_device.html', title='connectdevice', form=form, username=username)


@app.route("/user/<string:username>/connecteddevices", methods=['GET', 'POST'])
def connected_devices(username):
    url = "{}/{}".format(api_url, "users/device")
    data = {"username": username}
    r = requests.get(url, json=data)
    device_list = r.json()
    devices = device_list["list_of_devices"]
    return render_template("connected_devices.html", title="connecteddevices", devices=devices, username=username)


@app.route("/user/<string:username>/bridge/rostopic", methods=['GET', 'POST'])
def bridge_ros_topic(username):
    form = BridgePublisher()
    if form.validate_on_submit():
        topic_name = form.topicname.data
        topic_type = form.topictype.data
        device_name = form.devicename.data
        rabbitmq.bridge_publisher(topicname=topic_name, topictype=topic_type, devicename=device_name)
        flash("Done", "success")
        return redirect(url_for("login_home", username=username))
    return render_template("bridge_publisher.html", title="bridgepublisher", form=form, username=username)


@app.route("/user/<string:username>/bridge/brokertopic", methods=['GET', 'POST'])
def bridge_broker_topic(username):
    form = BridgePublisher()
    if form.validate_on_submit():
        topic_name = form.topicname.data
        topic_type = form.topictype.data
        device_name = form.devicename.data
        rabbitmq.bridge_subscriber(topicname=topic_name, topictype=topic_type, devicename=device_name)
        flash("Done", "success")
        return redirect(url_for("login_home", username=username))
    return render_template("bridge_subscriber.html", title="bridgesubscriber", form=form, username=username)


@app.route("/user/<string:username>/terminate/rostopic", methods=['GET', 'POST'])
def terminate_ros_topic(username):
    form = TerminateTopic()
    if form.validate_on_submit():
        topic_name = form.topicname.data
        device_name = form.devicename.data
        rabbitmq.terminate_publisher(topicname=topic_name, devicename=device_name)
        flash("Done", "success")
        return redirect(url_for("login_home", username=username))
    return render_template("terminate_topic.html", title="Terminatetopic", form=form, username=username)


@app.route("/user/<string:username>/terminate/brokertopic", methods=['GET', 'POST'])
def terminate_broker_topic(username):
    form = TerminateTopic()
    if form.validate_on_submit():
        topic_name = form.topicname.data
        device_name = form.devicename.data
        rabbitmq.terminate_subscriber(topicname=topic_name, devicename=device_name)
        flash("Done", "success")
        return redirect(url_for("login_home", username=username))
    return render_template("terminate_broker_topic.html", title="Terminatetopic", form=form, username=username)


@app.route("/user/<string:username>/terminate/service", methods=['GET', 'POST'])
def terminate_service(username):
    form = TerminateService()
    if form.validate_on_submit():
        service_name = form.servicename.data
        device_name = form.devicename.data
        rabbitmq.terminate_service(servicename=service_name, devicename=device_name)
        flash("Done", "success")
        return redirect(url_for("login_home", username=username))
    return render_template("terminate_service.html", title="Terminateservice", form=form, username=username)


@app.route("/user/<string:username>/bridge/service", methods=['GET', 'POST'])
def bridge_service(username):
    form = BridgeService()
    if form.validate_on_submit():
        srv_name = form.servicename.data
        srv_type = form.servicetype.data
        device_name = form.devicename.data
        rabbitmq.bridge_service(servicename=srv_name, servicetype=srv_type, devicename=device_name)
        flash("Done", "success")
        return redirect(url_for("login_home", username=username))
    return render_template("bridge_service.html", title="bridgeservice", form=form, username=username)


if __name__ == '__main__':
    app.run(debug=True)
