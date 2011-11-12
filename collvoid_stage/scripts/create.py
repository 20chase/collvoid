#!/usr/bin/env python

import math
import sys
import getopt
import commands

def create_world_file(argv):
    numRobots = 0
    circleSize = 0
    centerX = -2.2
    centerY = 2
    omni = False
    localization = True
    simulation = True
    runExperiments = False
    scaleRadius = False
    useNoise = False
    useBagFile = False
    bagFileName = "collvoid.bag"
    try:
        opts, args= getopt.getopt(argv, "hn:s:Rolxf:N", ["help","numRobots=","circleSize=","radiusScaling","omni","localization","experiments","bagFileName=","noise"])
    except getopt.GetoptError:
        print 'create.py -n <numRobots> -s <circleSize> <-h> <-l> <-x> <-f> bagFile <-R>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'create.py -n <numRobots> -s <circleSize> <-h> <-l> <-x><-f> bagfile <-R>'
            sys.exit(2)
        elif opt in ("-n","--numRobots"):
            numRobots = int(arg)
        elif opt in ("-s","--circleSize"):
            circleSize = float(arg)
        elif opt in ("-o","--omni"):
            omni = True
        elif opt in ("-l","--localization"):
            localization = False
        elif opt in ("-x", "--experiments"):
            runExperiments = True
        elif opt in ("-f", "--bagFileName"):
            useBagFile = True
            bagFileName = str(arg)
        elif opt in ("-R", "--radiusScaling"):
            scaleRadius = True
        elif opt in ("-N"):
            useNoise = True
    
    direct = commands.getoutput('rospack find collvoid_stage')
    worldFileTemp = open(direct + '/world/swarmlab_template.world','r')
    worldFileNew = open(direct + '/world/swarmlab_created.world','w')
    worldFileNew.write(worldFileTemp.read())
    direct = commands.getoutput('rospack find stage')

    colors = open(direct + '/share/stage/rgb.txt','r')
    line = colors.readline()
    line = colors.readline()
    cols = []
    while line:
        cols.append(line[line.rfind("\t")+1:line.rfind("\n")])
        line = colors.readline()
    colors.close()
    #print cols
    for x in range(numRobots):
        angle = 360.0 / numRobots
        anglePrint = x * angle-180-45
        angle = x * angle - 45
        posX = circleSize*math.cos(angle/360*2*math.pi)
        
        posY = circleSize*math.sin(angle/360*2*math.pi)
        if (omni):
           worldFileNew.write('pr2( pose [ {0:f} {1:f} 0 {2:f} ] name "robot_{3:d}" color "{4}")\n'.format(centerX+posX,centerY+posY,anglePrint,x,cols[40 +  10 * x]))
        else:
            worldFileNew.write('roomba( pose [ {0:f} {1:f} 0 {2:f} ] name "robot_{3:d}" color "{4}")\n'.format(centerX+posX,centerY+posY,anglePrint,x,cols[40 +  10 * x]))

    
    #tele_robot( pose [ -1 0 0 180.000 ] name "bob" color "blue")
    worldFileTemp.close()
    worldFileNew.close()
    create_yaml_file(circleSize,numRobots,omni,simulation,localization,centerX,centerY,scaleRadius,useNoise)
    create_launch_file(numRobots,omni,runExperiments,bagFileName,localization,useBagFile)
    
    
def create_yaml_file(circleSize, numRobots,omni,simulation,localization,centerX,centerY,scaleRadius,useNoise):
    direct = commands.getoutput('rospack find collvoid_stage')
    yamlWrite = open(direct + '/params_created.yaml','w')
    yamlWrite.write("/use_sim_time: true\n")
    yamlWrite.write("/simulation_mode: true\n")
    if not localization:
        yamlWrite.write('/use_ground_truth: true\n')
    else:
        yamlWrite.write('/use_ground_truth: false\n')
    if (scaleRadius):
       yamlWrite.write('/scale_radius: true\n')
    else:
       yamlWrite.write('/scale_radius: false\n')
    if not useNoise:
        yamlWrite.write("/init_guess_noise_std: 0.0\n")
    else:
        yamlWrite.write("/init_guess_noise_std: 0.20\n")
  
    yamlWrite.write('/num_robots: ' + str(numRobots) + '\n')
    
    angle = 360.0 / numRobots
    for x in range(numRobots):
        angleX = 90 + x * angle - 45
        posX = circleSize*math.cos(angleX/360*2*math.pi)
        posY = circleSize*math.sin(angleX/360*2*math.pi)
  
        yamlWrite.write('robot_{0}:\n'.format(x))
        yamlWrite.write('    goals:\n')
        yamlWrite.write('        x: [{0:f}]\n'.format(centerX-posY))
        yamlWrite.write('        y: [{0:f}]\n'.format(centerY+posX))
        yamlWrite.write('        ang: [{0:f}]\n'.format((angleX+90) / 360.0 * 2 * math.pi))
    
    yamlWrite.close()
    
def create_launch_file(numRobots,omni,runExperiments, bagFilename, localization,useBagFile):
    direct = commands.getoutput('rospack find collvoid_stage')

    launchWrite = open(direct + '/launch/sim_created.launch','w')
    launchWrite.write("<launch>\n")
    launchWrite.write('  <node name="map_server" pkg="map_server" type="map_server" args="$(find collvoid_stage)/world/swarmlab_map.yaml"/>\n')
    launchWrite.write('  <rosparam command="load" file="$(find collvoid_stage)/params_created.yaml"/>\n')
   # if (runExperiments):
   #     launchWrite.write('<node pkg="collvoid_controller" type="watchdog.py" name="watchdog" output="screen"/>\n')
   # else:
   #     launchWrite.write('<node pkg="collvoid_controller" type="controller.py" name="controller" output="screen"/>\n')
    launchWrite.write('  <node pkg="stage" type="stageros" name="stageros" args="$(find collvoid_stage)/world/swarmlab_created.world" respawn="false" output="screen" />\n')
    for x in range(numRobots):
        #if localization: # TODO: use "not localizationx" amcl is still used in orca_planner
        if (omni):
            launchWrite.write('  <include file="$(find collvoid_stage)/launch/amcl_omni_multi.launch">\n')
        else:
            launchWrite.write('  <include file="$(find collvoid_stage)/launch/amcl_diff_multi.launch">\n')
        launchWrite.write('    <arg name="robot" value="robot_{0}"/>\n'.format(x))
        launchWrite.write('  </include>\n')
        
        launchWrite.write('  <node pkg="move_base" type="move_base" respawn="false" name="move_base" ns="robot_{0}" output="screen">\n'.format(x))
        if (omni):
            launchWrite.write('    <rosparam command="load" file="$(find collvoid_stage)/params/params_pr2.yaml" />\n')
        else:
            launchWrite.write('    <rosparam command="load" file="$(find collvoid_stage)/params/params_turtle.yaml" />\n')
        launchWrite.write('    <remap from="map" to="/map" />\n')
        launchWrite.write('    <param name="~tf_prefix" value="robot_{0}" />\n'.format(x))
        launchWrite.write('    <param name="~/global_costmap/robot_base_frame" value="robot_{0}/base_link" /> \n    <param name="~/local_costmap/robot_base_frame" value="robot_{1}/base_link" /> \n    <param name="~/local_costmap/global_frame" value="robot_{0}/odom" /> \n'.format(x,x,x))
        launchWrite.write('    <param name="base_local_planner" value="collvoid_local_planner/CollvoidLocalPlanner" />\n')
        launchWrite.write('    <param name="base_global_planner" value="collvoid_simple_global_planner/CollvoidSimpleGlobalPlanner" />\n')

        launchWrite.write('  </node> \n')
        launchWrite.write('  <node pkg="collvoid_controller" type="controllerRobots.py" name="controllerRobots" ns="robot_{0}" output="screen" />\n'.format(x))
    launchWrite.write('  <node pkg="collvoid_controller" type="controller.py" name="controller" output="screen" />\n')
  
    s = ""

#    for x in range(numRobots):
#        s += "/robot_%d/debug "%(x)
    if useBagFile:
        launchWrite.write('  <node pkg="rosbag" type="record" name="rosbag" args="record {0} /stall /stall_resolved /exceeded -O $(find collvoid_stage)/{1}" output="screen"/>\n'.format(s,bagFilename))
    
    launchWrite.write('  <node pkg="rviz" type="rviz" name="rviz" args="-d $(find collvoid_stage)/double_view.vcg" output="screen" />\n')
    launchWrite.write("</launch>\n")
    launchWrite.close()

    
if __name__ == "__main__":
    create_world_file(sys.argv[1:])

