#!/usr/bin/env python

import os
import wireless
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

iface = os.environ.get('IFACE', 'wlan0')

# Start wpa_supplicant
wireless.wpa_supplicant(iface)

# Store the list of networks
networks = wireless.scan(iface)
current = None


@app.route('/reload', methods=['GET'])
def reload():
    networks = wireless.scan(iface)
    app.logger.debug(networks)
    return jsonify(result=True)


@app.route('/list', methods=['GET'])
def list(notification=None):
    id = int(request.args.get('id', -1))
    choice = networks[id] if len(networks) > 0 and id >= 0 else None

    # Reload the list if no choice is made
    if not choice:
        reload()

    return render_template('list.html', networks=networks,
                           current=current, choice=choice,
                           notification=notification, enumerate=enumerate)


@app.route('/list', methods=['POST'])
def join():
    id = int(request.form.get('id', -1))
    choice = networks[id] if id >= 0 else None

    notification = None
    if choice:
        passwd = None
        if choice['Encryption'] != 'Open':
            passwd = request.form.get('password', None)

        network = wireless.join(iface, choice['Name'], passwd)
        if network:
            notification = dict(success=True, message='Succesfully connected to network %s' % choice['Name'])
            current = choice
            current['Supplicant_Id'] = network
        else:
            notification = dict(success=False, message='An error ocurred connecting to network %s' % choice['Name'])

    return list(notification)
