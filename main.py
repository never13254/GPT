import pygame
import random
import math

WIDTH, HEIGHT = 800, 600
PLAYER_COUNT = 10

HEAVY = "heavy"
LIGHT = "light"

WEAPON_DATA = {
    "submachine_gun": {"damage": 10, "bullet": LIGHT, "speed_penalty": 0, "vision_bonus": 0},
    "shotgun": {"damage": 25, "bullet": HEAVY, "speed_penalty": 0, "vision_bonus": 0},
    "assault_rifle": {"damage": 15, "bullet": LIGHT, "speed_penalty": 0, "vision_bonus": 0},
    "pistol": {"damage": 8, "bullet": LIGHT, "speed_penalty": 0, "vision_bonus": 0},
    "machete": {"damage": 30, "bullet": None, "speed_penalty": 0, "vision_bonus": 0},
    "light_machine_gun": {"damage": 12, "bullet": HEAVY, "speed_penalty": 1, "vision_bonus": 0},
    "sniper_rifle": {"damage": 40, "bullet": HEAVY, "speed_penalty": 1, "vision_bonus": 150},
}

ARMOR_DATA = {
    1: {"protection": 0.2, "capacity": 3, "durability": 100},
    2: {"protection": 0.4, "capacity": 5, "durability": 150},
    3: {"protection": 0.6, "capacity": 7, "durability": 200},
}

class Weapon:
    def __init__(self, name):
        data = WEAPON_DATA[name]
        self.name = name
        self.damage = data["damage"]
        self.bullet_type = data["bullet"]
        self.speed_penalty = data["speed_penalty"]
        self.vision_bonus = data["vision_bonus"]
        self.ammo = 30

class Armor:
    def __init__(self, level):
        data = ARMOR_DATA[level]
        self.level = level
        self.protection = data["protection"]
        self.capacity = data["capacity"]
        self.durability = data["durability"]

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, name="bot"):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.name = name
        self.health = 100
        self.weapon = None
        self.armor = None
        self.speed = 2.5
        self.vision = 200
        self.inventory = {"small_med":0, "large_med":0, "grenade":0, "smoke":0, "molotov":0}

    def update_stats(self):
        if self.weapon:
            self.speed = 2.5 - self.weapon.speed_penalty
            self.vision = 200 + self.weapon.vision_bonus
        else:
            self.speed = 2.5
            self.vision = 200

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def take_damage(self, amount):
        if self.armor:
            absorbed = amount * self.armor.protection
            self.armor.durability -= absorbed
            amount -= absorbed
            if self.armor.durability <= 0:
                self.armor = None
        self.health -= amount

    def heal(self, amount):
        self.health = min(100, self.health + amount)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, owner):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        self.owner = owner
        self.speed = 8

    def update(self):
        self.rect.x += math.cos(self.angle) * self.speed
        self.rect.y += math.sin(self.angle) * self.speed
        if not pygame.Rect(0, 0, WIDTH, HEIGHT).contains(self.rect):
            self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((6,6))
        self.image.fill((0,255,0))
        self.rect = self.image.get_rect(center=(x,y))
        self.angle = angle
        self.speed = 4
        self.timer = 180

    def update(self):
        if self.timer > 0:
            self.rect.x += math.cos(self.angle) * self.speed
            self.rect.y += math.sin(self.angle) * self.speed
            self.speed *= 0.98
            self.timer -= 1
        else:
            self.kill()
            Explosion(self.rect.centerx, self.rect.centery)

class Explosion(pygame.sprite.Sprite):
    instances = pygame.sprite.Group()
    def __init__(self, x, y):
        super().__init__(Explosion.instances)
        self.image = pygame.Surface((80,80), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255,150,0,180), (40,40), 40)
        self.rect = self.image.get_rect(center=(x,y))
        self.timer = 15

    def update(self):
        self.timer -= 1
        if self.timer <=0:
            self.kill()

class Smoke(pygame.sprite.Sprite):
    instances = pygame.sprite.Group()
    def __init__(self, x,y):
        super().__init__(Smoke.instances)
        self.image = pygame.Surface((100,100), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200,200,200,150), (50,50), 50)
        self.rect = self.image.get_rect(center=(x,y))
        self.timer = 300

    def update(self):
        self.timer -= 1
        if self.timer <=0:
            self.kill()

class Fire(pygame.sprite.Sprite):
    instances = pygame.sprite.Group()
    def __init__(self, x,y):
        super().__init__(Fire.instances)
        self.image = pygame.Surface((60,60), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255,0,0,150), (30,30), 30)
        self.rect = self.image.get_rect(center=(x,y))
        self.timer = 300

    def update(self):
        self.timer -=1
        if self.timer <=0:
            self.kill()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Mini Battle Royale")
        self.clock = pygame.time.Clock()
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.grenades = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.human = Player(WIDTH//2, HEIGHT//2, (0,255,0), name="player")
        self.players.add(self.human)
        self.all_sprites.add(self.human)
        for i in range(9):
            bot = Player(random.randint(0, WIDTH), random.randint(0, HEIGHT), (255,0,0))
            self.players.add(bot)
            self.all_sprites.add(bot)
        self.weapon_pickups = []
        self.armor_pickups = []
        self.med_pickups = []
        self.grenade_pickups = []
        self.smoke_pickups = []
        self.molotov_pickups = []
        self.spawn_items()

    def spawn_items(self):
        names = list(WEAPON_DATA.keys())
        random.shuffle(names)
        for name in names:
            rect = pygame.Rect(random.randint(0, WIDTH-20), random.randint(0, HEIGHT-20),20,20)
            self.weapon_pickups.append((name, rect))
        for level in [1,2,3]:
            rect = pygame.Rect(random.randint(0, WIDTH-20), random.randint(0, HEIGHT-20),20,20)
            self.armor_pickups.append((level, rect))
        for i in range(3):
            rect = pygame.Rect(random.randint(0, WIDTH-20), random.randint(0, HEIGHT-20),20,20)
            self.med_pickups.append((25, rect))
            rect2 = pygame.Rect(random.randint(0, WIDTH-20), random.randint(0, HEIGHT-20),20,20)
            self.med_pickups.append((75, rect2))
        for i in range(3):
            self.grenade_pickups.append(pygame.Rect(random.randint(0,WIDTH-20),random.randint(0,HEIGHT-20),20,20))
            self.smoke_pickups.append(pygame.Rect(random.randint(0,WIDTH-20),random.randint(0,HEIGHT-20),20,20))
            self.molotov_pickups.append(pygame.Rect(random.randint(0,WIDTH-20),random.randint(0,HEIGHT-20),20,20))

    def pickup(self, player):
        for name, rect in self.weapon_pickups[:]:
            if player.rect.colliderect(rect):
                player.weapon = Weapon(name)
                player.update_stats()
                self.weapon_pickups.remove((name, rect))
                break
        for level, rect in self.armor_pickups[:]:
            if player.rect.colliderect(rect):
                player.armor = Armor(level)
                player.update_stats()
                self.armor_pickups.remove((level, rect))
                break
        for amount, rect in self.med_pickups[:]:
            if player.rect.colliderect(rect):
                if amount==25:
                    player.inventory["small_med"]+=1
                else:
                    player.inventory["large_med"]+=1
                self.med_pickups.remove((amount, rect))
        for rect in self.grenade_pickups[:]:
            if player.rect.colliderect(rect):
                player.inventory["grenade"]+=1
                self.grenade_pickups.remove(rect)
        for rect in self.smoke_pickups[:]:
            if player.rect.colliderect(rect):
                player.inventory["smoke"]+=1
                self.smoke_pickups.remove(rect)
        for rect in self.molotov_pickups[:]:
            if player.rect.colliderect(rect):
                player.inventory["molotov"]+=1
                self.molotov_pickups.remove(rect)

    def human_input(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1
        self.human.move(dx, dy)
        if keys[pygame.K_SPACE] and self.human.weapon and self.human.weapon.ammo>0:
            mx, my = pygame.mouse.get_pos()
            angle = math.atan2(my-self.human.rect.centery, mx-self.human.rect.centerx)
            bullet = Bullet(self.human.rect.centerx, self.human.rect.centery, angle, self.human)
            self.bullets.add(bullet)
            self.all_sprites.add(bullet)
            self.human.weapon.ammo -= 1
        if keys[pygame.K_1] and self.human.inventory["small_med"]>0:
            self.human.inventory["small_med"]-=1
            self.human.heal(25)
        if keys[pygame.K_2] and self.human.inventory["large_med"]>0:
            self.human.inventory["large_med"]-=1
            self.human.heal(75)
        if keys[pygame.K_g] and self.human.inventory["grenade"]>0:
            mx, my = pygame.mouse.get_pos()
            angle = math.atan2(my-self.human.rect.centery, mx-self.human.rect.centerx)
            grenade = Grenade(self.human.rect.centerx, self.human.rect.centery, angle)
            self.grenades.add(grenade)
            self.all_sprites.add(grenade)
            self.human.inventory["grenade"]-=1
        if keys[pygame.K_h] and self.human.inventory["smoke"]>0:
            mx, my = pygame.mouse.get_pos()
            Smoke(mx, my)
            self.human.inventory["smoke"]-=1
        if keys[pygame.K_j] and self.human.inventory["molotov"]>0:
            mx, my = pygame.mouse.get_pos()
            Fire(mx, my)
            self.human.inventory["molotov"]-=1

    def bot_ai(self):
        for bot in self.players:
            if bot is self.human:
                continue
            angle = math.atan2(self.human.rect.centery-bot.rect.centery, self.human.rect.centerx-bot.rect.centerx)
            bot.move(math.cos(angle), math.sin(angle))
            if bot.weapon and bot.weapon.ammo>0:
                bullet = Bullet(bot.rect.centerx, bot.rect.centery, angle, bot)
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)
                bot.weapon.ammo -= 1
            else:
                self.pickup(bot)

    def check_hits(self):
        for bullet in self.bullets:
            hits = [p for p in self.players if p.rect.colliderect(bullet.rect) and p is not bullet.owner]
            for p in hits:
                p.take_damage(bullet.owner.weapon.damage if bullet.owner.weapon else 10)
                bullet.kill()
        for explosion in Explosion.instances:
            for p in self.players:
                if p.rect.centerx in range(explosion.rect.left, explosion.rect.right) and p.rect.centery in range(explosion.rect.top, explosion.rect.bottom):
                    p.take_damage(50)
        for fire in Fire.instances:
            for p in self.players:
                if fire.rect.colliderect(p.rect):
                    p.take_damage(0.5)

    def draw_items(self):
        for name, rect in self.weapon_pickups:
            pygame.draw.rect(self.screen, (0,0,255), rect)
        for level, rect in self.armor_pickups:
            pygame.draw.rect(self.screen, (150,150,150), rect)
        for amount, rect in self.med_pickups:
            color = (0,255,0) if amount==25 else (0,150,0)
            pygame.draw.rect(self.screen, color, rect)
        for rect in self.grenade_pickups:
            pygame.draw.rect(self.screen, (0,255,0), rect)
        for rect in self.smoke_pickups:
            pygame.draw.rect(self.screen, (200,200,200), rect)
        for rect in self.molotov_pickups:
            pygame.draw.rect(self.screen, (255,100,0), rect)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.human_input()
            self.bot_ai()
            self.pickup(self.human)
            self.all_sprites.update()
            Explosion.instances.update()
            Smoke.instances.update()
            Fire.instances.update()
            self.check_hits()
            self.screen.fill((50,50,50))
            self.draw_items()
            self.all_sprites.draw(self.screen)
            Explosion.instances.draw(self.screen)
            Smoke.instances.draw(self.screen)
            Fire.instances.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    Game().run()
