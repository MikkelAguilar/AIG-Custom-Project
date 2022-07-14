import pygame

class Node:
    def __init__(self, world, x, y, relative_x, relative_y, is_grass = False, is_goal = False, is_start = False, is_border = False, is_path = False, path_type = 0):
        self.world = world
        self.screen = world.screen
        
        self.is_grass = is_grass
        self.is_goal = is_goal
        self.is_start = is_start
        self.is_border = is_border
        self.is_path = is_path
        self.path_type = path_type

        if not self.is_goal and not self.is_start and not self.is_border and not self.is_path: #set is normal to true of it is nto a goal, start, border or path node
            self.is_normal = True
        
        self.x = x
        self.y = y
        self.square = (x, y)
        self.relative_x = relative_x
        self.relative_y = relative_y
        self.relative_square = (relative_x, relative_y)

        self.neighbours = {}

        self.image_width = 40
        self.image_height = 40

        self.path_image_names = ["", "_top", "_bottom", "_left", "_right", "_top_left", "_top_right", "_bottom_left", "_bottom_right", "_left_right", "_top_bottom"]

        #Initialize different images depending ont he node type
        if self.is_border:
            self.image = pygame.transform.scale(pygame.image.load("assets/grass.png").convert(), (self.image_width, self.image_height))
        elif self.is_grass:
            self.image = pygame.transform.scale(pygame.image.load("assets/blank.png").convert(), (self.image_width, self.image_height))
        elif self.is_path:
            for i in range(len(self.path_image_names)):
                if i == self.path_type:
                    self.image = pygame.transform.scale(pygame.image.load("assets/paths/path" + self.path_image_names[i] + ".png").convert(), (self.image_width, self.image_height))
        elif self.is_goal:
            self.image = pygame.transform.scale(pygame.image.load("assets/goal.png"), (self.image_width, self.image_height))
        elif self.is_start:
            self.image = pygame.transform.scale(pygame.image.load("assets/start.png"), (self.image_width, self.image_height))
    
    def initialize_neighbours(self, all_nodes): #Initialize the neighbour nodes
        for node in all_nodes: #Loop through the nodes and see if the relative square is one square away from the node
            if node.relative_square == (self.relative_x + 1, self.relative_y):
                self.neighbours['right'] = node
            elif node.relative_square == (self.relative_x - 1, self.relative_y):
                self.neighbours['left'] = node
            elif node.relative_square == (self.relative_x, self.relative_y + 1): 
                self.neighbours['down'] = node
            elif node.relative_square == (self.relative_x, self.relative_y - 1):
                self.neighbours['up'] = node
        
    def draw(self): #Draw the node images
        self.screen.blit(self.image, (self.x - (self.image_width / 2), self.y - (self.image_height / 2)))
    
    def draw_lines(self): #Draw the lines connecting the paths and the goal
        if self.is_path or self.is_goal:
            for neighbour in self.neighbours.values():
                if neighbour.is_path or neighbour.is_goal:
                    pygame.draw.line(self.screen, (0, 0, 0), self.square, neighbour.square)
    
    def on_click(self, mouse_pos): #Check if node is clicked
        mouse_x, mouse_y = mouse_pos
        if self.x - 20 < mouse_x < self.x + 20 and self.y - 20 < mouse_y < self.y + 20:
            return True
        return False

    def number_of_enemies_in_range(self, tower_range): #Given a range find the number of enemies within that range
        no_of_enemies = 0
        for enemy in self.world.enemy_agents:
            if self.x - (tower_range[0] / 2) < enemy.x < self.x + (tower_range[0] / 2) and\
            self.y - (tower_range[1] / 2) < enemy.y <  self.y + (tower_range[1] / 2):
                no_of_enemies += 1
        
        return no_of_enemies