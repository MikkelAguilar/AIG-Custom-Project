import pygame
import math

class Projectile():
    def __init__(self, tower, world, x, y, target):
        self.world = world
        self.screen = world.screen
        self.screen_rect = world.screen.get_rect()

        self.x = x
        self.y = y

        self.target_x, self.target_y = target

        self.image = None
        self.image_width = 40
        self.image_height = 40

        self.tower = tower
        self.reached_destination = False
        self.animation_count = 0

    def update(self): #Update the projectile by its x and y velocities
        self.y -= float(self.y_vel)
        self.x -= float(self.x_vel)

        self.draw()

    def outside_screen(self): #Check if projectile is within the screen
        if self.x > self.screen_rect.width or self.x < 0 or self.y < 0 or self.y > self.screen_rect.height:
            return True
        return False

    def collision(self, object): #Check if object has collided with an object
        if object.x - 14 - self.radius < self.x < object.x + 14 + self.radius \
        and object.y - 14 - self.radius < self.y < object.y + 14 + self.radius:
            return True
        return False

    def load_images(self, file_location, no_of_sprites): #Load image for sprite animation
        images = []
        for i in range(no_of_sprites):
            images.append(pygame.transform.scale(pygame.image.load(file_location + str(i) + ".png"), (self.image_width, self.image_height)))

        return images

    #Abstract Methods
    def set_images(self):
        pass
    
    def draw(self):
        pass
    
    def handle_collision(self, enemy):
        pass

class Bullet(Projectile):
    def __init__(self, tower, world, x, y, target, load_images = True):
        super().__init__(tower, world, x, y, target)
        self.radius = 3
        self.speed = 4
        self.angle = math.atan2(y - self.target_y, x - self.target_x)
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed
    
    def draw(self): #Draw the bullet as a circle object
        pygame.draw.circle(self.screen, (255, 255, 255), (self.x, self.y), self.radius)
    
    def handle_collision(self, enemy): #Handles collision
        if self.collision(enemy): #If the projectile collides with an enemy, remove the projectile and lower the health of the enemy by tower damage
            self.tower.projectiles.remove(self)
            enemy.health -= self.tower.damage
            if enemy.health <= 0: #If the enemy is killed, add to the kill counter
                self.tower.kill_counter += 1
            return True
        return False    
    
    def position_in_frames(self, frames): #Find the position of the bullet in a certain amount of frames
        x_copy = self.x
        y_copy = self.y

        for i in range(frames): #Copies the update function but repeats it by a certain number of frames
            y_copy -= float(self.y_vel)
            x_copy -= float(self.x_vel)
        
        return(x_copy, y_copy)

class Fire(Projectile):
    def __init__(self, tower, world, x, y, target, duration, load_images = True):
        super().__init__(tower, world, x, y, target)
        self.radius = 5
        self.speed = 2

        self.angle = math.atan2(y - self.target_y, x - self.target_x)
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed

        self.fire_duration = duration
        self.fire_timer = 0

        if load_images:
            self.image = pygame.transform.scale(pygame.image.load("assets/fire/fire0.png"), (self.image_width, self.image_height))
            self.images = self.load_images("assets/fire/fire", 10)
    
    def update(self): #Update the projectile
        super().update()
        #If the projectile hits its target, set its velocities to 0 and set reached destination to true
        if self.target_x - 2 < self.x < self.target_x + 2 \
        and self.target_y - 2 < self.y < self.target_y + 2:
            self.x_vel = 0
            self.y_vel = 0
            self.x = self.target_x
            self.y = self.target_y
            self.fire_timer += 1
            self.reached_destination = True
            if self.fire_timer == self.fire_duration: #If the timer reached the duration remove the projectile
                self.tower.projectiles.remove(self)
    
    def draw(self): #Draw the fire image
        self.animation_count += 1
        if self.animation_count == len(self.images) * 10:
            self.animation_count = 0
        self.image = self.images[self.animation_count // 10]

        self.screen.blit(self.image, (self.x - (self.image_width / 2), self.y - (self.image_height / 2)))

    def handle_collision(self, enemy): #Handle collision
        if self.collision(enemy): #If the projectile collides with an enemy lower the enemeis health by tower damage
            enemy.health -= self.tower.damage
            return True

        return False

class Explosive(Projectile):
    def __init__(self, tower, world, x, y, target, load_images = True):
        super().__init__(tower, world, x, y, target)
        self.radius = 3
        self.speed = 4
        self.angle = math.atan2(y - self.target_y, x - self.target_x)
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed

        self.hit_object = False

        self.explosion_counter = 0
        self.explosion_duration = 180
        self.explosion_range = self.tower.explosion_range

        self.image_height = self.tower.explosion_height #180
        self.image_width = self.tower.explosion_width #180

        if load_images:
            self.image = pygame.transform.scale(pygame.image.load("assets/explosion/explosion_0.png"), (self.image_width, self.image_height))
            self.images = self.load_images("assets/explosion/explosion_", 21)
    
    def draw(self): #Draw the explosion
        if self.hit_object: #If an object is hit, play the explosion animmation
            self.animation_count += 1
            if self.animation_count == len(self.images) * 10:
                self.animation_count = 0

            self.image = self.images[self.animation_count // 10]

            self.screen.blit(self.image, (self.x - (self.image_width / 2), self.y - (self.image_height / 2)))
            self.explosion_counter += 1
            if self.explosion_counter >= self.explosion_duration: #If the counter exceed or equals the duration, remove it from the towers projectiles
                self.tower.projectiles.remove(self)
        else: #If the explosion has not hit anything yet, draw a circle
            pygame.draw.circle(self.screen, (255, 255, 255), (self.x, self.y), self.radius)
    
    def handle_collision(self, enemy):
        if not self.hit_object:
            if self.collision(enemy): #If the projectile collides with an enemy set the velocities to 0 and set hit object ot true
                self.hit_object = True
                self.x_vel = 0
                self.y_vel = 0
                enemy.health -= self.tower.damage
                nearby_enemies = enemy.in_range(self.world.enemy_agents, self.explosion_range) #find all the enemies in range of the explosion
                for neighbour_enemy in nearby_enemies:
                    neighbour_enemy.health -= self.tower.aoe_damage #Every neighbour enemy loses health based on the towers AOE damage
                return True

        return False    
    
    def position_in_frames(self, frames): #Find the position of the projectile in a certain amount of frames
        x_copy = self.x
        y_copy = self.y

        for i in range(frames): #copy the update functions and loop by the number of frames
            y_copy -= float(self.y_vel)
            x_copy -= float(self.x_vel)
        
        return(x_copy, y_copy)
    
    def set_images(self): #Set the images of the projectile
        self.image = pygame.transform.scale(pygame.image.load("assets/explosion/explosion_0.png"), (self.image_width, self.image_height))
        self.images = self.load_images("assets/explosion/explosion_", 21)