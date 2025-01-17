import pygame
import sys
import os

# Proje kök dizinini bul
PROJE_DIZINI = os.path.dirname(os.path.abspath(__file__))

# Global değişkenler
iksir_alindi = False  # İksir durumu için global değişken ekle

# Sabitler
KARE_BOYUTU = 40
SUTUNLAR = 10
SATIRLAR = 8

# Initialize pygame
pygame.init()

# Windows pencere boyutunu ayarla (örnek boyutlar)
EKRAN_GENISLIK = 1200
EKRAN_YUKSEKLIK = 800

# Tile boyutunu pencere boyutuna göre ayarla
KARE_BOYUTU = min(EKRAN_GENISLIK // SUTUNLAR, EKRAN_YUKSEKLIK // SATIRLAR)

# Normal pencere modunda başlat
screen = pygame.display.set_mode((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
pygame.display.set_caption("Sokoban")

# Ekran boyutlarını güncelle
EKRAN_GENISLIK = screen.get_width()
EKRAN_YUKSEKLIK = screen.get_height()

# Tile boyutunu tekrar ayarla
KARE_BOYUTU = min(EKRAN_GENISLIK // SUTUNLAR, EKRAN_YUKSEKLIK // SATIRLAR)

# Colors
BEYAZ = (255, 255, 255)
SIYAH = (0, 0, 0)
GRI = (200, 200, 200)
MAVI = (0, 0, 255)
YESIL = (0, 255, 0)
KIRMIZI = (255, 0, 0)

# Symbols
DUVAR = "#"
ZEMIN = "."
OYUNCU = "O"
KUTU = "K"
HEDEF = "H"
iksir = "i"
# Map layout
def harita_oku(dosya_yolu):
    try:
        with open(dosya_yolu, 'r') as dosya:
            return [satir.strip() for satir in dosya.readlines()]
    except FileNotFoundError:
        print(f"HATA: {dosya_yolu} dosyası bulunamadı!")
        return None

# Varsayılan harita yerine dosyadan oku
harita_yolu = os.path.join(PROJE_DIZINI, "seviye", "seviye1.txt")
oyun_haritasi = harita_oku(harita_yolu)
if oyun_haritasi is None:
    print("Harita dosyası bulunamadı!")
    pygame.quit()
    sys.exit()

# Harita boyutlarını güncelle
SUTUNLAR = len(oyun_haritasi[0])
SATIRLAR = len(oyun_haritasi)

# Kare boyutunu yeni harita boyutlarına göre güncelle
KARE_BOYUTU = min(EKRAN_GENISLIK // SUTUNLAR, EKRAN_YUKSEKLIK // SATIRLAR)

# Load assets
font = pygame.font.SysFont(None, 36)
try:
    # Farklı yönler için oyuncu görselleri
    oyuncu_gorsel = {
        "SAG": pygame.image.load(os.path.join(PROJE_DIZINI, "oyunGorsel", "oyuncu_right.png")),
        "SOL": pygame.image.load(os.path.join(PROJE_DIZINI, "oyunGorsel", "oyuncu_left.png")),
        "VARSAYILAN": pygame.image.load(os.path.join(PROJE_DIZINI, "oyunGorsel", "oyuncu.png")),
    
        "KAZANDI": pygame.image.load(os.path.join(PROJE_DIZINI, "oyunGorsel", "oyuncu_kazandin.png")),
        "KUTU_CEKER": pygame.image.load(os.path.join(PROJE_DIZINI, "oyunGorsel", "oyuncu_kutucekerken.png"))

    }
    # Duvar, kutu ve iksir görselleri
    duvar_gorsel = pygame.image.load(os.path.join(PROJE_DIZINI, "oyunGorsel", "duvar.png"))
    kutu_gorsel = pygame.image.load(os.path.join(PROJE_DIZINI, "oyunGorsel", "kutu.png"))
    iksir_gorsel = pygame.image.load(os.path.join(PROJE_DIZINI, "oyunGorsel", "iksir.png"))
    
    # Görselleri ölçeklendir
    duvar_gorsel = pygame.transform.scale(duvar_gorsel, (KARE_BOYUTU, KARE_BOYUTU))
    kutu_gorsel = pygame.transform.scale(kutu_gorsel, (KARE_BOYUTU, KARE_BOYUTU))
    iksir_gorsel = pygame.transform.scale(iksir_gorsel, (KARE_BOYUTU, KARE_BOYUTU))
    
    # Tüm oyuncu görsellerini ölçeklendir
    for yon in oyuncu_gorsel:
        oyuncu_gorsel[yon] = pygame.transform.scale(oyuncu_gorsel[yon], (KARE_BOYUTU, KARE_BOYUTU))
    mevcut_yon = "VARSAYILAN"
except pygame.error as e:
    print(f"HATA: Görseller yüklenemedi! {e}")
    oyuncu_gorsel = None
    duvar_gorsel = None
    kutu_gorsel = None
    iksir_gorsel = None
    mevcut_yon = None

def kare_ciz(x, y, renk, offset_x=0, offset_y=0):
    pygame.draw.rect(screen, renk, 
                    (offset_x + x * KARE_BOYUTU, 
                     offset_y + y * KARE_BOYUTU, 
                     KARE_BOYUTU, KARE_BOYUTU))


def harita_ciz(oyun_haritasi):
    # Haritayı ekranın ortasına yerleştirmek için offset hesapla
    offset_x = (EKRAN_GENISLIK - (SUTUNLAR * KARE_BOYUTU)) // 2
    offset_y = ((EKRAN_YUKSEKLIK - MENU_YUKSEKLIK) - (SATIRLAR * KARE_BOYUTU)) // 2 + MENU_YUKSEKLIK
    
    for y, satir in enumerate(oyun_haritasi):
        for x, kare in enumerate(satir):
            # Hedef alanları için yeşil, diğer kareler için beyaz zemin
            if kare == HEDEF:
                kare_ciz(x, y, YESIL, offset_x, offset_y)
            else:
                kare_ciz(x, y, BEYAZ, offset_x, offset_y)
            if kare == DUVAR:
                if duvar_gorsel:
                    screen.blit(duvar_gorsel, 
                              (offset_x + x * KARE_BOYUTU, 
                               offset_y + y * KARE_BOYUTU))
                else:
                    kare_ciz(x, y, GRI, offset_x, offset_y)
            elif kare == OYUNCU:
                if oyuncu_gorsel and mevcut_yon in oyuncu_gorsel:
                    try:
                        # İksir alındıysa kutu çeker görselini kullan
                        kullanilacak_gorsel = "KUTU_CEKER" if iksir_alindi else mevcut_yon
                        if kullanilacak_gorsel in oyuncu_gorsel:
                            screen.blit(oyuncu_gorsel[kullanilacak_gorsel], 
                                      (offset_x + x * KARE_BOYUTU, 
                                       offset_y + y * KARE_BOYUTU))
                        else:
                            # Eğer belirtilen görsel yoksa varsayılan görsel kullan
                            screen.blit(oyuncu_gorsel["VARSAYILAN"], 
                                      (offset_x + x * KARE_BOYUTU, 
                                       offset_y + y * KARE_BOYUTU))
                    except Exception as e:
                        print(f"Oyuncu görseli çizilirken hata: {e}")
                        kare_ciz(x, y, MAVI, offset_x, offset_y)
                else:
                    kare_ciz(x, y, MAVI, offset_x, offset_y)
            elif kare == KUTU:
                if kutu_gorsel:
                    screen.blit(kutu_gorsel, 
                              (offset_x + x * KARE_BOYUTU, 
                               offset_y + y * KARE_BOYUTU))
                else:
                    kare_ciz(x, y, KIRMIZI, offset_x, offset_y)
            elif kare == iksir:
                if iksir_gorsel:
                    screen.blit(iksir_gorsel, 
                              (offset_x + x * KARE_BOYUTU, 
                               offset_y + y * KARE_BOYUTU))
                else:
                    kare_ciz(x, y, YESIL, offset_x, offset_y)


def kazanma_kontrol(oyun_haritasi):
    global mevcut_yon
    # Hedef noktalarını ve kutuları kontrol et
    for y, satir in enumerate(oyun_haritasi):
        for x, kare in enumerate(satir):
            if kare == HEDEF:  # Eğer bir hedef noktası varsa
                return False  # Henüz kazanılmadı
            if kare == KUTU:  # Kutu hedefte değilse
                # Kutunun etrafındaki hedefleri kontrol et
                if oyun_haritasi[y-1][x] == HEDEF or \
                   oyun_haritasi[y+1][x] == HEDEF or \
                   oyun_haritasi[y][x-1] == HEDEF or \
                   oyun_haritasi[y][x+1] == HEDEF:
                    return False  # Kutu henüz hedefe ulaşmadı
    
    # Tüm kutular hedeflere ulaştıysa oyuncu görselini değiştir
    mevcut_yon = "KAZANDI"
    return True  # Tüm kutular hedeflere ulaştı

def oyuncu_hareket(oyun_haritasi, yon):
    global iksir_alindi
    dx, dy = 0, 0
    if yon == "YUKARI":
        dy = -1
    elif yon == "ASAGI":
        dy = 1
    elif yon == "SOL":
        dx = -1
    elif yon == "SAG":
        dx = 1

    # Oyuncu pozisyonunu bul
    for y, satir in enumerate(oyun_haritasi):
        for x, kare in enumerate(satir):
            if kare == OYUNCU:
                oyuncu_x, oyuncu_y = x, y
                break

    # Hedef pozisyon
    hedef_x, hedef_y = oyuncu_x + dx, oyuncu_y + dy

    # İksir kontrolü
    if oyun_haritasi[hedef_y][hedef_x] == iksir:
        iksir_alindi = True
        oyun_haritasi[oyuncu_y] = oyun_haritasi[oyuncu_y][:oyuncu_x] + ZEMIN + oyun_haritasi[oyuncu_y][oyuncu_x + 1:]
        oyun_haritasi[hedef_y] = oyun_haritasi[hedef_y][:hedef_x] + OYUNCU + oyun_haritasi[hedef_y][hedef_x + 1:]
        return oyun_haritasi

    # Kutu çekme özelliği
    if iksir_alindi and yon in ["SOL", "SAG"]:  # Sadece yatay çekme
        ters_x, ters_y = oyuncu_x - dx, oyuncu_y  # Oyuncunun arkasındaki pozisyon
        if 0 <= ters_x < len(oyun_haritasi[0]):  # Sınırları kontrol et
            if oyun_haritasi[ters_y][ters_x] == KUTU:  # Arkada kutu varsa
                if oyun_haritasi[hedef_y][hedef_x] in [ZEMIN, HEDEF]:  # Önü boşsa
                    # Kutuyu çek
                    oyun_haritasi[ters_y] = oyun_haritasi[ters_y][:ters_x] + ZEMIN + oyun_haritasi[ters_y][ters_x + 1:]
                    oyun_haritasi[oyuncu_y] = oyun_haritasi[oyuncu_y][:oyuncu_x] + KUTU + oyun_haritasi[oyuncu_y][oyuncu_x + 1:]
                    oyun_haritasi[hedef_y] = oyun_haritasi[hedef_y][:hedef_x] + OYUNCU + oyun_haritasi[hedef_y][hedef_x + 1:]
                    return oyun_haritasi

    # Sınırları ve hedef üzerine gelmeyi kontrol et
    if oyun_haritasi[hedef_y][hedef_x] == DUVAR or oyun_haritasi[hedef_y][hedef_x] == HEDEF:
        return oyun_haritasi

    # Oyuncuyu hareket ettir
    if oyun_haritasi[hedef_y][hedef_x] == ZEMIN:
        oyun_haritasi[oyuncu_y] = oyun_haritasi[oyuncu_y][:oyuncu_x] + ZEMIN + oyun_haritasi[oyuncu_y][oyuncu_x + 1:]
        oyun_haritasi[hedef_y] = oyun_haritasi[hedef_y][:hedef_x] + OYUNCU + oyun_haritasi[hedef_y][hedef_x + 1:]
    elif oyun_haritasi[hedef_y][hedef_x] == KUTU:
        kutu_hedef_x, kutu_hedef_y = hedef_x + dx, hedef_y + dy
        if oyun_haritasi[kutu_hedef_y][kutu_hedef_x] in (ZEMIN, HEDEF):
            oyun_haritasi[oyuncu_y] = oyun_haritasi[oyuncu_y][:oyuncu_x] + ZEMIN + oyun_haritasi[oyuncu_y][oyuncu_x + 1:]
            oyun_haritasi[hedef_y] = oyun_haritasi[hedef_y][:hedef_x] + OYUNCU + oyun_haritasi[hedef_y][hedef_x + 1:]
            if oyun_haritasi[kutu_hedef_y][kutu_hedef_x] == HEDEF:
                # Kutu hedefe ulaştığında hedefi kaldır ve kutuyu koy
                oyun_haritasi[kutu_hedef_y] = oyun_haritasi[kutu_hedef_y][:kutu_hedef_x] + KUTU + oyun_haritasi[kutu_hedef_y][kutu_hedef_x + 1:]
            else:
                oyun_haritasi[kutu_hedef_y] = oyun_haritasi[kutu_hedef_y][:kutu_hedef_x] + KUTU + oyun_haritasi[kutu_hedef_y][kutu_hedef_x + 1:]

    return oyun_haritasi

# Toplam seviye sayısını belirle
def seviye_sayisini_bul():
    seviye_klasoru = os.path.join(PROJE_DIZINI, "seviye")
    seviye_dosyalari = [f for f in os.listdir(seviye_klasoru) if f.startswith("seviye") and f.endswith(".txt")]
    return len(seviye_dosyalari)

# Oyun başlangıcında seviye sayısını belirle
maksimum_seviye = seviye_sayisini_bul()

# Seviye yönetimi için yeni değişkenler
mevcut_seviye = 1

def sonraki_seviye():
    global iksir_alindi, mevcut_seviye, oyun_haritasi, oyun_kazanildi, oyun_bitti
    iksir_alindi = False  # İksir etkisini sıfırla
    
    # Bir sonraki mevcut seviyeyi bul
    sonraki_seviye_bulundu = False
    while not sonraki_seviye_bulundu and mevcut_seviye < 100:  # Maksimum 100 seviye kontrolü
        mevcut_seviye += 1
        harita_yolu = os.path.join(PROJE_DIZINI, "seviye", f"seviye{mevcut_seviye}.txt")
        if os.path.exists(harita_yolu):
            yeni_harita = harita_oku(harita_yolu)
            if yeni_harita is not None:
                oyun_haritasi = yeni_harita
                oyun_kazanildi = False
                sonraki_seviye_bulundu = True
                # Harita boyutlarını güncelle
                global SUTUNLAR, SATIRLAR, KARE_BOYUTU
                SUTUNLAR = len(oyun_haritasi[0])
                SATIRLAR = len(oyun_haritasi)
                KARE_BOYUTU = min(EKRAN_GENISLIK // SUTUNLAR, EKRAN_YUKSEKLIK // SATIRLAR)
    
    # Hiç seviye bulunamadıysa oyunu bitir
    if not sonraki_seviye_bulundu:
        oyun_bitti = True
        oyun_kazanildi = False
        print(f"Tebrikler! Tüm seviyeleri tamamladınız!")

# İlk haritayı yükle ve kontrol et
harita_yolu = os.path.join(PROJE_DIZINI, "seviye", "seviye1.txt")
oyun_haritasi = harita_oku(harita_yolu)
if oyun_haritasi is None:
    print("İlk seviye bulunamadı!")
    pygame.quit()
    sys.exit()

# Oyun döngüsü değişkenleri
saat = pygame.time.Clock()
calisiyor = True
oyun_kazanildi = False
oyun_bitti = False
kazanma_mesaji_zamani = 0

# Menü butonları için sabitler
MENU_YUKSEKLIK = 50
MENU_ARKAPLAN = (50, 50, 50)  # Koyu gri
MENU_BUTON_RENK = (100, 100, 100)  # Açık gri
MENU_BUTON_AKTIF = (150, 150, 150)  # Daha açık gri
MENU_YAZI_RENK = (255, 255, 255)  # Beyaz

def menu_ciz():
    # Menü arkaplanı
    pygame.draw.rect(screen, MENU_ARKAPLAN, (0, 0, EKRAN_GENISLIK, MENU_YUKSEKLIK))
    
    # Butonları oluştur - seviye bilgisini ekleyerek
    butonlar = [
        {"text": f"Seviye: {mevcut_seviye}/{maksimum_seviye}", "x": 10},  # Mevcut/Toplam seviye
        {"text": "Tekrar Başlat", "x": 160},
        {"text": "Yardım", "x": 310},
        {"text": "Çıkış", "x": 460}
    ]
    
    # Mouse pozisyonunu al
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    for buton in butonlar:
        buton_genislik = 130
        buton_rect = pygame.Rect(buton["x"], 5, buton_genislik, 30)
        
        # Mouse butonun üzerinde mi kontrol et
        if buton_rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, MENU_BUTON_AKTIF, buton_rect)
        else:
            pygame.draw.rect(screen, MENU_BUTON_RENK, buton_rect)
        
        # Buton yazısı
        text = font.render(buton["text"], True, MENU_YAZI_RENK)
        text_rect = text.get_rect(center=buton_rect.center)
        screen.blit(text, text_rect)

def seviyeyi_yeniden_baslat():
    global oyun_haritasi, iksir_alindi, oyun_kazanildi
    harita_yolu = os.path.join(PROJE_DIZINI, "seviye", f"seviye{mevcut_seviye}.txt")
    oyun_haritasi = harita_oku(harita_yolu)
    iksir_alindi = False
    oyun_kazanildi = False

def yardim_goster():
    yardim_metni = [
        "Yardım:",
        "- Yön tuşları ile hareket edin",
        "- Kutuları hedeflere itin",
        "- İksiri alarak kutuları çekebilirsiniz",
        "- ESC tuşu ile çıkış yapın",
        "",
        "Devam etmek için bir tuşa basın"
    ]
    
    yardim_ekrani = True
    while yardim_ekrani:
        screen.fill(SIYAH)
        y_pozisyon = EKRAN_YUKSEKLIK // 4
        
        for satir in yardim_metni:
            text = font.render(satir, True, BEYAZ)
            text_rect = text.get_rect(center=(EKRAN_GENISLIK // 2, y_pozisyon))
            screen.blit(text, text_rect)
            y_pozisyon += 40
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                yardim_ekrani = False
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# Oyun döngüsünü güncelle
while calisiyor:
    screen.fill(SIYAH)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            calisiyor = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Mouse tıklamalarını kontrol et
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_y < MENU_YUKSEKLIK:  # Menü alanında tıklama
                if 160 <= mouse_x <= 290:  # Tekrar Başlat butonu
                    seviyeyi_yeniden_baslat()
                elif 310 <= mouse_x <= 440:  # Yardım butonu
                    yardim_goster()
                elif 460 <= mouse_x <= 590:  # Çıkış butonu
                    calisiyor = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                calisiyor = False
            elif not oyun_kazanildi and not oyun_bitti:
                if event.key == pygame.K_UP:
                    oyun_haritasi = oyuncu_hareket(oyun_haritasi, "YUKARI")
                elif event.key == pygame.K_DOWN:
                    oyun_haritasi = oyuncu_hareket(oyun_haritasi, "ASAGI")
                elif event.key == pygame.K_LEFT:
                    mevcut_yon = "SOL"
                    oyun_haritasi = oyuncu_hareket(oyun_haritasi, "SOL")
                elif event.key == pygame.K_RIGHT:
                    mevcut_yon = "SAG"
                    oyun_haritasi = oyuncu_hareket(oyun_haritasi, "SAG")
                
                # Her hareketten sonra kazanma durumunu kontrol et
                if kazanma_kontrol(oyun_haritasi):
                    oyun_kazanildi = True
                    kazanma_mesaji_zamani = pygame.time.get_ticks()
                    
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                mevcut_yon = "VARSAYILAN"

    # Haritayı çiz
    harita_ciz(oyun_haritasi)
    
    # Mesajları göster ve sonraki seviyeye geçiş kontrolü
    if oyun_bitti:
        bitis_metni = font.render("Tebrikler! Tüm Seviyeleri Tamamladınız!", True, YESIL)
        metin_alani = bitis_metni.get_rect(center=(EKRAN_GENISLIK/2, EKRAN_YUKSEKLIK/2))
        screen.blit(bitis_metni, metin_alani)
    elif oyun_kazanildi:
        kazanma_metni = font.render("Tebrikler! Sonraki Seviye için SPACE'e Basın", True, YESIL)
        metin_alani = kazanma_metni.get_rect(center=(EKRAN_GENISLIK/2, EKRAN_YUKSEKLIK/2))
        screen.blit(kazanma_metni, metin_alani)
        
        # SPACE tuşuna basılınca sonraki seviyeye geç
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            sonraki_seviye()
    
    # En son menüyü çiz
    menu_ciz()
    
    pygame.display.flip()
    saat.tick(30)

pygame.quit()
sys.exit()
