from pygame.constants import K_x, VIDEOEXPOSE, VIDEORESIZE
import pygame.display;
import time;
import pygame.color;
from pygame.locals import *
import pygame.event;
import sys
import math
from shapely.geometry.point import Point
import copy
import random


from gui import GUI
from board import Board, DIRECTION_DOWNWARDS, DIRECTION_LEFTWARDS, DIRECTION_RIGHTWARDS, DIRECTION_UPWARDS, Edge
from boardObjects import Marker


# To be removed, waiting on UI elements to be implemented first

# pygame.display.update()

def main():

    uiLoop = True
    while uiLoop:

        fpsclock=pygame.time.Clock()

        gui = GUI()

        if gui.render_initial_screen():
            level = int(gui.selected_difficulty)
        else:
            break

        print("Creating Board...")

        board = Board()
        board.gameStart(level)  # Calls createEntities

        print("Start!")

        # BoardObjects can only be accessed through the board
        player = board.getMarker()
        sparx1 = board.getSparx1()
        sparx2 = board.getSparx2()
        qix = board.getQix()

        sparxHolder = [sparx1,sparx2]

        collisionTime = 0
        previousMoveVector = None
        startingIncurringEdge = None
        exit = True

        gameLoop = True
        while gameLoop:
            fpsclock.tick(30)

            keys = pygame.key.get_pressed()
            moveVector = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_DOWN] - keys[pygame.K_UP])
            moveVector = limitVectorDirection(moveVector)
            touchingEdge = None # Start from no touchingEdge
            
            # If nothing is being pressed, ignore the code
            if not moveVector == (0,0) and not keys[pygame.K_SPACE]:
                
                touchingEdge = currentEdge(player, board)
                
                if touchingEdge:
                    # The player is touching an edge
                    pass
                
                # Try moving in a direction
                player.updateLocation(player.x + moveVector[0], player.y + moveVector[1])

                touchingEdge = currentEdge(board.getMarker(), board)

                # If an edge was not found, revert the movement
                if not touchingEdge:
                    player.updateLocation(player.x - moveVector[0], player.y - moveVector[1])
                    # TODO: Consider error handling here; The player should always be on an edge

            if touchingEdge and not keys[pygame.K_SPACE]:
                board.getMarker().setIsPushing(False)

            if keys[pygame.K_SPACE]:
                # If the player is currently touching the edge while doing an incursion, and if the stored incursion is of length 1, initialise the environment
                # If the player is not currently incurring, initialise the environment
                if currentEdge(player, board) and player.isPushing() and board.edgesBuffer == board.firstEdgeBuffer\
                    or not player.isPushing():
                    player.setIsPushing(True)

                    playerPos = (player.x, player.y)
                    board.edgesBuffer = Edge(playerPos, None)

                    board.firstEdgeBuffer = board.edgesBuffer
                    previousMoveVector = moveVector
                    startingIncurringEdge = currentEdge(player, board)
                
                if player.isPushing():
                    handleIncursion(player, board, moveVector, previousMoveVector, startingIncurringEdge)
                    previousMoveVector = moveVector


                # General Enemy Movement:
                # Qix and Sparx both use a random movement algorithm
                # 1. They will generate a movelist based on the adjacent points to their current position
                # 2. Filter through movelist checking if a move satisfies the specific criteria
                # 3. Choose a random move based on the moves that have been screened

                # For the Sparx's
            for sparx in sparxHolder:

                if sparx:
                    sparx.generateMoves()
                    moveList = []

                    for move in sparx.possibleMoves:

                        if move in sparx.tail:  # Sparx tail to prevent backtracking
                            continue
                        
                        prevX = copy.deepcopy(sparx.x)
                        prevY = copy.deepcopy(sparx.y)

                        sparx.updateLocation(move[0], move[1])

                        touchingEdge = currentEdge(sparx,board)

                        if not touchingEdge:
                            sparx.updateLocation(prevX, prevY)
                        else:
                            moveList.append(move)

                    if moveList:
                        move = random.choice(moveList)
                        sparx.updateTail((move[0], move[1]))
                        sparx.updateLocation(move[0], move[1])
                        # If the sparx is touching the start of the incursion
                        
                        if player.isPushing() and sparx.x == board.firstEdgeBuffer.start[0] and sparx.y == board.firstEdgeBuffer.start[1]:
                            # Reset the player position
                            player.updateLocation(board.firstEdgeBuffer.start[0], board.firstEdgeBuffer.start[1])
                            player.setIsPushing(False)
                            board.firstEdgeBuffer = None
                            board.edgesBuffer = None
                    else:
                        gameLoop = False
                        pygame.quit()
                        exit = False
                        
                    sparx.resetMoves()

            if exit == False:
                break


            # Qix
            if qix:
                qix.generateMoves() # Generates moves based on the position of Rect.center
                moveList = []

                for move in qix.possibleMoves:
                    prevX = copy.deepcopy(qix.x)
                    prevY = copy.deepcopy(qix.y)

                    qix.updateLocation(move[0], move[1])
                    touchingEdge = currentEdge(qix, board)

                    if touchingEdge:
                        qix.updateLocation(prevX, prevY)
                    else:
                        moveList.append(move)

                if moveList:
                    move = random.choice(moveList)
                    # -4 to counteract the offset of using Rect.center for generating moves
                    qix.updateLocation(move[0]-4, move[1]-4) 

                qix.resetMoves()

            board.draw()
            
            # The player got hit
            if board.collide():
                collisionTime = pygame.time.get_ticks()
                player.toggleInvincibility(True)

            if pygame.time.get_ticks() - collisionTime > 1000:
                collisionTime = 0
                player.toggleInvincibility(False)

            if player.getHealth() == 0:
                pygame.quit()
                break
            if board.score >= 75:
                pygame.quit()
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameLoop = False
                    pygame.quit()

        gui.set_user_score(board.score)
        
        if not gui.render_game_over_screen():
            uiLoop = False
            break

       
def limitVectorDirection(vector):
    """
    Converts a vector to (+-1,0), (0,+-1), or (0,0).
        Assumption: The input vector consists of two numerical elements.
        Returns: A tuple in the form: (val, val)
    """
    if abs(vector[0]) == 1:
        return (math.copysign(1, vector[0]), 0)
    elif abs(vector[1]) == 1:
        return (0, math.copysign(1, vector[1]))
    
    return (0,0)

        # for event in pygame.event.get(): # Check for quit event (closing window)
        #     if event.type == pygame.QUIT:
        #         running = False
        #         pygame.quit()
        #     if event == VIDEORESIZE: # Check for resize
        #         mysurface = pygame.display.set_mode((event.w,event.h), pygame.RESIZABLE)
def currentEdge(obj, board:Board):
    """
    Finds an edge that corresponds to the players current position.
        Returns: Edge if an edge was found. Otherwise: None
    """
    edge = board.firstEdge
    if posInRange(edge.start, edge.end, (obj.x, obj.y)):
        return edge
    
    # Move to the next element    
    edge = edge.next
    while edge != board.firstEdge:
        if posInRange(edge.start, edge.end, (obj.x, obj.y)):
            return edge
        edge = edge.next
    return None
        
def posInRange(start, end, position):
    
    return inRange(start[0], end[0], position[0]) and inRange(start[1], end[1], position[1])

def inRange(minVal, maxVal, target):
    return min(minVal, maxVal) <= target and target <= max(minVal, maxVal)

def handleIncursion(player, board, moveVector, previousMoveVector, startingIncurringEdge):
    newPlayerPos = Point(player.x + moveVector[0], player.y + moveVector[1])
    newPositionIsContainedInArea = board.playableAreaPolygon.contains(newPlayerPos)
    newPositionIsTouchingArea = board.playableAreaPolygon.touches(newPlayerPos)

    # If the player is attempint to move into an invalid section, stop the incursion
    if not newPositionIsContainedInArea and not newPositionIsTouchingArea:
        board.getMarker().setIsPushing(False)
        previousMoveVector = None
        startingIncurringEdge = None
        return

    # Try moving
    # The player can move anywhere, BUT:
    #   - they cannot travel backwards along their path, AND
    #   - when they change vector direction they close one edge and start a new one
    edge = board.edgesBuffer

    # The direction changed
    if not currentEdge(player, board) and moveVector != (0,0) and previousMoveVector != moveVector:
        # Finish this edge and start a new one
        playerPos = (player.x, player.y)

        if playerPos != edge.start: 
            edge.end = playerPos

            edge.next = Edge(edge.end, None)
            edge.next.previous = edge

            board.edgesBuffer = edge.next

    elif moveVector != (0,0): # Probably refactor this LOL (put this in a method or something)
        player.updateLocation(player.x + moveVector[0], player.y + moveVector[1])
        touchingEdge = currentEdge(player, board)
        
        # If an edge is being touched after the movement, the incursion is finished
        if touchingEdge and board.firstEdgeBuffer != board.edgesBuffer:
            # Close the current edge
            playerPos = (player.x, player.y)
            edge.end = playerPos
            
            # If same edge, figure out which one is first by comparing the 
            if touchingEdge == startingIncurringEdge:
                handleSameEdgeIncursion(touchingEdge, edge, board)
            else:
                handleCrossEdgeIncursion(touchingEdge, startingIncurringEdge, edge, board)
            
            # Update the firstEdge if it was removed during the incursion
            
            board.firstEdge = edge
            # Insert the buffer into the edge
            board.getMarker().setIsPushing(False)
            board.firstEdgeBuffer = None
            board.edgesBuffer = None
            board.playableAreaPolygon = board.remakePlayableArea()
            board.updateScore(int(round(100 - 100 * board.playableAreaPolygon.area / board.startingAreaPolygon.area)))
            print("Captured Area: ", int(round(100 - 100 * board.playableAreaPolygon.area / board.startingAreaPolygon.area)), "%")

def handleCrossEdgeIncursion(touchingEdge, startingIncurringEdge, edge, board):
    touchingEdgeDirection = touchingEdge.getDirection()
    startingEdgeDirection = startingIncurringEdge.getDirection()
    
    rightwardIncursion = board.firstEdgeBuffer.start[0] < edge.end[0]
    leftwardIncursion = board.firstEdgeBuffer.start[0] > edge.end[0]
    
    # Accept incursions from:
    #   - downwards to upwards (rightward horizontal incursion)
    #   - rightwards to leftwards (upward vertical incursion)
    #   - downwards to rightwards
    #   - downwards to downwards
    #   - rightwards to upwards
    #   - upwards to leftwards
    #   - leftwards to downwards
    #   - downwards to leftwards in a rightwards-incursion. This is specified so that the smaller area is taken during an incursion
    #   - leftwards to leftwards in a rightwards-incursion. Same reasoning as above
    #   - upwards to upwards. Same reasoning as above
    #   - rightwards to rightwards. Same reasoning as above
    #   - upwards to rightwards
    if     startingEdgeDirection == DIRECTION_DOWNWARDS     and touchingEdgeDirection == DIRECTION_UPWARDS and rightwardIncursion\
        or startingEdgeDirection == DIRECTION_DOWNWARDS     and touchingEdgeDirection == DIRECTION_DOWNWARDS \
        or startingEdgeDirection == DIRECTION_DOWNWARDS     and touchingEdgeDirection == DIRECTION_RIGHTWARDS \
        or startingEdgeDirection == DIRECTION_RIGHTWARDS    and touchingEdgeDirection == DIRECTION_LEFTWARDS    and leftwardIncursion\
        or startingEdgeDirection == DIRECTION_UPWARDS       and touchingEdgeDirection == DIRECTION_LEFTWARDS \
        or startingEdgeDirection == DIRECTION_LEFTWARDS     and touchingEdgeDirection == DIRECTION_DOWNWARDS    and leftwardIncursion\
        or startingEdgeDirection == DIRECTION_LEFTWARDS     and touchingEdgeDirection == DIRECTION_LEFTWARDS    and leftwardIncursion \
        or startingEdgeDirection == DIRECTION_DOWNWARDS     and touchingEdgeDirection == DIRECTION_LEFTWARDS    and leftwardIncursion \
        or startingEdgeDirection == DIRECTION_UPWARDS       and touchingEdgeDirection == DIRECTION_UPWARDS      and rightwardIncursion \
        or startingEdgeDirection == DIRECTION_UPWARDS       and touchingEdgeDirection == DIRECTION_RIGHTWARDS   and rightwardIncursion \
        or startingEdgeDirection == DIRECTION_RIGHTWARDS    and touchingEdgeDirection == DIRECTION_RIGHTWARDS   and rightwardIncursion \
        or startingEdgeDirection == DIRECTION_RIGHTWARDS    and touchingEdgeDirection == DIRECTION_UPWARDS      and rightwardIncursion\
        or startingEdgeDirection == DIRECTION_RIGHTWARDS    and touchingEdgeDirection == DIRECTION_DOWNWARDS    and rightwardIncursion\
        or startingEdgeDirection == DIRECTION_LEFTWARDS     and touchingEdgeDirection == DIRECTION_UPWARDS      and leftwardIncursion\
        or startingEdgeDirection == DIRECTION_UPWARDS       and touchingEdgeDirection == DIRECTION_DOWNWARDS    and rightwardIncursion\
        or startingEdgeDirection == DIRECTION_LEFTWARDS     and touchingEdgeDirection == DIRECTION_RIGHTWARDS   and leftwardIncursion:
        startingIncurringEdge.end = board.firstEdgeBuffer.start
        startingIncurringEdge.next = board.firstEdgeBuffer
        touchingEdge.start = edge.end
        edge.next = touchingEdge
    
    # Accept incursions from:
    #   - leftwards to upwards
    #   - downwards to leftwards
    #   - rightwards to downwards
    #   - upwards to rightwards
    #   - upwards to downwards (horizontal incursion)
    #   - leftwards to rightwards (downward vertical incursion)
    else:
        printList(board.firstEdgeBuffer)
        oldFirstEdge = board.firstEdgeBuffer
        board.firstEdgeBuffer = reverseLinkedList(board.firstEdgeBuffer)
        
        startingIncurringEdge.start = oldFirstEdge.end
        touchingEdge.end = board.firstEdgeBuffer.start
        touchingEdge.next = board.firstEdgeBuffer
        oldFirstEdge.next = startingIncurringEdge

def handleSameEdgeIncursion(touchingEdge, edge, board):
    downwardEdge = touchingEdge.start[1] < touchingEdge.end[1]
    upwardEdge = touchingEdge.start[1] > touchingEdge.end[1]
    rightwardEdge = touchingEdge.start[0] < touchingEdge.end[0]
    leftwardEdge = touchingEdge.start[0] > touchingEdge.end[0]

    if downwardEdge and board.firstEdgeBuffer.start[1] < edge.start[1] \
        or upwardEdge and board.firstEdgeBuffer.start[1] > edge.start[1] \
        or rightwardEdge and board.firstEdgeBuffer.start[0] < edge.start[0]\
        or leftwardEdge and board.firstEdgeBuffer.start[0] > edge.start[0]:
                            
        touchingEdge.addAfter(board.firstEdgeBuffer)
    else:
        # If the direction of the incursion was made in opposite of the direction of the edge
        # Reverse the list and insert it
        board.firstEdgeBuffer = reverseLinkedList(board.firstEdgeBuffer)
        touchingEdge.addAfter(board.firstEdgeBuffer)

def reverseLinkedList(inputList):
    prev = None
    curr = inputList
    nextRef = None

    while curr != None:
      nextRef = curr.next
      curr.next = prev
      oldEnd = curr.end
      curr.end = curr.start
      curr.start = oldEnd
      prev = curr
      curr = nextRef
    
    return prev

def printList(inputList):
    edge = inputList
    print(edge)
    edge = edge.next
    while edge != None and edge != inputList:
        print(edge)
        edge = edge.next


def limitVectorDirection(vector):
    """
    Converts a vector to (+-1,0), (0,+-1), or (0,0).
        Assumption: The input vector consists of two numerical elements.
        Returns: A tuple in the form: (val, val)
    """
    if abs(vector[0]) == 1:
        return (math.copysign(1, vector[0]), 0)
    elif abs(vector[1]) == 1:
        return (0, math.copysign(1, vector[1]))
    
    return (0,0)

main()