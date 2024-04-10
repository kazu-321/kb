from pynput import keyboard # type: ignore
import sys
import rclpy,threading # type: ignore
from rclpy.node import Node # type: ignore
from std_msgs.msg import String # type: ignore
from geometry_msgs.msg import Twist  # type: ignore

send=""

class kbinput(Node):
    def __init__(self):
        super().__init__("key")
        self.cmdpub=self.create_publisher(String,"cmd",10)
        self.velpub=self.create_publisher(Twist,"cmd_vel",10)
        self.timer = self.create_timer(0.01,self.call)
        self.cmd=String()
        self.vel=Twist()
        self.keys=set()
        self.start()

    def call(self):
        global send
        self.vel.linear.x=0.0
        self.vel.linear.y=0.0
        for key in self.keys:
            if key=="w":
                self.vel.linear.x+=1.0
            elif key=="a":
                self.vel.linear.y+=1.0
            elif key=="s":
                self.vel.linear.x-=1.0
            elif key=="d":
                self.vel.linear.y-=1.0
        self.velpub.publish(self.vel)

        if send!="":
            self.cmd.data=send
            send=""
            self.cmdpub.publish(self.cmd)
    
    def on_press(self,key):
        try:
            if key.char in list("wasd"):
                self.keys.add(key.char)
        except:
            pass

    def on_release(self,key):
        try:
            if key.char in list("wasd"):
                self.keys.remove(key.char)
        except:
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
    node=kbinput()
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
    try:
        ext.join()
        it.join()
    except:
        pass