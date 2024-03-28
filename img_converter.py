import base64

input_file = input('Enter image path: ')
with open(input_file, 'rb') as image:
    encoded_img = base64.b64encode(image.read())
    print(encoded_img.decode('utf-8'))