import subprocess

subprocess.call(["docker","build","-t", "filebeat:17.6.0", "/appcode/spiderdoc/BT/containers/Filebeat/."])

#run filebeat image
subprocess.Popen(["docker", "run","-v","/containers/output:/var/log/trades/", "filebeat:17.6.0"])