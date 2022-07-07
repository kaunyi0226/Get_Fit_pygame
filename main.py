import pygame
import random #讓石頭隨機落下
import os #載入路徑

#遊戲基本設定
pygame.init() #遊戲初始化
pygame.mixer.init() #音效初始化
FPS= 60 #設定遊戲畫面更新率
WIDTH= 500
HEIGHT= 600
BLACK=(0,0,0)
WHITE=(255,255,255)
RED= (255,0,0) 
ORANGE= (255,130,71)

screen= pygame.display.set_mode((WIDTH,HEIGHT)) #建立遊戲視窗:傳入tuple，設定視窗寬度、高度
clock= pygame.time.Clock() #創造一個物件，操控時間
pygame.display.set_caption("減肥大作戰") #遊戲標題

#載入圖片(記得要先pygame初始化)
background_img= pygame.image.load(os.path.join("教學8pygame","image","background.png")).convert() #os.path:當前資料夾 #再轉換成pygame易讀取的格式(跑比較快)
player_img= pygame.image.load(os.path.join("教學8pygame","image","fat.png")).convert()
bullet_img= pygame.image.load(os.path.join("教學8pygame","image","bullet.png")).convert()

heart_img= pygame.transform.scale(pygame.image.load(os.path.join("教學8pygame","image","heart.png")).convert(),(25,19))
heart_img.set_colorkey(BLACK)

tool_img={}
tool_img['carrot']= pygame.transform.scale(pygame.image.load(os.path.join("教學8pygame","image","carrot.png")).convert(),(30,30))
tool_img['gun']= pygame.image.load(os.path.join("教學8pygame","image","gun.png")).convert()

food_imgs= [] #創造列表放6種不同食物的圖片
for i in range(6):
    food_imgs.append(pygame.image.load(os.path.join("教學8pygame","image",f"food{i}.png")).convert())

player_img.set_colorkey(BLACK)
pygame.display.set_icon(player_img) #設定遊戲icon
#載入爆炸動畫(一系列圖片):lg(食物大爆炸)、sm(飛船小爆炸)
expl_anim= {}
expl_anim['lg']= [] #大爆炸
expl_anim['sm']= [] #小爆炸
expl_anim['player']=[] #角色爆炸
for i in range(9):
    expl_img= pygame.image.load(os.path.join("教學8pygame","image",f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img,(75,75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img,(30,30)))

    player_expl_img= pygame.image.load(os.path.join("教學8pygame","image",f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(player_expl_img)

#載入音效(記得要先pygame.mixer初始化)
shooting_sound= pygame.mixer.Sound(os.path.join("教學8pygame","sound","shoot.wav")) #射擊音效
die_sound= pygame.mixer.Sound(os.path.join("教學8pygame","sound","rumble.ogg")) #角色死亡音效
carrot_sound= pygame.mixer.Sound(os.path.join("教學8pygame","sound","pow0.wav"))
gun_sound= pygame.mixer.Sound(os.path.join("教學8pygame","sound","pow1.wav"))

expl_sounds= [
    pygame.mixer.Sound(os.path.join("教學8pygame","sound","expl0.wav")),
    pygame.mixer.Sound(os.path.join("教學8pygame","sound","expl1.wav"))
] #兩種爆炸音效

#載入背景音樂(無限循環)
pygame.mixer.music.load(os.path.join("教學8pygame","sound","background.ogg"))
pygame.mixer.music.set_volume(0.7) #設定背景音樂音量(係數0~1)

#載入字體(引入微軟正黑)
font_name= os.path.join("教學8pygame","font.ttf")
def draw_text(surf,text,size,x,y): 
    font= pygame.font.Font(font_name,size) #先創造文字物件(傳入兩個參數:字體、大小)
    text_surface= font.render(text, True, BLACK) #渲染出來，參數:內容、是否反鋸齒、顏色

    #定位輸入的文字
    text_rect= text_surface.get_rect()
    text_rect.centerx= x #中心位置會在傳進來的x
    text_rect.top= y
    surf.blit(text_surface,text_rect) #畫出來，參數:畫出什麼、畫在哪裡

#畫出血條
def draw_health(surf,hp,x,y):
    if hp<0:
        hp=0
    BAR_LENGTH= 100
    BAR_HIGH= 10
    fill= (hp/100)*BAR_LENGTH

    #畫出血條矩形
    outline_rect= pygame.Rect(x,y,BAR_LENGTH,BAR_HIGH) #血條外框座標、長寬
    fill_rect= pygame.Rect(x,y,fill,BAR_HIGH) #目前血條
    pygame.draw.rect(surf,BLACK,outline_rect,2) #畫外框(最後記得傳入外框幾像素)
    pygame.draw.rect(surf,ORANGE,fill_rect) #畫裡面填滿的方形

#畫出剩多少命
def draw_lives(surf,lives,img,x,y):
    for i in range(lives):
        img_rect= img.get_rect() #定位
        img_rect.x= x+33*i
        img_rect.y= y
        surf.blit(img, img_rect) #畫出來

#畫初始畫面
def draw_init():
    screen.blit(background_img, (0,0))
    #寫文字
    draw_text(screen,'減肥大作戰',64,WIDTH/2,HEIGHT/4)
    draw_text(screen,'← →操控人物，空白鍵發射子彈',22,WIDTH/2,HEIGHT/2)
    draw_text(screen,'按任意鍵開始遊戲',18,WIDTH/2,HEIGHT*3/4)
    pygame.display.update() #記得寫這行，才會畫出來

    waiting= True #等待玩家按任意鍵開始遊戲
    while waiting:
        clock.tick(FPS) #限制迴圈1秒最多執行60次(參數即FPS)，避免每台電腦執行速度不同，因而體驗不同
        #取得輸入
        for event in pygame.event.get(): #pygame.event.get():回傳所有發生的事件，是一個list(可能同時發生很多個)
            if event.type == pygame.QUIT: #按下X鍵，即退出遊戲
                pygame.quit()
                return True #回傳關閉視窗

            elif event.type== pygame.KEYUP: #按下鍵盤又鬆開
                waiting= False
                return False #回傳沒有關閉視窗

#SPRITES
class PLAYER(pygame.sprite.Sprite): #創造PLAYER類別，去繼承內建的Sprite類別
    def __init__(self): #初始函式裡需要兩個屬性: image(表示圖片 ), rect(定位圖片)
        pygame.sprite.Sprite.__init__(self)
        self.image= pygame.transform.scale(player_img,(50,45))
        self.image.set_colorkey(BLACK) #傳入RGB參數，讓圖片背景變透明 

        self.rect= self.image.get_rect() #記得打這行
        self.radius= 20
        #pygame.draw.circle(self.image,RED,self.rect.center,self.radius) :檢視看看碰撞體的圓形符合期望嗎

        self.rect= self.image.get_rect()
        self.rect.x= WIDTH/2-25
        self.rect.y= HEIGHT-60 #圖片左上角座標為(x,y)，注意:向下為y軸正向
        self.speedx= 8 #設定移動速度

        self.health= 100 #設定初始生命值
        self.lives= 3 #設定有幾條命
        self.hidden= False #初始隱藏狀態(無)---死了才有隱藏狀態
        self.hide_time= 0 

        self.gun= 1 #吃到道具前只能一次射1發
        self.gun_time= 0

    def update(self):
        #控制左右移動
        key_pressed= pygame.key.get_pressed() #回傳一串布林值，判斷鍵盤有沒有被按
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx
        if key_pressed[pygame.K_d]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_a]:
            self.rect.x -= self.speedx
        #避免移動到式窗外
        if self.rect.right > WIDTH: #若物體右邊座標超過寬度，禁止它繼續向右
            self.rect.right= WIDTH
        if self.rect.left<0 :
            self.rect.left= 0

        #讓死亡後隱藏的飛船現形
        if self.hidden and pygame.time.get_ticks() - self.hide_time>1000:
            self.hidden= False
            self.rect.x= WIDTH/2-25
            self.rect.y= HEIGHT-60

        #吃到道具後，過一段時間讓子彈等級下降(變回射1發)
        now= pygame.time.get_ticks()
        if self.gun>1 and now -self.gun_time>3000:
            self.gun-= 1 #等級下降
            self.gun_time= now

    def shoot(self):
        if not(self.hidden): #死亡隱藏時不能發射子彈
            if self.gun== 1: #一次射1發
                bullet= Bullet(self.rect.centerx,self.rect.top)
                all_sprites.add(bullet) #加到sprites群組
                bullets.add(bullet) #加到bullets群組
                shooting_sound.play() #播放射擊音效
            elif self.gun> 1: #吃到道具後一次射2發(並改成從兩側發射)
                bullet1= Bullet(self.rect.left,self.rect.centery)
                bullet2= Bullet(self.rect.right,self.rect.centery)
                all_sprites.add(bullet1) 
                all_sprites.add(bullet2) 
                bullets.add(bullet1)
                bullets.add(bullet2)
                shooting_sound.play()         

    def hide(self):
        self.hidden= True
        self.hide_time= pygame.time.get_ticks()
        self.rect.center= (WIDTH/2,HEIGHT+500) #定位到視窗外，即為隱藏
        #定位回原本位置

    def gunup(self):
        self.gun+=1
        self.gun_time= pygame.time.get_ticks()
                         
class FOOD(pygame.sprite.Sprite): 
    def __init__(self): 
        pygame.sprite.Sprite.__init__(self)
        self.image_ori= pygame.transform.scale(random.choice(food_imgs),(50,40)) #存放無失真的圖片(旋轉時，圖片會慢慢失真)
        self.image_ori.set_colorkey(BLACK)
        self.image= self.image_ori.copy()
        

        self.rect= self.image.get_rect() #記得打這行
        self.radius= self.rect.width/2.5
        #pygame.draw.circle(self.image,RED,self.rect.center,self.radius) :檢視看看碰撞體的圓形符合期望嗎

        self.rect= self.image.get_rect()
        self.rect.x= random.randrange(0,WIDTH-self.rect.width) #不要讓食物生成位置超出邊界，故要減去食物寬度
        self.rect.y= random.randrange(-100,-40)
        self.speedy= random.randrange(2,10) #設定隨機食物掉落垂直速度
        self.speedx= random.randrange(-3,3) #設定隨機食物掉落水平速度

        self.total_degree= 0 #原始旋轉角為0
        self.rot_degree=random.randrange(-3,3) #每次轉的角度

    def rotate(self):#每秒轉60次(FPS)
        self.total_degree += self.rot_degree
        self.total_degree= self.total_degree%360 #取餘數，避免轉超過360
        self.image= pygame.transform.rotate(self.image_ori,self.total_degree) #讓原本的圖片轉動起來，角度參數為5

        #讓石頭轉動時不要怪怪的(抽動)，因為中心一直偏移
        center= self.rect.center
        self.rect= self.image.get_rect()
        self.rect.center= center

    def update(self):
        self.rotate()

        self.rect.y += self.speedy
        self.rect.x += self.speedx
        #若食物掉落到視窗外，重設它的位置，讓食物在遊戲中不停掉落
        if self.rect.y> HEIGHT or self.rect.right<0 or self.rect.left> WIDTH:
            self.rect.x= random.randrange(0,WIDTH-self.rect.width) 
            self.rect.y= random.randrange(-100,-40)
            self.speedy= random.randrange(2,9) 
            self.speedx= random.randrange(-3,3) 

class Bullet(pygame.sprite.Sprite): 
    def __init__(self,x,y): #子彈位置跟角色位置有關，要傳入x,y資訊 
        pygame.sprite.Sprite.__init__(self)
        self.image= bullet_img
        self.image.set_colorkey(BLACK)
         
        self.rect= self.image.get_rect()
        self.rect.centerx= x #中央x為傳進來的x
        self.rect.bottom= y #底部座標為傳進來的y
        self.speedy= -10 #往上射子彈
       

    def update(self):
        self.rect.y += self.speedy
        if self.rect.y< 0:
            self.kill() #若子彈超出視窗，則刪除子彈

class Explosion(pygame.sprite.Sprite): 
    def __init__(self,center,size): #中心點、大小
        pygame.sprite.Sprite.__init__(self)
        self.size= size
        self.image= expl_anim[self.size][0] #第0張
         
        self.rect= self.image.get_rect()
        self.rect.center= center 
        self.frame= 0 #更新到第幾張爆炸圖片

        #避免用原本的update更新太快了(判斷是否已經過50毫秒)
        self.last_update= pygame.time.get_ticks() #紀錄上一次更新的時間
        self.frame_rate= 50 #數字越大，動畫越慢
       

    def update(self):
        now= pygame.time.get_ticks() #現在時間
        if now-self.last_update >self.frame_rate:
            self.last_update= now #把最後一次更新時間改成現在
            self.frame +=1 #換下一張爆炸圖片

            #判斷是否更新到最後一張
            if self.frame == len(expl_anim[self.size]):
                self.kill() #更新完最後一張了
            else:
                self.image= expl_anim[self.size][self.frame]
                center= self.rect.center
                self.rect= self.image.get_rect() #重新定位
                self.rect.center= center

class Tool(pygame.sprite.Sprite): 
    def __init__(self,center): #參數:寶物顯示位置
        pygame.sprite.Sprite.__init__(self)
        self.type= random.choice(['carrot','gun']) #隨機選擇掉落寶物種類
        self.image= tool_img[self.type]
        self.image.set_colorkey(BLACK)
        
        self.rect= self.image.get_rect()
        self.rect.center= center
        self.speedy= 3 #向下掉落寶物
       

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top> HEIGHT:
            self.kill() #若寶物超出視窗，則刪除           

pygame.mixer.music.play(-1) #播放音樂:參數為重覆播放次數(-1即無限播放)

#定義生成新食物的函式(避免重複撰寫)，避免之後運行時，食物數量不斷減少
def new_food():
    f= FOOD()
    all_sprites.add(f)
    food.add(f)

#建立遊戲迴圈
running= True
show_init= True #初始畫面顯示中    

while running:
    if show_init:
        close= draw_init() #讀取"畫初始畫面"函式之回傳值(True or False)
        if close:
            break #跳出遊戲的while迴圈，讓遊戲順利關閉，不會跑之後的程式

        show_init= False

        #分別創造食物&子彈的群組，來判定碰撞
        food= pygame.sprite.Group()
        bullets= pygame.sprite.Group()
        #創造寶物群組
        tools=  pygame.sprite.Group()
        #把SPRITES物件放入群組裡
        all_sprites= pygame.sprite.Group() #建立sprite群組，可放許多物件
        player= PLAYER()
        all_sprites.add(player) #建立player物件，放入群組裡
        
        for i in range(10): #一次掉落10個食物
            f= FOOD()
            all_sprites.add(f) #加到sprite群組
            food.add(f)

        score=0 #初始分數
    
    clock.tick(FPS) #限制迴圈1秒最多執行60次(參數即FPS)，避免每台電腦執行速度不同，因而體驗不同
    #取得輸入
    for event in pygame.event.get(): #pygame.event.get():回傳所有發生的事件，是一個list(可能同時發生很多個)
        if event.type == pygame.QUIT: #按下X鍵，即退出遊戲
            running= False

        elif event.type== pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot() #呼叫shoot
    #更新遊戲
    all_sprites.update() #執行群組裡每一個物件的update函式
    
    #(子彈撞食物)
    hits= pygame.sprite.groupcollide(food,bullets,True,True) #食物跟子彈群組碰撞後，食物是否要刪除(True)，子彈是否要刪除(True)。會回傳一個列表
    for hit in hits: #射完食物後，食物會消失，所以每射掉一個食物，要再生成一個食物出來
        score += hit.radius #根據射到的食物大小加分數

        expl= Explosion(hit.rect.center,'lg')
        all_sprites.add(expl) #增加大爆炸動畫
        
        #有機率掉落寶物
        if random.random()<0.05: #隨機從0~1選一數
            tool= Tool(hit.rect.center) #把撞擊中央傳入寶物函式中
            all_sprites.add(tool) #畫出寶物
            tools.add(tool) #加到寶物群組，方便與角色互動

        new_food() #重新生成食物

        random.choice(expl_sounds).play() #隨機播放其中一種爆炸音效

    #(寶物撞角色)
    hits= pygame.sprite.spritecollide(player,tools,True)
    for hit in hits:
        if hit.type== 'carrot':
            player.health+= 10 #回10滴血
            if player.health >100:
                player.health= 100
            carrot_sound.play()
        elif hit.type== 'gun':
            player.gunup()
            gun_sound.play()

    #(食物撞角色)
    hits= pygame.sprite.spritecollide(player,food,True,pygame.sprite.collide_circle) #角色跟食物碰撞，食物要刪除(True)，會回傳碰到角色的食物；#預設是矩形碰撞，改成較精準的圓形碰撞(但要記得賦予物件radius)
    for hit in hits:
        player.health -= 25
        new_food() #重新生成食物

        expl= Explosion(hit.rect.center,'sm')
        all_sprites.add(expl) #增加小爆炸動畫

        if player.health <=0:
            #死亡動畫
            death_expl= Explosion(player.rect.center,'player')
            all_sprites.add(death_expl)
            #死亡音效
            die_sound.play()

            player.lives -=1 #減一條命
            player.health= 100 #並且生命值回滿
            player.hide()

    if player.lives==0 and not(death_expl.alive()): #最後一次死亡爆炸動畫播完，遊戲才結束
        show_init= True
    
    #畫面顯示
    screen.fill((0,0,0)) #設定遊戲背景顏色，參數為(R,G,B)，數值0~255
    screen.blit(background_img,(0,0))
    all_sprites.draw(screen) #畫出群組內所有物件
    draw_text(screen, str(score), 18, WIDTH/2, 10) #畫在screen上、分數轉字串、size、x座標、y座標
    draw_health(screen,player.health,5,15)
    draw_lives(screen,player.lives, heart_img, WIDTH-100, 15)
    pygame.display.update()

pygame.quit()
