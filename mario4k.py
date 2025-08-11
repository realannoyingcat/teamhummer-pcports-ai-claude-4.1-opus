# koopa_engine_nes_hummer.py
# NES ROMHACK ENGINE - Team Hummer SMW Bootleg Style
# 256x240 NES Resolution, 8-bit limitations, Koopa Everything!
# files=off, 100% procedural, byte-accurate NES feel

import pygame
import math
import random
import struct
import time

# --- NES Hardware Constants ---
NES_WIDTH = 256
NES_HEIGHT = 240
SCALE = 2  # Scale for modern displays
FPS = 60  # NTSC
TILE_SIZE = 8  # NES uses 8x8 tiles
SPRITE_SIZE = 16  # 8x16 sprite mode

# NES APU init (bootleg quality)
pygame.mixer.pre_init(11025, -8, 1, 128)  # Low quality for authentic bootleg sound
pygame.init()

SCREEN = pygame.display.set_mode((NES_WIDTH * SCALE, NES_HEIGHT * SCALE))
DISPLAY = pygame.Surface((NES_WIDTH, NES_HEIGHT)).convert()
pygame.display.set_caption("KOOPA ENGINE ◆ TEAM HUMMER STYLE")
CLOCK = pygame.time.Clock()

# ---------------------------------------------
# NES Palette (PPU 2C02)
# ---------------------------------------------
NES_PALETTE = [
    (124,124,124), (0,0,252), (0,0,188), (68,40,188),
    (148,0,132), (168,0,32), (168,16,0), (136,20,0),
    (80,48,0), (0,120,0), (0,104,0), (0,88,0),
    (0,64,88), (0,0,0), (0,0,0), (0,0,0),
    (188,188,188), (0,120,248), (0,88,248), (104,68,252),
    (216,0,204), (228,0,88), (248,56,0), (228,92,16),
    (172,124,0), (0,184,0), (0,168,0), (0,168,68),
    (0,136,136), (0,0,0), (0,0,0), (0,0,0),
    (248,248,248), (60,188,252), (104,136,252), (152,120,248),
    (248,120,248), (248,88,152), (248,120,88), (252,160,68),
    (248,184,0), (184,248,24), (88,216,84), (88,248,152),
    (0,232,216), (120,120,120), (0,0,0), (0,0,0),
    (252,252,252), (164,228,252), (184,184,248), (216,184,248),
    (248,184,248), (248,164,192), (240,208,176), (252,224,168),
    (248,216,120), (216,248,120), (184,248,184), (184,248,216),
    (0,252,252), (248,216,248), (0,0,0), (0,0,0)
]

# Bootleg palette selections (Team Hummer style)
WORLD_PALETTES = [
    # World 1 - Green Hills
    {'bg': 0x22, 'fg': [0x1A, 0x29, 0x19, 0x09], 'sprite': [0x17, 0x27, 0x37]},
    # World 2 - Underground
    {'bg': 0x0F, 'fg': [0x03, 0x13, 0x23, 0x33], 'sprite': [0x15, 0x25, 0x35]},
    # World 3 - Water
    {'bg': 0x21, 'fg': [0x11, 0x21, 0x31, 0x0C], 'sprite': [0x16, 0x26, 0x36]},
    # World 4 - Castle
    {'bg': 0x07, 'fg': [0x07, 0x17, 0x27, 0x06], 'sprite': [0x08, 0x18, 0x28]},
    # World 5 - Sky
    {'bg': 0x2C, 'fg': [0x20, 0x30, 0x31, 0x3C], 'sprite': [0x14, 0x24, 0x34]},
]

# ---------------------------------------------
# Pattern Tables (CHR ROM simulation)
# ---------------------------------------------
class PatternTable:
    """Simulate NES CHR ROM with procedural tiles"""
    
    @staticmethod
    def make_tile(pattern_type, param=0):
        """Generate 8x8 tile pattern (2 bitplanes like NES)"""
        tile = [[0 for _ in range(8)] for _ in range(8)]
        
        if pattern_type == "solid":
            # SMW-style ground block
            patterns = [
                [3,1,1,1,1,1,1,3],
                [1,2,2,2,2,2,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,2,2,2,2,2,1],
                [3,1,1,1,1,1,1,3],
            ]
            tile = patterns
                    
        elif pattern_type == "brick":
            # Classic brick pattern
            patterns = [
                [3,3,3,3,3,3,3,0],
                [3,2,2,2,2,2,3,0],
                [3,2,2,2,2,2,3,0],
                [0,0,0,0,0,0,0,0],
                [0,3,3,3,3,3,3,3],
                [0,3,2,2,2,2,2,3],
                [0,3,2,2,2,2,2,3],
                [0,0,0,0,0,0,0,0],
            ]
            tile = patterns
                        
        elif pattern_type == "koopa_shell":
            # Better shell pattern
            shell = [
                [0,0,1,2,2,1,0,0],
                [0,1,2,3,3,2,1,0],
                [1,2,3,2,2,3,2,1],
                [2,3,2,3,3,2,3,2],
                [2,3,3,2,2,3,3,2],
                [1,2,3,3,3,3,2,1],
                [0,1,2,2,2,2,1,0],
                [0,0,1,1,1,1,0,0],
            ]
            tile = shell
            
        elif pattern_type == "question":
            # Better ? block
            q = [
                [3,3,3,3,3,3,3,3],
                [3,2,2,2,2,2,2,3],
                [3,2,0,2,2,0,2,3],
                [3,2,2,0,0,2,2,3],
                [3,2,2,2,2,2,2,3],
                [3,2,2,0,0,2,2,3],
                [3,2,2,2,2,2,2,3],
                [3,3,3,3,3,3,3,3],
            ]
            tile = q
            
        elif pattern_type == "pipe":
            # Better pipe tile
            patterns = [
                [2,3,1,1,1,1,3,2],
                [2,3,1,1,1,1,3,2],
                [2,3,1,1,1,1,3,2],
                [2,3,1,1,1,1,3,2],
                [2,3,1,1,1,1,3,2],
                [2,3,1,1,1,1,3,2],
                [2,3,1,1,1,1,3,2],
                [2,3,1,1,1,1,3,2],
            ]
            tile = patterns
                        
        return tile
    
    @staticmethod
    def render_tile(tile_data, palette, scale=1):
        """Render tile with NES palette"""
        size = 8 * scale
        surf = pygame.Surface((size, size)).convert()
        for y in range(8):
            for x in range(8):
                color_idx = tile_data[y][x]
                # Ensure palette index is valid
                pal_idx = palette[min(color_idx, len(palette)-1)]
                # Ensure NES palette index is valid
                pal_idx = min(max(0, pal_idx), len(NES_PALETTE)-1)
                color = NES_PALETTE[pal_idx]
                rect = (x * scale, y * scale, scale, scale)
                surf.fill(color, rect)
        return surf

# ---------------------------------------------
# NES APU (Bootleg Sound)
# ---------------------------------------------
class BootlegAPU:
    """Team Hummer style bootleg NES sound"""
    
    def __init__(self):
        self.sample_rate = 11025
        self.enabled = pygame.mixer.get_init() is not None
        
    def make_square_wave(self, freq, duration, duty=0.5):
        """NES square wave channel"""
        if not self.enabled:
            return None
        samples = int(self.sample_rate * duration)
        wave = []
        period = self.sample_rate / freq
        for i in range(samples):
            phase = (i % period) / period
            wave.append(127 if phase < duty else -128)
        
        # Pack as 8-bit signed
        data = struct.pack('b' * len(wave), *wave)
        return pygame.mixer.Sound(buffer=data)
    
    def make_triangle_wave(self, freq, duration):
        """NES triangle wave channel"""
        if not self.enabled:
            return None
        samples = int(self.sample_rate * duration)
        wave = []
        period = self.sample_rate / freq
        for i in range(samples):
            phase = (i % period) / period
            val = abs(4 * phase - 2) - 1
            wave.append(int(val * 64))
        
        data = struct.pack('b' * len(wave), *wave)
        return pygame.mixer.Sound(buffer=data)
    
    def make_noise(self, duration, freq_div=16):
        """NES noise channel (LFSR)"""
        if not self.enabled:
            return None
        samples = int(self.sample_rate * duration)
        wave = []
        lfsr = 1
        counter = 0
        for i in range(samples):
            counter += 1
            if counter >= freq_div:
                counter = 0
                bit0 = lfsr & 1
                bit1 = (lfsr >> 1) & 1
                lfsr >>= 1
                if bit0 ^ bit1:
                    lfsr |= 0x4000
            wave.append(64 if lfsr & 1 else -64)
        
        data = struct.pack('b' * len(wave), *wave)
        return pygame.mixer.Sound(buffer=data)

    def play_bootleg_music(self, world):
        """Generate Team Hummer style music"""
        if not self.enabled:
            return
            
        # Bootleg music patterns (simplified)
        notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00]
        
        # Play a simple melody
        for note in notes:
            sound = self.make_square_wave(note, 0.2)
            if sound:
                sound.play()
                pygame.time.wait(200)

APU = BootlegAPU()

# ---------------------------------------------
# Sprite Rendering (OAM simulation)
# ---------------------------------------------
class SpriteOAM:
    """Object Attribute Memory for sprites"""
    
    def __init__(self):
        self.sprites = []  # Max 64 sprites on NES
        
    def add_sprite(self, x, y, tile, palette, flip_h=False, flip_v=False):
        if len(self.sprites) < 64:
            self.sprites.append({
                'x': x, 'y': y, 'tile': tile,
                'palette': palette, 'flip_h': flip_h, 'flip_v': flip_v
            })
    
    def clear(self):
        self.sprites = []
    
    def render(self, surface):
        # NES can only show 8 sprites per scanline (we'll simplify)
        for sprite in self.sprites[:64]:
            tile_surf = sprite['tile']
            if sprite['flip_h']:
                tile_surf = pygame.transform.flip(tile_surf, True, False)
            if sprite['flip_v']:
                tile_surf = pygame.transform.flip(tile_surf, False, True)
            surface.blit(tile_surf, (sprite['x'], sprite['y']))

OAM = SpriteOAM()

# ---------------------------------------------
# Koopa Entity (NES Style)
# ---------------------------------------------
class KoopaNES:
    def __init__(self, x, y, color_type=0):
        self.x = x
        self.y = y
        self.vx = -0.5  # Slow like NES
        self.vy = 0
        self.width = 16
        self.height = 16
        self.color_type = color_type
        self.frame = 0
        self.alive = True
        self.in_shell = False
        
        # Generate sprite
        self.generate_sprite()
    
    def generate_sprite(self):
        """Generate procedural Koopa sprite"""
        # Use palette based on type
        pal = WORLD_PALETTES[self.color_type % len(WORLD_PALETTES)]
        colors = [NES_PALETTE[pal['sprite'][i] if i < len(pal['sprite']) else 0x0F] for i in range(4)]
        
        # Build detailed koopa sprite
        self.sprite = pygame.Surface((16, 16), pygame.SRCALPHA)
        self.sprite.fill((0,0,0,0))
        
        # Koopa sprite pattern (16x16)
        koopa_pattern = [
            #0123456789ABCDEF
            "                ",  # 0
            "     ####       ",  # 1 - head
            "    ######      ",  # 2
            "    #@@##@#     ",  # 3 - eyes
            "    ######      ",  # 4
            "   ########     ",  # 5 - shell top
            "  ##########    ",  # 6
            " ############   ",  # 7
            " #####  #####   ",  # 8
            " ####    ####   ",  # 9
            " ############   ",  # A
            "  ##########    ",  # B
            "   ########     ",  # C
            "    ######      ",  # D
            "    ##  ##      ",  # E - feet
            "   ###  ###     ",  # F
        ]
        
        # Color mapping
        for y in range(16):
            for x in range(16):
                if x < len(koopa_pattern[y]):
                    char = koopa_pattern[y][x]
                    if char == '#':  # Shell
                        color_idx = (x + y) % 2
                        self.sprite.set_at((x, y), colors[1 + color_idx])
                    elif char == '@':  # Eyes
                        self.sprite.set_at((x, y), (0, 0, 0))
                    elif char == ' ':  # Transparent
                        pass
    
    def update(self, level):
        # Simple NES-style physics
        self.x += self.vx
        self.vy += 0.2  # Gravity
        if self.vy > 4:
            self.vy = 4
        self.y += self.vy
        
        # Collision with ground (simplified)
        ground_y = 200
        if self.y + self.height > ground_y:
            self.y = ground_y - self.height
            self.vy = 0
        
        # Turn at edges
        if self.x < 0 or self.x > NES_WIDTH - self.width:
            self.vx = -self.vx
        
        self.frame += 1
    
    def draw(self, surface, cam_x):
        if self.alive:
            x = int(self.x - cam_x)
            if -16 <= x <= NES_WIDTH:
                # Animate with simple flip
                flip = (self.frame // 8) % 2 == 0
                sprite = pygame.transform.flip(self.sprite, flip, False) if flip else self.sprite
                surface.blit(sprite, (x, int(self.y)))

# ---------------------------------------------
# Player (Koopa Mario)
# ---------------------------------------------
class KoopaPlayer:
    def __init__(self):
        self.x = 32
        self.y = 100
        self.vx = 0
        self.vy = 0
        self.width = 16
        self.height = 16
        self.on_ground = False
        self.facing_right = True
        self.run_held = False
        self.jump_held = False
        self.jump_buffer = 0
        self.state = "small"  # small, big, fire
        self.invincible = 0
        self.lives = 3
        
        self.generate_sprite()
    
    def generate_sprite(self):
        """Generate player Koopa sprite"""
        # Classic Mario colors in NES palette
        colors = {
            'red': NES_PALETTE[0x16],     # Mario's red
            'blue': NES_PALETTE[0x11],    # Mario's blue overalls
            'skin': NES_PALETTE[0x27],    # Skin tone
            'brown': NES_PALETTE[0x07],   # Brown for shoes
            'white': NES_PALETTE[0x30],   # White
            'green': NES_PALETTE[0x1A],   # Koopa green
        }
        
        self.sprite = pygame.Surface((16, 16), pygame.SRCALPHA)
        self.sprite.fill((0,0,0,0))
        
        # Koopa Mario sprite pattern
        mario_pattern = [
            #0123456789ABCDEF
            "                ",  # 0
            "     ####       ",  # 1 - koopa head
            "    ######      ",  # 2
            "    #SSSS#      ",  # 3 - face
            "   #S@SS@S#     ",  # 4 - eyes
            "   #SSSSSS#     ",  # 5
            "    ######      ",  # 6 - shell top (mario colored)
            "   RRRRRRRR     ",  # 7 - red shirt
            "  RRRRRRRRRR    ",  # 8
            "  BBBRRBRBBB    ",  # 9 - blue overalls
            "  BBBBBBBBB     ",  # A
            "  BBBBBBBBB     ",  # B
            "   BBBBBBB      ",  # C
            "    BB  BB      ",  # D
            "   SSS  SSS     ",  # E - feet/shoes
            "  BBBB  BBBB    ",  # F - shoes
        ]
        
        # Color mapping
        for y in range(16):
            for x in range(16):
                if x < len(mario_pattern[y]):
                    char = mario_pattern[y][x]
                    if char == '#':  # Koopa shell (green)
                        self.sprite.set_at((x, y), colors['green'])
                    elif char == 'S':  # Skin
                        self.sprite.set_at((x, y), colors['skin'])
                    elif char == '@':  # Eyes (black)
                        self.sprite.set_at((x, y), (0, 0, 0))
                    elif char == 'R':  # Red shirt
                        self.sprite.set_at((x, y), colors['red'])
                    elif char == 'B':  # Blue overalls/shoes
                        if y >= 15:  # Shoes row
                            self.sprite.set_at((x, y), colors['brown'])
                        else:
                            self.sprite.set_at((x, y), colors['blue'])
                    elif char == ' ':  # Transparent
                        pass
    
    def update(self, keys, level):
        # NES-style controls
        # Movement
        if keys[pygame.K_LEFT]:
            self.vx = -2 if self.run_held else -1
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.vx = 2 if self.run_held else 1
            self.facing_right = True
        else:
            self.vx *= 0.8  # Friction
        
        # Run button (B)
        self.run_held = keys[pygame.K_x]
        
        # Jump (A button)
        if keys[pygame.K_z]:
            if not self.jump_held and self.on_ground:
                self.vy = -6 if self.run_held else -5
                self.jump_buffer = 0
            self.jump_held = True
        else:
            self.jump_held = False
            if self.vy < -2:
                self.vy = -2  # Variable jump height
        
        # Apply physics
        self.x += self.vx
        self.vy += 0.25  # Gravity
        if self.vy > 5:
            self.vy = 5
        self.y += self.vy
        
        # Ground collision (simplified)
        ground_y = 200
        if self.y + self.height > ground_y:
            self.y = ground_y - self.height
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        # Screen bounds
        if self.x < 0:
            self.x = 0
        if self.x > level.width * TILE_SIZE - self.width:
            self.x = level.width * TILE_SIZE - self.width
        
        # Update invincibility
        if self.invincible > 0:
            self.invincible -= 1
    
    def draw(self, surface, cam_x):
        # Flicker when invincible
        if self.invincible > 0 and self.invincible % 4 < 2:
            return
        
        x = int(self.x - cam_x)
        if -16 <= x <= NES_WIDTH:
            sprite = pygame.transform.flip(self.sprite, not self.facing_right, False)
            surface.blit(sprite, (x, int(self.y)))

# ---------------------------------------------
# Level (Procedural NES Style)
# ---------------------------------------------
class NESLevel:
    def __init__(self, world, level_num):
        self.world = world
        self.level_num = level_num
        self.width = 256  # In tiles
        self.height = 30  # In tiles (NES nametable height)
        self.tilemap = []
        self.enemies = []
        
        # Generate tilemap
        self.generate()
        
        # Spawn enemies
        self.spawn_enemies()
    
    def generate(self):
        """Generate Team Hummer style level"""
        random.seed(self.world * 100 + self.level_num)
        
        # Initialize empty
        self.tilemap = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Ground
        ground_height = 25
        for x in range(self.width):
            # Vary height
            h = ground_height + int(math.sin(x * 0.1) * 2)
            for y in range(h, self.height):
                self.tilemap[y][x] = 1  # Solid tile
            
            # Random platforms
            if x % 20 == 10:
                platform_y = h - random.randint(5, 10)
                if platform_y > 10:
                    for dx in range(5):
                        if x + dx < self.width:
                            self.tilemap[platform_y][x + dx] = 1
            
            # Pipes (Team Hummer loves pipes)
            if x % 35 == 20:
                pipe_height = random.randint(3, 6)
                for dy in range(pipe_height):
                    y = h - 1 - dy
                    if y >= 0:
                        self.tilemap[y][x] = 2  # Pipe tile
                        if x + 1 < self.width:
                            self.tilemap[y][x + 1] = 2
            
            # Question blocks
            if x % 15 == 7:
                block_y = h - random.randint(4, 8)
                if block_y > 10:
                    self.tilemap[block_y][x] = 3  # Question block
    
    def spawn_enemies(self):
        """Spawn Koopa enemies"""
        for x in range(20, self.width * TILE_SIZE, 200):
            y = 180  # Simple placement
            self.enemies.append(KoopaNES(x, y, self.world))
    
    def get_tile(self, x, y):
        """Get tile at position"""
        tx = x // TILE_SIZE
        ty = y // TILE_SIZE
        if 0 <= tx < self.width and 0 <= ty < self.height:
            return self.tilemap[ty][tx]
        return 0
    
    def draw(self, surface, cam_x):
        """Draw visible tiles"""
        # Calculate visible range
        start_x = max(0, cam_x // TILE_SIZE - 1)
        end_x = min(self.width, (cam_x + NES_WIDTH) // TILE_SIZE + 2)
        
        pal = WORLD_PALETTES[self.world % len(WORLD_PALETTES)]
        
        # Draw background elements first (parallax clouds/hills)
        for i in range(5):
            cloud_x = (i * 80 - cam_x // 4) % (NES_WIDTH + 100) - 50
            cloud_y = 40 + (i % 3) * 20
            # Simple cloud shape with circles
            pygame.draw.circle(surface, NES_PALETTE[pal['bg'] + 1], 
                             (cloud_x, cloud_y), 12)
            pygame.draw.circle(surface, NES_PALETTE[pal['bg'] + 1], 
                             (cloud_x + 10, cloud_y), 10)
            pygame.draw.circle(surface, NES_PALETTE[pal['bg'] + 1], 
                             (cloud_x - 10, cloud_y), 10)
        
        # Draw tiles
        for y in range(self.height):
            for x in range(start_x, end_x):
                tile = self.tilemap[y][x]
                if tile > 0:
                    screen_x = x * TILE_SIZE - cam_x
                    screen_y = y * TILE_SIZE
                    
                    if tile == 1:  # Solid block
                        tile_data = PatternTable.make_tile("brick")
                        tile_surf = PatternTable.render_tile(tile_data, pal['fg'])
                        surface.blit(tile_surf, (screen_x, screen_y))
                    elif tile == 2:  # Pipe
                        tile_data = PatternTable.make_tile("pipe")
                        # Pipes get special green palette
                        pipe_pal = [0x0F, 0x1A, 0x2A, 0x3A]
                        tile_surf = PatternTable.render_tile(tile_data, pipe_pal)
                        surface.blit(tile_surf, (screen_x, screen_y))
                    elif tile == 3:  # Question block
                        # Animate question blocks
                        frame = (pygame.time.get_ticks() // 500) % 2
                        if frame == 0:
                            tile_data = PatternTable.make_tile("question")
                        else:
                            tile_data = PatternTable.make_tile("solid")
                        # Question blocks are yellow
                        q_pal = [0x0F, 0x27, 0x37, 0x30]
                        tile_surf = PatternTable.render_tile(tile_data, q_pal)
                        surface.blit(tile_surf, (screen_x, screen_y))

# ---------------------------------------------
# Game State Machine
# ---------------------------------------------
class KoopaEngine:
    def __init__(self):
        self.state = "TITLE"
        self.world = 0
        self.level_num = 0
        self.level = None
        self.player = None
        self.camera_x = 0
        self.frame_counter = 0
        self.score = 0
        self.time = 400
        
        # Title screen animation
        self.title_y = 0
        self.title_flash = 0
    
    def start_game(self):
        """Initialize game"""
        self.world = 0
        self.level_num = 0
        self.score = 0
        self.start_level()
    
    def start_level(self):
        """Start a level"""
        self.level = NESLevel(self.world, self.level_num)
        self.player = KoopaPlayer()
        self.camera_x = 0
        self.time = 400
        
        # Play music
        APU.play_bootleg_music(self.world)
    
    def update(self):
        """Update game logic"""
        self.frame_counter += 1
        keys = pygame.key.get_pressed()
        
        if self.state == "TITLE":
            # Animate title
            self.title_y = int(math.sin(self.frame_counter * 0.05) * 10)
            self.title_flash = (self.frame_counter // 15) % 2
            
            # Start game
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                self.state = "GAME"
                self.start_game()
        
        elif self.state == "GAME":
            # Update player
            self.player.update(keys, self.level)
            
            # Update enemies
            for enemy in self.level.enemies:
                enemy.update(self.level)
                
                # Collision with player
                if enemy.alive:
                    px = self.player.x
                    py = self.player.y
                    ex = enemy.x
                    ey = enemy.y
                    
                    if (abs(px - ex) < 14 and abs(py - ey) < 14):
                        if self.player.vy > 1 and py < ey:
                            # Stomp enemy
                            enemy.alive = False
                            self.player.vy = -3
                            self.score += 100
                        elif self.player.invincible == 0:
                            # Hurt player
                            self.player.invincible = 120
                            self.player.lives -= 1
                            if self.player.lives <= 0:
                                self.state = "GAMEOVER"
            
            # Update camera (bootleg scrolling)
            target_cam = self.player.x - NES_WIDTH // 2
            self.camera_x += (target_cam - self.camera_x) * 0.1
            self.camera_x = max(0, min(self.camera_x, 
                                       self.level.width * TILE_SIZE - NES_WIDTH))
            
            # Timer
            if self.frame_counter % 60 == 0:
                self.time -= 1
                if self.time <= 0:
                    self.state = "GAMEOVER"
            
            # Check goal
            if self.player.x > (self.level.width - 10) * TILE_SIZE:
                self.level_num += 1
                if self.level_num > 3:
                    self.level_num = 0
                    self.world += 1
                    if self.world > 4:
                        self.state = "WIN"
                    else:
                        self.start_level()
                else:
                    self.start_level()
        
        elif self.state == "GAMEOVER":
            if keys[pygame.K_RETURN]:
                self.state = "TITLE"
        
        elif self.state == "WIN":
            if keys[pygame.K_RETURN]:
                self.state = "TITLE"
    
    def draw(self):
        """Render everything"""
        # Clear with background color
        pal = WORLD_PALETTES[self.world % len(WORLD_PALETTES)] if self.level else WORLD_PALETTES[0]
        bg_color = NES_PALETTE[pal['bg']]
        DISPLAY.fill(bg_color)
        
        if self.state == "TITLE":
            # Title screen (Team Hummer style)
            self.draw_title()
        
        elif self.state == "GAME":
            # Draw level
            self.level.draw(DISPLAY, int(self.camera_x))
            
            # Draw enemies
            for enemy in self.level.enemies:
                enemy.draw(DISPLAY, int(self.camera_x))
            
            # Draw player
            self.player.draw(DISPLAY, int(self.camera_x))
            
            # Draw HUD
            self.draw_hud()
        
        elif self.state == "GAMEOVER":
            self.draw_text("GAME OVER", NES_WIDTH // 2 - 32, NES_HEIGHT // 2 - 4)
            self.draw_text("PRESS START", NES_WIDTH // 2 - 40, NES_HEIGHT // 2 + 12)
        
        elif self.state == "WIN":
            self.draw_text("KOOPA CHAMPION!", NES_WIDTH // 2 - 56, NES_HEIGHT // 2 - 12)
            self.draw_text("THANK YOU KOOPA!", NES_WIDTH // 2 - 60, NES_HEIGHT // 2 + 4)
            self.draw_text("PRESS START", NES_WIDTH // 2 - 40, NES_HEIGHT // 2 + 20)
        
        # Scale up for display
        pygame.transform.scale(DISPLAY, (NES_WIDTH * SCALE, NES_HEIGHT * SCALE), SCREEN)
        pygame.display.flip()
    
    def draw_title(self):
        """Draw title screen"""
        # Gradient background (bootleg style)
        for y in range(NES_HEIGHT):
            grad_color = NES_PALETTE[0x0C if y < 80 else 0x01 if y < 160 else 0x00]
            pygame.draw.line(DISPLAY, grad_color, (0, y), (NES_WIDTH, y))
        
        # Background pattern grid
        for y in range(0, NES_HEIGHT, 32):
            for x in range(0, NES_WIDTH, 32):
                if (x // 32 + y // 32) % 2:
                    tile = PatternTable.make_tile("koopa_shell")
                    surf = PatternTable.render_tile(tile, [0x11, 0x21, 0x31, 0x30])
                    DISPLAY.blit(surf, (x + 8, y + 8))
        
        # Main Title with shadow
        title = "KOOPA ENGINE"
        # Shadow
        self.draw_text(title, NES_WIDTH // 2 - 44 + 2, 40 + self.title_y + 2, 
                      color=NES_PALETTE[0x0F])
        # Main text
        self.draw_text(title, NES_WIDTH // 2 - 44, 40 + self.title_y, 
                      color=NES_PALETTE[0x20 if self.title_flash else 0x30])
        
        # Subtitle with shadow
        self.draw_text("TEAM HUMMER", NES_WIDTH // 2 - 44 + 1, 65 + 1, NES_PALETTE[0x0F])
        self.draw_text("TEAM HUMMER", NES_WIDTH // 2 - 44, 65, NES_PALETTE[0x16])
        
        self.draw_text("BOOTLEG STYLE", NES_WIDTH // 2 - 52 + 1, 80 + 1, NES_PALETTE[0x0F])
        self.draw_text("BOOTLEG STYLE", NES_WIDTH // 2 - 52, 80, NES_PALETTE[0x1A])
        
        # Box around instructions
        pygame.draw.rect(DISPLAY, NES_PALETTE[0x30], (NES_WIDTH // 2 - 60, 130, 120, 40), 2)
        
        # Instructions
        if self.title_flash:
            self.draw_text("PRESS START", NES_WIDTH // 2 - 44, 140)
        self.draw_text("Z=JUMP X=RUN", NES_WIDTH // 2 - 48, 155)
        
        # Credits
        self.draw_text("(C)2024 BOOTLEG", NES_WIDTH // 2 - 60, 195, 
                      color=NES_PALETTE[0x16])
        self.draw_text("KOOPA CORP", NES_WIDTH // 2 - 40, 205, 
                      color=NES_PALETTE[0x1A])
        
        # Animated koopas (multiple)
        for i in range(3):
            koopa_x = 40 + i * 80 + int(math.sin(self.frame_counter * 0.05 + i) * 20)
            koopa_y = 100 + int(math.cos(self.frame_counter * 0.04 + i) * 5)
            temp_koopa = KoopaNES(koopa_x, koopa_y, i)
            temp_koopa.draw(DISPLAY, 0)
        
        # Version info
        self.draw_text("NES 256X240", 4, NES_HEIGHT - 12, NES_PALETTE[0x12])
        self.draw_text("60FPS", NES_WIDTH - 40, NES_HEIGHT - 12, NES_PALETTE[0x12])
    
    def draw_hud(self):
        """Draw HUD (NES style)"""
        # Top bar with gradient effect
        for y in range(24):
            color = NES_PALETTE[0x0F if y < 2 or y > 21 else 0x00]
            pygame.draw.line(DISPLAY, color, (0, y), (NES_WIDTH, y))
        
        # HUD background box
        pygame.draw.rect(DISPLAY, NES_PALETTE[0x0F], (2, 2, NES_WIDTH - 4, 20))
        
        # Score with icon
        self.draw_text("$", 8, 7, NES_PALETTE[0x37])
        self.draw_text(f"{self.score:06d}", 16, 7, NES_PALETTE[0x30])
        
        # World indicator
        self.draw_text("WORLD", NES_WIDTH // 2 - 36, 7, NES_PALETTE[0x36])
        self.draw_text(f"{self.world+1}-{self.level_num+1}", NES_WIDTH // 2 + 4, 7, NES_PALETTE[0x30])
        
        # Time with clock icon
        self.draw_text("TIME", NES_WIDTH - 72, 7, NES_PALETTE[0x27])
        time_color = NES_PALETTE[0x16] if self.time < 100 else NES_PALETTE[0x30]
        self.draw_text(f"{self.time:03d}", NES_WIDTH - 40, 7, time_color)
        
        # Lives (bottom of HUD)
        self.draw_text("KOOPA", 8, 14, NES_PALETTE[0x1A])
        self.draw_text("X", 48, 14, NES_PALETTE[0x30])
        self.draw_text(f"{self.player.lives:02d}", 56, 14, NES_PALETTE[0x30])
    
    def draw_text(self, text, x, y, color=None):
        """Draw NES-style text"""
        if color is None:
            color = NES_PALETTE[0x30]  # White
        
        # NES-style 8x8 bitmap font patterns
        font_data = {
            'A': [0x18,0x3C,0x66,0x7E,0x66,0x66,0x66,0x00],
            'B': [0x7C,0x66,0x66,0x7C,0x66,0x66,0x7C,0x00],
            'C': [0x3C,0x66,0x60,0x60,0x60,0x66,0x3C,0x00],
            'D': [0x78,0x6C,0x66,0x66,0x66,0x6C,0x78,0x00],
            'E': [0x7E,0x60,0x60,0x78,0x60,0x60,0x7E,0x00],
            'F': [0x7E,0x60,0x60,0x78,0x60,0x60,0x60,0x00],
            'G': [0x3C,0x66,0x60,0x6E,0x66,0x66,0x3C,0x00],
            'H': [0x66,0x66,0x66,0x7E,0x66,0x66,0x66,0x00],
            'I': [0x3C,0x18,0x18,0x18,0x18,0x18,0x3C,0x00],
            'J': [0x1E,0x0C,0x0C,0x0C,0x0C,0x6C,0x38,0x00],
            'K': [0x66,0x6C,0x78,0x70,0x78,0x6C,0x66,0x00],
            'L': [0x60,0x60,0x60,0x60,0x60,0x60,0x7E,0x00],
            'M': [0x63,0x77,0x7F,0x6B,0x63,0x63,0x63,0x00],
            'N': [0x66,0x76,0x7E,0x7E,0x6E,0x66,0x66,0x00],
            'O': [0x3C,0x66,0x66,0x66,0x66,0x66,0x3C,0x00],
            'P': [0x7C,0x66,0x66,0x7C,0x60,0x60,0x60,0x00],
            'Q': [0x3C,0x66,0x66,0x66,0x66,0x3C,0x0E,0x00],
            'R': [0x7C,0x66,0x66,0x7C,0x78,0x6C,0x66,0x00],
            'S': [0x3C,0x66,0x60,0x3C,0x06,0x66,0x3C,0x00],
            'T': [0x7E,0x18,0x18,0x18,0x18,0x18,0x18,0x00],
            'U': [0x66,0x66,0x66,0x66,0x66,0x66,0x3C,0x00],
            'V': [0x66,0x66,0x66,0x66,0x66,0x3C,0x18,0x00],
            'W': [0x63,0x63,0x63,0x6B,0x7F,0x77,0x63,0x00],
            'X': [0x66,0x66,0x3C,0x18,0x3C,0x66,0x66,0x00],
            'Y': [0x66,0x66,0x66,0x3C,0x18,0x18,0x18,0x00],
            'Z': [0x7E,0x06,0x0C,0x18,0x30,0x60,0x7E,0x00],
            '0': [0x3C,0x66,0x6E,0x76,0x66,0x66,0x3C,0x00],
            '1': [0x18,0x18,0x38,0x18,0x18,0x18,0x7E,0x00],
            '2': [0x3C,0x66,0x06,0x0C,0x30,0x60,0x7E,0x00],
            '3': [0x3C,0x66,0x06,0x1C,0x06,0x66,0x3C,0x00],
            '4': [0x06,0x0E,0x1E,0x66,0x7F,0x06,0x06,0x00],
            '5': [0x7E,0x60,0x7C,0x06,0x06,0x66,0x3C,0x00],
            '6': [0x3C,0x66,0x60,0x7C,0x66,0x66,0x3C,0x00],
            '7': [0x7E,0x66,0x0C,0x18,0x18,0x18,0x18,0x00],
            '8': [0x3C,0x66,0x66,0x3C,0x66,0x66,0x3C,0x00],
            '9': [0x3C,0x66,0x66,0x3E,0x06,0x66,0x3C,0x00],
            ' ': [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
            ':': [0x00,0x18,0x18,0x00,0x00,0x18,0x18,0x00],
            '-': [0x00,0x00,0x00,0x7E,0x00,0x00,0x00,0x00],
            '!': [0x18,0x18,0x18,0x18,0x00,0x00,0x18,0x00],
            '(': [0x0E,0x18,0x30,0x30,0x30,0x18,0x0E,0x00],
            ')': [0x70,0x18,0x0C,0x0C,0x0C,0x18,0x70,0x00],
            '=': [0x00,0x00,0x7E,0x00,0x7E,0x00,0x00,0x00],
            '.': [0x00,0x00,0x00,0x00,0x00,0x18,0x18,0x00],
        }
        
        char_width = 8
        for i, char in enumerate(text.upper()):
            char_x = x + i * char_width
            if char in font_data:
                pattern = font_data[char]
                for row in range(8):
                    for col in range(8):
                        if pattern[row] & (1 << (7 - col)):
                            DISPLAY.set_at((char_x + col, y + row), color)

# ---------------------------------------------
# Main Game Loop
# ---------------------------------------------
def main():
    engine = KoopaEngine()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update
        engine.update()
        
        # Draw
        engine.draw()
        
        # Frame rate
        CLOCK.tick(FPS)
    
    pygame.quit()
if __name__ == "__main__":
    main()
