-- Configure Wireless Internet

local publicWifi={}
local ssid = nil
local password = nil

function publicWifi.setupwifi()
    print('Set wifi mode='..STATION)
    wifi.setmode(wifi.STATION)
    
end
-- wifi list access points
function listaps(t)
    print('\nLISTING AVAILABLE ACCESS POINTS\n')
    print('\n SSID  AUTHMODE  RSSI  BSSID  CHANNEL')
    for ssid,v in pairs(t) do
        authmode, rssi, bssid, channel =
        string.match(v, "(%d),(-?%d+),(%x%x:%x%x:%x%x:%x%x:%x%x:%x%x),(%d+)")     
        print(ssid,authmode,rssi,bssid,channel)
    end
    --print("\nConnect to access point by running:")
    --print("connect('SSID','PASSWORD')")
end
-- connect to access point
function connect(s,p)
    inet_conf = {ssid=s, pwd=p}
    print('\nConnecting to: '..s)
    wifi.sta.config(inet_conf)
    wifi.sta.connect()
    -- wait for an IP
    waitForIP(10)

end

function waitForIP(time)
    cnt = time
    tmr.alarm(0,1000,1,function()
        if wifi.sta.getip()==nil then
            cnt = cnt-1
            if cnt<=0 then
                -- Did not get an IP in time, so quitting
                tmr.stop(0)
                print("Not connected to wifi.")
                print("Wifi status is: ",wifi.sta.status())
            end
        else
            -- Connected to the wifi
            tmr.stop(0)
            print("\nConnected to: ",publicWifi.ssid())
            print("IP: ",wifi.sta.getip())
        end
    end)
end

function publicWifi.isConnected()
    if wifi.sta.getip() == nil then
        return false
    else
        return true
    end
end

function publicWifi.ssid()
    return ssid
end   

function publicWifi.ip()
    return wifi.sta.getip()
end

function publicWifi.ssid()
    local x=wifi.sta.getapinfo()
    local y=wifi.sta.getapindex()
    return x[y].ssid
end



--User Commands

function wifi_info()
    print('Wifi mode='..wifi.getmode())
    print('MAC Address: ',wifi.sta.getmac())
    print('Chip ID: ',node.chipid())
    print('Heap Size: ',node.heap(),'\n')
    if publicWifi.isConnected() == true then
        print("Connected to: "..publicWifi.ssid())
    else
        print("Currently not connected to a network")
    end
end

function showAPs()
    publicWifi.setupwifi()
    wifi.sta.getap(listaps)
end

return publicWifi
