#!/bin/bash

# declare the array of topics
topicol=("project.created" "components.create" "environment.development.create" "environment.production.create" "environment.technologies.create" "infrastructure.provision" "orchestration.being")

# print each topic 
echo "will now print each topic..."
printf "\n"
for i in "${topicol[@]}"
do
        echo "currently working on topic $i"
        /opt/kafka/bin/kafka-topics.sh --create \
        --topic "$i" \
        --bootstrap-server broker:29092 \
        --if-not-exists \
        --partitions 3 \
        --replication-factor 1

    if [ $? -eq 0 ]; then
        echo "topic $i created successfully"
    else
        echo "topic $i failed to create"
    fi

done


echo "done creating topics"

