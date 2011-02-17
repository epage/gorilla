#!/usr/bin/env python

import os
import sys

try:
	import py2deb
except ImportError:
	import fake_py2deb as py2deb

import constants


__app_name__ = constants.__app_name__
__description__ = """Remake of the Gorillas.bas banana artillery game
REPLACEME
.
Homepage: REPLACEME
"""
__author__ = "Ed Page"
__email__ = "eopage@byu.net"
__version__ = constants.__version__
__build__ = constants.__build__
__changelog__ = """
* Initial packaging for Maemo
""".strip()


__postinstall__ = """#!/bin/sh -e

gtk-update-icon-cache -f /usr/share/icons/hicolor
rm -f ~/.%(name)s/%(name)s.log
""" % {"name": constants.__app_name__}

__preremove__ = """#!/bin/sh -e
"""


def find_files(prefix, path):
	for root, dirs, files in os.walk(path):
		for file in files:
			if file.startswith(prefix+"-"):
				fileParts = file.split("-")
				unused, relPathParts, newName = fileParts[0], fileParts[1:-1], fileParts[-1]
				assert unused == prefix
				relPath = os.sep.join(relPathParts)
				yield relPath, file, newName


def unflatten_files(files):
	d = {}
	for relPath, oldName, newName in files:
		if relPath not in d:
			d[relPath] = []
		d[relPath].append((oldName, newName))
	return d


def build_package(distribution):
	try:
		os.chdir(os.path.dirname(sys.argv[0]))
	except:
		pass

	py2deb.Py2deb.SECTIONS = py2deb.SECTIONS_BY_POLICY[distribution]
	p = py2deb.Py2deb(__app_name__)
	p.prettyName = constants.__pretty_app_name__
	p.description = __description__
	p.bugTracker = "REPLACEME"
	p.author = __author__
	p.mail = __email__
	p.license = "lgpl"
	p.depends = ", ".join([
		"python2.6 | python2.5",
		"python-simplejson",
	])
	p.depends += {
		"debian": ", python-qt4, python-pygame",
		"diablo": ", python2.5-qt4-core, python2.5-qt4-gui, python2.5-pygame",
		"fremantle": ", python2.5-qt4-core, python2.5-qt4-gui, python2.5-qt4-maemo5, python-pygame",
	}[distribution]
	p.section = {
		"debian": "games",
		"diablo": "user/games",
		"fremantle": "user/games",
	}[distribution]
	p.arch = "all"
	p.urgency = "low"
	p.distribution = "diablo fremantle debian"
	p.repository = "extras"
	p.changelog = __changelog__
	p.postinstall = __postinstall__
	p.preremove = __preremove__
	p.icon = {
		"debian": "26x26-%s.png" % constants.__app_name__,
		"diablo": "26x26-%s.png" % constants.__app_name__,
		"fremantle": "48x48-%s.png" % constants.__app_name__,
	}[distribution]
	p["/opt/%s/bin" % constants.__app_name__] = [ "%s.py" % constants.__app_name__ ]
	for relPath, files in unflatten_files(find_files("src", ".")).iteritems():
		fullPath = "/opt/%s/lib" % constants.__app_name__
		if relPath:
			fullPath += os.sep+relPath
		p[fullPath] = list(
			"|".join((oldName, newName))
			for (oldName, newName) in files
		)
	p["/usr/share/applications/hildon"] = ["%s.desktop" % constants.__app_name__]
	p["/usr/share/icons/hicolor/26x26/hildon"] = ["26x26-%s.png|%s.png" % (constants.__app_name__, constants.__app_name__)]
	p["/usr/share/icons/hicolor/48x48/hildon"] = ["48x48-%s.png|%s.png" % (constants.__app_name__, constants.__app_name__)]
	p["/usr/share/icons/hicolor/64x64/hildon"] = ["64x64-%s.png|%s.png" % (constants.__app_name__, constants.__app_name__)]

	print p
	if distribution == "debian":
		print p.generate(
			version="%s-%s" % (__version__, __build__),
			changelog=__changelog__,
			build=True,
			tar=False,
			changes=False,
			dsc=False,
		)
	else:
		print p.generate(
			version="%s-%s" % (__version__, __build__),
			changelog=__changelog__,
			build=False,
			tar=True,
			changes=True,
			dsc=True,
		)
	print "Building for %s finished" % distribution


if __name__ == "__main__":
	if len(sys.argv) == 1:
		distribution = "fremantle"
	else:
		distribution = sys.argv[1]
	build_package(distribution)
