
#!/bin/bash

while read line
do 
	echo "----------------download: ${line}-------------------"
	curl -o `echo $line | awk -F '/' '{print $5}'` $line 
	[[ $? -eq 0 ]] && echo "----------------success------------------"
done < a.txt



