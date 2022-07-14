import pygame
import numpy as np
from projectile import Bullet, Explosive, Fire
from operator import attrgetter
from random import choice
from game_data import tower1_stats, tower2_stats, tower3_stats

class Tower(): #Parent Class of other towers
    def __init__(self, world, node):
        self.world = world
        self.screen = world.screen

        if node != None:
            self.current_node = node
            self.x = node.x
            self.y = node.y

        self.x = None
        self.y = None
        self.image_width = 50
        self.image_height = 50

        self.activated = False
        self.selected = False

        self.enemies_in_range = []
        self.projectiles = []
        self.shoot_timer = 0
        self.shoot_cooldown = 30
        
        self.level = 1
        self.animation_count = 0
        self.images = []

        #Variables different for every tower
        self.image = None
        self.damage = None
        self.buy_cost = None
        self.tower_range = None
        self.upgrade_costs = None
        
        
    def update(self): #Draw the tower, call the state machine and update the enemies in range
        self.enemies_in_range = self.in_range(self.world.enemy_agents)
        self.current_state()
        self.draw()

    def draw(self): #Draw the tower with animation
        if self.activated: #If activeted, draw the animated image of the tower
            self.animation_count += 1
            if self.animation_count >= len(self.images) * 10:
                self.animation_count = 0
            self.image = self.images[self.animation_count // 10]
            self.screen.blit(self.image, (self.x - (self.image_width / 2), self.y - (self.image_height / 2)))
            if self.selected: #Draw the tower range if selected
                self.draw_tower_range()
        else: #If not activated draw the static image at the mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.screen.blit(self.image, (mouse_x - (self.image_width / 2), mouse_y - (self.image_height / 2)))
    
    def load_images(self, file_location, no_of_sprites): #Load a group of images for animation
        images = []
        for i in range(no_of_sprites):
            images.append(pygame.transform.scale(pygame.image.load(file_location + str(i) + ".png"), (self.image_width, self.image_height)))

        return images
    
    def activate_tower(self, node): #Set the tower to active and initialize its position
        self.activated = True
        self.current_node = node
        self.x = node.x
        self.y = node.y
    
    def on_click(self, mouse_pos): #Check if the mouse position is on the tower
        mouse_x, mouse_y = mouse_pos
        if self.x - 20 < mouse_x < self.x + 20 and self.y - 20 < mouse_y < self.y + 20:
            return True
        return False
    
    def draw_tower_range(self): #Draw a transparent range
        image = pygame.Surface(self.tower_range) #Set the image to surface
        image.set_colorkey((0, 100, 0)) 
        image.set_alpha(60) #Add transparancy to the image
        pygame.draw.rect(image, (169, 169, 169), image.get_rect(), 4)
        self.screen.blit(image, (self.x - (image.get_width() / 2), self.y - (image.get_height() / 2)))
    
    def in_range(self, objects): #
        in_range = []
        for object in objects:
            if self.x - (self.tower_range[0] / 2) < object.x < self.x + (self.tower_range[0] / 2) and\
            self.y - (self.tower_range[1] / 2) < object.y <  self.y + (self.tower_range[1] / 2):
                in_range.append(object)
        
        return in_range
    
    def optimal_projectile(self, target, type = Bullet): #Return an optimal projectile that intersects the target in a certain amount of frames
        target_position_in_frames = target.find_position_in_frames(30) #Find the enemies position in 30 frames
        projectiles = {}
        for x in range(int(target.x), int(target.x) + 30, 1): #Create sample bullets to find their position in 30 frames and add it to the dictionary
            for y in range(int(target.y) - 30, int(target.y) + 30, 1):
                projectile = type(self, self.world, self.x, self.y, (x, y), load_images = False)
                position_in_frames = projectile.position_in_frames(30)
                projectiles[position_in_frames] = projectile

        closest = self.closest_point(list(projectiles.keys()), target_position_in_frames) #Find the projectile that has the closest point the targets position
        proj = projectiles[closest]
        proj.set_images() #Load image of the chosen projectile
        return proj

    def closest_point(self, points, target): #Givena list of points, find the closest point to the target
        points = np.array(points)
        target_point = np.array(target)
        distances = np.linalg.norm(points-target_point, axis=1)
        min_index = np.argmin(distances)
        return tuple(points[min_index])
    
    def current_state(self):
        pass
    
    def upgrade(self):
        pass


class BloodMoonTower(Tower): #Inherits from tower
    Name = "Blood Moon Tower" #Static Variabhles
    Value = tower1_stats[0][4]
    Cost = tower1_stats[0][0]
    def __init__(self, world, node):
        super().__init__(world, node)
        self.name = "Blood Moon Tower"
        self.image = pygame.transform.scale(pygame.image.load("assets/blood_moon_tower/level1_0.png"), (self.image_width, self.image_height))
        self.damage = tower1_stats[self.level - 1][1]
        self.buy_cost = tower1_stats[self.level - 1][0]
        self.tower_range = tower1_stats[self.level - 1][2]

        self.level1_images = self.load_images("assets/blood_moon_tower/level1_", 11) #Load images for each level
        self.level2_images = self.load_images("assets/blood_moon_tower/level2_", 11)
        self.level3_images = self.load_images("assets/blood_moon_tower/level3_", 11)

        self.level_images = [self.level1_images, self.level2_images, self.level3_images]

        self.recharging_images = self.load_images("assets/blood_moon_tower/recharging", 11) #Load recharging imgaes

        self.images = self.level_images[self.level - 1]

        self.rebuilding_cooldown = tower1_stats[self.level - 1][3]
        self.rebuilding_timer = 0
        self.rebuild_available = False

        self.kill_counter = 0
        self.overdrive_threshold = 10
        self.overdrive_counter = 0

        self.upgrade_costs = [tower1_stats[1][0], tower1_stats[2][0]]
        self.value = tower1_stats[0][4]
        self.upgrade_values = [tower1_stats[1][4], tower1_stats[2][4]]
    
    def current_state(self): #Handles state machine
        self.images = self.level_images[self.level - 1] #Set images to approriate level images
        if self.world.enemy_agents:
            if self.enemies_in_range: #If there are enemies in range set to attacking state, otherwise dormant
                self.attacking_state()
            else:
                self.dormant_state()

    def attacking_state(self):
        if self.kill_counter < self.overdrive_threshold: #If kill counter less than threshold set to shooting state, otherwise overdrive
            self.shooting_state()
        else:
            self.overdrive_state()

    def shooting_state(self): #Handles shooting state
        best_target = max(self.enemies_in_range, key = attrgetter('x')) #Finds the enemy with the highest x value to target
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_cooldown:
            self.projectiles.append(self.optimal_projectile(best_target)) #Shoot the optimal projectile at the target
            self.shoot_timer = 0

    def overdrive_state(self): #Handles overdrive state
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_cooldown:
            for x in range(-50, 51, 20): #Shoot bullet projectiles in every direction of the tower
                for y in range(-50, 51, 20):
                    self.projectiles.append(Bullet(self, self.world, self.x, self.y, (self.x + x, self.y + y)))
            self.shoot_timer = 0
            self.overdrive_counter += 1
            if self.overdrive_counter >= 4: #If overdrive counter is greater than 4 reset kill counter and overdrive counter
                self.kill_counter = 0
                self.overdrive_counter = 0

    def dormant_state(self): #Handles dormant state
        if self.rebuild_available: #If rebuilding is available set to rebuilding state, otherwise recharging state
            self.rebuilding_state()
        else:
            self.recharging_state()

    def rebuilding_state(self): #Handles rebuilding state
        best_node = self.find_best_node()
        self.current_node = best_node
        self.x = best_node.x
        self.y = best_node.y
        self.rebuild_available = False

    def recharging_state(self): #Handles recharging state
        self.images = self.recharging_images #Change images to recharging images
        self.rebuilding_timer += 1
        if self.rebuilding_timer >= self.rebuilding_cooldown: #If timer exceeds the cooldown, make rebuild available
            self.rebuild_available = True
            self.rebuilding_timer = 0

    def find_best_node(self): #Used to find the best node, out of all valid nodes, to rebuild to based on the enemies around each node
        occupied = [x.current_node for x in self.world.towers]
        valid_nodes = [node for node in self.world.nodes if node.is_grass and node not in occupied]

        enemies_in_node_range = {}

        for node in valid_nodes:
            enemies_in_node_range[node] = node.number_of_enemies_in_range(self.tower_range)
        
        best_node_value = max(enemies_in_node_range.values())
        best_nodes = []

        for node, enemies_in_range in enemies_in_node_range.items():
            if enemies_in_range == best_node_value:
                best_nodes.append(node)

        return choice(best_nodes) #Return a random choice of one of the best nodes

    def upgrade(self, level): #Upgrade stats
        self.level = level
        self.damage = tower1_stats[level - 1][1]
        self.tower_range = tower1_stats[level - 1][2]
        self.rebuilding_cooldown = tower1_stats[level - 1][3]

class FireTotem(Tower):
    Name = "Fire Totem Tower"
    Value = tower2_stats[0][3]
    Cost = tower2_stats[0][0]
    def __init__(self, world, node):
        super().__init__(world, node)
        self.image = pygame.transform.scale(pygame.image.load("assets/fire_totem_tower/level1_0.png"), (self.image_width, self.image_height))
        self.damage = 100
        self.buy_cost = tower2_stats[self.level - 1][0]
        self.tower_range = (600, 600)

        self.level1_images = self.load_images("assets/fire_totem_tower/level1_", 7)
        self.level2_images = self.load_images("assets/fire_totem_tower/level2_", 7)
        self.level3_images = self.load_images("assets/fire_totem_tower/level3_", 7)

        self.level_images = [self.level1_images, self.level2_images, self.level3_images]
        
        self.images = self.level_images[self.level - 1]

        self.spawn_fire_timer = 300
        self.spawn_fire_cooldown = 300
        self.fire_duration = tower2_stats[self.level - 1][1]
        self.fires_thrown = 0
        self.overdrive_threshold = tower2_stats[self.level - 1][2]

        self.upgrade_costs = [tower2_stats[1][0], tower2_stats[2][0]]

        self.value = tower2_stats[0][3]
        self.upgrade_values = [tower2_stats[1][3], tower2_stats[2][3]]
        self.name = "Fire Totem Tower"
    
    def current_state(self): #State machine
        self.images = self.level_images[self.level - 1]
        if self.world.enemy_agents:
            if self.fires_thrown <= self.overdrive_threshold: #Shooting state if fires thrown is less than threshold, otherwise put to overdrive
                self.shooting_state()
            else:
                self.overdrive_state()
    
    def shooting_state(self): #Shoot fire projectiles once timer reached the cooldown number
        self.spawn_fire_timer += 1
        if self.spawn_fire_timer >= self.spawn_fire_cooldown:
            in_range_nodes = self.in_range(self.world.nodes)
            valid_nodes = [x for x in in_range_nodes if x.is_path] #Find all nodes in range that are paths
            random_node = choice(valid_nodes) #Send fires to random locations of valid nodes
            self.projectiles.append(Fire(self, self.world, self.x, self.y, random_node.square, self.fire_duration))
            self.fires_thrown += 1
            self.spawn_fire_timer = 0
    
    def overdrive_state(self): #Handles the overdrive state where multiple fire projectiles are launched simultaneously 
        self.spawn_fire_timer += 1
        if self.spawn_fire_timer >= self.spawn_fire_cooldown:
            in_range_nodes = self.in_range(self.world.nodes)
            valid_nodes = [x for x in in_range_nodes if x.is_path]
            for i in range(6):
                random_node = choice(valid_nodes)
                self.projectiles.append(Fire(self, self.world, self.x, self.y, random_node.square, self.fire_duration))
            self.spawn_fire_timer = 0
            self.fires_thrown = 0
    
    def upgrade(self, level): #Upgrade stats
        self.level = level
        self.fire_duration = tower2_stats[self.level - 1][1]
        self.overdrive_threshold = tower2_stats[self.level - 1][2]

class BlueFireTotem(Tower):
    Name = "Blue Fire Totem Tower"
    Value = tower3_stats[0][4]
    Cost = tower3_stats[0][0]
    def __init__(self, world, node):
        super().__init__(world, node)
        self.name = "Blue Fire Totem Tower"
        self.image = pygame.transform.scale(pygame.image.load("assets/blue_fire_totem_tower/level1_0.png"), (self.image_width, self.image_height))
        self.damage = tower3_stats[self.level - 1][1]
        self.aoe_damage = tower3_stats[self.level - 1][2]
        self.explosion_range = tower3_stats[self.level - 1][3]
        self.buy_cost = tower3_stats[self.level - 1][0]
        self.tower_range = (400, 400)

        self.level1_images = self.load_images("assets/blue_fire_totem_tower/level1_", 7)
        self.level2_images = self.load_images("assets/blue_fire_totem_tower/level2_", 7)
        self.level3_images = self.load_images("assets/blue_fire_totem_tower/level3_", 7)

        self.level_images = [self.level1_images, self.level2_images, self.level3_images]
        
        self.images = self.level_images[self.level - 1]

        self.spawn_fire_timer = 600
        self.spawn_fire_cooldown = 0

        self.level_width = [80, 150, 300]
        self.level_height = [80, 150, 300]
        self.explosion_width = self.level_width[self.level - 1]
        self.explosion_height = self.level_height[self.level - 1]

        self.overdrive = False
        self.overdrive_count = 0
        self.overdrive_threshold = 600
        self.overdrive_bullets = 0

        self.upgrade_costs = [tower3_stats[1][0], tower3_stats[2][0]]
        self.value = tower3_stats[0][4]
        self.upgrade_values = [tower3_stats[1][4], tower3_stats[2][4]]

    
    def current_state(self): #Handles state machine
        self.images = self.level_images[self.level - 1]
        if self.world.enemy_agents:
            if self.enemies_in_range: #Set to attacking state if enemies in range, otherwise dormant
                self.attacking_state()
            else:
                self.dormant_state()
    
    def attacking_state(self):
        if not self.overdrive: #Set to shooting stae if overdrive is unavailable, otherwise overdrive
            self.shooting_state()
        else:
            self.overdrive_state()

    def shooting_state(self): #Shoot explosive projectiles every 30 frames
        best_target = max(self.enemies_in_range, key = attrgetter('number_of_enemies_in_range')) #Find the enemy with the highest value of enemies in range
        self.shoot_timer += 1
        if self.shoot_timer >= 30:
            self.projectiles.append(self.optimal_projectile(best_target, type = Explosive)) #Find the optimal projectile 
            self.shoot_timer = 0
    
    def dormant_state(self): #Handles dormant state
        self.overdrive_count += 1
        if self.overdrive_count >= self.overdrive_threshold:
            self.overdrive = True
            self.overdrive_count = 0
    
    def overdrive_state(self): #handles overdrive state
        best_target = max(self.enemies_in_range, key = attrgetter('number_of_enemies_in_range'))
        self.shoot_timer += 1
        if self.shoot_timer >= 5: #Shoots explosives at an extremely fast rate
            self.projectiles.append(self.optimal_projectile(best_target, type = Explosive))
            self.shoot_timer = 0
            self.overdrive_bullets += 1
            if self.overdrive_bullets == 10: #Shoots only 10 bullets during overdrive
                self.overdrive_bullets = 0
                self.overdrive = False
    
    def upgrade(self, level): #Upgrade stats
        self.level = level
        self.damage = tower3_stats[self.level - 1][1]
        self.aoe_damage = tower3_stats[self.level - 1][2]
        self.explosion_range = tower3_stats[self.level - 1][3]
        self.explosion_width = self.level_width[self.level - 1]
        self.explosion_height = self.level_height[self.level - 1]