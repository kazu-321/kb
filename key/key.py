from pynput import keyboard
import sys
import rclpy,threading
from rclpy.node import Node 
from std_msgs.msg import String
dir={"w":[0,1],"a":[-1,0],"s":[0,-1],"d":[1,0],"Key.up":[0,1],"Key.down":[0,-1],"Key.right":[1,0],"Key.left":[-1,0]}
a={"[0, 0]":0,"[0, 1]":0,"[1, 0]":90,"[-1, 0]":-90,"[1, 1]":45,"[-1, 1]":-45,"[1, -1]":135,"[-1, -1]":-135}
old=["",""]
send=""

def arc(d):
    if d==[0,-1]:
        if 0<old[1]:
            return 180
        else:
            return -180
    else:
        return a[str(d)]

class pineapple(Node):
    def __init__(self):
        super().__init__("key")
        self.pub=self.create_publisher(String,"cmd",10)
        self.pub_n=self.create_publisher(String,"nucleo_cmd",10)
        self.timer = self.create_timer(0.1,self.call)
        self.cmd=String()
        self.keys=set()
        self.start()

    def call(self):
        global send
        d=[0,0]
        c=[0,0]
        speed=0
        for key in self.keys:
            if key in list("wasd"):
                d[0]+=dir[key][0]
                d[1]+=dir[key][1]
            elif key[4:] in ["up","down","right","left"]:
                c[0]+=dir[key][0]
                c[1]+=dir[key][1]
        self.cmd.data="#C"+str(c[0]).replace("-1","-").replace("1","+")+str(c[1]).replace("-1","-").replace("1","+")
        if old[0]!=self.cmd.data:
            self.pub.publish(self.cmd)
            old[0]=self.cmd.data
        d=arc(d)
        self.cmd.data="/cd "+str(d)
        if old[1]!=d:
            self.pub.publish(self.cmd)
            old[1]=d
        if send!="":
            self.cmd.data="/"+send
            send=""
            self.pub.publish(self.cmd)
    
    def on_press(self,key):
        try:
            # print('press: {}'.format(key.char))
            self.keys.add(key.char)
        except AttributeError:
            # print('spkey press: {}'.format(key))
            self.keys.add(str(key))
    
    def on_release(self,key):
        try:
            # print('release: {}'.format(key.char))
            self.keys.remove(key.char)
            if key.char in list("rpceuz"):
                r=String()
                r.data="?"+str(key.char)
                self.pub_n.publish(r)
        except AttributeError:
            # print('release: {}'.format(key))
            try:
                self.keys.remove(str(key))
            except:
                pass
        except KeyError:
            pass
        if( key == keyboard.Key.esc):
            print("StopKey")
            self.listener.stop()
            self.listener = None
            
    def start(self):
        self.listener = keyboard.Listener(on_press=self.on_press,on_release=self.on_release)
        self.listener.start()
        
    def getstatus(self):
        if(self.listener == None):
            return False       
        return True

def i():
    global send
    while True:
        send=input("cmd>>> /")

def main():
    rclpy.init()
    node=pineapple()
    ex=rclpy.executors.MultiThreadedExecutor()
    ex.add_node(node)
    ext=threading.Thread(target=ex.spin,daemon=True)
    it=threading.Thread(target=i,daemon=True)
    ext.start()
    it.start()
    try:
        while rclpy.ok():
            pass
    except:
        rclpy.shutdown()
    ext.join()
    it.join()