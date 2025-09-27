import os
import sys
import asyncio
from pygame.math import Vector2 as vector
import json
from pytmx.util_pygame import load_pygame
from overlay import Overlay
import pygame
from tile import Tile,CollisionTile,MovingPlatform
from player import Player
from bullet import Bullet,FireAnimation
from enemy import Enemy

class AllSprites(pygame.sprite.Group):
    def __init__(self,settings):
        super().__init__()
        self.display_surface=pygame.display.get_surface()
        self.offset=vector()
        self.settings=settings

        # sky
        self.fg_sky=pygame.image.load(os.path.join('graphics','sky','fg_sky.png')).convert_alpha()
        self.bg_sky=pygame.image.load(os.path.join('graphics','sky','bg_sky.png')).convert_alpha()
        tmx_map=load_pygame(os.path.join('data','map.tmx'))
        self.padding=self.settings['window_width']/2
        self.sky_width=self.bg_sky.get_width()
        map_width=tmx_map.tilewidth*tmx_map.width+2*self.padding
        self.sky_num=int(map_width//self.sky_width)
        

    def custom_draw(self,player):
        self.offset.x=player.rect.centerx-self.settings['window_width']/2
        self.offset.y=player.rect.centery-self.settings['window_height']/2

        # sky
        for x in range(self.sky_num):
            xpos=x*self.sky_width
            self.display_surface.blit(self.bg_sky,(xpos-self.offset.x/2.5,850-self.offset.y/2.5))
            self.display_surface.blit(self.fg_sky,(xpos-self.offset.x/2,800-self.offset.y/2))

        for sprite in sorted(self.sprites(),key=lambda sprite:sprite.z):
            offset_rect=sprite.rect.copy()
            offset_rect.center-=self.offset
            self.display_surface.blit(sprite.image,offset_rect)

class Game:
    def __init__(self):
        pygame.init()
        f=open('settings.json')
        self.settings=json.load(f)
        del f
        self.display_surface=pygame.display.set_mode((self.settings['window_width'],self.settings['window_height']))
        pygame.display.set_caption('Contra')
        self.clock=pygame.time.Clock()
        self.all_sprites=AllSprites(self.settings)
        self.collision_sprites=pygame.sprite.Group()
        self.platform_sprites=pygame.sprite.Group()
        self.vulnerable_sprites=pygame.sprite.Group()
        self.bullet_sprites=pygame.sprite.Group()
        self.setup()
        self.overlay=Overlay(self.player,self.settings)
        self.music=pygame.mixer.Sound(os.path.join('audio','music.wav'))
        self.music.set_volume(.5)

    def setup(self):
        map_tmx=load_pygame(os.path.join('data','map.tmx'))
        # tiles
        for x,y,surface in map_tmx.get_layer_by_name('Level').tiles():
            CollisionTile((x*64,y*64), surface, [self.all_sprites,self.collision_sprites])
        # layers
        for _ in ['BG','BG Detail','FG Detail Bottom','FG Detail Top']:
            for x,y,surface in map_tmx.get_layer_by_name(_).tiles():
                Tile((x*64,y*64),surface,self.all_sprites,self.settings['layers'][_])
        # entities
        for obj in map_tmx.get_layer_by_name('Entities'):
            if obj.name=='Player':
                self.player=Player(
                    (obj.x,obj.y),
                    [self.all_sprites,self.vulnerable_sprites],
                    os.path.join('graphics','player'),
                    self.collision_sprites,
                    self.shoot
                )
            if obj.name=='Enemy':
                Enemy(
                    (obj.x,obj.y),
                    [self.all_sprites,self.vulnerable_sprites],
                    os.path.join('graphics','enemies'),
                    self.shoot,self.player,
                    self.collision_sprites
                )
        # platforms
        for obj in map_tmx.get_layer_by_name('Platforms'):
            MovingPlatform((obj.x,obj.y),[self.all_sprites,self.collision_sprites,self.platform_sprites])

    def shoot(self,position,direction,entity):
        Bullet(position,direction,[self.all_sprites,self.bullet_sprites],entity)
        FireAnimation(entity,direction,self.all_sprites)

    def bullet_collisions(self):
        # bullets vs collision sprites
        for bullet in self.bullet_sprites.sprites():
            collision_sprites=pygame.sprite.spritecollide(bullet,self.collision_sprites,False,pygame.sprite.collide_mask)
            if collision_sprites:
                bullet.kill()
        
        # bullets vs vulnerable sprites
        for bullet in self.bullet_sprites.sprites():
            for sprite in self.vulnerable_sprites.sprites():
                if sprite==bullet.entity:
                    continue
                if pygame.sprite.spritecollide(bullet,[sprite],False,pygame.sprite.collide_mask):
                    sprite.damage()
                    bullet.kill()

    def platform_collisions(self):
        for platform in self.platform_sprites.sprites():
            if platform.rect.colliderect(self.player.rect) and self.player.rect.centery<platform.rect.centery:
                if platform.direction.y<0:
                    if self.player.rect.bottom<platform.rect.centery:
                        platform.rect.top=self.player.rect.bottom
                        platform.position.y=platform.rect.centery
                        platform.direction.y=-1
            if platform.rect.colliderect(self.player.rect) and self.player.rect.centery>platform.rect.centery:
                platform.rect.bottom=self.player.rect.top
                platform.position.y=platform.rect.centery
                platform.direction.y=-1

    async def run(self):
        """Main game loop - now async for web compatibility"""
        self.music.play(loops=-1)
        frame_count = 0
        
        while True:
            dt = self.clock.tick(60) / 1000
            frame_count += 1
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Update game logic
            self.platform_collisions()
            self.all_sprites.update(dt)
            self.bullet_collisions()

            # Draw everything
            self.display_surface.fill((249, 131, 103))
            self.all_sprites.custom_draw(self.player)
            self.overlay.display()

            # Update display
            pygame.display.flip()
            
            # Yield control back to browser (crucial for web)
            await asyncio.sleep(0)

async def main():
    """Main entry point for web version"""
    print("🎮 Starting Contra Web Game...")
    game = Game()
    print("✅ Game initialized successfully!")
    await game.run()

if __name__ == '__main__':
    # For web deployment
    asyncio.run(main())