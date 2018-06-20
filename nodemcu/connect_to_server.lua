--connect to server--
local publicServerInteract={};
local host = nil
local port = nil
local connection = false

--Proceed to connect to server-
function sendMessage(message)
    if host == nil or port == nil then
        print('Host and port must be set')
        --return setupconnection()
    else
        print('Connecting to server: '..host..':'..port)
        srv = net.createConnection(net.TCP,0)
        srv:on("receive", function(sck, msg)
            msg = sjson.decode(msg)
            print(msg["status"])
            print(msg["message"])  
            if msg["status"] == 1 then
                print("Server is ready for data")
                print("Sending Message")
                sck:on("sent", function()
                    print("Message sent")
                    sck:close()
                    print("Connection closed")
                end)
                sck:send(message)       
            end 
        end)
        srv:connect(port,host)
    end
    
    --waitForConEvnt(10)
end

function setHostPort(h,p)
    host = h
    port = p
end

function publicServerInteract.returnHost()
    return host
end

function publicServerInteract.returnPort()
    return port
end

function setupServerConnection()
    print("Please set host and port data should be sent to:")
    print("setHostPort('host',port)")
    print("Messages can then be sent by doing:")
    print("sendMessage('message')")
end

return publicServerInteract
