from pynput import keyboard # type: ignore
import sys
import rclpy,threading # type: ignore
from rclpy.node import Node # type: ignore
from std_msgs.msg import String # type: ignore
from geometry_msgs.msg import Twist  # type: ignore
kb1=list("wasdWASD")
kb2=["up","down","right","left","shift"]
kb3=list("cpznt")
kb4=list("8462")
send=[]
unko=2

class kbinput(Node):
    def __init__(self):
        super().__init__("key")
        self.cmdpub=self.create_publisher(String,"cmd",10)
        self.velpub=self.create_publisher(Twist,"cmd_vel",10)
        self.nav=self.create_subscription(Twist,"cmd_vel_nav",self.nav,10)
        self.timer = self.create_timer(0.01,self.call)
        self.checker=self.create_timer(2,self.check)
        self.cmd=String()
        self.vel=Twist()
        self.vel_nav=Twist()
        self.keys=set()
        self.alive=False
        self.start()

    def nav(self,msg):
        self.vel_nav=msg

    def check(self):
        if not self.alive:
            datas=self.get_subscriptions_info_by_topic("cmd")
            if "_CREATED_BY_BARE_DDS_APP_" in [data._node_name for data in datas]:
                print("find!!")
                self.alive=True
            else:
                print("not connected...")

    def call(self):
        global send
        global unko
        self.vel.linear.x=0.0
        self.vel.linear.y=0.0
        self.vel.angular.z=0.0
        for key in self.keys:
            if key=="w":
                self.vel.linear.x+=1.0
            elif key=="a":
                self.vel.linear.y+=1.0
            elif key=="s":
                self.vel.linear.x-=1.0
            elif key=="d":
                self.vel.linear.y-=1.0
            elif key=="right":
                self.vel.angular.z-=1.0
            elif key=="left":
                self.vel.angular.z+=1.0
        
        self.vel.linear.x-=self.vel_nav.linear.x*1.5
        self.vel.linear.y+=self.vel_nav.linear.y*1.5
        self.vel.angular.z+=self.vel_nav.angular.z*1.5

        self.velpub.publish(self.vel)

        while len(send)!=0:
            self.cmd.data=send[-1]
            send.pop(-1)
            self.cmdpub.publish(self.cmd)
    
    def on_press(self,key):
        global send
        try:
            if key.char in kb1:
                self.keys.add(key.char.lower())
        except AttributeError:
            if str(key)[4:] in kb2:
                self.keys.add(str(key)[4:])
                if str(key)[4:]=="shift":
                    send.append("unko 1.25")
                elif str(key)[4:]=="shift_r":
                    send.append("unko 3")
        except:
            pass

    def on_release(self,key):
        global send
        try:
            # print(key.char)
            if key.char in kb1:
                self.keys.remove(key.char.lower())
            elif key.char in kb3:
                send.append(key.char)
            elif key.char in kb4:
                if key.char=="8":
                    send.append("g 0")
                elif key.char=="4":
                    send.append("g -90")
                elif key.char=="6":
                    send.append("g 90")
                elif key.char=="2":
                    send.append("g 180")
                elif key.char=="*":
                    send.append("r")
        except AttributeError:
            # print(str(key)[4:])
            if str(key)[4:] in kb2:
                self.keys.remove(str(key)[4:])
                if str(key)[4:] in ["shift","shift_r"]:
                    send.append("unko 2")
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
        send.append(input("cmd>>> /"))


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

if __name__=="__main__":
    main()
