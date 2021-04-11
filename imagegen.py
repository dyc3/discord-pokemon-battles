import requests
import urllib.request
import os
import io
import argparse
from user_agents import parse
from bs4 import BeautifulSoup
from PIL import Image

from cv2 import cv2
import numpy as np

base_dir = os.getcwd()
dir_name = ("images".split('/')[-1]).split('.')[0]
dir_path = os.path.join(base_dir, dir_name)


def getPokemonImage(name):
	r = f"https://img.pokemondb.net/artwork/large/{name}.jpg"
	# download_image(r)
	process3(r)
	# soup = BeautifulSoup(r.content, 'html.parser')
	# image = soup.find_all("img")
	pass


def download_image(url):
	print("[INFO] downloading {}".format(url))
	name = str(url.split('/')[-1].split('.')[0])
	# opener = urllib.request.build_opener()
	# opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	# urllib.request.install_opener(opener)

	# urllib.request.urlretrieve(url, os.path.join(dir_path, name))
	image_content = requests.get(url).content
	image_file = io.BytesIO(image_content)
	image = Image.open(image_file).convert('RGBA')
	file_path = (
		R"C:\Users\Avery\Documents\GitHub\discord-pokemon-battles\imagegen\\"
	) + name + ".png"
	image = process_image(image)
	image.save(file_path, "PNG")


def process_image(image):
	# Transparency
	newImage = []
	for item in image.getdata():
		if item[:3] == (255, 255, 255):
			newImage.append((255, 255, 255, 0))
		else:
			newImage.append(item)
	image.putdata(newImage)
	return image

def url_to_image(url):
	# download the image, convert it to a NumPy array, and then read
	# it into OpenCV format

	opener = urllib.request.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	urllib.request.install_opener(opener)
	resp = urllib.request.urlopen(url)

	image = np.asarray(bytearray(resp.read()), dtype="uint8")
	image = cv2.imdecode(image, cv2.IMREAD_COLOR)
	# return the image
	return image

def smart_process_image(url):
	#== Parameters =======================================================================
	BLUR = 21
	CANNY_THRESH_1 = 10
	CANNY_THRESH_2 = 200
	MASK_DILATE_ITER = 10
	MASK_ERODE_ITER = 10
	MASK_COLOR = (0.0, 0.0, 1.0) # In BGR format

	#== Processing =======================================================================

	#-- Read image -----------------------------------------------------------------------
	img = url_to_image(url)
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	#-- Edge detection -------------------------------------------------------------------
	edges = cv2.Canny(gray, CANNY_THRESH_1, CANNY_THRESH_2)
	edges = cv2.dilate(edges, None)
	edges = cv2.erode(edges, None)

	#-- Find contours in edges, sort by area ---------------------------------------------
	contour_info = []
	contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
	# Previously, for a previous version of cv2, this line was:
	#  contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
	# Thanks to notes from commenters, I've updated the code but left this note
	for c in contours:
		contour_info.append((
			c,
			cv2.isContourConvex(c),
			cv2.contourArea(c),
		))
	contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
	max_contour = contour_info[0]

	#-- Create empty mask, draw filled polygon on it corresponding to largest contour ----
	# Mask is black, polygon is white
	mask = np.zeros(edges.shape)
	cv2.fillConvexPoly(mask, max_contour[0], (255))

	#-- Smooth mask, then blur it --------------------------------------------------------
	mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
	mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
	mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
	mask_stack = np.dstack([mask] * 3) # Create 3-channel alpha mask

	#-- Blend masked img into MASK_COLOR background --------------------------------------
	mask_stack = mask_stack.astype('float32') / 255.0 # Use float matrices,
	img = img.astype('float32') / 255.0 #  for easy blending

	masked = (mask_stack * img) + ((1 - mask_stack) * MASK_COLOR) # Blend
	masked = (masked * 255).astype('uint8') # Convert back to 8-bit

	cv2.imshow('img', masked) # Display
	cv2.waitKey()

	#cv2.imwrite('C:/Temp/person-masked.jpg', masked)           # Save

def process2(url):

	img = url_to_image(url)
	# convert to graky
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	# threshold input image as mask
	mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]

	# negate mask
	mask = 255 - mask

	# apply morphology to remove isolated extraneous noise
	# use borderconstant of black since foreground touches the edges

	kernel = np.ones((3,3), np.uint8)
	mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
	mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

	# anti-alias the mask -- blur then stretch
	# blur alpha channel
	mask = cv2.GaussianBlur(mask, (0,0), sigmaX=2, sigmaY=2, borderType = cv2.BORDER_DEFAULT)

	# linear stretch so that 127.5 goes to 0, but 255 stays 255
	# mask = (2*(mask.astype(np.float32))-255.0).clip(0,255).astype(np.uint8)

	# put mask into alpha channel
	result = img.copy()
	result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
	result[:, :, 3] = mask

	# save resulting masked image
	cv2.imwrite('person_transp_bckgrnd.png', result)

	# display result, though it won't show transparency
	cv2.imshow("INPUT", img)
	cv2.imshow("GRAY", gray)
	cv2.imshow("MASK", mask)
	cv2.imshow("RESULT", result)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def process3(url):

	img = url_to_image(url)

	# convert to hsv
	hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

	# threshold using inRange
	range1 = (50,0,50)
	range2 = (120,120,170)
	mask = cv2.inRange(hsv,range1,range2)

	# invert mask
	mask = 255 - mask

	# apply morphology closing and opening to mask
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15,15))
	mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
	mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

	result = img.copy()
	result[mask==0] = (255,255,255)

	# write result to disk
	# cv2.imwrite("man_face_mask.png", mask)
	# cv2.imwrite("man_face_white_background.jpg", result)

	# display it
	cv2.imshow("mask", mask)
	cv2.imshow("result", result)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

print(getPokemonImage("monferno"))
