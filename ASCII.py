import os
import sys
import time
import random
import shutil
import msvcrt


def get_key():
    if msvcrt.kbhit():
        ch = msvcrt.getch()
        try:
            return ch.decode('ascii')
        except UnicodeDecodeError:
            return ''
    return None

COLORS = [31, 32, 33, 34, 35, 36]
BRIGHTNESS = [2, 22, 1]
RESET = '\033[0m'

DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1)]


class Firefly:
    def __init__(self, W, H):
        self.x = random.randrange(W)
        self.y = random.randrange(H)
        self.dx, self.dy = random.choice(DIRS)
        self.stop_timer = 0
        self.bright_timer = random.randint(5, 25)
        self.brightness = random.choice(BRIGHTNESS)
        self.color = random.choice(COLORS)

    def update(self, W, H):
        if self.stop_timer > 0:
            self.stop_timer -= 1
        else:
            if random.random() < 0.05:
                self.stop_timer = random.randint(10, 40)
            else:
                self.x += self.dx
                self.y += self.dy
                if self.x < 0:
                    self.x, self.dx = 0, -self.dx
                elif self.x >= W:
                    self.x, self.dx = W - 1, -self.dx
                if self.y < 0:
                    self.y, self.dy = 0, -self.dy
                elif self.y >= H:
                    self.y, self.dy = H - 1, -self.dy
        self.bright_timer -= 1
        if self.bright_timer <= 0:
            self.bright_timer = random.randint(20, 30)
            self.brightness = random.choice(BRIGHTNESS)


def render(fireflies, W, H, paused, speed):
    grid = [[' '] * W for _ in range(H)]
    for f in fireflies:
        if 0 <= f.x < W and 0 <= f.y < H:
            grid[f.y][f.x] = f

    buf = ['\033[H']                      
    for y in range(H):
        row = []
        for x in range(W):
            c = grid[y][x]
            if c == ' ':
                row.append(' ')
            else:
                if paused:
                    style = f"\033[2;{c.color}m"
                else:
                    style = f"\033[{c.brightness};{c.color}m"
                row.append(style + '*' + RESET)
        row.append('\033[K\r\n')
        buf.append(''.join(row))

    status = (f"\033[1mFireflies: {len(fireflies)}  "
              f"Speed: {speed:.2f}x  "
              f"{'PAUSED' if paused else 'running'}   "
                "добавление \"f\", скорость \"+/-\", пауза \"пробел\", выход \"q\"  \033[0m\033[K")
    buf.append(status)

    sys.stdout.write(''.join(buf))
    sys.stdout.flush()


def main():
    size = shutil.get_terminal_size(fallback=(80, 24))
    W = max(size.columns - 1, 10)
    H = max(size.lines - 2, 5)  
    os.system('')

    fireflies = [Firefly(W, H) for _ in range(5)]
    paused = False
    speed = 1.0
    base_delay = 0.08
    running = True

    sys.stdout.write('\033[2J\033[?25l\033[H')
    sys.stdout.flush()

    try:
        while running:
            key = get_key()
            if key:
                k = key.lower() if key.isalpha() else key
                if k == ' ':
                    paused = not paused
                elif k in ('+', '='):
                    speed = min(speed * 1.3, 10.0)
                elif k in ('-', '_'):
                    speed = max(speed / 1.3, 0.1)
                elif k == 'f':
                    fireflies.append(Firefly(W, H))
                elif k == 'q':
                    running = False

            if not paused:
                for f in fireflies:
                    f.update(W, H)

            render(fireflies, W, H, paused, speed)

            time.sleep(base_delay / speed)

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(RESET + '\033[?25h')
        sys.stdout.flush()


if __name__ == '__main__':
    main()