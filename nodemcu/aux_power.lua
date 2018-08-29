
--Auxiliry Power

function aux_on()
    gpio.mode(7, gpio.OUTPUT)
    print('Turning on Auxiliry Power')
    gpio.write(7, gpio.LOW)
end

function aux_off()
    print('Turning off Auxiliry Power')
    gpio.write(7, gpio.HIGH)
    gpio.mode(7, gpio.INPUT, gpio.FLOAT) --D7 set to High Z
end