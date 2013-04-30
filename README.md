Algorithmic Dance Server
========================

Detect user skeleton movement and send it over a WebSocket.

Uses OpenNI, Python and [gevent-websocket](http://www.gelens.org/code/gevent-websocket/)

Requirements
------------

* OpenNI 1.5.x (I'm using OpenNI 1.5.4). We're not using OpenNI 2 because
  language wrappers like PyOpenNI or node-openni don't support it. Also,
  OpenNI 2 only supports the Kinect controller through the official Kinect SDK
  which is only available for Windows and requires a lot of Visual Studio cruft
  to use.
* Python 2.7 
* Virtualenv (optional). This can be installed on Ubuntu with
  ``apt-get install python-virtualenv``
* PyOpenNI, a Python wrapper for the OpenNI library
* libevent 1.4.x (needed by gevent)
* Python packages listed in requirements.txt

Installation
------------

These are installation instructions for Ubuntu Linux, as that's what I run
on my notebook, but I don't see any reason why this won't work on other
Linux distros or Mac OS.

1. Install OpenNI, NiTE middleware and the Kinect driver. By far the easiest
   way to do this is by [downloading one of the binary packages](https://code.google.com/p/simple-openni/downloads/list)
   made available by the [simple-openni](https://code.google.com/p/simple-openni/)
   project. [This tutorial](http://ramsrigoutham.com/2012/07/08/getting-started-with-kinect-on-ubuntu-12-04-openni-nite-simpleopenni-and-processing/)
   has useful instructions for installing these dependencies on Ubuntu.
   You can ignore the Processing stuff.
2. Clone this repo from GitHub
3. Install [PyOpenNi](https://github.com/jmendeth/PyOpenNI) following its
   instructions. Copy the openni.so file in the top-level directory of the 
   cloned repo
4. Create a virtualenv for this project. By far the easiest way to work
   with Python dependencies is using virtualenv. In the cloned repo directory
   run ``virtualenv --python=python2.7 venv``.  Then activate the
   virtualenv with ``. ./venv/bin/activate``. 
5. Install the dependency packages using ``pip install -r requirements.txt``

Usage
-----

If you're using ``virtualenv`` to isolate Python dependenices as
recommended, make sure you activate your virtualenv using
``. ./venv/bin/activate`` first.

Connect the Kinect controller to your computer's USB port and start the 
server with:

``./server.py``

or

``python server.py``

Why Python
----------

I was excited to use Node.js and [node-openni](https://github.com/pgte/node-openni), but I couldn't
get the JavaScript callbacks to work on my system. We tried it on a
system at the Work Department, and it worked initially but then the server
kept segfaulting.

I've found PyOpenNI to be more stable, even though I found writing the
websocket code a little more unintuitive than when using Node.js.

Technical Resources
-------------------

* [Gevent Tutorial](http://sdiehl.github.io/gevent-tutorial/)
