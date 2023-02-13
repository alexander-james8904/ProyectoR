from machine import Pin, UART, Timer, ADC #Para utilizar pines de entrada y salida
import time, utime#Para utilizar demoras
import _thread #Para utilizar doble núcleo???
from gpio_lcd import GpioLcd #Libreria para controlar el display
import _thread #Para utilizar doble núcleo

def core0_thread(): #Tarea del segundo núcleo (únicamente parpadear el LED de la Pico como testigo de funcionamiento)
    led = Pin(25, Pin.OUT)
    while True:
        led.value(not led.value())
        time.sleep(0.1)

#Cosas importantes mas adelante
lcdtime = 0#Para apagar el display
threshold = 50
uart = UART(0,9600)#Utilizacion del UART 0, ubicado en pin 1 TX0 y en el pin 2 RX0
#Entradas
btnd = Pin(6, Pin.IN, Pin.PULL_UP) #Entrada pulsador cambio hacia abajo
btnu = Pin(7, Pin.IN, Pin.PULL_UP) #Entrada pulsador cambio hacia arriba

luzadc = ADC(26)#Entrada del fotoresistor
humadc =ADC(27)#Entrada
#Salidas
bluali = Pin(2, Pin.OUT)#Alimentación del Bluetooth
senali = Pin(28, Pin.OUT)#Alimentación del sensor de humedad
lcdali = Pin(22, Pin.OUT)#Alimentación del display
optali = Pin(15, Pin.OUT)#Alimentación del optoacoplador para la bomba.
lcd = GpioLcd(rs_pin=Pin(16),
              enable_pin=Pin(17),
              d4_pin=Pin(18),
              d5_pin=Pin(19),
              d6_pin=Pin(20),
              d7_pin=Pin(21),
              num_lines=2, num_columns=16)#Declaración de pines para el display



#    if uart.any():
 #       command = uart.readline()
  #      print(command)
   #     time.sleep(0.5)




def check_timer(timer):
    print(threshold)
    global lcdtime
    if lcdtime == 1:
        lcdali.off()
    else:
        lcdtime = 1
    check() 
    lcdali.on()#Enciende el display
   

def thr_down(): #Interrupcíon para bajar el límite
    global  threshold
    lcdali.on()
    lcdtime = 0
    threshold = threshold-1 #Cambia el valor del límite
    lcd.clear() #Limpia el display
    thr=str(threshold)
    lcd.putstr(thr+"%")#Muestra el nuevo límite en el display
    time.sleep(0.2) #Antirrebote
    
def thr_up(): #Interrupcíon para subir el límite
    global  threshold
    lcdali.on()
    lcdtime = 0
    threshold = threshold+1 #Cambia el valor del límite
    lcd.clear() #Limpia el display
    thr=str(threshold)
    lcd.putstr(thr+"%")#Muestra el nuevo límite en el display
    time.sleep(0.2) #Antirrebote
    
def luz_check():
    return luzadc.read_u16()

def hum_check():
    senali.on()
    time.sleep(0.3)#Delay por las dudas, hay que probar sacarlo
    x=humadc.read_u16()
    y=(x*100)/16000#Paso a % el resultado
    senali.off()
    return y

def giesen():
    optali.on()
    time.sleep(10)
    optali.off()
    
def check():
    global threshold
    luz=luz_check()
    if luz< 5000 :
        hum=hum_check()
        if hum<threshold:
            giesen()
        else:
            pass
    else:
        pass

#Interrupciones
timer=Timer()   
timer.init(freq=1, mode=Timer.PERIODIC, callback=check_timer)#Llama a la función "Check" cada cierto tiempo
btnd.irq(trigger=Pin.IRQ_RISING, handler=thr_down)#Por presionar un botón
btnu.irq(trigger=Pin.IRQ_RISING, handler=thr_up)#Por presionar un botón
#while True:
 #   if btnd.value()==0:
  #      thr_down()
   # if btnu.value()==0:
    #    thr_up()
    #print (btnd.value())
    #time.sleep(1)