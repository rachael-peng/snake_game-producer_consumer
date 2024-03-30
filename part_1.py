# Group#:           33
# Student Names:    Rachael Peng, Michael Koon

"""
    This program implements a variety of the snake 
    game (https://en.wikipedia.org/wiki/Snake_(video_game_genre))
"""

import threading
import queue        #the thread-safe queue from Python standard library

from tkinter import Tk, Canvas, Button
import random, time

class Gui():
    """
        This class takes care of the game's graphic user interface (gui)
        creation and termination.
    """
    def __init__(self):
        """        
            The initializer instantiates the main window and 
            creates the starting icons for the snake and the prey,
            and displays the initial gamer score.
        """
        #some GUI constants
        scoreTextXLocation = 60
        scoreTextYLocation = 15
        textColour = "white"
        #instantiate and create gui
        self.root = Tk()
        self.canvas = Canvas(self.root, width = WINDOW_WIDTH, 
            height = WINDOW_HEIGHT, bg = BACKGROUND_COLOUR)
        self.canvas.pack()
        #create starting game icons for snake and the prey
        self.snakeIcon = self.canvas.create_line(
            (0, 0), (0, 0), fill=ICON_COLOUR, width=SNAKE_ICON_WIDTH)
        self.preyIcon = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=ICON_COLOUR, outline=ICON_COLOUR)
        #display starting score of 0
        self.score = self.canvas.create_text(
            scoreTextXLocation, scoreTextYLocation, fill=textColour, 
            text='Your Score: 0', font=("Helvetica","11","bold"))
        #binding the arrow keys to be able to control the snake
        for key in ("Left", "Right", "Up", "Down"):
            self.root.bind(f"<Key-{key}>", game.whenAnArrowKeyIsPressed)

    def gameOver(self):
        """
            This method is used at the end to display a
            game over button.
        """
        gameOverButton = Button(self.canvas, text="Game Over!", 
            height = 3, width = 10, font=("Helvetica","14","bold"), 
            command=self.root.destroy)
        self.canvas.create_window(200, 100, anchor="nw", window=gameOverButton)
    

class QueueHandler():
    """
        This class implements the queue handler for the game.
    """
    def __init__(self):
        self.queue = gameQueue
        self.gui = gui
        self.queueHandler()
    
    def queueHandler(self):
        '''
            This method handles the queue by constantly retrieving
            tasks from it and accordingly taking the corresponding
            action.
            A task could be: game_over, move, prey, score.
            Each item in the queue is a dictionary whose key is
            the task type (for example, "move") and its value is
            the corresponding task value.
            If the queue.empty exception happens, it schedules 
            to call itself after a short delay.
        '''
        try:
            while True:
                task = self.queue.get_nowait()
                if "game_over" in task:
                    gui.gameOver()
                elif "move" in task:
                    points = [x for point in task["move"] for x in point]
                    gui.canvas.coords(gui.snakeIcon, *points)
                elif "prey" in task:
                    gui.canvas.coords(gui.preyIcon, *task["prey"])
                elif "score" in task:
                    gui.canvas.itemconfigure(
                        gui.score, text=f"Your Score: {task['score']}")
                self.queue.task_done()
        except queue.Empty:
            gui.root.after(100, self.queueHandler)


class Game():
    '''
        This class implements most of the game functionalities.
    '''
    def __init__(self):
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        self.queue = gameQueue
        self.score = 0
        #starting length and location of the snake
        #note that it is a list of tuples, each being an
        # (x, y) tuple. Initially its size is 5 tuples.       
        self.snakeCoordinates = [(495, 55), (495-PREY_ICON_WIDTH, 55), (495-2*PREY_ICON_WIDTH, 55), # first tuple represents snake "head"
                                 (495-3*PREY_ICON_WIDTH, 55), (495-4*PREY_ICON_WIDTH, 55)]  # (495, 55), (485, 55), (475, 55), (465, 55), (455, 55)
        #initial direction of the snake
        self.direction = "Left"
        self.gameNotOver = True
        self.createNewPrey()
    
    def superloop(self) -> None: 
        """
            This method implements a main loop
            of the game. It constantly generates "move" 
            tasks to cause the constant movement of the snake.
            Use the SPEED constant to set how often the move tasks
            are generated.
        """
        SPEED = 0.15     #speed of snake updates (sec)
        while self.gameNotOver:
            # generate a move task and put in queue
            self.queue.put({"move": self.snakeCoordinates})
            # set how often move tasks generated (speed of snake movement)
            time.sleep(SPEED)
            # move snake
            self.move()

    def whenAnArrowKeyIsPressed(self, e) -> None:
        """ 
            This method is bound to the arrow keys
            and is called when one of those is clicked.
            It sets the movement direction based on 
            the key that was pressed by the gamer.
            Use as is.
        """
        currentDirection = self.direction
        #ignore invalid keys
        if (currentDirection == "Left" and e.keysym == "Right" or 
            currentDirection == "Right" and e.keysym == "Left" or
            currentDirection == "Up" and e.keysym == "Down" or
            currentDirection == "Down" and e.keysym == "Up"):
            return
        self.direction = e.keysym

    def move(self) -> None:
        """ 
            This method implements what is needed to be done
            for the movement of the snake.
            It generates a new snake coordinate. 
            If based on this new movement, the prey has been 
            captured, it adds a task to the queue for the updated
            score and also creates a new prey.
            It also calls a corresponding method to check if 
            the game should be over. 
            The snake coordinates list (representing its length 
            and position) should be correctly updated.
        """
        NewSnakeCoordinates = self.calculateNewCoordinates()

        # update snake coordinates list with new coordinates by:
        # adding new coordinate at head, removing coordinate at tail - equivalent to shifting snake in specified direction
        self.snakeCoordinates.append(NewSnakeCoordinates) # add new snake head coordinate
        self.snakeCoordinates.pop(0) # remove tail

        preyCoordinatesMatch: int = 0

        # first check if the snake head has "eaten" or touched the prey icon
        xDistPreySnake: int = NewSnakeCoordinates[0] - self.preyCoordinates[0] # x distance between one side of prey icon and snake head 
        yDistPreySnake: int = NewSnakeCoordinates[1] - self.preyCoordinates[1] # y distance between one side of prey icon and snake head 
        
        if self.direction == "Up" or self.direction == "Down":
            if yDistPreySnake <= PREY_ICON_WIDTH and xDistPreySnake >= 0: 
                preyCoordinatesMatch += 1  
            if xDistPreySnake <= 1.5 * PREY_ICON_WIDTH and xDistPreySnake >= 0:
                preyCoordinatesMatch += 1  
        else:
            if yDistPreySnake <= PREY_ICON_WIDTH and xDistPreySnake >= 0: 
                preyCoordinatesMatch += 1 
            if xDistPreySnake <= PREY_ICON_WIDTH and xDistPreySnake >= 0: 
                preyCoordinatesMatch += 1  
            
            # whenever snake head begins to touch prey icon/is touching prey icon, coordinate counts as prey "eaten"
               
        # if both coordinates match, then prey is eaten
        if preyCoordinatesMatch == 2:
            self.score += 1 # 1 prey eaten means1 point increase in score 
            self.queue.put_nowait({"score": self.score}) # add to queue to display the new score 

            # increase the length of the snake
            addLength: tuple = () # coordinate added to increase length of snake 

            # determine the position of this new coordinate to add
            if self.snakeCoordinates[0][0] == self.snakeCoordinates[1][0]: # check if last 2 coordinates on the same line vertically
                if self.snakeCoordinates[0][1] > self.snakeCoordinates[1][1]: # check if snake tail points down or up,
                                                                              # adding new length at open end
                    # if open tail end points up (if snake tail y coordinate greater than 2nd y coordinate next to snake tail)
                    addLength = (self.snakeCoordinates[0][0], self.snakeCoordinates[0][1] + PREY_ICON_WIDTH)
                else: # otherwise open tail end points down, add length below
                    addLength = (self.snakeCoordinates[0][0], self.snakeCoordinates[0][1] - PREY_ICON_WIDTH)
            else: # otherwise last 2 coordinates are on the same line horizontally
                if self.snakeCoordinates[0][0] > self.snakeCoordinates[1][0]: # check if snake tail open end poinst left or right
                                                                              # adding new length at open end
                    # if open tail end points right (if snake tail x coordinate greater than 2nd x coordinate next to snake tail)
                    addLength = (self.snakeCoordinates[0][0] + PREY_ICON_WIDTH, self.snakeCoordinates[0][1])
                else: # otherwise open tail end points left, add length left 
                    addLength = (self.snakeCoordinates[0][0] - PREY_ICON_WIDTH, self.snakeCoordinates[0][1])

            self.snakeCoordinates.insert(0, addLength)
            self.createNewPrey() # generate a new prey

        # check if game is over, passing coordinates of snake head
        self.isGameOver(NewSnakeCoordinates)
        #complete the method implementation below

    def calculateNewCoordinates(self) -> tuple:
        """
            This method calculates and returns the new 
            coordinates to be added to the snake
            coordinates list based on the movement
            direction and the current coordinate of 
            head of the snake.
            It is used by the move() method.    
        """
        lastX, lastY = self.snakeCoordinates[-1] # represents snake head 
        newX: int = lastX # represents new x coordinate to be added 
        newY: int = lastY # represents new y coordinate to be added 

        if self.direction == "Right":
            newX += PREY_ICON_WIDTH # move to the right 
        elif self.direction == "Left":
            newX -= PREY_ICON_WIDTH # move to the left 
        elif self.direction == "Up":
            newY -= PREY_ICON_WIDTH # move up
        elif self.direction == "Down":
            newY += PREY_ICON_WIDTH # move down 

        return (newX, newY)
        #complete the method implementation below

    def isGameOver(self, snakeCoordinates) -> None:
        """
            This method checks if the game is over by 
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver 
            field and also adds a "game_over" task to the queue. 
        """
        x, y = snakeCoordinates # coordinates of snake head

        # check if snake hit any of left or right walls or top or bottom walls 
        # use >= <= to account for latency, so as long as the snake head touches any point of prey icon it is eaten
        if x >= WINDOW_WIDTH or x <= 0 or y >= WINDOW_HEIGHT or y <= 0:
            self.gameNotOver = False
        # if the snake head coordinate is equal to any other snake coordinate, then snake bit itself 
        else:
            for coordinate in self.snakeCoordinates: # check if snake head matches any tuples in snakeCoordiantes
                if (x, y) == coordinate and coordinate != self.snakeCoordinates[-1]:  # don't check that head is equal to itself
                    self.gameNotOver = False
        
        if self.gameNotOver == False:
            self.queue.put({"game_over": self.gameNotOver}) # block until complete

    def createNewPrey(self) -> None:
        """ 
            This methods picks an x and a y randomly as the coordinate 
            of the new prey and uses that to calculate the 
            coordinates (x - 5, y - 5, x + 5, y + 5). [you need to replace 5 with a constant]
            It then adds a "prey" task to the queue with the calculated
            rectangle coordinates as its value. This is used by the 
            queue handler to represent the new prey.                    
            To make playing the game easier, set the x and y to be THRESHOLD
            away from the walls. 
        """
        THRESHOLD = 15   #sets how close prey can be to borders
        # generate x, y integer coordinates of prey randomly and make sure they account for border threshold
        xyCoordinates: tuple = (random.randint(THRESHOLD, WINDOW_WIDTH - THRESHOLD), 
                                      random.randint(THRESHOLD, WINDOW_HEIGHT - THRESHOLD))
        # generate rectangular prey coordinates using the formula specified in documentation 
        self.preyCoordinates: tuple = (xyCoordinates[0] - PREY_ICON_WIDTH / 2, xyCoordinates[1] - PREY_ICON_WIDTH / 2,
                                   xyCoordinates[0] + PREY_ICON_WIDTH / 2, xyCoordinates[1] + PREY_ICON_WIDTH / 2)
        # put coordinates of new prey in queue
        self.queue.put_nowait({"prey": self.preyCoordinates})


if __name__ == "__main__":
    #some constants for our GUI
    WINDOW_WIDTH = 500           
    WINDOW_HEIGHT = 300 
    SNAKE_ICON_WIDTH = 15
    PREY_ICON_WIDTH = 10   

    BACKGROUND_COLOUR = "green"   #you may change this colour if you wish
    ICON_COLOUR = "yellow"        #you may change this colour if you wish

    gameQueue = queue.Queue()     #instantiate a queue object using python's queue class

    game = Game()        #instantiate the game object

    gui = Gui()    #instantiate the game user interface
    
    QueueHandler()  #instantiate the queue handler    
    
    #start a thread with the main loop of the game
    threading.Thread(target = game.superloop, daemon=True).start()

    #start the GUI's own event loop
    gui.root.mainloop()