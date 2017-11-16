#!/bin/python

#  Author: Chlorek <chlorek@protonmail.com>
# License: GNU General Public License v2

import dbus
import argparse
import sys
import webbrowser
import urllib.request
import urllib.parse
import re
from PyQt4 import QtGui, QtCore

def getSearchUrl(search_string):
	return "https://youtube.com/results?" + urllib.parse.urlencode({"search_query" : search_string})

def getTrackSearchString(artists):
	metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
	return (metadata['xesam:artist'][0] + " " + metadata['xesam:title']).encode('utf-8')

def main():
	parser = argparse.ArgumentParser(prog="spotatube", description='find currently playing track from Spotify on Youtube')
	# Actions
	parser.add_argument('-o', '--open',	help='open url in browser',  action='store_true', default=False)
	parser.add_argument('-c', '--clip',	help='put url in clipboard',  action='store_true', default=False)
	# Options
	parser.add_argument('-p', '--page', help='specify page you want to find, defaults to track', choices=['search', 'track'], default='track')
	parser.add_argument('-a', '--artists', help='(doesn\'t work) specify how many artists should be in search query, default=1', type=int, default=1)
	parser.add_argument('-m', '--originalmix',	help='append "(Original Mix)" on end of search query (if it is not already there), false by default',  action='store_true', default=False)
	parser.add_argument('-f', '--foreground',	help='bring webbrowser to foreground (support depends on webbrowser), true by default',  action='store_true', default=True)
	
	args = parser.parse_args()

	if not args.open and not args.clip:
		print('At least one action is required (--open and/or --clip)')
		return

	search_string = getTrackSearchString(args.artists)
	search_url = getSearchUrl(search_string + (' (Original Mix)'.encode('ascii') if args.originalmix and not re.search(re.compile('(?i)original'.encode('ascii')), search_string) else ''.encode('ascii')))

	if args.page == 'search':
		if args.open:
			webbrowser.open(search_url, new=0, autoraise=args.foreground)
		if args.clip:
			app.clipboard().setText(search_url)
	elif args.page == 'track':
		print('Searching for matches...')
		html = urllib.request.urlopen(search_url)
		videos = re.findall(r'href=\"\/watch\?v=(.{11})', html.read().decode())
		video_url = 'https://youtube.com/watch?v=' + videos[0]
		if args.open:
			webbrowser.open(video_url, new=0, autoraise=args.foreground)
		if args.clip:
			app.clipboard().setText(video_url)
	print('All done.')

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv);
	session_bus = dbus.SessionBus()
	spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
	spotify_properties = dbus.Interface(spotify_bus, "org.freedesktop.DBus.Properties")
	main()