# Caleb Bitting
# Bruce Maxwell and Caitrin Eaton
# CS 152 Spring 2020
# Project 10
#

# importing libraries
import graphicsPlus as gr
from math import sin, cos, pi
import math
import statistics
import random
import argparse
import time

# global variables
shapes = []

# Implement decorators
def is_not_negative_num(f):

	def wrapper(*args, **kwargs):
		if isinstance(args[-1], (int, float)) and args[-1] >= 0:		# Make sure that the last positional argument is both number and non-negative
			return f(*args, **kwargs)
		else: raise Exception(f'{args[-1]} is not a non-negative number')

	return wrapper

def is_num(f):

	def wrapper(*args, **kwargs):
		if isinstance(args[-1], (int, float)):					# Make sure that the last positional argument is a number
			return f(*args, **kwargs)
		else: raise Exception(f'{args[-1]} is not a number')

	return wrapper

def is_two_element_list(f):

	def wrapper(*args, **kwargs):
		if isinstance(args[-1], list) and len(args[-1]) == 2:			# Make sure that the last positional argument is a two-element list
			return f(*args, **kwargs)					
		else: raise Exception('new_pos needs to be a two-element list.')		

	return wrapper

# Class definitions
class Block(gr.Rectangle):

	# Get access to shapes list
	global shapes

	# Initialization method
	def __init__(self, center, width, height, velocity=[0,0], acceleration=[0,0], elasticity=.4, color=(0, 0, 0), type='Block'):
		'''Give this function a center Point object, a width, and a height.'''
		p1 = gr.Point((center.getX() - width/2), (center.getY() - height/2))
		p2 = gr.Point((center.getX() + width/2), (center.getY() + height/2))
		super().__init__(p1, p2)
		self.center = center
		self.width = width
		self.height = height
		self.velocity = velocity
		self.acceleration = acceleration
		self.elasticity = elasticity
		self.color = color
		self.type = type
		shapes.append(self)
		r, g, b = color
		self.setFill(gr.color_rgb(r, g, b))

	# Getter methods
	def getPosition(self): return [self.getCenter().getX(), self.getCenter().getY()]

	def getCenter(self): return self.center

	def getWidth(self): return self.width

	def getHeight(self): return self.height

	def getVelocity(self): return self.velocity

	def getAcceleration(self): return self.acceleration

	def getElasticity(self): return self.elasticity

	def getColor(self): return self.color

	def getCenter(self): return gr.Point(statistics.mean([self.getP1().getX(), self.getP2().getX()]), statistics.mean([self.getP1().getY(), self.getP2().getY()]))

	def getType(self): return self.type

	def getBoundingBox(self):
		width = self.getWidth()
		height = self.getHeight()
		pos = self.getPosition()
		return ([pos[0] - width/2, pos[0] + width/2], [pos[1] - height/2, pos[1] + height/2])		# Return a tuple of lists; the lists are the upper and lower bounds for the box


	# Setter methods
	@is_two_element_list
	def setVelocity(self, new_vel):
		self.velocity = new_vel

	@is_two_element_list
	def setAcceleration(self, new_acc):
		self.acceleration = new_acc

	@is_two_element_list
	def setPosition(self, new_pos):
		dx = new_pos[0] - self.getCenter().getX()
		dy = new_pos[1] - self.getCenter().getY()
		self.move(dx, dy)
		self.position = new_pos

	@classmethod
	def fromP1P2(cls, p1, p2, velocity=[0,0], acceleration=[0,0], elasticity=.4, color=(0, 0, 0), type='Block'):
		center = gr.Point(statistics.mean(p1.getX(), p2.getX()), statistics.mean(p1.getY(), p2.getY()))
		width = p2.getX() - p1.getX()
		height = p2.getY() - p1.getY()
		return cls(center, width, height, velocity, acceleration, elasticity, color, type)

	def update(self, dt=.02):
		'''Update the ball based on the laws of physics.'''
		vel_x_new = self.acceleration[0]*dt + self.velocity[0]
		vel_y_new = self.acceleration[1]*dt + self.velocity[1]
		vel_new = [vel_x_new, vel_y_new]
		pos_x_new = self.getCenter().x + self.velocity[0]*dt + (.5*self.acceleration[0]*dt**2)
		pos_y_new = self.getCenter().y + self.velocity[1]*dt + (.5*self.acceleration[1]*dt**2)
		self.setPosition([pos_x_new, pos_y_new])
		self.setVelocity(vel_new)

	# Dunder methods
	def __repr__(self): return f'Block({self.center}, {self.getWidth()}, {self.getHeight()}, {self.getVelocity()}, {self.getAcceleration()}, {self.getElasticity()}, {self.getColor()}, {self.getType()}.'

	def __str__(self):
		this_object = 'Block Object:'
		center = str(self.getCenter())
		width = str(self.getWidth())
		height = str(self.getHeight())
		velocity = str(self.getVelocity())
		acceleration = str(self.getAcceleration())
		elasticity = str(self.getElasticity())
		color = str(self.getColor())
		this_object += f'\n center={center}'
		this_object += f'\n width={width}'
		this_object += f'\n height={height}'
		this_object += f'\n velocity={velocity}'
		this_object += f'\n acceleration={acceleration}'
		this_object += f'\n elasticity={elasticity}'
		this_object += f'\n color={color}'
		return this_object

class Ball(gr.Circle):

	# Get access to shapes list
	global shapes

	# Initialization method
	def __init__(self, center, radius, velocity=[0,0], acceleration=[0,0], elasticity=.65, color=(0, 0, 0), type='Ball'):
		'''Give this function a center Point object and a radius.'''
		super().__init__(center, radius)
		self.velocity = velocity
		self.acceleration = acceleration
		self.elasticity = elasticity
		self.color = color
		self.type = type
		shapes.append(self)
		if isinstance(color, tuple):
			r, g, b = color
			self.setFill(gr.color_rgb(r, g, b))
		else:
			self.setFill(color)

	# Getter methods
	def getPosition(self): return [self.getCenter().getX(), self.getCenter().getY()]

	def getVelocity(self): return self.velocity

	def getAcceleration(self): return self.acceleration

	def getElasticity(self): return self.elasticity

	def getColor(self): return self.color

	def getType(self): return self.type

	# These four methods are needed to move the Player object in project11
	def moveUp(self): 
		if self.getPosition()[1] + self.getRadius() > 800:
			pass
		else:
			self.setPosition([self.getPosition()[0], self.getPosition()[1]+10])

	def moveDown(self):
		if self.getPosition()[1] - self.getRadius() < 0:
			pass
		else:
			self.setPosition([self.getPosition()[0], self.getPosition()[1]-10])

	def moveLeft(self):
		if self.getPosition()[0] - self.getRadius() < 0:
			pass
		else:
			self.setPosition([self.getPosition()[0]-10, self.getPosition()[1]])

	def moveRight(self):
		if self.getPosition()[0] + self.getRadius() > 1200:
			pass
		else:
			self.setPosition([self.getPosition()[0]+10, self.getPosition()[1]])

	# Setter methods
	@is_two_element_list
	def setPosition(self, new_pos):
		dx = new_pos[0] - self.getCenter().getX()
		dy = new_pos[1] - self.getCenter().getY()
		self.move(dx, dy)
		self.position = new_pos

	@is_two_element_list
	def setVelocity(self, new_vel): self.velocity = new_vel

	@is_two_element_list
	def setAcceleration(self, new_acc): self.acceleration = new_acc

	# Class methods
	@classmethod
	def forSnowman(cls, center, radius, velocity, acceleration, elasticity, color, type='Ball'):
		snow_body = cls(center, radius, velocity, acceleration, elasticity, color, type='Ball')
		shapes.remove(snow_body)
		return snow_body

	# Utility methods
	def isClose(self, objects):
		'''Pass this function a either a single object or a list of objects to test for proximity. If passed a list and Carol is close to an environmental object, 
		   the function will return the index of the close object. If she is not close, it will return False. If passed one object, this function will return True or False
		   based upon Carol\'s proximity to that object.'''
		if isinstance(objects, list):
			for index, thing in enumerate(objects):
				if self.isClose(thing):
					return index
			return None
		else:
			object_center = RotatingLine.pt_to_list(objects.getAnchor())
			dist = RotatingLine.dist_formula(self.getPosition(), object_center)
			return True if dist <= 100 else None

	# Dunder methods
	def __repr__(self): return f'Ball({self.getCenter()}, {self.getRadius()}, {self.getVelocity()}, {self.getAcceleration()}, {self.getElasticity()}, {self.getColor()}, {self.getType()}'

	def __str__(self):
		this_object = 'Ball Object:'
		center = str(self.getCenter())
		radius = str(self.getRadius())
		velocity = str(self.getVelocity())
		acceleration = str(self.getAcceleration())
		elasticity = str(self.getElasticity())
		color = str(self.getColor())
		this_object += f'\n center={center}'
		this_object += f'\n radius={radius}'
		this_object += f'\n velocity={velocity}'
		this_object += f'\n acceleration={acceleration}'
		this_object += f'\n elasticity={elasticity}'
		this_object += f'\n color={color}'
		return this_object

	def update(self, dt=.02):
		'''Update the ball based on the laws of physics.'''
		vel_x_new = self.acceleration[0]*dt + self.velocity[0]
		vel_y_new = self.acceleration[1]*dt + self.velocity[1]
		vel_new = [vel_x_new, vel_y_new]
		pos_x_new = self.getCenter().x + self.velocity[0]*dt + (.5*self.acceleration[0]*dt**2)
		pos_y_new = self.getCenter().y + self.velocity[1]*dt + (.5*self.acceleration[1]*dt**2)
		self.setPosition([pos_x_new, pos_y_new])
		self.setVelocity(vel_new)

class CoronaProtester(Ball):

	# Used in project 11. Same as the Ball class just with a couple userper methods

	def __init__(self, center, radius, level, player_ref, velocity=[0,0], acceleration=[0,0], elasticity=.65, color=(0, 0, 0), type='Ball'):
		super().__init__(center, radius, velocity, acceleration, elasticity, color, type)
		max_vel_router = {'medium':random.triangular(100,150,125), 'hard':random.triangular(100,200,160), 'easy':random.triangular(60,120,90)}
		max_acc_router = {'easy':250, 'hard':500, 'medium':400}
		color_router = {'medium':(255, 142, 43), 'easy':(255, 240, 89), 'hard':(255, 0, 89)}
		self.level = level
		self.max_velocity = max_vel_router.get(level)
		self.max_acceleration = max_acc_router.get(level)
		self.player_target = player_ref
		self.colorize(color_router.get(level))

	# Additional getters
	def getMaxVelocity(self): return self.max_velocity

	def getMaxAcceleration(self): return self.max_acceleration

	def getPlayerTarget(self): return self.player_target

	def slowMaxVelocity(self, new_vel): self.max_velocity = random.triangular(225,325,275)

	def colorize(self, rgb_tuple):
		r, g, b = rgb_tuple
		self.setFill(gr.color_rgb(r, g, b))


	# Userper methods
	def updateAbsentCollision(self, dt=.02):
		# Deal with position
		pos_x_new = self.getCenter().x + self.velocity[0]*dt + (.5*self.acceleration[0]*dt**2)
		pos_y_new = self.getCenter().y + self.velocity[1]*dt + (.5*self.acceleration[1]*dt**2)

		# Deal with velocity
		vel_x_new = self.acceleration[0]*dt + self.velocity[0]
		vel_y_new = self.acceleration[1]*dt + self.velocity[1]
		mag_vel = math.hypot(vel_x_new, vel_y_new)
		# Make sure it doesn't exceed the max velocity
		if mag_vel > self.getMaxVelocity():
			adjustment_factor = self.getMaxVelocity()/mag_vel
			vel_x_new *= adjustment_factor
			vel_y_new *= adjustment_factor

		# Point acceleration towards the player
		goal_pos = self.getPlayerTarget().getCenter()
		center = self.getCenter()
		dx = goal_pos.getX() - center.getX()
		dy = goal_pos.getY() - center.getY()
		d_hypot = math.hypot(dx, dy)
		adjustment_factor = self.getMaxAcceleration()/d_hypot
		dx *= adjustment_factor
		dy *= adjustment_factor

		# Set the various vectors
		self.setPosition([pos_x_new, pos_y_new])
		self.setVelocity([vel_x_new, vel_y_new])
		self.setAcceleration([dx, dy])

	def __repr__(self): return 'scum'

	def __str__(self): return 'scum'

class ShittySnowman(gr.Circle):

	global shapes

	def __init__(self, bottom_center, bottom_radius, velocity=[0,0], acceleration=[0,0], elasticity=.4, color=('white'), type='Shitty Snowman'):
		'''Give this function a Point object for the center of the bottom circle of the snowman and a radiius for the bottom of the snowman.'''
		top_center = gr.Point(bottom_center.getX(), bottom_center.getY()+2.3*bottom_radius)
		top = Ball.forSnowman(top_center, .63*bottom_radius, velocity, acceleration, elasticity, color, type)
		middle_center = gr.Point(bottom_center.getX(), bottom_center.getY()+1.3*bottom_radius)
		middle = Ball.forSnowman(middle_center, .85*bottom_radius, velocity, acceleration, elasticity, color, type)
		bottom = Ball.forSnowman(bottom_center, bottom_radius, velocity, acceleration, elasticity, color, type)
		body_parts = [bottom, middle, top]
		self.body_parts = body_parts
		self.type = type
		for circle in body_parts:
			circle.setFill(color)
			circle.color = color
			circle.velocity = velocity
			circle.acceleration = acceleration
			circle.elasticity = elasticity
			circle.type = type
		shapes.append(self)
	
	# Getter methods
	def getBodyParts(self): return self.body_parts

	def getVelocity(self): return self.velocity

	def getAcceleration(self): return self.acceleration

	def getElasticity(self): return self.elasticity

	def getColor(self): return self.color

	def getType(self): return self.type

	# Setter methods
	@is_two_element_list
	def setPosition(self, new_pos):
		dx = new_pos[0] - self.getBodyParts()[0].getCenter().getX()
		dy = new_pos[1] - self.getBodyParts()[0].getCenter().getY()
		self.move(dx, dy)
		self.position = new_pos

	@is_two_element_list
	def setVelocity(self, new_vel): self.velocity = new_vel

	@is_two_element_list
	def setAcceleration(self, new_acc): self.acceleration = new_acc

	# Usurper methods
	def draw(self, graphwin):
		for circle in self.getBodyParts():
			circle.draw(graphwin)

	def move(self, dx, dy):
		for circle in self.getBodyParts():
			circle.move(dx, dy)

	# Dunder methods
	def __repr__(self): return [circle.__repr__() for circle in self.getBodyParts()]

class Triangle(gr.Polygon):

	# global variable imports
	global shapes

	# Initialization
	def __init__(self, center, dist_to_extreme, velocity=[0,0], acceleration=[0,0], elasticity=.35, color=(0, 0, 0), type='Triangle'):
		'''Give this function a Point object for a center and an int to represent the distance towards extremes.'''
		self.top_point = gr.Point(center.getX(), center.getY()+dist_to_extreme)
		self.left_point = gr.Point(center.getX()+dist_to_extreme*math.cos((7/6)*math.pi), center.getY()+dist_to_extreme*math.sin((7/6)*math.pi))
		self.right_point = gr.Point(center.getX()+dist_to_extreme*math.cos((11/6)*math.pi), center.getY()+dist_to_extreme*math.sin((11/6)*math.pi))
		super().__init__([self.top_point, self.left_point, self.right_point])
		self.center = center
		self.velocity = velocity
		self.acceleration = acceleration
		self.elasticity = elasticity
		self.color = color
		self.type = type
		r, g, b = color
		self.setFill(gr.color_rgb(r, g, b))
		shapes.append(self)

	# Getter methods
	def getRadius(self): return self.getWidth()/2

	def getCenter(self): return self.center

	def getPosition(self): return [self.center.getX(), self.center.getY()]

	def getWidth(self): return self.right_point.getX() - self.left_point.getX()

	def getVelocity(self): return self.velocity

	def getAcceleration(self): return self.acceleration

	def getElasticity(self): return self.elasticity

	def getColor(self): return self.color

	def getType(self): return self.type

	# Setter methods
	@is_two_element_list
	def setPosition(self, new_pos):
		self.position = new_pos
		dx = new_pos[0] - self.getCenter().getX()
		dy = new_pos[1] - self.getCenter().getY()
		self.move(dx, dy)

	@is_two_element_list
	def setVelocity(self, new_vel): self.velocity = new_vel

	@is_two_element_list
	def setAcceleration(self, new_acc): self.acceleration = new_acc
			
class RotatingLine(gr.Line):

	global shapes

	def __init__(self, p1, p2, win, aor=None, omega=0):
		'''Give this a start and an end point (gr.Point objects) and a GraphWin object reference. kwargs = axis of rotation (aor) and rotational velocity (omega).'''
		super().__init__(p1, p2)
		self._win = win
		self.position = [statistics.mean([p1.getX(), p2.getX()]), statistics.mean([p1.getY(), p2.getY()])]
		delta_x = p1.getX() - p2.getX()
		delta_y = p1.getY() - p2.getY()
		self.length = math.hypot(delta_x, delta_y)			# Determine the length of the line using the distance formula
		self.height = 1
		if aor != None:
			self.aor = aor
		else:
			self.aor = self.position[:]
		self.points = [p1, p2]
		try:
			self.theta = math.atan(delta_y/delta_x)			# Use the angle the points make to find theta without explicitly stating it
		except ZeroDivisionError:
			self.theta = pi/2								# If the line is vertical, theta must be manually assinged
		self.omega = omega
		shapes.append(self)

	# Getter methods
	def getPoints(self): return self.points

	def getAOR(self): return self.aor

	def getTheta(self): return self.theta

	def getOmega(self): return self.omega

	def getLength(self): return self.length

	def getWidth(self): return self.width

	def getHeight(self): return self.height

	# Setter methods
	def setTheta(self, new_theta):
		d_theta = new_theta - self.getTheta()
		return self.rotate(d_theta)

	@is_two_element_list
	def setAOR(self, new_aor): self.aor = new_aor

	@is_two_element_list
	def setPosition(self, new_pos):
		dx = new_pos[0] - self.getCenter().getX()
		dy = new_pos[1] - self.getCenter().getY()
		self.move(dx, dy)
		self.position = new_pos

	@is_not_negative_num
	def setLength(self, new_len, update=False):
		center = self.position
		theta = self.getTheta()
		half_len = new_len/2
		dx = cos(theta)*half_len
		dy = sin(theta)*half_len
		p1 = gr.Point(center[0] + dx, center[1] + dy)
		p2 = gr.Point(center[0] - dx, center[1] - dy)
		new_line = RotatingLine(p1, p2, self._win, self.getAOR(), self.getOmega())			# This function just remakes the line
		RotatingLine.replace_on_win(self, new_line, update)
		return new_line

	# Utility methods
	def rotate(self, d_theta, update=False):
		'''This function rotates the line by d_theta. kwargs = update (default False). Returns the new Line object.'''
		pts = [RotatingLine.pt_to_list(i) for i in self.getPoints()]
		aor = self.getAOR()
		new_pts = []
		for pt in pts:							# Translate the points, rotate, then move back before creating the new shape.
			x_old = pt[0] - aor[0]
			y_old = pt[1] - aor[1]
			x_new = x_old*cos(d_theta) - y_old*sin(d_theta) + aor[0]
			y_new = x_old*sin(d_theta) + y_old*cos(d_theta) + aor[1]
			new_pts.append(gr.Point(x_new, y_new))
		new_line = RotatingLine(new_pts[0], new_pts[1], self._win, aor, self.getOmega())
		RotatingLine.replace_on_win(self, new_line, update)
		return new_line

	@staticmethod
	def dist_formula(point1, point2):		# The distance formula
		delta_x = point1[0] - point2[0]
		delta_y = point1[1] - point2[1]
		return math.hypot(delta_x, delta_y)

	@staticmethod
	def pt_to_list(point): return [point.getX(), point.getY()]		# Converts a Point object into its corresponding list

	@staticmethod
	def replace_on_win(old, new, update):			# Undraws an old object and removes it from memorty and the shapes list and draws the new object. Updates the window if update is passed
		old.undraw()
		shapes.remove(old)
		del(old)
		new.draw(new._win)
		if update:
			new._win.update()

class RotatingBlock(gr.Polygon):

	global shapes

	def __init__(self, points, grwin, aor=None, omega=0, elasticity=.4, color=(0, 0, 0), type='Rotating Block'):
		super().__init__(points)
		self._win = grwin
		x_values = [point.getX() for point in points]
		y_values = [point.getY() for point in points]
		self.position = [statistics.mean(x_values), statistics.mean(y_values)]		# The center is the average of all the points
		delta_y = points[0].getY() - points[3].getY()
		delta_x = points[0].getX() - points[3].getX()
		self.width = math.hypot(delta_y, delta_x)			# The width is the length of one of the sides
		dy = points[0].getY() - points[1].getY()
		dx = points[0].getX() - points[1].getX()
		self.height = math.hypot(dy, dx)					# The height is the length of a side perpendicular to the one used to calculate width
		if aor != None:
			self.aor = aor
		else:
			self.aor = self.position[:]
		self.points = points
		try:
			self.theta = math.atan(delta_y/delta_x)			# Using the width to set theta
		except ZeroDivisionError:
			self.theta = pi/2
		self.omega = omega
		self.elasticity = elasticity
		self.color = color
		self.type = type
		if isinstance(self.color, tuple):
			r, g, b = self.color
			self.setFill(gr.color_rgb(r, g, b))
		elif isinstance(self.color, str):
			self.setFill(self.color)
		shapes.append(self)

	@classmethod
	def flatInitiation(cls, width, height, center, grwin, aor=None, omega=0, elasticity=.4, color=(0, 0, 0), type='Rotating Block'):
		'''If a width and height and center initiation is required, this converts those parameters into a list of points to use for the normal __init__ method.'''
		p1 = gr.Point((center[0] - width/2), (center[1] - height/2))
		p2 = gr.Point((center[0] - width/2), (center[1] + height/2))
		p3 = gr.Point((center[0] + width/2), (center[1] + height/2))
		p4 = gr.Point((center[0] + width/2), (center[1] - height/2))
		points = [p1, p2, p3, p4]
		box = cls(points, grwin, aor=aor, omega=omega, elasticity=elasticity, color=color, type=type)
		return box

	# Getter methods
	def getPoints(self): return self.points

	def getElasticity(self): return self.elasticity

	def getAOR(self): return self.aor

	def getTheta(self): return self.theta

	def getOmega(self): return self.omega

	def getWidth(self): return self.width

	def getHeight(self): return self.height

	def getType(self): return self.type

	def getPosition(self): return self.position

	def getBoundingBox(self):
		'''Returns a tuple containing the length of the radius of the bounding box and the center position.'''
		edge = RotatingLine.pt_to_list(self.getPoints()[0])
		position = self.getPosition()
		r = RotatingLine.dist_formula(edge, position)
		return (r, position)		# A circle is used to represent the box because it is spinning and therefore cannot be represented with a standard bounding box

	# Setter methods
	@is_two_element_list
	def setAOR(self, new_aor): self.aor = new_aor

	@is_num
	def setOmega(self, new_omega): self.omega = new_omega

	@is_num
	def setTheta(self, new_theta):
		d_theta = new_theta - self.getTheta()
		return self.rotate(d_theta)

	@is_not_negative_num
	def setWidth(self, new_width, update=False):
		new_rect = RotatingBlock.flatInitiation(new_width, self.getHeight(), self.getPosition(), self._win, aor=self.getAOR(), omega=self.getOmega(), elasticity=self.getElasticity(), color=self.getColor(), type=self.getType())
		theta = self.getTheta()
		new_rect = new_rect.setTheta(theta)
		RotatingLine.replace_on_win(self, new_rect, update)
		return new_rect

	@is_not_negative_num
	def setHeight(self, new_height, update=False):
		new_rect = RotatingBlock.flatInitiation(self.getWidth(), new_height, self.getPosition(), self._win, aor=self.getAOR(), omega=self.getOmega(), elasticity=self.getElasticity(), color=self.getColor(), type=self.getType())
		theta = self.getTheta()
		new_rect = new_rect.setTheta(theta)
		RotatingLine.replace_on_win(self, new_rect, update)
		return new_rect

	# Utility Methods
	@is_num
	def rotate(self, d_theta, update=False):
		pts = [RotatingLine.pt_to_list(i) for i in self.getPoints()]		# Get a list of points
		aor = self.getAOR()
		new_pts = []
		for pt in pts:
			x_old = pt[0] - aor[0]
			y_old = pt[1] - aor[1]				# Move axis of rotation to center
			x_new = x_old*cos(d_theta) - y_old*sin(d_theta) + aor[0]		# Rotate about center and add aor back in
			y_new = x_old*sin(d_theta) + y_old*cos(d_theta) + aor[1]
			new_pts.append(gr.Point(x_new, y_new))
		new_polygon = RotatingBlock(new_pts, self._win, aor, self.getOmega(), self.elasticity, self.color, self.type)
		RotatingLine.replace_on_win(self, new_polygon, update)			# Create a new object and replace the old one then return the new one
		return new_polygon

	def reverseOmega(self): self.setOmega(-1*self.getOmega())

	@is_num
	def update(self, dt):
		da = self.getOmega() * dt
		if da != 0:
			new_obj = self.rotate(da)
		return new_obj

	def __repr__(self): return f'Polygon: {self.getPoints()[0]}{self.getPoints()[1]}{self.getPoints()[2]}{self.getPoints()[3]}'

# Program execution
def main():
	# Allows all the functionality of the program to be run from command line
	function_router = {'itemTwo':itemTwo, 'ballTest':ballTest, 'blockTest':blockTest, 'triangleTest':triangleTest, 'snowmanTest':snowmanTest}
	# Parser used to determine what funcitonaly is desired
	parser = argparse.ArgumentParser()
	parser.add_argument('--optfunc', type=str, choices=['itemTwo', 'ballTest', 'blockTest', 'triangleTest', 'snowmanTest'], help='perform one of the test functions')
	args = parser.parse_args()
	# Run the obstacle course if no flag called, but run the chosen function if a flag is called
	if not args.optfunc:
		obstacleCourse()
	else:
		function_router[args.optfunc]()

def test():
	win = gr.GraphWin('test', 500, 500, False)
	win.setCoords(0, 0, 500, 500)
	test_ball = Ball(gr.Point(100, 100), 15)
	test_ball.draw(win)
	win.update()
	test_ball.setPosition([4, 5])
	win.getMouse()
	win.close()

if __name__ == '__main__':
	test()