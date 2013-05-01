#!/usr/bin/env python
## The equivalent of:
##  "Working with the Skeleton"
## in the OpenNI user guide.

"""
This shows how to identify when a new user is detected, look for a pose for
that user, calibrate the users when they are in the pose, and track them,
sending updates about joint position over a websocket.

"""
import os
import json
import errno
import socket
import gevent
from gevent.pywsgi import WSGIServer
import geventwebsocket
from openni import (Context, UserGenerator, SkeletonJoint,
        CALIBRATION_STATUS_OK, SKEL_PROFILE_ALL)

# Pose to use to calibrate the user
pose_to_use = 'Psi'

ctx = Context()
ctx.init()

# Create the user generator
user = UserGenerator()
user.create(ctx)

# Obtain the skeleton & pose detection capabilities
skel_cap = user.skeleton_cap
pose_cap = user.pose_detection_cap

# A set of all connected websockets
connected_sockets = set()

def broadcast(msg):
    """Send a message to all connected websockets"""
    disconnected = []
    for ws in connected_sockets:
        try:
            ws.send(msg)
        except geventwebsocket.WebSocketError, e:
            print "{0}: {1}".format(e.__class__.__name__, e)
        except socket.error, e:
            # It seems like socket.io sends a heartbeat and tracks this.
            # If the current method of detecting disconnections doesn't work,
            # we could try using gevent-socketio instead of gevent-websocket
            if isinstance(e.args, tuple):
                print "errno is %d" % e[0]
                if e[0] == errno.EPIPE:
                    # Send failed, consider the given socket disconnected
                    disconnected.append(ws)
            else:
                # Unexpected error, raise it
                raise e

    for ws in disconnected:
        # Remove the disconnected sockets from the set
        connected_sockets.discard(ws)


# Declare the callbacks
def new_user(src, id):
    print "1/4 User {} detected. Looking for pose..." .format(id)
    pose_cap.start_detection(pose_to_use, id)

# TODO: Eliminate pose detection if possible
def pose_detected(src, pose, id):
    print "2/4 Detected pose {} on user {}. Requesting calibration..." .format(pose,id)
    pose_cap.stop_detection(id)
    skel_cap.request_calibration(id, True)

def calibration_start(src, id):
    print "3/4 Calibration started for user {}." .format(id)

# TODO: broadcast when a new user is being tracked 
def calibration_complete(src, id, status):
    if status == CALIBRATION_STATUS_OK:
        print "4/4 User {} calibrated successfully! Starting to track." .format(id)
        skel_cap.start_tracking(id)
    else:
        print "ERR User {} failed to calibrate. Restarting process." .format(id)
        new_user(user, id)

# TODO: broadcast when a user is lost
def lost_user(src, id):
    print "--- User {} lost." .format(id)

# Register them
user.register_user_cb(new_user, lost_user)
pose_cap.register_pose_detected_cb(pose_detected)
skel_cap.register_c_start_cb(calibration_start)
skel_cap.register_c_complete_cb(calibration_complete)

# Set the profile
skel_cap.set_profile(SKEL_PROFILE_ALL)

# Start generating
ctx.start_generating_all()
print "0/4 Starting to detect users. Press Ctrl-C to exit."


def poll_openni():
    while True:
        # Update to next frame
        ctx.wait_and_update_all()

        # Extract joint positions of each tracked user
        for id in user.users:
            if skel_cap.is_tracking(id):
                for joint_name, joint in SkeletonJoint.names.iteritems():
                    if skel_cap.is_joint_active(joint):
                        pos = skel_cap.get_joint_position(id, joint)
                        joint_event_msg = {
                            'user': id,
                            'joint': joint_name,
                            'x': pos.point[0],
                            'y': pos.point[1],
                            'z': pos.point[0]
                        }
                        broadcast(json.dumps(joint_event_msg))
        gevent.sleep(0)

def ws_handler(environ, start_response):
    websocket = environ.get("wsgi.websocket")

    if websocket is None:
        return http_handler(environ, start_response)
    try:
        connected_sockets.add(websocket)
        while True:
            msg = websocket.receive()
            if msg is None:
                break
            gevent.sleep(0)
        connected_sockets.discard(websocket)
        websocket.close()
    except geventwebsocket.WebSocketError, ex:
        print "{0}: {1}".format(ex.__class__.__name__, ex)

def http_handler(environ, start_response):
    if environ["PATH_INFO"].strip("/") == "version":
        start_response("200 OK", [])
        return [agent]

    else:
        start_response("400 Bad Request", [])

        return ["WebSocket connection is expected here."]

# TODO: Serve html file and js, maybe with Flask
# TODO: Make port an option
if __name__ == '__main__':
    path = os.path.dirname(geventwebsocket.__file__)
    agent = "gevent-websocket/%s" % (geventwebsocket.__version__)
    print "Running %s from %s" % (agent, path)
    gevent.spawn(poll_openni)
    WSGIServer(("0.0.0.0", 8080), ws_handler, handler_class=geventwebsocket.WebSocketHandler).serve_forever()
