from pynput import keyboard
import sys
import rclpy
from rclpy.node import Node 
from std_msgs.msg import String
dir={"w":0,"a":-90,"s":180,"d":90}

class pineapple(Node):
    def __init__(self):
        super().__init__("key")
        self.pub=self.create_publisher(String,"to_pc_cmd",0)
        self.pub_n=self.create_publisher(String,"to_nucleo_cmd",0)
        self.timer = self.create_timer(0.01,self.call)
        self.cmd=String()
        self.keys=set()

    def call(self):
        d=0
        i=0
        for key in self.keys:
            if key in ["w","a","s","d"]:
                d+=dir[key]
                i+=1
        if i!=0:
            d//=i
        self.cmd.data="/cd "+str(d)
        self.pub.publish(self.cmd)
    
    def on_press(self,key):
        try:
            print('press: {}'.format(key.char))
            self.keys.add(key.char)
        except AttributeError:
            print('spkey press: {}'.format(key))
    
    def on_release(self,key):
        try:
            print('release: {}'.format(key.char))
            self.keys.remove(key.char)
            if key.char=="r":
                r=String()
                r.data="/r"
                self.pub_n.publish(r)
        except AttributeError:
            print('release: {}'.format(key))
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