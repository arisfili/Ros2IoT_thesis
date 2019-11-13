import rosservice
import rostopic
import rosnode
from rospy import client




if __name__ == '__main__':
    service_list = rosservice.get_service_list()
    list = client.get_published_topics('/')
    type = rostopic.get_topic_type('/rosout_agg')
    type = rosservice.get_service_type('/rosout/get_loggers')
    printvalue = True
    # question = "select the topics"
    # title = "bridge"
    # listofoptions = ["option1" , "option2"]
    # choise = easygui.multchoicebox(question,title,listofoptions)
    pass
