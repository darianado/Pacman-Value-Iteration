# mapAgents.py
# parsons/11-nov-2017
#
# Version 1.0
#
# A simple map-building to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is an extension of the above code written by Simon
# Parsons, based on the code in pacmanAgents.py
# 
# Value Iteration implemented by Dariana Dorin

from pacman import Directions
from game import Agent
import api
import util

#set a number as reward
reward = -0.04
#set a number as discount
discount = 0.8
# set distance from ghost for pacman to run away
danger = 3

# Grid class from 5th practical
#build map
class Grid:
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    # print map at terminal.
    def prettyDisplay(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                gr= self.grid[self.height - (i + 1)][j]
                print (gr),
            # A new line after each line of the grid
            print
            print
        # A line after the grid
        print

    # Set and get the values of specific elements in the grid.
    def setValue(self, x, y, value):
        self.grid[int(y)][int(x)] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    def getMap(self):
        return self.grid

    def copy(self, m):
        for i in range(self.height):
            for j in range(self.width):
                self.grid[i][j]=m.getMap()[i][j]
    
    def existsValue(self,v):
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j]==v: return True
        return False



class MDPAgent(Agent):
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

    def final(self, state):
        print "Looks like the game just ended!"

    def getHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1  

    # adds the walls to a givven map
    def putWalls(self,state,map):
        walls = api.walls(state)
        for i in range(len(walls)):
            map.setValue(walls[i][0], walls[i][1], '%')
    
    # adds food to a given map
    # if there is food in corners, only add those
    def putFood(self,state,map):    
        food = api.food(state) + api.capsules(state)
        corners= api.corners(state)
        foodCorners=[]
        for c in corners:
            x=c[0]
            y=c[1]
            if x==0: x=1 
            else: x=x-1
            if y==0: y=1
            else: y=y-1
            if (x,y) in food:
                foodCorners.append((x,y))
        done=False
        if len(foodCorners)>0:
            for f in range(len(foodCorners)):
                if map.getValue(foodCorners[f][0], foodCorners[f][1])!=-1:
                    map.setValue(foodCorners[f][0], foodCorners[f][1],1)
                    done=True
        if not done:
            for i in range(len(food)):
                # dont add the food if a ghost is there
                if map.getValue(food[i][0], food[i][1])!=-1:
                    map.setValue(food[i][0], food[i][1],1)

    # returns the value on the next position towards specified direction 
    # value of a wall is the current value
    def getDirectionValue(self,map,x,y,direction):
        if direction=="east":
            if map.getValue(x+1,y) == "%":
                return map.getValue(x,y)
            else: return map.getValue(x+1,y)
        if direction=="west":
            if map.getValue(x-1,y) == "%":
                return map.getValue(x,y)
            else: return map.getValue(x-1,y)
        if direction=="north":
            if map.getValue(x,y+1) == "%":
                return map.getValue(x,y)
            else: return map.getValue(x,y+1)
        if direction=="south":
            if map.getValue(x,y-1) == "%":
                return map.getValue(x,y)
            else: return map.getValue(x,y-1)
        return "error no valid direction"

    # one step of value iteration
    def updateUtil(self, state, map, auxMap):
        corners = api.corners(state)
        height = self.getHeight(corners)
        width  = self.getWidth(corners)
        for i in range(width):
            for j in range(height):
                # only calculates free spaces
                if map.getValue(i,j) != '%' and map.getValue(i,j) != 1 and map.getValue(i,j) != -1 :
                    east=self.getDirectionValue(map,i,j,"east")
                    west=self.getDirectionValue(map,i,j,"west")
                    north=self.getDirectionValue(map,i,j,"north")
                    south=self.getDirectionValue(map,i,j,"south")
                    
                    horizontal=0.1*west+0.1*east
                    vertical=0.1*north+0.1*south
                    best=max(0.8*east+vertical,0.8*west+vertical,0.8*north+horizontal,0.8*south+horizontal)

                    utility= reward+discount*best
                    auxMap.setValue(i,j,utility)
        return auxMap
    
    # checks if 2 maps are equal with an error of 0.00001
    def equalMaps(self,m1,m2):
        for j in range(m1.getHeight()):
            for i in range(m1.getWidth()):
                if m1.getValue(i,j)!="%":
                    if abs(float(m1.getValue(i,j))-float(m2.getValue(i,j)))>0.00001:
                        return False
        return True

    # recursivly find the shorthest distance to a specific value
    def minDs(self,q,map,find):
        list=[]
        while not q.isEmpty():
            now=q.pop()
            x,y=now
            if map.getValue(x,y)!="%" or map.getValue(x,y)!="-": 
                if map.getValue(x,y)==find:
                    return 0
                map.setValue(x,y,"-")

                if map.getValue(x+1,y)!="%" and map.getValue(x+1,y)!="-":
                    list.append((x+1,y))
                if map.getValue(x-1,y)!="%" and map.getValue(x-1,y)!="-":
                    list.append((x-1,y))
                if map.getValue(x,y+1)!="%" and map.getValue(x,y+1)!="-":
                    list.append((x,y+1))
                if map.getValue(x,y-1)!="%" and map.getValue(x,y-1)!="-":
                    list.append((x,y-1))
        
        for p in list:
            q.push(p)
        return 1+ self.minDs(q,map,find)
  
    # returns the shorthest accesible distance between 2 points
    def minDist(self,state,x,y,x1,y1):
        map= Grid(self.width,self.height)
        self.putWalls(state,map)
        map.setValue(x1,y1,100)

        q = util.Queue()
        q.push((x,y))

        return self.minDs(q,map,100)
    
    # given a ghost position, makes all food in its danger area unaccesible
    def removeDangerFood(self,state,g,map):
        food = api.food(state) + api.capsules(state)
        for f in food:
            if self.minDist(state,int(g[0]),int(g[1]),f[0],f[1]) <=danger and map.getValue(f[0],f[1])!=-1:
                map.setValue(f[0],f[1],0)
    
    # add the farthest food from the pacman to the map
    def addFarthestFood(self,pac,toMap,food):
        max=0
        save=(0,0)
        for f in food:
            if util.manhattanDistance(pac,f)>max:
                max=util.manhattanDistance(pac,f)
                save=f
        toMap.setValue(save[0],save[1],1)
        

    def getAction(self, state):
        
        pacman = api.whereAmI(state)
        xPac, yPac = pacman[0], pacman[1]

        legal = api.legalActions(state)
        
        ghosts = api.ghosts(state)
        corners = api.corners(state)
        
        self.height = self.getHeight(corners)
        self.width  = self.getWidth(corners)
        
        # initialise the working map
        map = Grid(self.width,self.height)
        self.putWalls(state,map)

        # saves not eatable ghosts
        activeGhosts=[]

        # add the ghosts to the map depending on their state
        for g in range(len(ghosts)):
            if api.ghostStates(state)[g][1]==0:
                activeGhosts.append(ghosts[g])
                map.setValue(ghosts[g][0], ghosts[g][1],-1)
                # active ghost makes the one move neighbours a negative reward as well
                map.setValue(ghosts[g][0]+1, ghosts[g][1],-1)
                map.setValue(ghosts[g][0]-1, ghosts[g][1],-1)
                map.setValue(ghosts[g][0], ghosts[g][1]+1,-1)
                map.setValue(ghosts[g][0], ghosts[g][1]-1,-1)
            else:
                # not active ghost means food
                map.setValue(ghosts[g][0], ghosts[g][1],1)
        
        # add the walls to the map
        self.putWalls(state,map)

        # add the food if all ghosts are active
        # (else the pacman will reach for the eatable ghosts)
        if len(activeGhosts)==len(ghosts):
            self.putFood(state,map)
        
        # remove the food from danger area of active ghosts
        for g in activeGhosts:
            self.removeDangerFood(state,g,map)

        # in case no positive terminal reward exists on the map anymore
        if not map.existsValue(1):
            self.addFarthestFood(pacman,map,api.food(state))

        # initialise helping copy of map for value iteration
        auxMap = Grid(self.width,self.height)
        auxMap.copy(map)
        
        auxMap=self.updateUtil(state,map,auxMap)

        # update utilities until the 2 maps are equal
        while not self.equalMaps(map,auxMap):
            help=Grid(self.width,self.height)
            help.copy(auxMap)
            map=help
            auxMap=self.updateUtil(state,map,auxMap)

        # save the needed utilities for pacman to make a decision
        myUtility= map.getValue(xPac,yPac)
        
        if (map.getValue(xPac+1, yPac) != '%'):
            eastUtil = map.getValue(xPac+1, yPac)
        else: eastUtil = myUtility

        if (map.getValue(xPac-1, yPac) != '%'):
            westUtil = map.getValue(xPac-1, yPac)
        else: westUtil = myUtility

        if (map.getValue(xPac,yPac+1) != '%'):
            northUtil = map.getValue(xPac, yPac+1)
        else: northUtil = myUtility

        if (map.getValue(xPac,yPac-1) != '%'):
            southUtil = map.getValue(xPac, yPac-1)
        else: southUtil = myUtility

        # save the legal directions to take
        dir=[]
        if Directions.SOUTH in legal :
            dir.append(southUtil)
        if Directions.EAST in legal :
            dir.append(eastUtil)
        if Directions.NORTH in legal :
            dir.append(northUtil)
        if Directions.WEST in legal :
            dir.append(westUtil)
        
        go=[]
        if len(dir) == 0:
            # only stop if no legal directions
            go.append(Directions.STOP)
        else:
            bestUtil= max(dir)

            # save the directions with the best utility
            if southUtil==bestUtil and Directions.SOUTH in legal:
                go.append(Directions.SOUTH)
            if eastUtil==bestUtil and Directions.EAST in legal:
                go.append(Directions.EAST)
            if northUtil==bestUtil and Directions.NORTH in legal:
                go.append(Directions.NORTH)
            if westUtil==bestUtil and Directions.WEST in legal:
                go.append(Directions.WEST)
           
            if len(go)>1:
                # in case more moves can be made, prioritizes 
                # reaching the closest margin, vertical to horizontal
                if Directions.NORTH in go and yPac>=self.height/2:
                    go=[Directions.NORTH]
                elif Directions.SOUTH in go and yPac<self.height/2:
                    go=[Directions.SOUTH]
                elif Directions.WEST in go and xPac<self.width/2:
                    go=[Directions.WEST]
                elif Directions.EAST in go and xPac>=self.width/2:
                    go=[Directions.EAST]

        # make the best move
        return api.makeMove(go[0], legal)
