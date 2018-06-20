--Read Moisture Sensor

D0 = 0 -- DIODE RES NETWORK CONNECTED TO THIS PIN
D1 = 1 -- NO OTHER CONNECTIONS
D2 = 2 -- NO OTHER CONNECTIONS
D3 = 3 -- RES NETWORK CONNECTED
D4 = 4 -- RES NETWORK CONNECTED
D5 = 5 -- NO OTHER CONNECTIONS
D6 = 6 -- NO OTHER CONNECTIONS
D7 = 7 -- NO OTHER CONNECTIONS
D8 = 8 -- RES NETWORK CONNECTED
D9 = 9 -- NO OTHER CONNECTIONS
D10 = 10 -- NO OTHER CONNECTIONS

publicSoilMoist = {}

function clean_up()
    print('Clean up state')
    gpio.mode(D1, gpio.INPUT, gpio.FLOAT)
    gpio.mode(D2, gpio.INPUT, gpio.FLOAT)
    gpio.mode(D5, gpio.INPUT, gpio.FLOAT)
    gpio.mode(D6, gpio.INPUT, gpio.FLOAT)
end

function pol_top()
    -- Setup the circuit for "TOP" polarity.
    -- D2 sets 3.3V, D1 and D5 is set to GND.
    -- Sensor signal is on same net as D6,
    -- D6 is hence set to high impedance.
    gpio.mode(D1, gpio.OUTPUT)
    gpio.mode(D2, gpio.OUTPUT)
    gpio.mode(D5, gpio.OUTPUT) 
    
    -- Setting pin values
    gpio.write(D1, gpio.LOW)
    gpio.write(D2, gpio.HIGH)
    gpio.mode(D6, gpio.INPUT, gpio.FLOAT) -- D6 Z input
    gpio.write(D5, gpio.LOW)
end

function pol_bot()
    -- Setup the circuit for "BOTTOM" polarity.
    -- D1 sets 3.3V, D2 and D6 is set to GND.
    -- Sensor signal is on same net as D5,
    -- D5 is hence set to high impedance.
    gpio.mode(D1, gpio.OUTPUT)
    gpio.mode(D2, gpio.OUTPUT)
    gpio.mode(D6, gpio.OUTPUT)
    
    -- Setting pin values
    gpio.write(D1, gpio.HIGH)
    gpio.write(D2, gpio.LOW)
    gpio.mode(D5, gpio.INPUT, gpio.FLOAT) -- D5 Z input
    gpio.write(D6, gpio.LOW)
end
    
function publicSoilMoist.read_adc(i)
    if i % 2 == 0 then
        pol_top()
        print('Reading top')
    else
        pol_bot()
        print('Reading bottom')
    end
    moist = adc.read(0)
    clean_up()
    return moist
end

return publicSoilMoist
    




