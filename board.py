from boardObjects import Marker, Qix, Sparx
import pygame
import copy
import shapely
from shapely import geometry

DIRECTION_UPWARDS = (0, -1)
DIRECTION_DOWNWARDS = (0, 1)
DIRECTION_RIGHTWARDS = (1,0)
DIRECTION_LEFTWARDS = (-1,0)

# NOTE: USE.
class Vertex():
    def __init__(self):
        self.x = 0
        self.y = 0

class Edge():
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.next = None
        self.previous = None

    def addAfter(self, new):
        # Any edge references in between self and the end of new will be discarded by Python Garbage Collection
        
        oldNext = self.next
        oldEnd = self.end
        self.next = new
        self.end = new.start
        while new.next != None: new = new.next
        new.next = Edge(new.end, oldEnd)

        new.next.next = oldNext

    def getDirection(self):
        if self.start[1] < self.end[1]: return DIRECTION_DOWNWARDS
        elif self.start[1] > self.end[1]: return DIRECTION_UPWARDS
        elif self.start[0] < self.end[0]: return DIRECTION_RIGHTWARDS
        else: return DIRECTION_LEFTWARDS
    
    def __str__(self):
        return f"EDGE: start: {self.start} end:{self.end}"
class Board():

    def __init__(self):
        self.mainBoard = []         # Contains all possible coordinates entites can exist on
        self.captured = []          # Contains coordinates of 'captured' space
        self.capturedBuffer = []    # Contains all coordinates of space to be 'captured'
        self.playableEdge = []      # Contains coordinates of all traversable space
        self.uncaptured = []        # Contains coordinates of 'uncaptured' space
        self.edges = []             # Contains coordinates of all traversal space
        self.edgesBuffer = []       # Contains edges on Current push
        self.entities = []          # Contains all boardObjects in play

        self.score = 0             # Percent of the board captured

        self.firstEdgeBuffer = None
        self.edgesBuffer = None   # Contains a linked list reference on the current push
        # self.playableAreaPolygon = None # Contains Polygon object representing player's non-push movable area. Polygon is useful for calculating area and determining 'insideness' for collisions
        # self.startingAreaPolygon = None # Used to measure captured area

        initialPoints = [(36,6), (36,94), (124, 94), (124,6)]
        self.startingAreaPolygon = shapely.geometry.Polygon(initialPoints)

        # Initialise four corners
        self.firstEdge = Edge(initialPoints[0], initialPoints[1])
        self.firstEdge.next = Edge(initialPoints[1], initialPoints[2])
        self.firstEdge.next.next = Edge(initialPoints[2], initialPoints[3])
        self.firstEdge.next.next.next = Edge(initialPoints[3], initialPoints[0])
        self.firstEdge.next.next.next.next = self.firstEdge
        
        pygame.display.init()
        pygame.display.set_caption('QIX')
        self.mysurface = pygame.display.set_mode((1280, 800))
        self.resized = pygame.transform.scale(self.mysurface, (160, 100))
        
        self.playableAreaPolygon = self.remakePlayableArea()

    def gameStart(self, level):
        self.createEntities(level)
        self.initializeFonts()
        

    def createEntities(self, level):
        # Level determines number of enemy entities:
        # Level 1 = No Enemies
        # Level 2 = 1 Sparx
        # Level 3 = 2 Sparxs
        # Level 4 = 2 Sparxs + 1 Qix

        # All Entities have fixed Starting positions
        # Sparx Tails will determine the starting direction 

        player = Marker(80, 94, 5, False)
        self.entities.append(player)

        if level >= 2:
            sparx1 = Sparx(60, 6, (61,6))   # Tail is right of the Sparx, move left first
            self.entities.append(sparx1)
            
        if level >= 3:
            sparx2 = Sparx(100, 6, (99,6))  # Tail is left of the Sparx, move right first
            self.entities.append(sparx2)
                
        if level == 4:
            qix = Qix(80, 50)
            self.entities.append(qix)

    def initializeFonts(self):  # Putting this inside the constructor will crash pygame on restart attempts
        pygame.font.init()
        self.header = pygame.font.SysFont('Terminal', 60)
        self.healthText = self.header.render('HP:', True, pygame.Color('white'))
        self.scoreText = self.header.render('Captured:', True, pygame.Color('white'))

        self.scorePercent = pygame.font.SysFont('Terminal', 100)
        self.scorePercentText = self.scorePercent.render(str(self.score) + "%", True, pygame.Color('white'))

    
    def updateScore(self, score):  # 50% of board must be captured to win
        self.score = score
        return self.setScoreText()
    
    def setScoreText(self):
        self.scorePercentText = self.scorePercent.render(str(self.score) + "%", True, pygame.Color('white'))
        return

    def getMarker(self):
        return self.entities[0]

    def getSparx1(self):
        if len(self.entities) >= 2:
            return self.entities[1]
        return None

    def getSparx2(self):
        if len(self.entities) >= 3:
            return self.entities[2]
        return None

    def getQix(self):
        if len(self.entities) == 4:
            return self.entities[3]
        return None
    
    def collide(self):  # Check if Marker overlaps with an enemy object
        for index in range(1,len(self.entities),1):
            
            if self.getMarker().isInvincible():
                return False

            if pygame.Rect.colliderect(self.getMarker().theRect, self.entities[index].theRect):

                self.getMarker().updateHealth()
                self.getMarker().toggleInvincibility(True)

                # print("now!")
                return True

    def draw(self): # UI elements are also drawn here
        self.resized.fill(pygame.Color(0,0,0))
        # self.resized.fill(0)
        
        # Iterate through the linked edges
        edge = self.firstEdge
        
        pygame.draw.line(self.resized, pygame.Color(210,105,30), edge.start, edge.end)
        edge = edge.next
        while edge != self.firstEdge:
            pygame.draw.line(self.resized, pygame.Color(210,105,30), edge.start, edge.end)
            edge = edge.next

        edge = self.firstEdge
        
        pygame.draw.line(self.resized, pygame.Color(210,105,30), edge.start, edge.end)
        
        edge = self.firstEdgeBuffer
        while edge and edge != self.edgesBuffer:
            if not edge: break
            if edge.start and edge.end:
                pygame.draw.line(self.resized, pygame.Color(255,255,255), edge.start, edge.end)
            
            if not edge.next:
                break
            edge = edge.next
        
        for entity in self.entities:    # Objects draw their rects onto the screen that is passed
            entity.draw(self.resized)

        self.mysurface.blit(pygame.transform.scale(self.resized, self.mysurface.get_rect().size), (0,0)) 
        self.getMarker().drawHealth(self.mysurface)

        self.mysurface.blit(self.healthText, (50,50))
        self.mysurface.blit(self.scoreText, (1035,50))
        self.mysurface.blit(self.scorePercentText, (1035,100))

        pygame.display.flip()

    def validateMove(self, keyPress, incr):
        return

    def updateLocations(self):

        return

    def remakePlayableArea(self):  # Happens when an incursion is finished, to induct the incursion shape into the playable area
        
        iterator = self.firstEdge.next
        shapeList = []

        while True:
            if iterator == self.firstEdge:
                shapeList.append(iterator.end)
                break
            shapeList.append(iterator.end)
            iterator = iterator.next
        
        shape = shapely.geometry.Polygon(shapeList)
        return shape
