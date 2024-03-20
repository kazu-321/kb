from pynput import keyboard
import sys
import rclpy,threading
from rclpy.node import Node 
from std_msgs.msg import String
dir={"w":[0,1],"a":[-1,0],"s":[0,-1],"d":[1,0],"Key.up":[0,1],"Key.down":[0,-1],"Key.right":[1,0],"Key.left":[-1,0]}
a={"[0, 0]":0,"[0, 1]":0,"[1, 0]":90,"[-1, 0]":-90,"[1, 1]":45,"[-1, 1]":-45,"[1, -1]":135,"[-1, -1]":-135}
old=["",""]
send=""
d=[0,0]
arg=0

# バイナリデータを読み込む場合の一時ファイル用
from tempfile import NamedTemporaryFile

from pydub import AudioSegment
import simpleaudio

class SoundPlayer:
    """SoundPlayer module."""

    @classmethod
    def play(cls, filename, audio_format="mp3", wait=False, stop=False):
        """Play audio file."""

        if stop:
            simpleaudio.stop_all()

        seg = AudioSegment.from_file(filename, audio_format)
        playback = simpleaudio.play_buffer(
            seg.raw_data,
            num_channels=seg.channels,
            bytes_per_sample=seg.sample_width,
            sample_rate=seg.frame_rate
        )

        if wait:
            playback.wait_done()

    @classmethod
    def play_from_buffer(cls, audio_content, audio_format="mp3", wait=False, stop=False):
        """Play from buffer."""
        with NamedTemporaryFile() as fd:
            fd.write(audio_content)
            # Revert head of file. It is neccesary to play audio.
            fd.seek(0)
            cls.play(fd.name, audio_format=audio_format, wait=wait, stop=stop)


def arc():
    global d
    global arg
    if d==[0,-1]:
        if 0<int(old[1].split(" ")[1]):
            arg= 180
        else:
            arg= -180
    else:
        arg= a[str(d)]


class pineapple(Node):
    def __init__(self):
        super().__init__("key")
        self.pub=self.create_publisher(String,"cmd",10)
        self.timer = self.create_timer(0.1,self.call)
        self.cmd=String()
        self.keys=set()
        self.start()

    def call(self):
        global send
        global d
        global arg
        c=[0,0]
        speed=0
        trig=False
        for key in self.keys:
            if key in list("wad"):
                if not trig:
                    trig=True
                    d=[0,0]
                d[0]+=dir[key][0]
                d[1]+=dir[key][1]
            elif key[4:] in ["up","down","right","left"]:
                c[0]+=dir[key][0]
                c[1]+=dir[key][1]
            elif key=="f":
                speed+=100
            elif key=="b":
                speed-=100
        self.cmd.data="#C"+str(c[0]).replace("-1","-").replace("1","+")+str(c[1]).replace("-1","-").replace("1","+")
        if old[0]!=self.cmd.data:
            self.pub.publish(self.cmd)
            old[0]=self.cmd.data
        arc()
        self.cmd.data="/cd "+str(arg)+" "+str(speed)
        if old[1]!=self.cmd.data:
            self.pub.publish(self.cmd)
            old[1]=self.cmd.data
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
                self.pub.publish(r)
            try:
                SoundPlayer.play("/home/kazu/music/"+key.char+".mp3",stop=True)
            except:
                pass
            if key.char=="@":
                # SoundPlayer.play("/home/kazu/music/bekobeko/be.mp3")
                # SoundPlayer.play("/home/kazu/music/bekobeko/ko.mp3")
                # SoundPlayer.play("/home/kazu/music/bekobeko/be.mp3")
                # SoundPlayer.play("/home/kazu/music/bekobeko/ko.mp3")
                # SoundPlayer.play("/home/kazu/music/bekobeko/tin.mp3")
                # SoundPlayer.play("/home/kazu/music/bekobeko/tin.mp3")
                # SoundPlayer.play("/home/kazu/music/bekobeko/a.mp3")
                # SoundPlayer.play("/home/kazu/music/bekobeko/nko.mp3")
                SoundPlayer.play("/home/kazu/music/bekobeko.mp3")
        except AttributeError:
            # print('release: {}'.format(key))
            try:
                self.keys.remove(str(key))
            except:
                pass
            try:
                SoundPlayer.play("/home/kazu/music/"+str(key)+".mp3",stop=True)
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
    try:
        ext.join()
        it.join()
    except:
        pass