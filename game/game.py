# -*- coding: utf-8 -*-
import random
import math
from pgzero.actor import Actor
from pgzero.keyboard import keyboard
import pgzrun

pgzrun.go()
WIDTH = 800
HEIGHT = 600

game_state = "menu"
music_on = True

background = Actor("background")
music.play("bgmusic")
music.set_volume(0.5)

platforms = [
    Rect((100, 500), (200, 20)),
    Rect((300, 450), (200, 20)),
    Rect((500, 350), (200, 20)),
    Rect((200, 250), (200, 20)),
    Rect((400, 150), (200, 20)),
]

hero = None
enemies = []
flag = Actor("flag", (WIDTH // 2, 100))

def draw():
    screen.clear()
    background.draw()
    if game_state == "menu":
        draw_menu()
    elif game_state == "game":
        hero.draw()
        for enemy in enemies:
            enemy.draw()
        for platform in platforms:
            screen.draw.filled_rect(platform, "brown")
        flag.draw()
        screen.draw.text(f"HP: {hero.hp}", topleft=(10, 10), fontsize=30, color="white")
    elif game_state == "win":
        screen.draw.text("YOU WIN!", center=(WIDTH // 2, HEIGHT // 2 - 30), fontsize=80, color="gold")
        screen.draw.text("Click to return to menu", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=40, color="white")

def update():
    global game_state
    if game_state == "game":
        hero.update()
        check_platform_collision(hero)
        for enemy in enemies:
            enemy.update()
            if hero.actor.colliderect(enemy.actor):
                hero.hp -= 1
                if hero.hp <= 0:
                    hero.respawn()
        if check_finish():
            game_state = "win"

def draw_menu():
    screen.draw.text("MY PLATFORMER", center=(WIDTH // 2, 100), fontsize=60, color="white")
    screen.draw.text("Start Game", center=(WIDTH // 2, 230), fontsize=40, color="yellow")
    screen.draw.text("ON/OFF Music", center=(WIDTH // 2, 300), fontsize=40, color="cyan")
    screen.draw.text("Exit", center=(WIDTH // 2, 370), fontsize=40, color="red")

def on_mouse_down(pos):
    global game_state, music_on, enemies, hero

    if game_state == "menu":
        if 300 < pos[0] < 500 and 210 < pos[1] < 250:
            game_state = "game"
            enemies = []
            for platform in random.sample(platforms[1:], 3):
                if random.choice([True, False]):
                    enemies.append(Enemy(platform))
                else:
                    enemies.append(Enemy2(platform))
            hero.respawn()
        elif 300 < pos[0] < 500 and 280 < pos[1] < 320:
            music_on = not music_on
            if music_on:
                music.play("bgmusic")
                music.set_volume(0.5)
            else:
                music.stop()
        elif 300 < pos[0] < 500 and 350 < pos[1] < 390:
            exit()
    elif game_state == "win":
        game_state = "menu"

class Hero:
    def __init__(self):
        self.idle_frames_right = ["hero_idle1", "hero_idle2"]
        self.idle_frames_left = ["hero_idle1_left", "hero_idle2_left"]
        self.run_frames_right = ["hero_run1", "hero_run2"]
        self.run_frames_left = ["hero_run1_left", "hero_run2_left"]
        self.jump_frame_right = "hero_jump"
        self.jump_frame_left = "hero_jump_left"
        self.index = 0
        self.direction = 1
        self.actor = Actor(self.idle_frames_right[self.index])
        self.actor.x = 150
        self.actor.y = 480
        self.vy = 0
        self.jumps_left = 2
        self.on_ground = False
        self.animation_counter = 0
        self.hp = 3
        self.can_jump = True

    def respawn(self):
        self.actor.x = 150
        self.actor.y = 480
        self.vy = 0
        self.hp = 3
        self.jumps_left = 2
        self.can_jump = True

    def update(self):
        moving = False

        if keyboard.a:
            self.actor.x -= 3
            self.direction = -1
            moving = True
        elif keyboard.d:
            self.actor.x += 3
            self.direction = 1
            moving = True

        if keyboard.w and self.can_jump and self.jumps_left > 0:
            self.vy = -10
            self.jumps_left -= 1
            self.can_jump = False
            if music_on:
                sounds.jump.set_volume(0.8)
                sounds.jump.play()
        elif not keyboard.w:
            self.can_jump = True

        self.vy += 0.5
        self.actor.y += self.vy

        if self.actor.y > HEIGHT:
            self.respawn()

        self.animation_counter += 1

        if self.vy < 0 or not self.on_ground:
            self.actor.image = self.jump_frame_right if self.direction == 1 else self.jump_frame_left
        elif moving:
            if self.animation_counter % 10 == 0:
                self.index = (self.index + 1) % len(self.run_frames_right)
            self.actor.image = self.run_frames_right[self.index] if self.direction == 1 else self.run_frames_left[self.index]
        else:
            if self.animation_counter % 20 == 0:
                self.index = (self.index + 1) % len(self.idle_frames_right)
            self.actor.image = self.idle_frames_right[self.index] if self.direction == 1 else self.idle_frames_left[self.index]

    def draw(self):
        self.actor.draw()


class Enemy:
    def __init__(self, platform):
        self.idle_frames = ["enemy_idle1", "enemy_idle2"]
        self.run_frames = ["enemy_walk1", "enemy_walk2"]
        self.index = 0
        self.actor = Actor(self.idle_frames[self.index])
        self.platform = platform
        self.actor.y = platform.top - 20
        self.actor.x = random.randint(platform.left + 20, platform.right - 20)
        self.left_bound = platform.left + 10
        self.right_bound = platform.right - 10
        self.speed = 2
        self.direction = 1
        self.animation_counter = 0

    def update(self):
        self.actor.x += self.speed
        if self.actor.x < self.left_bound or self.actor.x > self.right_bound:
            self.speed *= -1
            self.direction *= -1

        self.animation_counter += 1
        if self.animation_counter % 10 == 0:
            self.index = (self.index + 1) % len(self.run_frames)
            self.actor.image = self.run_frames[self.index]

        self.actor.flip_x = self.speed < 0

    def draw(self):
        self.actor.draw()


class Enemy2:
    def __init__(self, platform):
        self.idle_frames = ["enemy2_idle1", "enemy2_idle2"]
        self.index = 0
        self.actor = Actor(self.idle_frames[self.index])
        self.platform = platform
        self.actor.x = random.randint(platform.left + 20, platform.right - 20)
        self.actor.y = platform.top - 20
        self.base_y = self.actor.y
        self.jump_amplitude = 30
        self.jump_speed = 0.1
        self.time = 0
        self.animation_counter = 0

    def update(self):
        self.time += self.jump_speed
        self.actor.y = self.base_y + self.jump_amplitude * math.sin(self.time)

        self.animation_counter += 1
        if self.animation_counter % 10 == 0:
            self.index = (self.index + 1) % len(self.idle_frames)
            self.actor.image = self.idle_frames[self.index]

    def draw(self):
        self.actor.draw()

def check_platform_collision(hero):
    hero.on_ground = False
    for platform in platforms:
        if platform.collidepoint((hero.actor.x, hero.actor.y + hero.actor.height // 2)) and hero.vy >= 0:
            hero.actor.y = platform.top - hero.actor.height // 2
            hero.vy = 0
            if not hero.on_ground:
                hero.jumps_left = 2
            hero.on_ground = True
            return


def check_finish():
    return hero.actor.colliderect(flag)

hero = Hero()