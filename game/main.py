import pygame
import time
from pygame.locals import (KEYDOWN,
                           KEYUP,
                           K_LEFT,
                           K_RIGHT,
                           QUIT, 
                           K_ESCAPE, 
                           K_UP, K_DOWN, K_RCTRL, K_s, K_k, K_m, K_p, K_LCTRL, K_LEFTBRACKET, K_RIGHTBRACKET
                           
                           )
from fundo import Fundo
from elementos import ElementoSprite
import random
from sys import exit



class Jogo:
    def __init__(self, size=(800, 660), fullscreen=False):
        self.elementos = {}
        self.partida_iniciada = False
        self.jogador_perdeu = False
        self.nivel = 0
        self.pause = False
        pygame.init()
        flags = pygame.DOUBLEBUF
        if fullscreen:
            flags |= pygame.FULLSCREEN
        self.tela = pygame.display.set_mode(size, flags=flags, depth=16)
        self.fundo = Fundo()
        self.jogador = None
        self.interval = 0
        self.fonte = pygame.font.SysFont("monospace", 32)
        pygame.mixer.music.load('sons/musica.wav')
        self.gameover = pygame.mixer.Sound('sons/game-over.wav')
        pygame.mixer.music.play(-1)
        self.tiro = pygame.mixer.Sound('sons/tiro.wav')
        pygame.mixer.music.play(-1)
        
        self.music = True
        self.anti_loop  = False

        self.screen_size = self.tela.get_size()
        pygame.mouse.set_visible(0)
        pygame.display.set_caption('Corona Shooter')
        self.run = True
        
    def liga_desliga_musica(self):
        
        if self.music:
            pygame.mixer.music.pause()
            self.music = False
        else:
            pygame.mixer.music.unpause()
            self.music = True

    def ajusta_volume(self, m):
        volume = pygame.mixer.music.get_volume()
        volume *= m
        
        if volume > 1:
            volume = 1
        if volume < 0.1:
            volume = 0.1
        pygame.mixer.music.set_volume(volume)

    def painel_jogador(self):
        
        vida = self.jogador.get_lives()
        hp = pygame.image.load('imagens/coracao.png')
        hp = pygame.transform.scale(hp, (30, 30))
        
        for i in range(1, vida+1):
            
            self.tela.blit(hp, (i*30, 10))
           
        
        
        self.nivel = int(self.jogador.get_pontos()/500)
        
        
        
        score = self.fonte.render(f'Score: {self.jogador.pontos}', 1, (255, 255, 0), (0, 0, 0))
        nivel = self.fonte.render(f'Nivel: {self.nivel}', 1, (255, 255, 0), (0, 0, 0))
        
        self.tela.blit(score, (self.screen_size[0] - 450, 30))
        self.tela.blit(nivel, (self.screen_size[0] - 200, 30))
        
        
    def msg_fim_de_jogo(self):
        if self.jogador_perdeu == True:
            if self.anti_loop  == False:
                pygame.mixer.Sound.play(self.gameover)
                pygame.mixer.music.pause()
                self.anti_loop = True
            msg1 = "FIM DE JOGO"
            msg2 = "Pressione 'S' para jogar uma nova partida"
            
            texto1 = self.fonte.render(msg1, True, (255,225,0))
            texto2 = self.fonte.render(msg2, True, (255,255,255))
            self.tela.blit(texto1, (300,270))
            self.tela.blit(texto2, (10,330))
    def menu_inicial(self):
        if self.partida_iniciada == False and self.jogador_perdeu == False:
            msg = "Pressione 'K' para iniciar a partida"
            texto = self.fonte.render(msg, True, (255,255,0))
            self.tela.blit(texto, (35,200))
    def msg_pause(self):
        if self.pause == True:
            msg = "JOGO PAUSADO"
            texto1 = self.fonte.render(msg, True, (255,225,0))
            self.tela.blit(texto1,(300, 200))
    def manutenção(self):
        pontos = self.jogador.get_pontos()
        r = random.randint(0, 100)
        x = random.randint(1, self.screen_size[0])
        virii = self.elementos["virii"]
        coracao = self.elementos["coracoes"]
    
        if self.jogador.get_lives() == 1:
            hp = Vida([0,0])
           
            size2 = hp.get_size()
            
            hp.set_pos([min(max(x, size2[0] / 2), self.screen_size[0] - size2[0] / 2), size2[1] / 2])
            
            colisores = pygame.sprite.spritecollide(hp, coracao, False)
            
            if len(self.elementos["coracoes"]) < 1:
                self.elementos["coracoes"].add(hp)
            
            
        if r > (10 * len(virii)):
            enemy = Virus([0, 0])
            
            #virus ficam mais resistentes
            enemy.set_lives(pontos/500+1)
            
            ac = 0.4+self.jogador.get_pontos()/1000
            if self.nivel >= 0:
                enemy.acceleration = [ac,ac]
                
            
            size = enemy.get_size()
            
            enemy.set_pos([min(max(x, size[0] / 2), self.screen_size[0] - size[0] / 2), size[1] / 2])
            
            colisores = pygame.sprite.spritecollide(enemy, virii, False)
            if colisores:
                return
            self.elementos["virii"].add(enemy)
            
            #movimento aleatótio dos vírus
            for enemy in virii:
                k = random.randint(1,100)
                if 1<=k<50:
                    enemy.accel_left()
                    
                if 40<=k<70:
                    enemy.accel_right()
   
            
    def muda_nivel(self):
        
        if self.nivel % 2  == 0 and self.nivel > 0:
            self.fundo = Fundo("space1.png")
        if self.nivel % 2 > 0 and self.nivel > 0:
            self.fundo = Fundo("space.png")
       

    def atualiza_elementos(self, dt):
        self.fundo.update(dt)
        for v in self.elementos.values():
            v.update(dt)

    def desenha_elementos(self):
        self.fundo.draw(self.tela)
        for v in self.elementos.values():
            v.draw(self.tela)

    def verifica_impactos(self, elemento, list, action):
        """
        Verifica ocorrência de colisões.
        :param elemento: Instância de RenderPlain ou seja um grupo de sprites
        :param list: lista ou grupo de sprites
        :param action: função a ser chamada no evento de colisão
        :return: lista de sprites envolvidos na colisão
        """
        if isinstance(elemento, pygame.sprite.RenderPlain):
            hitted = pygame.sprite.groupcollide(elemento, list, 1, 0)
            for v in hitted.values():
                for o in v:
                    action(o)
            return hitted

        elif isinstance(elemento, pygame.sprite.Sprite):
            if pygame.sprite.spritecollide(elemento, list, 1):
                action()
            return elemento.morto

    def ação_elemento(self):
        """
        Executa as ações dos elementos do jogo.
        :return:
        """
        self.verifica_impactos(self.jogador, self.elementos["tiros_inimigo"],
                               self.jogador.alvejado)
        if self.jogador.morto:
            # self.run = False
            self.jogador_perdeu = True
            self.partida_iniciada = False
            self.jogador.kill()
            
           
            
            return

        # Verifica se o personagem trombou em algum inimigo
        self.verifica_impactos(self.jogador, self.elementos["virii"],
                               self.jogador.colisão)
        vida = self.jogador.get_lives()
        #verifica se o jogador encontrou alguma vida
        self.verifica_impactos(self.jogador, self.elementos["coracoes"],
                               self.jogador.colisão_hp)
        
        if self.jogador.morto:
            # self.run = False
            self.jogador_perdeu = True
            self.partida_iniciada = False
            self.jogador.kill()
            
            return
        # Verifica se o personagem atingiu algum alvo.
        hitted = self.verifica_impactos(self.elementos["tiros"],
                                        self.elementos["virii"],
                                        Virus.alvejado)

        # Aumenta a pontos baseado no número de acertos:
        self.jogador.set_pontos(self.jogador.get_pontos() + len(hitted))

    def trata_eventos(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.run = False
            pygame.quit()
            exit()

        if event.type in (KEYDOWN,):
            key = event.key
            if key == K_ESCAPE:
                self.run = False
                pygame.quit()
                exit()
                
            elif key in (K_LCTRL, K_RCTRL) and self.partida_iniciada:
                self.interval = 0
                self.jogador.atira(self.elementos["tiros"])
                pygame.mixer.Sound.play(self.tiro)
            elif key == K_UP and self.partida_iniciada:
                self.jogador.accel_top()
            elif key == K_DOWN and self.partida_iniciada:
                self.jogador.accel_bottom()
            elif key == K_RIGHT and self.partida_iniciada:
                self.jogador.accel_right()
            elif key == K_LEFT and self.partida_iniciada:
                self.jogador.accel_left()
            elif key == K_p and self.partida_iniciada:
                self.pause = not self.pause
           
            elif key == K_s:
                J = Jogo(fullscreen=False)
                J.partida_iniciada = True
                J.loop()
            elif key == K_k:
                self.partida_iniciada = True
            elif key == K_m:
                self.liga_desliga_musica()
            elif key == K_LEFTBRACKET:
                self.ajusta_volume(0.9)
            elif key == K_RIGHTBRACKET:
                self.ajusta_volume(1.1)
                
                
               
        keys = pygame.key.get_pressed()
        if self.interval > 10:
            self.interval = 0
            if keys[K_RCTRL] or keys[K_LCTRL]:
                self.jogador.atira(self.elementos["tiros"])
                pygame.mixer.Sound.play(self.tiro)

    def loop(self):
        clock = pygame.time.Clock()
        dt = 16
        self.jogador = Jogador([400, 400], 5)
        self.elementos['virii'] = pygame.sprite.RenderPlain(Virus([120, 50]))
        self.elementos['huns'] = pygame.sprite.RenderPlain(Virus([120, 50]))
        self.elementos['jogador'] = pygame.sprite.RenderPlain(self.jogador)
        self.elementos['tiros'] = pygame.sprite.RenderPlain()
        self.elementos['coracoes'] = pygame.sprite.RenderPlain()
        self.elementos['tiros_inimigo'] = pygame.sprite.RenderPlain()
        
        while self.run:
            clock.tick(1000 / dt)
           
            self.trata_eventos()
            self.ação_elemento()
            
            if self.partida_iniciada:
                self.manutenção()
            
           
                
            # Atualiza Elementos
            if self.pause == False:
                self.atualiza_elementos(dt)

            # Desenhe no back buffer
            self.desenha_elementos()
            self.painel_jogador()
            self.menu_inicial()
            self.msg_fim_de_jogo()
            self.msg_pause()
            self.muda_nivel()

            pygame.display.flip()


class Nave(ElementoSprite):
    def __init__(self, position, lives=0, speed=[0, 0], image=None, new_size=[83, 248]):
        
        self.acceleration = [3, 3]
        
        if not image:
            image = "seringa.png"
        super().__init__(image, position, speed, new_size)
        self.set_lives(lives)
        self.coronakill = pygame.mixer.Sound('sons/coronakill.wav')

    def get_lives(self):
        return self.lives

    def set_lives(self, lives):
        self.lives = lives

    def colisão(self):
        if self.get_lives() <= 0:
            self.kill()
        else:
            self.set_lives(self.get_lives() - 1)
            
    def colisão_hp(self):
            self.set_lives(self.get_lives() + 1)

    def atira(self, lista_de_tiros, image=None):
        s = list(self.get_speed())
        s[1] *= 2
        Tiro(self.get_pos(), s, image, lista_de_tiros)

    def alvejado(self):
        if self.get_lives() <= 0:
            self.kill()
            pygame.mixer.Sound.play(self.coronakill)
        else:
            self.set_lives(self.get_lives() - 1)
            

    @property
    def morto(self):
        return self.get_lives() == 0
        

    def accel_top(self):
        speed = self.get_speed()
        self.set_speed((speed[0], speed[1] - self.acceleration[1]))

    def accel_bottom(self):
        speed = self.get_speed()
        self.set_speed((speed[0], speed[1] + self.acceleration[1]))

    def accel_left(self):
        speed = self.get_speed()
        self.set_speed((speed[0] - self.acceleration[0], speed[1]))

    def accel_right(self):
        speed = self.get_speed()
        self.set_speed((speed[0] + self.acceleration[0], speed[1]))


class Virus(Nave):
    def __init__(self, position, lives=1, speed=None, image=None, size=(60, 60)):
        if not image:
            image = "virus.png"
        super().__init__(position, lives, speed, image, size)
       
        
    
        

class Jogador(Nave):
    """
    A classe Player é uma classe derivada da classe GameObject.
       No entanto, o personagem não morre quando passa da borda, este só
    interrompe o seu movimento (vide update()).
       E possui experiência, que o fará mudar de nivel e melhorar seu tiro.
       A função get_pos() só foi redefinida para que os tiros não saissem da
    parte da frente da nave do personagem, por esta estar virada ao contrário
    das outras.
    """

    def __init__(self, position, lives=10, image=None, new_size=[30, 120]):
        if not image:
            image = "seringa.png"
        super().__init__(position, lives, [0, 0], image, new_size)
        self.pontos = 0
        

    def update(self, dt):
        move_speed = (self.speed[0] * dt / 16,
                      self.speed[1] * dt / 16)
        self.rect = self.rect.move(move_speed)
        

        if (self.rect.right > self.area.right):
            self.rect.right = self.area.right

        elif (self.rect.left < 0):
            self.rect.left = 0

        if (self.rect.bottom > self.area.bottom):
            self.rect.bottom = self.area.bottom

        elif (self.rect.top < 0):
            self.rect.top = 0

    def get_pos(self):
        return (self.rect.center[0], self.rect.top)

    def get_pontos(self):
        return self.pontos

    def set_pontos(self, pontos):
        self.pontos = pontos

    def atira(self, lista_de_tiros, image=None):
        l = 1
        if self.pontos > 10:
            l = 3
        if self.pontos > 50:
            l = 5

        p = self.get_pos()
        speeds = self.get_fire_speed(l)
        for s in speeds:
            Tiro(p, s, image, lista_de_tiros)

    def get_fire_speed(self, shots):
        speeds = []

        if shots <= 0:
            return speeds

        if shots == 1:
            speeds += [(0, -5)]

        if shots > 1 and shots <= 3:
            speeds += [(0, -5)]
            speeds += [(-2, -3)]
            speeds += [(2, -3)]

        if shots > 3 and shots <= 5:
            speeds += [(0, -5)]
            speeds += [(-2, -3)]
            speeds += [(2, -3)]
            speeds += [(-4, -2)]
            speeds += [(4, -2)]

        return speeds


class Tiro(ElementoSprite):
    def __init__(self, position, speed=None, image=None, list=None, new_size=[30,30]):
        if not image:
            image = "tiro.png"
        super().__init__(image, position, speed, new_size)
        if list is not None:
            self.add(list)
            
class Vida(Nave):
    def __init__(self, position, lives=1, speed=None, image=None, size=(60, 60)):
         if not image:
            image = "coracao.png"
         super().__init__(position, lives, speed, image, size)
        
        
if __name__ == '__main__':
    J = Jogo(fullscreen=False)
    J.loop()
