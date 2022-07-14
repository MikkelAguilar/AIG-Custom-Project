import pygame
import sys
import itertools
from node import Node
from enemies import Enemy
from towers import BloodMoonTower, FireTotem, BlueFireTotem
from game_data import goal_position, spawn_positions, path_positions, waves, aesthetic_images

pygame.font.init()

class TowerDefence:
    def __init__(self, width, height):
        pygame.display.set_caption('Defenders!') #Set window title
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.font2 = pygame.font.SysFont('Comic Sans MS', 15)

        self.clock = pygame.time.Clock()
        
        self.goal = goal_position
        self.spawns = spawn_positions
        self.paths = path_positions

        self.nodes = self.create_nodes()
        self.nodes_on_fire = []
        self.show_lines = False

        self.enemy_agents = [] #Bug(self, self.find_node(self.spawns[0]))
        self.towers = []
        self.in_hand = None
        
        self.spawn_timer = 0
        self.waves = waves
        self.current_wave_index = -1
        self.waves_completed = True
        self.go_to_next_level = False
        self.wave_finished = False
        self.game_over = False

        self.lives = 100
        self.credits = 1300#100000

        self.world_changed = False

        self.recommended_actions = self.find_best_actions()
        self.recommended = False

        self.images = aesthetic_images

    
    def run_game(self): #Run the game loop
        while True: #Keep the game running
            self.clock.tick(60)
            self.screen.fill((128,180,84))
            self.check_inputs()
            if not self.game_over: #Keep the main game running if not game over
                if not self.wave_finished:
                    self.handle_spawning()
                self.draw_nodes()
                self.draw_aesthetics()
                self.udpate_towers()
                self.udpate_enemies()
                self.update_projectiles()
                self.draw_hand()
                if self.recommended:
                    if not self.enemy_agents: #Draw recommendations mid-waves
                        self.draw_recommendations()
            self.draw_text()
            pygame.display.flip()
    
    def check_inputs(self): #Handles and responsds to user input
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN: #Keyboard Inputs
                if event.key == pygame.K_s:
                    self.show_lines = not self.show_lines #Show lines for nodes
                if event.key == pygame.K_1: #Add towers to hand with numbers
                    self.in_hand = BloodMoonTower(self, None)
                if event.key == pygame.K_2:
                    self.in_hand = FireTotem(self, None)
                if event.key == pygame.K_3:
                    self.in_hand = BlueFireTotem(self, None)
                if event.key == pygame.K_u:
                    self.upgrade_tower()
                if event.key == pygame.K_r:
                    if not self.enemy_agents:
                        self.recommended_actions = self.find_best_actions()
                        self.recommended = not self.recommended
                if event.key == pygame.K_BACKSPACE: #Used to sell
                    self.sell_selected()
                if event.key == pygame.K_SPACE: #Used to start the next wave
                    if not self.enemy_agents:
                        self.recommended = False
                        self.go_to_next_level = not self.go_to_next_level
                if event.key == pygame.K_c:
                    self.credits += 10000
            elif event.type == pygame.MOUSEBUTTONDOWN: #Handle mouse input
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.in_hand:
                        self.place_tower(mouse_pos)
                    else:
                        self.tower_clicked(mouse_pos)
                if event.button == 3:
                    self.in_hand = None
            elif event.type == pygame.QUIT:
                pygame.quit() #Quit the application
                sys.exit()

    def draw_nodes(self): #Draw the nodes and their images
        for node in self.nodes:
            node.draw()
            if self.show_lines:
                node.draw_lines()
        
        if self.nodes_on_fire != self.find_nodes_on_fire(): #Check if nodes on fire have changed, if it has set world changed to true
            self.nodes_on_fire = self.find_nodes_on_fire()
            self.world_changed = True

    def draw_aesthetics(self): #Draw the aesthetic images (i.e. the trees)
        for image in self.images:
            self.screen.blit(image[0], image[1])

    def udpate_enemies(self): #Updates all the enemy agents
        dead_agents = []
        for enemy in self.enemy_agents:
            enemy.update()
            if self.world_changed: #If the world has changed, set the enemies change path to true
                enemy.change_path = True
            if enemy.health <= 0: #If the enemies have no health, increase credits and add the agent to the dead agents list
                self.credits += enemy.dropped_credits
                dead_agents.append(enemy)
                continue
            if enemy.goal_reached: #If the enemy reaches the goal remove lives and append to the dead agents list
                self.lives -= enemy.lost_lives
                dead_agents.append(enemy)
                if self.lives < 1: #If you have no lives, its game over
                    self.game_over = True
        self.world_changed = False
        for enemy in self.enemy_agents: #Remove all agents from dead agents from enemy agents list
            if enemy in dead_agents:
                self.enemy_agents.remove(enemy)
    
    def udpate_towers(self): #Update all the towers
        for tower in self.towers:
            tower.update()
    
    def draw_text(self):
        if not self.game_over:
            text_surface = self.font.render('Wave : ' + str(self.current_wave_index + 1) + "    Lives : " + str(self.lives) + "    Credits : " + str(self.credits), False, (0, 0, 0))
            self.screen.blit(text_surface, (600 - (text_surface.get_width() / 2), 740))
        else:
            text_surface = self.font.render('You Died at Wave : ' + str(self.current_wave_index + 1), False, (0, 0, 0))
            self.screen.blit(text_surface, (600 - (text_surface.get_width() / 2), self.height / 2 - (text_surface.get_height() / 2)))

    def create_nodes(self): #Used to initially create nodes
        nodes = []
        separator = 40
        x_index = 0
        for x in range(40, self.width - 40 + 1, separator): #Create a node every 40 units at the x axis
            y_index = 0
            for y in range(40, self.height - 40 + 1, separator): #Create a node every 40 units at the y axis
                skip_check = False
                for number in range(len(self.paths)):
                    if (x_index, y_index) in self.paths[number]: #Check if position is in the paths list
                        nodes.append(Node(self, x, y, x_index, y_index, is_path = True, path_type = number))
                        skip_check = True
                        break
                
                if not skip_check:
                    if (x_index, y_index) == goal_position: #Check if position is in the goal list
                        nodes.append(Node(self, x, y, x_index, y_index, is_goal = True))
                    elif (x_index, y_index) in self.spawns: #Check if position is in the spawn list
                        nodes.append(Node(self, x, y, x_index, y_index, is_start = True))
                    elif x_index == 0 or x_index == 28 or y_index == 0 or y_index == 18: #Check if position is a board
                        nodes.append(Node(self, x, y, x_index, y_index, is_border = True))
                    else: #Create a regular node
                        nodes.append(Node(self, x, y, x_index, y_index, is_grass = True))
                y_index += 1
            x_index += 1

        for node in nodes: #Initlalize all the neighbours of the nodes
            node.initialize_neighbours(nodes)
        
        return nodes
    
    def find_node(self, square, type = 'relative'): #Given a nodes relative or actual position, return the node itself
        for node in self.nodes:
            if type == 'relative':
                if node.relative_square == square:
                    return node
            elif type == 'actual':
                if node.square == square:
                    return node

        return None
    
    def upgrade_tower(self): #Upgrading the tower
        for tower in self.towers:
            if tower.selected: #Ugrade is available if the tower is selected, less than level 3 and credits are enough to purchase upgrade
                if tower.level < 3:
                    if self.credits >= tower.upgrade_costs[tower.level - 1]:
                        self.credits -= tower.upgrade_costs[tower.level - 1]
                        tower.upgrade(tower.level + 1)

    def sell_selected(self): #Remove the selected tower and gain credits for half its buy cost
        for tower in self.towers:
            if tower.selected:
                self.towers.remove(tower)
                self.credits += tower.buy_cost // 2
    


    ###  Spawning Mechanics  ###
    def generate_spawn_queue(self): #Create a spawn queue for 3 different spawning areas
        current_wave = self.waves[self.current_wave_index]
        spawn_queue = [[], [], []]
        for spawn_number in range(len(spawn_queue)): #Loop through the spawn queue, the current wave and the values in the current waves spawn number
            for x in range(len(current_wave[spawn_number])):
                for i in range(current_wave[spawn_number][x]): #Append different enemy types depending on the spawn nubmer
                    if x == 0:
                        spawn_queue[spawn_number].append(Enemy(self, self.find_node(self.spawns[spawn_number])))
                    elif x == 1:
                        spawn_queue[spawn_number].append(Enemy(self, self.find_node(self.spawns[spawn_number]), type = 'Fly'))
                    elif x == 2:
                        spawn_queue[spawn_number].append(Enemy(self, self.find_node(self.spawns[spawn_number]), type = 'Green Bug'))
                    elif x == 3:
                        spawn_queue[spawn_number].append(Enemy(self, self.find_node(self.spawns[spawn_number]), type = 'Long Bug'))
                    elif x == 4:
                        spawn_queue[spawn_number].append(Enemy(self, self.find_node(self.spawns[spawn_number]), type = 'Pink Bug'))
                    elif x == 5:
                        spawn_queue[spawn_number].append(Enemy(self, self.find_node(self.spawns[spawn_number]), type = 'Spider'))
        
        return spawn_queue

    def spawn(self, spawn_queue): #Spawn the enemies given a spawn queue
        spawn0 = spawn_queue[0]
        spawn1 = spawn_queue[1]
        spawn2 = spawn_queue[2]
        
        self.spawn_timer += 1
        if self.spawn_timer == 10: #Spawn in all locations every 10 frames
            if spawn0 or spawn1 or spawn2:
                if spawn0:
                    self.enemy_agents.append(spawn0[0])
                    spawn0.pop(0)
                if spawn1:
                    self.enemy_agents.append(spawn1[0])
                    spawn1.pop(0)
                if spawn2:
                    self.enemy_agents.append(spawn2[0])
                    spawn2.pop(0)
            else: #If thje spawn queues are empty, set waves completed to true
                self.waves_completed = True
            self.spawn_timer = 0
    
    def handle_spawning(self): #Handle the spawning of monsters
        if not self.waves_completed: #If the waves are not complete, keep spawning
            self.spawn(self.current_spawn)
        else: #If waves are complete, do nothing until the go to next level is set to true
            if self.go_to_next_level:
                self.current_wave_index += 1
                if self.current_wave_index == 10: #If 10 waves have been completed, stop spawning
                    self.wave_finished = True
                    return
                self.current_spawn = self.generate_spawn_queue() #Generate a new spawn queue
                self.go_to_next_level = False
                self.waves_completed = False
    
    def tower_clicked(self, mouse_pos): #If an activated tower is clicked, set that towers selected value to true
        for tower in self.towers:
            if tower.on_click(mouse_pos):
                tower.selected = True
            else:
                tower.selected = False
    


    ###  Hand Mechanics  ###
    def valid_node_on_mouse(self, mouse_pos): #Check if the node on the mouse position is a valid position for towers
        for node in self.nodes:
            if node.is_grass and not self.tower_in_node(node) and node.on_click(mouse_pos): #If the node is grass, there is no tower in the node and it is clicked, return the node
                return node
    
    def tower_in_node(self, node):
        for tower in self.towers:
            if (tower.x, tower.y) == (node.x, node.y):
                return True
        
        return False
        
    def draw_hand(self): #Draw the item you are currently holding
        if self.in_hand != None:
            self.in_hand.draw()
    
    def place_tower(self, mouse_pos): #Place the tower on a valid node
        node_hovered = self.valid_node_on_mouse(mouse_pos)
        if node_hovered and self.credits >= self.in_hand.buy_cost:
            self.in_hand.activate_tower(node_hovered) #Activate the tower in hand
            self.towers.append(self.in_hand)
            self.credits -= self.in_hand.buy_cost
            self.in_hand = None #Set the node in hand to None
    


    ### Projectile Mechanics ###
    def update_projectiles(self): #Update all the projectiles
        for tower in self.towers:
            for projectile in tower.projectiles:
                projectile.update()
                if projectile.outside_screen(): #Remove the projectile from the list if it is outside the screen
                    tower.projectiles.remove(projectile)
                    continue
                for enemy in self.enemy_agents: 
                    if projectile.handle_collision(enemy): #When colliding with an enemy, break the loop
                        break
    
    def find_nodes_on_fire(self): #Add to the list nodes on fire if a specific type of projectile (fire) has reached its destination node
        nodes_on_fire = []
        for tower in self.towers:
            for projectile in tower.projectiles:
                if projectile.reached_destination:
                    node = self.find_node((projectile.x, projectile.y), type = 'actual')
                    nodes_on_fire.append(node.relative_square)
        
        return nodes_on_fire




    ### Recommendation System Mechanics ###
    def find_best_actions(self): #Find the best course of action to take
        actions = self.find_actions()
        possible_combinations = list(itertools.combinations(actions, 3)) #Find all list of all possible combinations of 3 unique actions

        best_combination = None
        best_combination_value = None

        for combs in possible_combinations: #Loop through all the possible combinations
            value = 0
            cost = 0
            for action_name in combs:
                value += actions[action_name]['Value']
                cost += actions[action_name]['Cost']

            if cost <= self.credits: #If the total cost of the actions combined is less than the credits needed, checki if its value is greater than the current best value
                if best_combination == None:
                    best_combination = combs
                    best_combination_value = value
                else:
                    if value > best_combination_value: #If its value is greater than the current best, set it as the current best combination
                        best_combination = combs
                        best_combination_value = value
        
        return best_combination

    def find_actions(self): #Find all the possible actions
        actions = {}
        actions["Do Nothing (1)"] = {'Cost' : 0, 'Value' : 0} #Add 3 actions to do nothing as, the worse case scenrio would be having no credits to peform 1 to 3 actions 
        actions["Do Nothing (2)"] = {'Cost' : 0, 'Value' : 0}
        actions["Do Nothing (3)"] = {'Cost' : 0, 'Value' : 0}
        actions["Buy Blood Moon Tower"] = {'Cost' : BloodMoonTower.Cost, 'Value' : BloodMoonTower.Value} #By default add buying the towers as one of the options
        actions["Buy Fire Totem Tower"] = {'Cost' : FireTotem.Cost, 'Value' : FireTotem.Value}
        actions["Buy Blue Fire Totem Tower"] = {'Cost' : BlueFireTotem.Cost, 'Value' : BlueFireTotem.Value}
        for tower in self.towers:
            if tower.level < 3: #If the tower level is less than 3, add the action of upgrading that tower to actions with its designated cost and value
                actions[f"Upgrade {tower.name} to {tower.level + 1} at {tower.current_node.relative_square}"] = \
                    {'Cost' : tower.upgrade_costs[tower.level - 1], 'Value' : tower.upgrade_values[tower.level - 1]}#tower.upgrade_values[tower.level - 1]
        
        return actions
    
    def draw_recommendations(self): #Draw the Recommended actions at the bottom left of the screen if the action is not 'Do Nothing'
        index = 735
        if 'Do Nothing' in self.recommended_actions[0] and 'Do Nothing' in self.recommended_actions[1] and 'Do Nothing' in self.recommended_actions[2]: #If all three actions read do nothing, draw a text the says not enough credits
            text_surface = self.font2.render("Not Enough Credits", False, (0, 0, 0))
            self.screen.blit(text_surface, (65, 720))
        else:
            for action in self.recommended_actions: #Loop through actions and write them if they are do not have do nothing in them
                if "Do Nothing" not in action:
                    index -= 15
                    text_surface = self.font2.render(action, False, (0, 0, 0))
                    self.screen.blit(text_surface, (65, index))


if __name__ == '__main__':
    game = TowerDefence(1200, 800)
    game.run_game() 