import sys

def commands():
    comandos = [
        '0: setear origen',
        'o: prender led' ,
        'l: mover 10 a la izquierda',
        'h: mover 10 a la derecha',
        'a: apagar todos los leds',
        'q: salir'
    ]
    texto = ''
    for comando in comandos:
        texto = texto + comando + "\n"
    return texto



if __name__ == "__main__":
    from todo_junto.sph_module import SphericalController

    sph = SphericalController("/dev/ttyACM0")

    comando = ''

    while comando != 'q':
        comando = input(commands())
        if comando == '0':
            resp = sph.set_origin()
            print(resp)

        elif comando == 'l':
            resp = sph.rotate_left()
            print(resp)
            
        elif comando == 'h':
            resp = sph.rotate_right()
            print(resp)

        elif comando == 'o':
            led = input('seleccionar led ')
            tiempo = input('Seleccionar tiempo ')
            resp = sph.turn_on_led(int(led), 'g', int(tiempo))
            print(resp)

        elif comando == 'a':
            resp = sph.turn_off_leds()
            print(resp)

        else:
            print('comando incorrecto')

