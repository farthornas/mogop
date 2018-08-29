--This will be the sequence running on nodemcu
publicSequence = {}
--Setup file
local USERSETUPFILE = "usersetup.lua"
--CONTEXT DEFINES
local PLANT_SPECIES = "species"
local TX_TYPE = "type"
local MEASUREMENT_D = "period"
local setup = {}
--SENSORS
local SOILMOISTURE = "soilmoisture"
local LIGHT = "light"
local AVAIL_SENS = {SOILMOISTURE,LIGHT}
local sensors = {}
local measurements = {}

--TIMERS
local MAIN_ALARM = 0

--FILE INITS
local sens = dofile("sensors.lua")
--local user = dofile("user.lua")
local server = dofile("connect_to_server.lua")
local aux = dofile("aux_power.lua")

--******************* SENSING AND SLEEP *******************

function recordAndSleep()
    print("Doing Recordings")
    record_loop()
end
    
function record_loop()
    --todo make 10 separate recordings
    aux_on()
    for _,item in pairs(SENS) do
        if item == SOILMOISTURE then
            measurements[SOILMOISTURE] = sens.SoilMoisture()           
        end
    end
    aux_off()
    add_setup_param()
    send_json()
    tmr.alarm(1, 5000, tmr.ALARM_SINGLE, function()
        print("Going to Sleep")
        file.open("dsleepflag", "w")
        file.flush()
        file.close()
        sleep = PERIOD * 1000000
        node.dsleep(sleep)
    end)
end
function add_setup_param()
    measurements[PLANT_SPECIES] = SPECIES
    measurements[TX_TYPE] = TYPE
    measurements[MEASUREMENT_D] = PERIOD
end

function send_json()
    jsoned = sjson.encode(measurements)
    print("Data to be sent:"..jsoned)
    sendMessage(jsoned)
end

function stop_recording()
    file.remove("dsleepflag")
end

return publicSequence

