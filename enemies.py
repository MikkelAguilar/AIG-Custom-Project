
import pygame
from random import randrange

class Enemy():
    def __init__(self, world, node, type = 'Bug'):
        self.world = world
        self.screen = world.screen

        self.current_node = node
        self.x = node.x
        self.y = node.y

        self.goal_reached = False

        self.target_list = []
        self.target_index = None

        self.copy_target_list = []
        self.copy_target_index = None

        self.image_width = 60
        self.image_height = 60

        self.image = pygame.transform.scale(pygame.image.load("assets/bug/Bug_0.png"), (self.image_width, self.image_height)) #Placeholder image

        self.moving_up_images = []
        self.moving_down_images = []
        self.moving_right_images = []
        self.moving_left_images = []

        self.cost_to_move_up = randrange(1, 20)
        self.cost_to_move_down = randrange(1, 20)
        self.cost_to_move_right = randrange(1, 20)
        self.cost_to_move_left = randrange(1, 20)

        self.animation_count = 0

        self.range = (150, 150)
        self.enemies_in_range = []
        self.number_of_enemies_in_range = 0

        self.change_path = False

        self.find_path(world.nodes) #Find an initial path to follow

        if type == 'Bug': #Statistics for every type of enemy
            self.load_images("assets/bug/Bug_", 21)
            self.speed = 0.5
            self.health = 100
            self.lost_lives = 1
            self.dropped_credits = 50
        elif type == 'Fly':
            self.load_images("assets/fly/Fly_", 19)
            self.speed = 1.75
            self.health = 50
            self.lost_lives = 2
            self.dropped_credits = 75
        elif type == 'Green Bug':
            self.load_images("assets/green_bug/Green_Bug_", 19)
            self.speed = 1
            self.health = 100
            self.lost_lives = 3
            self.dropped_credits = 100
        elif type == 'Long Bug':
            self.load_images("assets/long_bug/Long_Bug_", 18)
            self.speed = 1.35
            self.health = 300
            self.lost_lives = 5
            self.dropped_credits = 200
        elif type == 'Pink Bug':
            self.load_images("assets/pink_bug/Pink_Bug_", 18)
            self.speed = 1.45
            self.health = 500
            self.lost_lives = 10
            self.dropped_credits = 350
        elif type == 'Spider':
            self.load_images("assets/spider/Spider_", 18)
            self.speed = 0.75
            self.health = 1000
            self.lost_lives = 15
            self.dropped_credits = 500

    def draw(self): #Draw the center of the enemy on its x and y position
        self.screen.blit(self.image, (self.x - (self.image_width / 2), self.y - (self.image_height / 2)))
    
    def in_range(self, enemies, range): #Find the other enemies in within a range that it sees
        enemies_in_range = []
        self.number_of_enemies_in_range = 0
        for enemy in enemies:
            if self.x - (range[0] / 2) < enemy.x < self.x + (range[0] / 2) and\
            self.y - (range[1] / 2) < enemy.y <  self.y + (range[1] / 2) and enemy != self: #If enemy is within range and its not itself, add the number of enemies in range
                enemies_in_range.append(enemy)
                self.number_of_enemies_in_range += 1
        
        return enemies_in_range

    def draw_enemy_range(self): #Draw the range with transparency
        image = pygame.Surface(self.range) #Set the image range as a surface
        image.set_colorkey((0, 100, 0))
        image.set_alpha(60) #Use alpha to create a transparent surface
        pygame.draw.rect(image, (169, 169, 169), image.get_rect(), 4)
        self.screen.blit(image, (self.x - (image.get_width() / 2), self.y - (image.get_height() / 2)))

    def move_to_node(self, node): #Given a node, move to it
        if node.x - 1 < self.x < node.x + 1 and node.y - 1 < self.y < node.y + 1: #If the enemy reacheda node, return true and set its positional values to the nodes position
            self.x = node.x
            self.y = node.y
            self.current_node = node
            if self.change_path == True: #If change path is true, find a new path and set it to false
                self.find_path(self.world.nodes)
                self.change_path = False
            return True

        if node.x > self.x: #If the nodes x value is greater than the current x value, increment the x value by speed and set the image to its moving right images
            self.x += self.speed
            self.image = self.moving_right_images[self.animation_count // 10]
        elif node.x < self.x:
            self.x -= self.speed
            self.image = self.moving_left_images[self.animation_count // 10]
        elif node.y > self.y:
            self.y += self.speed
            self.image = self.moving_down_images[self.animation_count // 10]
        elif node.y < self.y:
            self.y -= self.speed
            self.image = self.moving_up_images[self.animation_count // 10]

    def move(self): #Handle moving
        if self.target_index < len(self.target_list): #Check if target index is within the length of the target list
            if self.move_to_node(self.target_list[self.target_index]): #If the enemy reaches a landmark node, increate the target index by 1
                self.target_index += 1
        else: #If the index has exceeded the list, the enemy has reached the goal
            self.goal_reached = True

    def update(self): #Update the enemy with animations
        self.animation_count += 1
        if self.animation_count == len(self.moving_up_images) * 10:
            self.animation_count = 0

        if not self.goal_reached: #Continue to move if the goal has not been reached
            self.move()
        self.draw()
    
    def set_target_list(self, target_list): #Set the target list to the parameter and reset the index
        self.target_list = target_list
        self.target_index = 0
    
    def load_images(self, file_location, no_of_sprites): #Load images for sprite animation
        for i in range(no_of_sprites):
            self.moving_up_images.append(pygame.transform.scale(pygame.image.load(file_location + str(i) + ".png"), (self.image_width, self.image_height)))
            self.moving_left_images.append(pygame.transform.rotate(pygame.transform.scale(pygame.image.load(file_location + str(i) + ".png"), (self.image_width, self.image_height)), 90))
            self.moving_down_images.append(pygame.transform.rotate(pygame.transform.scale(pygame.image.load(file_location + str(i) + ".png"), (self.image_width, self.image_height)), 180))
            self.moving_right_images.append(pygame.transform.rotate(pygame.transform.scale(pygame.image.load(file_location + str(i) + ".png"), (self.image_width, self.image_height)), 270))
    
    def backtrace(self, parent, start, end): #Backtrace to find a path given a list of parents, the start node and the end node
        path = [end]
        while path[-1] != start:
            path.append(parent[path[-1]])

        path.reverse()
        return path
    
    def cost_to_move(self, node, origin_node = None, danger_nodes = []): #Find the cost to mvoe from one node to another
        cost_to_move = 0
        if origin_node != None:
            origin_node = self.world.find_node(origin_node)

            for move, neighbour in origin_node.neighbours.items(): #For their respective positions from the origin, set the cost to move
                if neighbour.relative_square == node:
                    if move == 'down':
                        cost_to_move = self.cost_to_move_down
                    elif move == 'up':
                        cost_to_move = self.cost_to_move_up
                    elif move == 'left':
                        cost_to_move = self.cost_to_move_left
                    elif move == 'right':
                        cost_to_move = self.cost_to_move_right

            if node in danger_nodes: #If node is in the list of danger nodes, increase the cost to move there by 1000
                cost_to_move += 1000
        
        return cost_to_move 
    
    def cost_to_reach_goal(self, node, goal): #Use the manhattan heuristic to find the cost to reach a goal
        n = self.world.find_node(node)
        g = self.world.find_node(goal)

        x = abs(n.relative_square[0] - g.relative_square[0]) #Use absolute value to find distance
        y = abs(n.relative_square[1] - g.relative_square[1])
        
        return x + y
    
    def convert_path_to_nodes(self, path): #Use a list of path coordinate squares, to a return a list of corresponding nodes
        x = []
        for node in path:
            x.append(self.world.find_node(node))

        return x

    def generate_graph(self, nodes): #Create a dictionary which contain a coordinate as a key, and their neighbours as a list of values
        graph = {}
        valid_nodes = [node for node in nodes if node.is_path or node.is_start]  #Nodes are valid if it is a start node or a path node

        for node in valid_nodes:
            graph[node.relative_square] = []
            for neighbour in node.neighbours.values(): #Loop through the neighbours of the node
                if neighbour.is_path or neighbour.is_goal or neighbour.is_start: #If the neighbour is a path, goal or start node, append its relative square to the dictionary
                    graph[node.relative_square].append(neighbour.relative_square)
                    
        return graph
    
    def a_star_search(self, graph, starting_node, end_node): #Use A* search to 
        visited = []
        open_list = {}
        open_list[starting_node] = self.cost_to_reach_goal(starting_node, end_node)
        parent = {}
        found_path = False

        if starting_node == end_node:
            return [starting_node]

        while open_list: #while the open list contains nodes, find the lowest square and check if it equals the end node
            lowest_square = min(open_list, key = open_list.get)
            open_list.pop(lowest_square)
            visited.append(lowest_square)

            if lowest_square == end_node:
                found_path = True
                break
            
            for neighbour in graph[lowest_square]: #Loop through the neigbhours of the lowest square and if it has not been visited add it to open list with its calculated cost
                if neighbour not in visited:
                    open_list[neighbour] = self.cost_to_reach_goal(neighbour, end_node) + self.cost_to_move(neighbour, lowest_square, danger_nodes = self.world.nodes_on_fire) #Set heuristic to the manhattan distance from the start to the goal node + the cost to move UP/DOWN/LEFT/RIGHT
                    if neighbour not in parent: #If it is not in parent add it tot he parent dictionary 
                        parent[neighbour] = lowest_square

        if found_path == True:
            return self.backtrace(parent, starting_node, end_node) #Backtrace to find the path
        else:
            return [] #If not path is found return an empty list
        
    def find_path(self, nodes): #Find a new path for the enemy to follow
        search = self.a_star_search(self.generate_graph(nodes), self.current_node.relative_square, self.world.goal) #Use a start search to find a path
        path = self.convert_path_to_nodes(search) #Convert to a list of nodes
        self.set_target_list(path) #Set the target list to the new path
    


    ### Shooting Prediction Mechanics ###
    def find_position_in_frames(self, frames): #Find the position in frames
        copy_x = self.x #Set copy values to uesr the necessary values of the object without chaging them
        copy_y = self.y
        self.copy_target_list = self.target_list
        self.copy_target_index = self.target_index

        for i in range(frames): #Use predict move to emulate the update function and iterate over the number of frames requird
            copy_x, copy_y = self.predict_move(copy_x, copy_y)
    
        return (copy_x, copy_y)
    
    def predict_move(self, x, y): #Works the same as the move function but does not change global variables
        if self.copy_target_index < len(self.copy_target_list):
            x, y, result = self.move_to_node_predict(self.copy_target_list[self.copy_target_index], x, y)
            if result:
                self.copy_target_index += 1
            return (x, y)
        else:
            return (self.copy_target_list[self.copy_target_index - 1].x, self.copy_target_list[self.copy_target_index - 1].y)

    def move_to_node_predict(self, node, x, y): #Works the same as the move to node function but does not change global variables
        if node.x - 1 < x < x + 1 and node.y - 1 < y < node.y + 1: #return the x and y values as well as true if the object hits the target node
            x = node.x
            y = node.y
            return (x, y, True)

        if node.x > x: #Copies from the move ot node function but does not change images
            x += self.speed
        elif node.x < x:
            x -= self.speed
        elif node.y > y:
            y += self.speed
        elif node.y < y:
            y -= self.speed
        
        return (x, y, False) #Return the new x and y + false