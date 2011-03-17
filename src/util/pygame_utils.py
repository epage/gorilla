#!/usr/bin/env python

from __future__ import with_statement
from __future__ import division

import logging

import pygame


_moduleLogger = logging.getLogger(__name__)


def makeSurfaceFromASCII(ascii, fgColor=(255, 255, 255), bgColor=(0, 0, 0)):
	"""Returns a new pygame.Surface object that has the image drawn on it as specified by the ascii parameter.
	The first and last line in ascii are ignored. Otherwise, any X in ascii marks a pixel with the foreground color
	and any other letter marks a pixel of the background color. The Surface object has a width of the widest line
	in the ascii string, and is always rectangular."""

	ascii = ascii.split('\n')[1:-1]
	width = max([len(x) for x in ascii])
	height = len(ascii)
	surf = pygame.Surface((width, height))
	surf.fill(bgColor)

	pArr = pygame.PixelArray(surf)
	for y in range(height):
		for x in range(len(ascii[y])):
			if ascii[y][x] == 'X':
				pArr[x][y] = fgColor
	return surf


def toProperCase(s, mod):
	"""Checks the state of the shift and caps lock keys, and switches the case of the s string if needed."""
	if bool(mod & pygame.locals.KMOD_RSHIFT or mod & pygame.locals.KMOD_LSHIFT) ^ bool(mod & pygame.locals.KMOD_CAPS):
		return s.swapcase()
	else:
		return s


if __name__ == "__main__":
	pass

