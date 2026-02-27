import reedsolo as rs
from PIL import Image, ImageDraw

def draw_finder_patterns(tab) -> None:
    size = len(tab)
    x_coords = [0,0,size-7]
    y_coords = [0,size-7,0]
    for l in range(len(y_coords)):    
        x = x_coords[l] 
        y = y_coords[l]
        for i in range(7): # border maker
            tab[i+x][0+y] = 1
            tab[i+x][6+y] = 1
            tab[0+x][i+y] = 1
            tab[6+x][i+y] = 1

        for j in range(3):   # fill pattern centers
            for k in range(3):
                tab[j+x+2][k+y+2] = 1
    for j in range(0,size-14,2):
        tab[6+j][6] = 1 # vertical synchronization line
        tab[6][6+j] = 1 # horizontal synchronization line

def add_alignment_patterns(tab,reserved, version) -> None:
    if version == 1:
        return
    size = len(tab)
    all_cords = [[],[],[6,18],[6,22],[6,26]]
    cords = all_cords[version]
    potential_centers = []
    for i in range(len(cords)):
        for j in range(len(cords)):
            potential_centers.append([cords[i],cords[j]])
    valid_cords = []
    for x,y in potential_centers:
        if x <= 7 and y <= 7:
            continue
        elif x <= 7 and y >= size - 8:
            continue
        elif x >= size - 8 and y <= 7:
            continue
        valid_cords.append([x,y])

    for x,y in valid_cords:
        tab[x][y] = 1
        for i in range(5):
            tab[x-2+i][y-2] = 1 # left side
            tab[x-2+i][y+2] = 1 # right side
            tab[x-2][y-2+i] = 1 # up 
            tab[x+2][y-2+i] = 1 # down
            for j in range(5):
                reserved[x-2+i][y-2+j] = 1 

def create_reserved_matrix(size) -> list:
    reserved = [[0 for _ in range(size)] for _ in range(size)]
    temp = 0 # temp is used to skip intersection when index is 6
    for i in range(8):
        reserved[8][size-8+i] = 3 # top-right format info area
        reserved[size-8+i][8] = 3 # bottom-left format info area
        if i == 6:
            temp = 1
        reserved[8][i+temp] = 3 # top-left format info (horizontal)
        reserved[temp+i][8] = 3 # top-left format info (vertical)
        for j in range(8):
            reserved[i][j] = 1 # top-left finder pattern
            reserved[i][j+size-8] = 1  # top-right finder pattern 
            reserved[i+size-8][j] = 1 # bottom-left finder pattern

    for k in range(size-16):
        reserved[8+k][6] = 2 # vertical timing pattern 
        reserved[6][8+k] = 2 # horizontal timing pattern
    reserved[size-8][8] = 1
    return reserved

def encode_text_to_bits(text) -> tuple:
    bits = "0100"
    char_count = len(text)
    bits += f"{char_count:08b}"
    for char in text:
        bits += f"{ord(char):08b}" # convert char to bits

    bits += "0000"
    while len(bits) % 8 != 0:
        bits += "0"
    size, version, total_capacity = find_version_and_capacity(bits)
    ec_bytes = [0,7,10,15,18]
    total_bits = (total_capacity//8) * 8
    bits_limit = total_bits - ec_bytes[version] * 8
    remaining_bits = bits_limit - len(bits)
    padding = ["11101100", "00010001"]
    i = 0
    while remaining_bits >= 8:
        bits += padding[i]
        i += 1
        i %= 2
        remaining_bits -= 8
    if remaining_bits > 0:
        bits += padding[i][:remaining_bits]
    return bits, size, version

def find_version_and_capacity(bits) -> tuple:
    char_count = len(bits)
    ec_bytes = [7,10,15,18]

    size = 21
    version = 0
    while True:
        ec_bits = ec_bytes[version] * 8
        test_matrix = [[0 for _ in range(size)] for _ in range(size)]
        test_reserved = create_reserved_matrix(size)

        add_alignment_patterns(test_matrix,test_reserved,version+1)
        free_modules = 0
        for row in test_reserved:
            free_modules += row.count(0)
        max_capacity = (free_modules//8)*8
        if max_capacity >= char_count + ec_bits:
            return size, version+1, free_modules
        size += 4
        version += 1

def place_data_bits(tab,reserved,word) -> list:
    size = len(tab)
    moving_up = True
    x = size - 1
    y = size - 1
    i = 0
    while y >= 0:
        for j in range(2):
            curr = y - j
            if curr >= 0 and reserved[x][curr] == 0:
                if i < len(word):
                    tab[x][curr] = int(word[i])
                    i += 1
                else:
                    tab[x][curr] = 0
        if moving_up:
            x -= 1
            if x < 0:
                y -= 2
                moving_up = False
                x = 0
                if y == 6:
                    y -= 1
        else:
            x += 1
            if x >= size:
                y -= 2
                moving_up = True
                x = size - 1     
                if y == 6:
                    y -= 1       
    return tab

def debug_print_matrix(tab) -> None:
    for i in range(len(tab)):
        for j in range(len(tab[0])):
            print(f"{tab[i][j]}, ", end="")
        print()

def print_qr_terminal(tab) -> None:
    for row in tab:
        line = ""
        for cell in row:
            line += "██" if cell == 1 else "  "
        print(line)

def apply_mask(tab,reserved) -> list:
    for i in range(len(tab)):
        for j in range(len(tab)):
            if reserved[i][j] != 0:
                continue
            if (i + j) % 2 == 0:
                tab[i][j] = 1 - tab[i][j]
            else:
                continue 
    return tab

def quiet_zone(tab) -> list:
    size = len(tab) + 8
    final = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(len(tab)):
        for j in range(len(tab)):
            final[i+4][j+4] = tab[i][j]
    return final

def add_error_correction(data_bits,version) -> str:
    ec_bytes = [0,7,10,15,18]
    data_bytes = [int(data_bits[i:i+8],2)
             for i in range(0, len(data_bits),8)]
    codec = rs.RSCodec(ec_bytes[version],fcr=0)
    encoded_bytes = codec.encode(data_bytes)
    final = ""
    for b in encoded_bytes:
        final += f"{b:08b}"
    return final

def add_format_info(tab) -> None:
    fmt = "111011111000100" # korekcja l, maska 0
    size = len(tab)
    skip1 = 0 # skip when index is on synchronization line
    skip2 = 0 # skip when index is on synchronization line
    for i in range(8):
        if i == 6:
            skip1 = 1
        tab[8][size-8+i] = int(fmt[7+i]) # top-left horizontal
        tab[8][i+skip1] = int(fmt[i]) # top-right horizontal
        if i == 1:
            skip2 = 1
        if i <= 6:
            tab[7-i-skip2][8] = int(fmt[8+i]) # top-left vertical
    for i in range(7):     
        tab[size-1-i][8] = int(fmt[i]) # bottom-left vertical
    tab[size-8][8] = 1 # dark module

def generate_qr_code(link) -> list:
    bits,size, version = encode_text_to_bits(link)
    bits = add_error_correction(bits,version)
    matrix = [[0 for _ in range(size)] for _ in range(size)]
    reserved = create_reserved_matrix(size)
    draw_finder_patterns(matrix)
    add_alignment_patterns(matrix,reserved,version)
    place_data_bits(matrix,reserved,bits)
    apply_mask(matrix,reserved)
    add_format_info(matrix)
    return quiet_zone(matrix)

def save_as_image(tab, file_name="moj_qr.png") -> None:
    size = len(tab)
    skala = 10
    img_size = size * skala

    img = Image.new('RGB', (img_size, img_size), "white")
    draw = ImageDraw.Draw(img) 
    
    for i in range(size):
        for j in range(size):
            if tab[i][j] == 1:
                x0 = j * skala
                y0 = i * skala
                x1 = x0 + skala - 1
                y1 = y0 + skala - 1
                
                draw.rectangle([x0, y0, x1, y1], fill=(0, 0, 0))
                        
    img.save(file_name)
    print(f"Zapisano jako {file_name}! Otwórz plik i zeskanuj.")

def create_and_save_qr(link, file_name):
    print(f"Trwa generowanie kodu QR dla: {link}")

    matrix = generate_qr_code(link)

    print("\n[PODGLAD KODU QR]")
    print_qr_terminal(matrix)
    
    save_as_image(matrix, file_name)
    print(f"\n[WYGENEROWANA KOD QR I ZAPISANO JAKO {file_name}]")


if __name__ == "__main__":
    print("=== Generator kodow QR ===")
    user_link = input("Podaj link do zakodowania: ")
    user_file_name = " "
    while " " in user_file_name:
        user_file_name = input("Podaj nazwe pliku (np. moj_qr): ")
        if " " in user_file_name:
            print("Wpisano niepoprawna nazwe pliku!\n"
                "Sprobuj jeszcze raz!")
    if not user_file_name:
        user_file_name = "qrcode"
    user_file_name += ".png"
    create_and_save_qr(user_link, user_file_name)