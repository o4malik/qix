import pygame

class Object():
    def __init__(self, xPos, yPos):
        self.x = xPos
        self.y = yPos

        self.theRect = pygame.Rect(self.x, self.y, 1, 1)
        self.colour = None

        self.possibleMoves = []

    def updateLocation(self, x, y):
        self.x = x
        self.y = y
        self.theRect.update(self.x, self.y, 1, 1)
    
    def getLocation(self):
        return (self.x, self.y)

    def draw(self, screen):
        pygame.draw.rect(screen, self.colour , self.theRect)

    def generateMoves(self):
        self.possibleMoves.append((self.x+1, self.y))
        self.possibleMoves.append((self.x, self.y+1))
        self.possibleMoves.append((self.x-1, self.y))
        self.possibleMoves.append((self.x, self.y-1))

    def resetMoves(self):
        self.possibleMoves = []


class Marker(Object):
    def __init__(self, xPos, yPos, health, pushState):
        super().__init__(xPos, yPos)

        self.health = health
        self.pushState = pushState

        self.colour = pygame.Color(0,204,0) # Green

    def isPushing(self):
        return self.pushState

    def setIsPushing(self, state):
        self.pushState = state

    def getHealth(self):
        return self.health

    def updateHealth(self):
        self.health -= 1


class Sparx(Object):
    def __init__(self, xPos, yPos, tail):
        super().__init__(xPos, yPos)

        self.colour = pygame.Color(51,51,255) # Blue

        # Tail prevents Sparx from moving back on itself
        self.tail = []
        self.tail.append((xPos,yPos))
        self.tail.append(tail)
        
        self.possibleMoves = []

    def updateTail(self, position):
        self.tail.insert(0, position)
        self.tail.pop()


class Qix(Object):
    def __init__(self, xPos, yPos):
        super().__init__(xPos, yPos)

        self.theRect = pygame.Rect(self.x, self.y, 3, 3)    # Override Rect dimensions
        self.colour = pygame.Color(204,204,255) # Light Navy Blue

    # Overload updateLocation as the qix will 3 by 3 instead of 1 by 1 
    def updateLocation(self, x, y):
        self.x = x
        self.y = y

        self.theRect.update(self.x, self.y, 3, 3)

    # Overload generateMoves as the qix will use find moves with the center point as the anchor because
    # the qix's x and y correlate to the top left edge of the Rect instead of the center
    def generateMoves(self):
        self.possibleMoves.append((self.theRect.center[0]+1, self.theRect.center[1]))
        self.possibleMoves.append((self.theRect.center[0]-1, self.theRect.center[1]))
        self.possibleMoves.append((self.theRect.center[0], self.theRect.center[1]+1))
        self.possibleMoves.append((self.theRect.center[0], self.theRect.center[1]-1))
    
