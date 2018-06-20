--init.lua

--look for dsleepflag if here erase it and initiate measurement
local run = dofile("sequence.lua")
local wifi = dofile("wifi_logon.lua")
local server = dofile("connect_to_server.lua")
dofile("usersetup.lua")
if file.exists("dsleepflag") then
    file.remove("dsleepflag")
    setHostPort(HOST,PORT) --host port defined in user setup
    waitForIP(10)
    recordAndSleep()
else
    print("\n Setup Sequence \n")  
    wifi_info()
    --options() 
end

function startRecording()
    local i = 0
    --if default == true then
    setHostPort(HOST,PORT)
    --end
    if server.returnHost()==nil then
        print("Server Host not set, set Host to start recording")
        i = i + 1
    end
    if server.returnPort()==nil then
        print("Server port not set, set Host to start recording")
        i = i + 1
    end
    if wifi.isConnected()==nil then
        print("Not connected to wifi, connect to wifi to start recording")
        i = i + 1
    end
    if i == 0 then
        print("got here")
        recordAndSleep()
    end
    i = 0
end
