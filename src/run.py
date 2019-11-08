import pygame as pg
import traceback
import datetime


if __name__ == '__main__':
    try:
        import game
        
        g = game.Game()
        g.run()
    except Exception:
        e = traceback.format_exc()
        print(e)
        with open('../errors.txt', 'a') as f:
            f.write(datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')+ '\n')
            f.write(e + '\n')
