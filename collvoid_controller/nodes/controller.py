#!/usr/bin/env python
import roslib; roslib.load_manifest('collvoid_controller')
import rospy
import commands
import string
try:
    import wx
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"

from std_msgs.msg import String
from geometry_msgs.msg import PoseWithCovarianceStamped,PoseStamped
from std_srvs.srv import Empty
from collvoid_msgs.msg import PoseTwistWithCovariance

import tf

class controller(wx.Frame):

    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,id,title)
        self.parent = parent
        self.initialize()
        
    def initialize(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)


        self.subCommonPositions = rospy.Subscriber("/position_share", PoseTwistWithCovariance, self.cbCommonPositions)
        self.pub = rospy.Publisher('/commands_robot', String)

        self.robotList = []
        self.robotList.append("all")

        self.reset_srv = rospy.ServiceProxy('/stageros/reset', Empty)

        static_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Controls"), wx.HORIZONTAL)
        sizer.Add(static_sizer, 0)
         
        start = wx.Button(self,-1,label="Start!")
        static_sizer.Add(start, 0)
        self.Bind(wx.EVT_BUTTON, self.start, start)
        
        stop = wx.Button(self,-1,label="Stop!")
        static_sizer.Add(stop, 0)
        self.Bind(wx.EVT_BUTTON, self.stop, stop)

        reset = wx.Button(self,-1,label="Reset!")
        static_sizer.Add(reset, 0)
        self.Bind(wx.EVT_BUTTON, self.reset, reset)


        grid_sizer = wx.GridBagSizer()
        static_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "New Goals"), wx.HORIZONTAL)
        static_sizer.Add(grid_sizer, 0)
        sizer.Add(static_sizer, 0)
 
        self.choiceBox = wx.Choice(self,-1,choices=self.robotList)

        grid_sizer.Add(self.choiceBox,(0,0),(1,2),wx.EXPAND)
        self.SetPosition(wx.Point(200,200))
        self.SetSize(wx.Size(600,200))
        
      
        sendInitGuess = wx.Button(self,-1,label="Send init Guess")
        grid_sizer.Add(sendInitGuess, (5,0))
        self.Bind(wx.EVT_BUTTON, self.sendInitGuess, sendInitGuess)

        sendNextGoal = wx.Button(self,-1,label="Send next Goal")
        grid_sizer.Add(sendNextGoal, (5,1))
        self.Bind(wx.EVT_BUTTON, self.sendNextGoal, sendNextGoal)

        
        grid_sizer.AddGrowableCol(0)
        self.SetSizer(sizer)

        self.Layout()
        self.Fit()
        self.Show(True)

               
    def cbCommonPositions(self,msg):
        if self.robotList.count(msg.robot_id) == 0:
            rospy.loginfo("robot added")
            self.robotList.append(msg.robot_id)
            self.choiceBox.Append(msg.robot_id)

    def sendNextGoal(self,event):
        string = "%s next Goal"%self.choiceBox.GetStringSelection()
        self.pub.publish(str(string))

    def sendInitGuess(self,event):
        string = "%s init Guess"%self.choiceBox.GetStringSelection()
        self.pub.publish(str(string))

    def stop(self,event):
        string = "%s Stop"%self.choiceBox.GetStringSelection()
        self.pub.publish(str(string))

    def start(self,event):
        string = "%s next Goal"%self.choiceBox.GetStringSelection()
        self.pub.publish(str(string))

    def reset(self,event):
        self.pub.publish("all Stop")
        rospy.sleep(0.2)
        self.pub.publish("all Restart")
        #rospy.sleep(0.2)
        self.reset_srv()
            
    
if __name__ == '__main__':
    rospy.init_node('controller')
    app = wx.App()
    frame = controller(None,-1,'Controller')

    app.MainLoop()
