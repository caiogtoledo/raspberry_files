from time import sleep
from ina219 import INA219

# Inicializando o sensor INA219
ina = INA219(shunt_ohms=0.1, max_expected_amps=0.6, address=0x40)

# Configuração do INA219
ina.configure(voltage_range=ina.RANGE_16V,
              gain=ina.GAIN_AUTO,
              bus_adc=ina.ADC_128SAMP,
              shunt_adc=ina.ADC_128SAMP)

try:
    while True:
        # Lendo os valores do INA219
        v = ina.voltage()
        i = ina.current()
        p = ina.power()
        
        # Imprimindo os resultados no terminal
        print(f'SENSOR: 0x40')
        print(f'Tensão: {v:0.1f} V')
        print(f'Corrente: {i:0.2f} mA')
        print(f'Potência: {p/1000:0.1f} W')
        print('-----------------------------')
        sleep(1)

except KeyboardInterrupt:
    print("\nCtrl-C pressionado. Programa encerrado...")