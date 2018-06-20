publicUser = {}

local MEASUREMENT_D = "period"
local USERSETUPFILE = "usersetup.lua"
local DEFAULTSETUPFILE = "defaultsetup.lua"
local USERSETUPOLD = "usersetup.old"

function options()
    print("User Options\n")
    print("Show Options:")
    print("options()\n")
    print("WIFI Options:")
    print(" Print Access points by typing:")
    print("     listAPs()")
    print(" Connect to Acces point by typing:")
    print("     connect('SSID','PASSWORD')")
    print(" Show WIFI info:")
    print("     wifi_info()\n")
    print("Server Options:")
    print(" Connect to server:")
    print("     setupServerConnection()\n")
    print("Measurements Options:")
    print(" Set period between measurements (seconds):")
    print("     set_period(seconds)")
    print(" Select measurements to be taken (soilmoisture):")
    print("     set_sensors({'soilmoisture','temperature','...'})")
    print(" Use default measurement setup (All sensors recorded every 60 seconds)")
    print("     default_setup()")
end

function default_setup()
    file.rename(USERSETUPFILE,USERSETUPOLD)
    file.rename(DEFAULTSETUPFILE,USERSETUPFILE)
    dofile(USERSETUPFILE)
    default = true
end

function user_write_file(input)
    file.open(USERSETUPFILE,"a+")
    file.writeline(input)
    file.flush()
    input = nil
    file.close()
end

function set_period(seconds)
    period = "PERIOD = \""..seconds.."\""
    user_write_file(period)
    print("Period set to: "..seconds.."s")
end

function set_sensors(sens)
    for _,item in pairs(sens) do 
        if item == 'all' then
            sensors = AVAIL_SENS
            --break
        end
        for _2,item2 in pairs(AVAIL_SENS) do 
            if item == item2 then
                table.insert(sensors,item2)
            else
                print(""..item.." is not an available sensor")
            end
        end
    end  
    print("\nThe following sensors will be recorded:")  
    for i,item in pairs(sensors) do
        print(item)
    end
    temp = "SENS = \""..sensors.."\""
    user_write_file(temp)
end

function publicUser.read_userinput()
    dofile(USERSETUPFILE)
    sensors = SENS
    period = PERIOD
end



return publicUser
