--Sensors
publicSensors = {}

local moist_sens = dofile("moistsens.lua")
local top_bot = nil

function publicSensors.SoilMoisture()
    top_bot = node.random(2)
    soilmoist = moist_sens.read_adc(top_bot)
    if top_bot == 1 then
        top_bot = 2
    else
        top_bot = 1
    end
    return soilmoist
end

return publicSensors
--function sensors_select(i)
--    if 
