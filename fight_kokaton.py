import random
import sys
import time

import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 3


def check_bound(area: pg.Rect, obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数1 area：画面SurfaceのRect
    引数2 obj：オブジェクト（爆弾，こうかとん）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < area.left or area.right < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < area.top or area.bottom < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    _delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        img = pg.image.load(f"ex03-20230509/fig/{num}.png")
        hanntaiimg=pg.transform.flip(img,True,False)
        self._houkou = {
            (+1, 0): 
            pg.transform.rotozoom(
                hanntaiimg,
                0,
                2.0),
            (+1, +1): 
            pg.transform.rotozoom(
                hanntaiimg,
                -45,
                2.0),
            (0, +1): 
            pg.transform.rotozoom(
                hanntaiimg,
                -90,
                2.0),
            (-1, +1): 
            pg.transform.rotozoom(
                img,
                45,
                2.0),
            (-1, 0): 
            pg.transform.rotozoom(
                img,
                0,
                2.0),
            (-1, -1): 
            pg.transform.rotozoom(
                img,
                -45,
                2.0),
            (0, -1): 
            pg.transform.rotozoom(
                hanntaiimg,
                90,
                2.0),
            (+1, -1): 
            pg.transform.rotozoom(
                hanntaiimg,
                45,
                2.0)
            }
        self._img = self._houkou[(+1, 0)]
        self._rct = self._img.get_rect()
        self._rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self._img = pg.transform.rotozoom(pg.image.load(f"ex03-20230509/fig/{num}.png"), 0, 2.0)
        screen.blit(self._img, self._rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        self.sum_mv =[0, 0]
        for k, mv in __class__._delta.items():
            if key_lst[k]:
                self._rct.move_ip(mv)
                self.sum_mv[0] = mv[0]
                self.sum_mv[1] += mv[1]
        if check_bound(screen.get_rect(), self._rct) != (True, True): # type: ignore
            for k, mv in __class__._delta.items():
                if key_lst[k]:
                    self._rct.move_ip(-mv[0], -mv[1])
        if not (self.sum_mv[0] == 0 and self.sum_mv[1] == 0):
            self._img = self._houkou[tuple(self.sum_mv)] # type: ignore
        screen.blit(self._img, self._rct)

class Bomb:
    """
    爆弾に関するクラス
    """
    _colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 255, 255)]
    _dires = [-1, 0, +1]
    def __init__(self):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        rad = random.randint(10, 40)
        self._img = pg.Surface((2*rad, 2*rad))
        color = random.choice(Bomb._colors)
        pg.draw.circle(self._img, color, (rad, rad), rad)
        self._img.set_colorkey((0, 0, 0))
        self._rct = self._img.get_rect()
        self._rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self._vx, self._vy = random.choice(Bomb._dires), random.choice(Bomb._dires)

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself._vx, self._vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(screen.get_rect(), self._rct) # type: ignore
        if not yoko:
            self._vx *= -1
        if not tate:
            self._vy *= -1
        self._rct.move_ip(self._vx, self._vy)
        screen.blit(self._img, self._rct)


class Beam:
    """
    ビームに関するクラス
    """
    def __init__(self, bird:Bird):
        if bird.sum_mv[0] is +1 and bird.sum_mv[1] is not +1 and bird.sum_mv[1] is not -1:
            self._img = pg.image.load(f"ex03-20230509/fig/beam.png")#画像surface
            self._rct = self._img.get_rect()#画像surfaceに対応したrect
            self._rct.centerx = bird._rct.centerx + 100#rectに座標を設定する
            self._rct.centery = bird._rct.centery
            self._dx,self._dy=3,0
        elif bird.sum_mv[0] is -1 and bird.sum_mv[1] is not +1 and bird.sum_mv[1] is not -1:
            self._img = pg.transform.flip(
                pg.image.load(f"ex03-20230509/fig/beam.png"),
                True,
                False)
            self._rct = self._img.get_rect()#画像surfaceに対応したrect
            self._rct.centerx = bird._rct.centerx - 100#rectに座標を設定する
            self._rct.centery = bird._rct.centery
            self._dx,self._dy=-3,0
        elif bird.sum_mv[1] is +1 and bird.sum_mv[0] is not +1 and bird.sum_mv[0] is not -1:
            self._img = pg.transform.rotozoom(
                pg.image.load(f"ex03-20230509/fig/beam.png"),
                -90,
                1.0)
            self._rct = self._img.get_rect()#画像surfaceに対応したrect
            self._rct.centerx = bird._rct.centerx #rectに座標を設定する
            self._rct.centery = bird._rct.centery + 100
            self._dx,self._dy=0,3
        elif bird.sum_mv[1] is -1 and bird.sum_mv[0] is not +1 and bird.sum_mv[0] is not -1:
            self._img = pg.transform.rotozoom(
                pg.image.load(f"ex03-20230509/fig/beam.png"),
                90,
                1.0)
            self._rct = self._img.get_rect()#画像surfaceに対応したrect
            self._rct.centerx = bird._rct.centerx #rectに座標を設定する
            self._rct.centery = bird._rct.centery - 100
            self._dx,self._dy=0,-3
        else :
            pass
    def update(self,screen:pg.Surface):
        self._rct.move_ip(self._dx,self._dy)
        screen.blit(self._img,self._rct)

        
def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    bg_img = pg.image.load("ex03-20230509/fig/pg_bg.jpg")

    bird = Bird(3, (900, 400))
    bombs = [Bomb() for i in range (NUM_OF_BOMBS)]
    beams = []


    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE :
                beams.append(Beam(bird))
        tmr += 1
        screen.blit(bg_img, [0, 0])
        
        for bomb in bombs:
            bomb.update(screen) # type: ignore
            if bird._rct.colliderect(bomb._rct): # type: ignore
                bird.change_img(8, screen) # type: ignore
                time.sleep(1)# ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                pg.display.update()
                return

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen) # type: ignore
        
        if len(beams) is not 0:
            for j , beam in enumerate(beams):
                if beam:
                    beam.update(screen) # type: ignore
                    if beam._rct.centerx > 1800 or beam._rct.centerx < 0 or beam._rct.centery > 900 or beam._rct.centery < 0:
                        del beams[j]
                    else:
                        for i , bomb in enumerate(bombs):
                            if beam._rct.colliderect(bomb._rct):# type: ignore
                                del beams[j]
                                del bombs[i]
                                bird.change_img(6, screen)# type: ignore
                                time.sleep(0.1)
                                break

        pg.display.update()
        clock.tick(1000)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
