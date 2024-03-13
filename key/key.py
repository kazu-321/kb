from pynput import keyboard
import sys
import rclpy
from rclpy.node import Node 
from std_msgs.msg import String
dir={"w":0,"a":-90,"s":180,"d":90,"Key.up":[0,1],"Key.down":[0,-1],"Key.right":[1,0],"Key.left":[-1,0]}
old=["",""]

class pineapple(Node):
    def __init__(self):
        super().__init__("key")
        self.pub=self.create_publisher(String,"cmd",10)
        self.pub_n=self.create_publisher(String,"nucleo_cmd",10)
        self.timer = self.create_timer(0.1,self.call)
        self.cmd=String()
        self.keys=set()

    def call(self):
        d=0
        i=0
        c=[0,0]
        for key in self.keys:
            if key in list("wasd"):
                d+=dir[key]
                i+=1
            elif key[4:] in ["up","down","right","left"]:
                c[0]+=dir[key][0]
                c[1]+=dir[key][1]
        if i!=0:
            d//=i
        self.cmd.data="#C"+str(c[0]).replace("-1","-").replace("1","+")+str(c[1]).replace("-1","-").replace("1","+")
        if old[0]!=self.cmd.data:
            self.pub.publish(self.cmd)
            old[0]=self.cmd.data
        self.cmd.data="/cd "+str(d)
        if old[1]!=self.cmd.data:
            self.pub.publish(self.cmd)
            old[1]=self.cmd.data

    
    def on_press(self,key):
        try:
            print('press: {}'.format(key.char))
            self.keys.add(key.char)
        except AttributeError:
            print('spkey press: {}'.format(key))
            self.keys.add(str(key))
    
    def on_release(self,key):
        try:
            print('release: {}'.format(key.char))
            self.keys.remove(key.char)
            if key.char in list("rpceuz"):
                r=String()
                r.data="?"+str(key.char)
                self.pub_n.publish(r)
        except AttributeError:
            print('release: {}'.format(key))
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

def main():
    rclpy.init()
    node=pineapple()
    node.start()
    rclpy.spin(node)
    while(True):
        status = node.getstatus()
        #print(str(status))
        if(status == False):
            print("break")
            break
    rclpy.shutdown()