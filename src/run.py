import pygame as pg
import traceback
import datetime

import cProfile
import pstats
from pstats import SortKey



def main():
    try:
        import game
        g = game.Game()
        g.run()

        fps_report(g)

    except Exception:
        e = traceback.format_exc()
        print(e)
        with open('../errors.txt', 'a') as f:
            f.write(datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')+ '\n')
            f.write(e + '\n')
        pg.quit()
        

def print_profile():
    # print only the most time consuming calls
    p = pstats.Stats('../data/profile')
    p.sort_stats(SortKey.TIME).print_stats(50)

def fps_report(game):
    import matplotlib.pyplot as plt

    print(f'Average FPS: {round(game.avg_fps, 1)} '
          f'for {len(game.fps_counter)} frames')

    plt.figure()
    plt.plot(game.fps_counter)
    plt.ylabel('Frame')
    plt.ylabel('FPS')
    plt.show()


if __name__ == '__main__':
    cProfile.run('main()', '../data/profile')
    print('\n')
    #print_profile()