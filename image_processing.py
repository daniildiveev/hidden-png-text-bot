import numpy as np
from PIL import Image
from config import STOP_INDICATOR


def encode_and_hide_message_in_png(image_path: str,
                                   message: str,
                                   stop_indicator: str = STOP_INDICATOR):
    assert image_path[-4:] == '.png', "Your image is not PNG format"

    image = Image.open(image_path, 'r')
    w, h = image.size

    if image.mode == "P":
        return 'Image mode not supported'

    img_array = np.array(list(image.getdata()))
    chnls = 4 if image.mode == 'RGBA' else 3
    n_pixels = img_array.size // chnls

    secret_query = message + stop_indicator
    byte_query = ''.join(f"{ord(c):08b}" for c in secret_query)
    n_bits = len(byte_query)

    if n_bits > n_pixels:
        return 'Not enough pixels'

    index = 0

    print(img_array.shape)

    for j in range(n_pixels):
        for i in range(0, 3):
            if index < n_bits:
                img_array[j][i] = int(bin(img_array[j][i])[2:-1] + byte_query[index], 2)
                index += 1

    img_array = np.reshape(img_array, (h, w, chnls))
    result = Image.fromarray(img_array.astype('uint8'), image.mode)

    new_image_path = f"{image_path[:-5]}_encoded.png"
    result.save(new_image_path)

    return 1, new_image_path

def retrieve_message_from_png(image_path: str,
                              stop_indicator: str = STOP_INDICATOR):
    assert image_path[-4:] == '.png', "Your image is not PNG format"

    image = Image.open(image_path, 'r')
    img_array = np.array(list(image.getdata()))

    chnls = 4 if image.mode == 'RGBA' else 3
    n_pixels = img_array.size // chnls

    secret_bits = [bin(img_array[i][j])[-1] for i in range(n_pixels) for j in range(0, 3)]
    secret_bits = ''.join(secret_bits)
    secret_bits = [secret_bits[i:i + 8] for i in range(0, len(secret_bits), 8)]

    secret_message = [chr(int(secret_bits[i], 2)) for i in range(len(secret_bits))]
    secret_message = ''.join(secret_message)

    if stop_indicator in secret_message:
        return secret_message[:secret_message.index(stop_indicator)]
    else:
        return -1