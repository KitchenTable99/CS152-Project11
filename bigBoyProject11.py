# Caleb Bitting
# CS152
# Bruce and Caitrin
# Final Project
#

# Importing needed libraries
import random
import os
import pygame
import time
import graphicsPlus as gr
import physics_objects as pho
import collision as coll
import itertools
import concurrent.futures
from breakout import playAtari

class ObjectivesText():

	def __init__(self, center_point=gr.Point(450, 330), initial_string='This is the objectives and hint screen. You can toggle this\nmenu at any time by pressing \'o\'. Do so when you get stuck.\n You can walk around with the arrow keys and interact\nwith your environment using the space bar.\n\nTry walking to the table and interacting with it.', future_list=['How would you like to kill your husband?\n\nYou can shoot him or you can put sardine oil\non his clothes and let the tigers eat him.\n\nPress \'g\' for gun and \'s\' for sardine oil.', 'Walk to your husband and interact with him.\n\n\nInteract with your environment using the space bar.']):
		temp = gr.Text(center_point, initial_string)
		temp.setSize(20)
		temp.setFace('courier')
		temp.setFill('black')
		self.text_obj = temp
		center_x = center_point.getX()
		center_y = center_point.getY()
		temp = gr.Rectangle(gr.Point(center_x-360, center_y-260), gr.Point(center_x+360, center_y+260))
		temp.setFill('white')
		self.rect_obj = temp
		self.future_list = future_list
		if future_list[0] != initial_string:
			future_list.insert(0, initial_string)

	# Choose your own adventure methods/setter methods
	def sardineDeath(self):
		self.future_list.append('You pour the sardine oil on his shoes.\n\nWhat do you say to your husband\nto get him to go to the tiger enclosure?\n\nClick anywhere when you\'re ready to tell him.')

	def gunDeath(self):
		self.future_list.append('Drag your husband\'s body to the water tower.\nBury him by interacting at the water tower.\n\n\nInteract with your environment using the space bar.')

	# Utility methods
	def draw(self, window):
		for obj in [self.rect_obj, self.text_obj]:
			obj.draw(window)

	def undraw(self):
			for obj in [self.rect_obj, self.text_obj]:
				obj.undraw()

	def toggle(self, window):
		if self.text_obj.canvas:
			self.undraw()
		else:
			self.draw(window)

	# Dunder methods
	# Allow for a cycling text object
	def __next__(self):
		current_instruction = self.future_list.index(self.text_obj.getText())
		current_instruction += 1
		self.text_obj.setText(self.future_list[current_instruction])

	def __repr__(self): return f'ObjectivesText({self.center_point}, {self.initial_string}, {self.future_list})'

# Establishing some global variables
pygame.mixer.init(frequency=48000)
music_channel = pygame.mixer.Channel(0)
music_channel.set_volume(.5)
sound_effects_channel = pygame.mixer.Channel(1)
win_sound = pygame.mixer.Sound('./audio_files/successNoise.ogg')
loss_sound = pygame.mixer.Sound('./audio_files/wrongBuzzer.ogg')
loss_sound.set_volume(.4)

shapes = pho.shapes

def userReady(window):
	'''Wait until the user presses the space bar. (Parameters: a GraphWin object)'''
	ready = False
	while not ready:
		key = window.checkKey()
		if key == 'space':
			ready = True
		window.update()

def rectangleBoundingBox(rect):
	'''Given a Rectangle object, this returns a tuple of a bounding box. (lowX, highX, lowY, highY)'''
	rect_p1 = rect.getP1()
	rect_p2 = rect.getP2()
	return (rect_p1.getX(), rect_p2.getX(), rect_p1.getY(), rect_p2.getY())

def displayMenu(activities_done, title_router):
	'''This function displays the main menu. (Parameters: a list of indices specifing which activities the player has already succeed at,
	   a title router to specify the words on the boxes::this function returns the index coresponding with the mini-game the user picked).'''
	# Create the window
	win = gr.GraphWin('Main Menu', 650, 500, False)
	win.setCoords(0, 0, 640, 500)
	win.setBackground('dark slate grey')

	# Create all the rectangles
	mini_games = []
	text_items = []
	points = [gr.Point(57, 210), gr.Point(187, 300)]		# The first box will be initialized with these points
	for _ in range(3):
		temp = gr.Rectangle(points[0], points[1])
		mini_games.append(temp)
		temp.setFill('slate grey')
		cent_point = temp.getCenter()						# Make sure the box has a corresponding label
		temp_text = gr.Text(cent_point, 'filler')
		text_items.append(temp_text)
		for point in points:								# Move the box over one
			point.move(200, 0)
	for game in mini_games[:]:								# Copy the above row exactly, but a 150 further down
		temp = game.clone()
		temp.move(0, -150)
		mini_games.append(temp)
		cent_point = temp.getCenter()
		temp_text = gr.Text(cent_point, 'filler')
		text_items.append(temp_text)

	# Check to see if the user has seen the menu before and handle both cases (play music/green out mini-games)
	if isinstance(activities_done, list):
		for completed_game in activities_done:		# Green out the completed mini-games
			mini_games[completed_game].setFill('green')	
		play_music = gr.Text(gr.Point(575, 20), 'Play music')
		play_music.setSize(9)
		text_items.append(play_music)
		music_rect = gr.Rectangle(gr.Point(545, 10), gr.Point(605, 30))
		music_rect.setFill('slate grey')
		mini_games.append(music_rect)
	else:
		print('It\'s The End Of The World As We Know It --R.E.M')
		music_channel.play(pygame.mixer.Sound('./audio_files/menuMusic.ogg'))

	# Write the correct titles for the games (instead of the string filler)
	for i in range(6):
		name, size = title_router[str(i)]
		text_items[i].setText(name)
		text_items[i].setSize(size)

	#Create all the remaining text elements
	header = gr.Text(gr.Point(325, 425), 'Welcome to the COVID-19 activity box!')
	header.setSize(26)
	text_items.append(header)
	directions = gr.Text(gr.Point(325, 385), 'Please click on your desired activity')
	directions.setSize(18)
	text_items.append(directions)		

	# Draw everything
	for thing in itertools.chain(mini_games, text_items):
		thing.draw(win)
	for item in text_items:
		item.setFace('courier')
		item.setFill('white')

	# Handle click
	action = False
	bounding_boxes = [rectangleBoundingBox(rectangle) for rectangle in mini_games]
	while not action:
		click = win.getMouse()
		for index, bounding_box in enumerate(bounding_boxes):				# Check to see if the user clicked in a box
			lowX, highX, lowY, highY = bounding_box
			if lowX <= click.getX() <= highX and lowY <= click.getY() <= highY:
				if index == 6:
					music_channel.set_volume(.5)
					print('It\'s The End Of The World As We Know It --R.E.M')
					music_channel.play(pygame.mixer.Sound('./audio_files/menuMusic.ogg'))		# If exactly the play music box is clicked, play the music but keep looping
				elif isinstance(activities_done, list) and index in activities_done:								# Make sure user hasn't successfully completed the selected mini-game
					pass
				else:
					action = True
					break
	# Stop the music, close the window, and return the chosen index
	pygame.mixer.fadeout(750)
	music_channel.set_volume(.5)
	win.close()
	return index


def playTigerKing():
	'''Play the Tiger King mini-game.'''
	# Initialize some things
	win = gr.GraphWin('Hey All You Cool Cats And Kittens', 900, 650, False)
	win.setCoords(0, 0, 900, 650)
	win.setBackground(gr.color_rgb(188, 141, 96))

	# Player
	carol_baskin = pho.Ball(gr.Point(450, 325), 25, color=(240, 132, 172))
	husband = pho.Block(gr.Point(180, 56), 35, 35, color=(45, 110, 238))

	# Draw instruction words
	instructions = gr.Text(gr.Point(450, 335), 'You are Carol Baskin (a pink ball) and want to kill your husband.\nGood luck and God speed.\n\n\n\npress space to start...')
	instructions.setSize(20)
	instructions.setFace('courier')
	instructions.setFill('black')

	# Create the objectives text object
	objectives_text = ObjectivesText()

	# Lists needed to make the background image objects
	image_list = []
	image_list.append('./image_files/tiger.gif')
	image_list.append('./image_files/waterTower.gif')
	image_list.append('./image_files/house.gif')
	image_list.append('./image_files/table.gif')
	anchor_list = [gr.Point(79, 582), gr.Point(794, 571), gr.Point(123, 94), gr.Point(776, 73)]

	# Instantiate the image resources
	environmental_image_objects = []
	for image, anchor in zip(image_list, anchor_list):
		temp = gr.Image(anchor, image)
		environmental_image_objects.append(temp)

	image_resource_dict = {}
	firingGun = gr.Image(gr.Point(0,0), './image_files/firingGun.gif')
	image_resource_dict['firingGun'] = firingGun
	gun = gr.Image(gr.Point(0,0), './image_files/gun.gif')
	image_resource_dict['gun'] = gun
	meat = gr.Image(gr.Point(0,0), './image_files/meat.gif')
	image_resource_dict['meat'] = meat
	fish = gr.Image(gr.Point(0,0), './image_files/fish.gif')
	image_resource_dict['fish'] = fish
	skull = gr.Image(gr.Point(0,0), './image_files/skull.gif')
	image_resource_dict['skull'] = skull
	sideOfTable = gr.Image(gr.Point(0,0), './image_files/sideOfTable.gif')
	image_resource_dict['sideOfTable'] = sideOfTable
	sardineOil = gr.Image(gr.Point(0,0), './image_files/sardineOil.gif')
	image_resource_dict['sardineOil'] = sardineOil
	pistol = gr.Image(gr.Point(0,0), './image_files/pistol.gif')
	image_resource_dict['pistol'] = pistol

	# Threading capabilities
	executor = concurrent.futures.ThreadPoolExecutor()

	# Interaction router
	interactive_router = {}
	interactive_router[0] = doNothing
	interactive_router[1] = waterTowerInteraction
	interactive_router[2] = houseInteraction
	interactive_router[3] = tableInteraction
	interactive_router[None] = doNothing

	# Draw instructions and wait for user press
	instructions.draw(win)
	userReady(win)

	# After ready-up, prepare for gameplay
	instructions.undraw()
	for thing in itertools.chain(environmental_image_objects, shapes):
		thing.draw(win)
	objectives_text.toggle(win)
	
	# Play!
	done = False
	close_obj = None
	pick = 'g'
	table = False
	carry_body = False
	music_channel.play(pygame.mixer.Sound('./audio_files/hereKittyKitty.ogg'))
	print('Here Kitty Kitty --Joe Exotic')
	while not done:
		# Check to see if the user pressed a key
		key = win.checkKey()
		if key == 'Up':
			carol_baskin.moveUp()
			if carry_body:
				image_resource_dict['skull'].move(0, 10)
		elif key == 'Left':
			carol_baskin.moveLeft()
			if carry_body:
				image_resource_dict['skull'].move(-10, 0)
		elif key == 'Down':
			carol_baskin.moveDown()
			if carry_body:
				image_resource_dict['skull'].move(0, -10)
		elif key == 'Right':
			carol_baskin.moveRight()
			if carry_body:
				image_resource_dict['skull'].move(10, 0)
		elif key == 'o':
			objectives_text.toggle(win)
		elif key == 'space':
			close_obj = carol_baskin.isClose(environmental_image_objects)

		# Call whatever function is needed based on what Carol is closed to
		reaction = interactive_router[close_obj](image_resource_dict, win, objectives_text, pick, hubbie=husband, normal_elements=itertools.chain(environmental_image_objects, shapes))
		# Deal with that reaction
		if reaction == 'g' or reaction == 's':
			pick = reaction
		if reaction == 'win':
			win.close()
			pygame.mixer.fadeout(750)
			music_channel.set_volume(.5)
			carol_baskin.undraw()
			shapes.remove(carol_baskin)
			return True
		if reaction == 'killed':
			carry_body = True

		# Redraw anything that got undrawn
		for thing in itertools.chain(environmental_image_objects, shapes):
			if not thing.canvas:
				thing.draw(win)

		close_obj = None 				# make sure that the interactive router isn't called a billion times
		win.update()

def tableInteraction(image_resource_dict, window, objectives_text, *args, normal_elements, **kwargs):
	'''This function deals with the interaction of Carol Baskin at the table. The arguments are really complicated because of the next two functions. This one takes a dictionary
	   of Image references, a GraphWin object, and the scrolling text for the menu, plus the elements that comprise the 'normal' window of this game. It returns a string
	   corresponding to the player's choice of death mechanism (s or g)'''
	init_time = time.time()
	seen_directions = False
	# Undraw everything
	for thing in normal_elements:
		thing.undraw()
	# Draw the appropriate images
	image_resource_dict['sideOfTable'].move(450, 300)
	image_resource_dict['sideOfTable'].draw(window) 
	image_resource_dict['sardineOil'].move(615, 483)
	image_resource_dict['sardineOil'].draw(window)
	image_resource_dict['pistol'].move(285, 433)
	image_resource_dict['pistol'].draw(window)
	window.update()
	# Advance the intructions and display that menu
	next(objectives_text)
	# Wait for user input
	done = False
	while not done:
		key = window.checkKey()
		if key == 'g' or key == 's':
			# Undraw the fish and gun and table
			image_resource_dict['sideOfTable'].undraw()
			image_resource_dict['pistol'].undraw()
			image_resource_dict['sardineOil'].undraw()
			# Advance instructions
			done = True
			if key == 'g': objectives_text.gunDeath()
			else: objectives_text.sardineDeath()
		elif key == 'o':
			objectives_text.toggle(window)
			seen_directions = True
		if time.time() - init_time >= 3.5 and not seen_directions:
			objectives_text.toggle(window)
			seen_directions = True
		window.update()
	next(objectives_text)
	if objectives_text.rect_obj.canvas:
		objectives_text.undraw()
	return key

def houseInteraction(image_resource_dict, window, objectives_text, pick, hubbie, **kwargs):
	'''This function deals with the interaction at the House. It takes a dictionary of image resources, a GraphWin, the scrolling text, the user chioce of death, and a reference
	   to the husband object. It returns 'killed' if the gun death was chosen or 'win' if the sardine death was chosen.'''
	# Gun death
	if pick == 'g':
		# Shoot the husband
		image_resource_dict['firingGun'].move(220, 50)
		image_resource_dict['firingGun'].draw(window)
		window.update()
		music_channel.pause()
		sound_effects_channel.play(pygame.mixer.Sound('./audio_files/gunshot.ogg'))
		time.sleep(.7)
		music_channel.unpause()
		# Hide the gun
		image_resource_dict['firingGun'].undraw()
		# Replace the husband with a skull
		h_pos = hubbie.getPosition()
		hubbie.undraw()
		shapes.remove(hubbie)
		image_resource_dict['skull'].move(h_pos[0], h_pos[1])
		image_resource_dict['skull'].draw(window)
		window.update()
		# Advance the instructions
		next(objectives_text)
		return 'killed'
	# Sardine death
	else:
		# Play a splash sound
		sound_effects_channel.play(pygame.mixer.Sound('./audio_files/splat.ogg'))
		# Advance the instructions
		next(objectives_text)
		# Display the instructions
		if not objectives_text.rect_obj.canvas:
			objectives_text.draw(window)
		# Ask for input
		entry = gr.Entry(gr.Point(450, 200), 50)
		entry.setFace('courier')
		entry.setSize(20)
		entry.setFill('white')
		entry.draw(window)
		window.getMouse()
		user_input = entry.getText()
		# Make the computer say it
		entry.undraw()
		objectives_text.toggle(window)
		window.update()
		os.system('say -v Samantha ' + user_input)
		# Animate husband walking over to pen
		hubbie.setVelocity([0, 50])
		for _ in range (342):
			hubbie.update()
			window.update()
		hubbie.setVelocity([-30, 50])
		for i in range (160):
			hubbie.update()
			window.update()
		# Play some sounds to make him die
		music_channel.set_volume(.2)
		sound_effects_channel.play(pygame.mixer.Sound('./audio_files/tigerRoar.ogg'))
		time.sleep(2)
		sound_effects_channel.play(pygame.mixer.Sound('./audio_files/wilhelmScream.ogg'))
		time.sleep(1)
		h_pos = hubbie.getPosition()
		image_resource_dict['skull'].move(h_pos[0], h_pos[1])
		image_resource_dict['skull'].draw(window)
		hubbie.undraw()
		shapes.remove(hubbie)
		window.update()
		time.sleep(3)
		return 'win'

def waterTowerInteraction(image_resource_dict, window, *args, hubbie, **kwargs):
	'''This function deals with the interaction at the water tower. It takes a dictionary of Image objects, a GraphWin object, and a reeference to the husband object.
	   It returns 'win'''
	# Bury the guy
	sound_effects_channel.play(pygame.mixer.Sound('./audio_files/dig.ogg'))
	time.sleep(5)
	image_resource_dict['skull'].undraw()
	window.update()
	time.sleep(3)
	return 'win'

def doNothing(*args, **kwargs):
	pass

def playMarieKondo():
	# Image dictionary
	image_resource_dict = {}
	bates = gr.Image(gr.Point(325, 250), './image_files/bates.gif')
	image_resource_dict['bates'] = bates
	clothes = gr.Image(gr.Point(325, 250), './image_files/clothes.gif')
	image_resource_dict['clothes'] = clothes
	harrypotteractionfigure = gr.Image(gr.Point(325, 250), './image_files/harrypotteractionfigure.gif')
	image_resource_dict['harrypotteractionfigure'] = harrypotteractionfigure
	kidDrawing = gr.Image(gr.Point(325, 250), './image_files/kidDrawing.gif')
	image_resource_dict['kidDrawing'] = kidDrawing
	mizuno = gr.Image(gr.Point(325, 250), './image_files/mizuno.gif')
	image_resource_dict['mizuno'] = mizuno
	oldBooks = gr.Image(gr.Point(325, 250), './image_files/oldBooks.gif')
	image_resource_dict['oldBooks'] = oldBooks
	pythonlogo = gr.Image(gr.Point(325, 250), './image_files/pythonlogo.gif')
	image_resource_dict['pythonlogo'] = pythonlogo
	pythonsnake = gr.Image(gr.Point(325, 250), './image_files/pythonsnake.gif')
	image_resource_dict['pythonsnake'] = pythonsnake
	goggles = gr.Image(gr.Point(325, 250), './image_files/goggles.gif')
	image_resource_dict['goggles'] = goggles
	image_list = list(image_resource_dict)

	# Create the window
	win = gr.GraphWin('Buck Fates', 650, 500, False)
	win.setCoords(0, 0, 650, 500)
	win.setBackground('dark slate grey')

	# Make visual items
	kondo_text_items = []
	input_boxes = []
	# Start with the instruction text
	disp_text = ObjectivesText(gr.Point(330, 350), 'You will be shown a series of images.\nYou must pretend like you are cleaning\nout your house. Think about Marie Kondo.\nWhat does and what does not\nspark joy when you look at it.\n\nThere is no wrong answer.\n\n \n \n press the space bar to continue...', ['This was going to be a personality test.', 'But I think we can cut it short now.','You lose.','Obviously.'])
	disp_text.text_obj.setFill('white')
	# Create the two boxes and their labesl
	yes = gr.Rectangle(gr.Point(60, 40), gr.Point(210, 140))
	yes.setFill('green')
	input_boxes.append(yes)
	yes_text = gr.Text(yes.getCenter(), 'This one\nsparks joy')
	yes_text.setFill('black')
	kondo_text_items.append(yes_text)
	no = gr.Rectangle(gr.Point(440, 40), gr.Point(590, 140))
	no.setFill('indian red')
	input_boxes.append(no)
	no_text = gr.Text(no.getCenter(), 'This one\ndoes not\nspark joy')
	no_text.setFill('black')
	kondo_text_items.append(no_text)
	# Set the common attributes for the text items
	for text in kondo_text_items:
		text.setSize(20)
		text.setFace('courier')

	# Display instructions and wait for user ready
	disp_text.draw(win)
	disp_text.rect_obj.undraw()
	print('Thank U Next --Ariana Grande')
	music_channel.play(pygame.mixer.Sound('./audio_files/thankYouNext.ogg'))
	userReady(win)
	disp_text.undraw()

	# Actual game
	# Draw the things
	for thing in itertools.chain(input_boxes, kondo_text_items):
		thing.draw(win)
	while len(image_list) != 0:
		rand_int = random.randint(0, len(image_list)-1)
		# Randomly select an image and remove it from the possible list
		rand_key = image_list.pop(rand_int)
		image_resource_dict[rand_key].draw(win)
		for thing in itertools.chain(input_boxes, kondo_text_items):
			thing.undraw()
			thing.draw(win)
		win.update()
		# Wait for the user to click on one of the two options
		is_click = False
		bounding_boxes = [rectangleBoundingBox(rectangle) for rectangle in input_boxes]
		while not is_click:
			click = win.getMouse()
			for index, bounding_box in enumerate(bounding_boxes):				# Check to see if the user clicked in a box
				lowX, highX, lowY, highY = bounding_box
				if lowX <= click.getX() <= highX and lowY <= click.getY() <= highY:
					is_click = True
					break
		# Make sure there wasn't any sacrilege
		if rand_key != 'bates':
			sound_effects_channel.play(win_sound)
			win.setBackground('lime')
			win.update()
			time.sleep(.5)
			win.setBackground('dark slate grey')
			win.update()
		elif index == 1:		# Bonus points for saying Bates is bad
			win.setBackground('lime')
			win.update()
			for _ in range(6):
				sound_effects_channel.play(win_sound)
				time.sleep(.4)
			win.setBackground('dark slate grey')
			win.update()
		elif index == 0:		# If you said Bates didn't spark joy the first time you played (first off good job), but go say that it does. This easter egg is good.
			music_channel.stop()
			win.setBackground('red')
			win.update()
			for _ in range(8):
				sound_effects_channel.play(loss_sound)
				time.sleep(.4)	
			image_resource_dict[rand_key].undraw()
			win.setBackground('dark slate grey')
			next(disp_text)
			disp_text.text_obj.draw(win)
			win.update()
			sound_effects_channel.play(pygame.mixer.Sound('./audio_files/gladosJoke.wav'))
			time.sleep(4)
			next(disp_text)
			win.update()
			time.sleep(4)
			sound_effects_channel.play(pygame.mixer.Sound('./audio_files/horriblePerson.wav'))
			time.sleep(11)
			next(disp_text)
			win.update()
			time.sleep(2)
			next(disp_text)
			win.update()
			time.sleep(3)
			win.close()
			return False
		image_resource_dict[rand_key].undraw()

	# After going through all the quotes:
	disp_text.draw(win)
	disp_text.rect_obj.undraw()
	for thing in itertools.chain(input_boxes, kondo_text_items):
		thing.undraw()
	# Display the end screen and return the result
	disp_text.text_obj.setFill('lime')	
	disp_text.text_obj.setText('you win!')
	win.update()
	time.sleep(2)
	pygame.mixer.fadeout(750)
	music_channel.set_volume(.5)
	win.close()
	return True

def timer(sleep_time):
	'''Given some time in seconds, this function will count down.'''
	while sleep_time > 0:
		time.sleep(1)
		sleep_time -= 1

def playGoForRun():
	'''Plays the Running mini-game.'''
	# Initialize some things
	win = gr.GraphWin('Go for a run', 1200, 800, False)
	win.setCoords(0, 0, 1200, 800)
	win.setBackground('light grey')

	# Player
	player = pho.Ball(gr.Point(500, 500), 15, color=(0, 255, 0), velocity=[.0001,.0001])

	# Draw instruction words
	instructions = gr.Text(gr.Point(600, 400), 'You (a green ball) went for a run, but encountered some\naggressive Coronavirus protesters (red balls).\nDon\'t let them give you Coronavirus!\n\nMake sure the entire window is on screen\nSurvive the duration of the song to win!\n\n\n\nPress space to start')
	instructions.setSize(20)
	instructions.setFace('courier')
	instructions.setFill('black')

	# Create router
	direction_router = {}
	direction_router['top'] = gr.Point(random.randint(0,1200), 820)
	direction_router['right'] = gr.Point(1220, random.randint(0, 800))
	direction_router['bottom'] = gr.Point(random.randint(0,1200), -20)
	direction_router['left'] = gr.Point(-20, random.randint(0, 800))

	# Draw instructions and wait for user press
	instructions.draw(win)
	userReady(win)

	# After ready-up, prepare game for play
	instructions.undraw()
	protesters = []
	for _ in range(3):
		random_center = gr.Point(random.randint(400, 1000)+300, random.randint(400, 800)+200)
		temp = pho.CoronaProtester(random_center, 15, 'easy', player)	
		protesters.append(temp)
	for shape in shapes:
		shape.draw(win)
	win.update()

	# Game loop
	chase = True
	# Play music
	print('Don\'t Stand So Close To Me --The Police')
	music_channel.play(pygame.mixer.Sound('./audio_files/walkDog.ogg'))

	# Run the game
	start_time = time.time()
	init_time = time.time()
	while chase:
		# Check for collisions
		possible_collisions = list(itertools.combinations(shapes, 2))
		shapes_collided = set()
		for col in possible_collisions:
			shape1, shape2 = col
			collided = coll.collision(shape1, shape2, .02)
			if collided:
				if shape1 == player or shape2 == player:
					chase = False
					break
				shapes_collided.add(shape1)
				shapes_collided.add(shape2)
		# Move non-colided objects
		maybe_moves = set(protesters)
		for shape in maybe_moves - shapes_collided:
			shape.updateAbsentCollision()

		# Check for user input
		key = win.checkKey()
		if key == 'Up':
			player.moveUp()
		elif key == 'Left':
			player.moveLeft()
		elif key == 'Down':
			player.moveDown()
		elif key == 'Right':
			player.moveRight()
		elif key == 's':
			os.system('open https://www.youtube.com/watch?v=dQw4w9WgXcQ')		# Go try this one
			
		win.update()

		# Check to see if timers are done
		if time.time() - init_time >= random.triangular(20, 40, 30):
			difficulty = random.choice(['easy', 'medium', 'hard'])
			direction = random.choice(['top', 'left', 'bottom', 'right'])
			temp = pho.CoronaProtester(direction_router.get(direction), 15, difficulty, player)	
			temp.draw(win)
			protesters.append(temp)
			init_time = time.time()
		if not music_channel.get_busy():
			chase = False

	total_time = time.time() - start_time
	music_channel.stop()
	# Deal with results of mini-game
	filler_text = gr.Text(gr.Point(600, 400), 'filler')
	filler_text.setFace('courier')
	filler_text.setSize(28)
	filler_text.draw(win)
	# Change the text and return the proper boolean value
	if total_time < 159:
		filler_text.setText('you lose :((\n\nYou lived for ' + str(round(total_time,2)) +' seconds.\n\nLive for 159 seconds to win.\nNext time press \'s\' to move faster.')
		filler_text.setFill('red')
		click = None
		init_time = time.time()
		while not click:
			click = win.checkMouse()
			if time.time() - init_time >= 5:
				break
			win.update()
		for ball in protesters:
			shapes.remove(ball)
			ball.undraw()
		shapes.remove(player)
		player.undraw()
		win.close()
		return False
	else:
		if total_time < 240:
			filler_text.setText('you win!\n\nYou lived for ' + str(round(total_time,2)) +' seconds.\n\nNot quite a perfect score, but I\'ll allow it.')
		else:
			filler_text.setText('you win!\n\nYou lived for 240 seconds.\n\nA perfect score! That\'s really difficult')
		filler_text.setFill('green')
		win.update()
		time.sleep(2)
		for ball in protesters:
			shapes.remove(ball)
			ball.undraw()
		shapes.remove(player)
		player.undraw()
		win.close()
		return True

def playFakeNews():
	'''Plays the Fake News mini-game'''
	# Create the quote and headline dictionaries
	trump_crazy = {}
	trump_crazy['"[Hillary] got schlonged, she lost, \nI mean she lost."'] = (True, 'Grand Rapids, Michigan rally::21 December 2015')
	trump_crazy['"You know, I see things -- I see numbers. \nThey don\'t matter to me."'] = (True, 'Rose Garden press breifing::29 March 2020')
	trump_crazy['"I’ve spoken to three, maybe, I guess, four\nfamilies unrelated to me. I lost a very\ngood friend. I also lost three other \nfriends — two of whom I didn’t know as \nwell, but they were friends and people I\ndid business with."'] = (True, 'White House Press Breifing::https://www.whitehouse.gov/briefings-statements/remarks-president-trump-supporting-nations-small-businesses-paycheck-protection-program/')
	trump_crazy['Q: What do you say to Americans who are \nwatching you right now, who are scared? \n\nA: I say that you\'re a terrible reporter. \nThat\'s what I say. I think that’s a \nvery nasty question and I think it’s\na very bad signal that you’re putting\nout to the American people.'] = (True, 'White House Press Breifing')
	trump_crazy['"And then I said, supposing you brought \nthe light inside of the body, which you \ncan do either through the skin or in some\nother way. And I think you said you\'re\ngoing to test that too. Sounds interesting."'] = (True, 'White House Press Breifing')
	trump_crazy['"When I hear facemasks go from 10,000 to\n300,000, and they constantly need more,\nand the biggest man in the business is,\nlike, shocked."'] = (True, 'White House Press Breifing')
	trump_crazy['"If [the economic shutdown continues],\ndeaths by suicide definitely would be in\nfar greater numbers than the [COVID-19\ndeath] numbers that we’re talking about."'] = (True, 'White House Press Breifing')
	trump_crazy['"Obviously, if you count blacks, it’s\ngoing to throw off your estimates of how\nbad this thing is. We’re doing a fantastic\njob containing the virus, but sadly some\ngovernors are stooping so low as to fake\ntheir numbers—not only with blacks, but\nwith people born in other countries, too."'] = (False, 'The Onion::https://www.theonion.com/trump-accuses-new-york-of-padding-state-s-mortality-rat-1843113132')
	trump_crazy['"For all of you out there who are worried\nabout contracting the Chinese virus,\njust go to a doctor who will just say you\nare totally healthy no matter what."'] = (False, 'The Onion::https://www.theonion.com/trump-advises-americans-worried-about-coronavirus-to-ju-1842318703')
	trump_crazy['Trump Quietly Checks With Aides To Make\nSure He’d Be Included In Receiving $1,000\nGovernment Checks'] = (False, 'The Onion')
	trump_crazy['Trump Administration Releases Best Case\nScenario Projections For Coronavirus\nWhere 8 Million Iranian People Die'] = (False, 'The Onion')
	trump_crazy['Trump Suggests Ceding New York To\nCoronavirus As Possible\nAppeasement Strategy'] = (False, 'The Onion')
	trump_crazy['Trump Announces Plan To Retrain Nation’s\n3 Million Unemployed Americans As\nHuman Ventilators'] = (False, 'The Onion')
	trump_crazy['Trump Delays Easter To July 15 To Keep\nPromise On Coronavirus'] = (False, 'The Onion')
	trump_crazy['Trump Tackles Medical Supply Shortage\nBy Awarding ExxonMobil Contract To Drill\nFor Ventilators In Arctic'] = (False, 'The Onion')
	trump_crazy['Trump Admits 18 New States To Increase\nCompetition For Medical Supplies'] = (False, 'The Onion')
	trump_crazy['Amid a Rising Death Toll, Trump Leaves\nThe Grieving To Others'] = (True, 'New York Times')
	trump_crazy['Trump Rips George W. Bush After He Calls\nFor Unity Amid Coronavirus Outbreak'] = (True, 'The Hill')
	trump_crazy['Trump’s ‘Operation Warp Speed’ Aims\nto Rush Coronavirus Vaccine'] = (True, 'Bloomberg')
	trump_crazy['Trump Suggested ‘Injecting’ Disinfectant\nto Cure Coronavirus?'] = (True, 'New York Times')
	trump_crazy_list = list(trump_crazy)

	# Create the window
	win = gr.GraphWin('Fake News?', 650, 500, False)
	win.setCoords(0, 0, 650, 500)
	win.setBackground('dark orange')

	# Make visual items
	trump_text_items = []
	input_boxes = []
	# Start with the instruction text
	disp_text = gr.Text(gr.Point(330, 350), 'You will be shown a series of quotes \nand headlines all about President Trump \n(hence the orange background)\nDetermine if the displayed item is\ntrue or FAKE NEWS. \n \n \n \n press the space bar to continue...')
	disp_text.setFill('white')
	trump_text_items.append(disp_text)
	# Create the two boxes and their labesl
	yes = gr.Rectangle(gr.Point(60, 40), gr.Point(210, 140))
	yes.setFill('light green')
	input_boxes.append(yes)
	yes_text = gr.Text(yes.getCenter(), 'True')
	yes_text.setFill('dark green')
	trump_text_items.append(yes_text)
	no = gr.Rectangle(gr.Point(440, 40), gr.Point(590, 140))
	no.setFill('indian red')
	input_boxes.append(no)
	no_text = gr.Text(no.getCenter(), 'Fake News')
	no_text.setFill('firebrick')
	trump_text_items.append(no_text)
	# Set the common attributes for the text items
	for text in trump_text_items:
		text.setSize(25)
		text.setFace('courier')

	# Display instructions and wait for user ready
	correct_guesses = 0
	trump_text_items[0].draw(win)
	print('Crazy Train --Ozzy Osbourne')
	music_channel.play(pygame.mixer.Sound('./audio_files/crazyTrain.ogg'))
	userReady(win)

	# Actual game
	# Draw the things
	for thing in itertools.chain(input_boxes, trump_text_items[1:]):
		thing.draw(win)
	while len(trump_crazy_list) != 0:
		rand_int = random.randint(0, len(trump_crazy_list)-1)
		# Randomly select a quote/headline and remove it from the possible list
		rand_key = trump_crazy_list.pop(rand_int)
		disp_text.setText(rand_key)
		win.update()
		# Wait for the user to click on one of the two options
		is_click = False
		bounding_boxes = [rectangleBoundingBox(rectangle) for rectangle in input_boxes]
		while not is_click:
			click = win.getMouse()
			for index, bounding_box in enumerate(bounding_boxes):				# Check to see if the user clicked in a box
				lowX, highX, lowY, highY = bounding_box
				if lowX <= click.getX() <= highX and lowY <= click.getY() <= highY:
					is_click = True
					break
		choice = True if index == 0 else False
		actual_veracity, _ = trump_crazy.get(rand_key)
		# Determine if they got the right or wrong choice
		if actual_veracity == choice:	# Correct
			correct_guesses += 1
			sound_effects_channel.play(win_sound)
			win.setBackground('lime')
			win.update()
			time.sleep(.5)
			win.setBackground('dark orange')
			win.update()
		else:							# Incorrect
			win.setBackground('crimson')
			sound_effects_channel.play(loss_sound)
			win.update()
			time.sleep(.5)
			win.setBackground('dark orange')
			win.update()

	# After going through all the quotes:
	pygame.mixer.fadeout(750)
	music_channel.set_volume(.5)
	win.setBackground('dark slate grey')
	for thing in itertools.chain(input_boxes, trump_text_items[1:]):
		thing.undraw()
	# Display the appropriate end screen and return the result
	if correct_guesses >= 15:
		trump_text_items[0].setFill('lime')
		trump_text_items[0].setText('you win!')
		win.update()
		time.sleep(2)
		win.close()
		return True
	else:
		trump_text_items[0].setFill('red')
		trump_text_items[0].setText('you lose :(')
		win.update()
		time.sleep(.75)
		sound_effects_channel.play(pygame.mixer.Sound('./audio_files/trumpWrong.ogg'))
		time.sleep(1.25)
		win.close()
		return False

def playProject6():
	'''Plays the project6 mini-game'''	
	# Initialize stuff
	project6_text_items = {}
	project6_text_items['Really?? You wanna watch project6 run?!'] = 2.72
	project6_text_items['You do realize that was the optimization\nof the elephant simulation?'] = 3.84
	project6_text_items['The project that would process for about\nfifteen minutes and then spit out\na four-decimal-place number...'] = 5.43
	project6_text_items['You don\'t wanna watch that. There are so\nmany more enjoyable things to watch.'] = 4.36
	project6_text_items['Like Tiger King'] = 1.85
	project6_text_items['Or The Witcher'] = 1.48
	project6_text_items['Or drying paint'] = 1.83
	project6_text_items['I know what you should do!'] = 1.93
	project6_text_items['Go queue up your favorite\nshow and make some popcorn...'] = 2.95
	project6_text_items['But pop it one kernel at a time,\nso that it takes longer.'] = 3.51
	project6_text_items['And listen to this song in the meantime.'] = 2.48
	project6_text_items_list = list(project6_text_items)

	disp_text = gr.Text(gr.Point(325, 255), 'filler')
	disp_text.setFace('courier')
	disp_text.setFill('white')
	disp_text.setSize(20)

	win = gr.GraphWin('project6', 650, 500, False)
	win.setCoords(0, 0, 650, 500)
	win.setBackground('dark slate grey')

	# Display silly text
	disp_text.draw(win)
	for text in project6_text_items_list:
		disp_text.setText(text)
		win.update()
		time.sleep(project6_text_items.get(text))

	# Play song
	print('Bored In The House --Tyga x Curtis Roach')
	music_channel.play(pygame.mixer.Sound('./audio_files/boredInHouse.ogg'))
	time.sleep(5)
	disp_text.setText('The menu will return shortly... Jam out!!')
	win.update()
	time.sleep(22)
	music_channel.stop()
	win.close()
	return True

def displayEndScreen():
	'''Does exactly what you think it does as long as you think it displays the end screen.'''
	# Make the window
	win = gr.GraphWin('End Screen', 500, 500, False)
	win.setCoords(0, 0, 500, 500)
	win.setBackground('dark slate grey')

	# Make the text
	text = gr.Text(gr.Point(250, 270), 'Congratulations on beating all six\nmini-games. I had a lot of fun making\nthem and I hope that you enjoyed\nplaying them. Please enjoy yet another\nsong that encapsulates this crazy time.')
	text.setFace('courier')
	text.setFill('white')
	text.setSize(20)
	text.draw(win)
	win.update()

	# Play the music and wait
	music_channel.play(pygame.mixer.Sound('./audio_files/kidsChance.ogg'))
	print('The Kids Don\'t Stand A Chance --Vampire Weekend')
	time.sleep(245)
	win.close()

def main():
	'''Actually play the box'''
	print('Don\'t worry, pygame is just for the audio. --Caleb')		# Because I didn't use pygame for anything but the audio even though it would be a better game
	print()

	# Intialize some stuff
	title_router = {'0':('Atari', 18), '1':('Tiger King', 18), '2':('Marie Kondo', 18), '3':('Go for a run', 17), '4':('Fake news?',18), '5':('Project 6',18)}
	game_router = {('Atari', 18):playAtari, ('Tiger King', 18):playTigerKing, ('Marie Kondo', 18):playMarieKondo, ('Go for a run', 17):playGoForRun, ('Fake news?',18):playFakeNews, ('Project 6',18):playProject6}
	completed_games = None
	done = False

	# Game loop
	while not done:

		choice_index = displayMenu(completed_games, title_router)
		desired_action = title_router.get(str(choice_index))

		# Play the minigame and store the resultant outcome
		result = game_router[desired_action]()
		# If this is the first attempt at a game, make sure the menu music won't play again unless asked
		if completed_games == None:
			completed_games = []
		# Check for a win and make sure duplicate games can't be played
		if result == True:
			completed_games.append(choice_index)
		# This program only stops when you beat everything--you have time. Keep playing.
		if set(completed_games) == {0, 1, 2, 3, 4, 5}:
			done = True

	displayEndScreen()

if __name__ == '__main__':
	main()





