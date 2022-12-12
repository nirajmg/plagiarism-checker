# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START functions_cloudevent_storage]
import functions_framework
from google.cloud import pubsub_v1
import os 

# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def process_trigger(cloud_event):
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]

    print(f"Event ID: {event_id}")
    print(f"Event type: {event_type}")
    print(f"Bucket: {bucket}")
    print(f"File: {name}")
    print(f"Metageneration: {metageneration}")
    print(f"Created: {timeCreated}")
    print(f"Updated: {updated}")
    publisher = pubsub_v1.PublisherClient()
    try:
        reports_topic = "plagiarism-reports"
        raw_topic = "plagiarism-raw"

        if "files" in name: 
            raw_topic = f'projects/plagiarism-368919/topics/{raw_topic}'
            print(f'Publishing to raw queue {raw_topic}')
            topic_name = raw_topic.format(
                project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
                topic=raw_topic,
            )
        elif "raw" in name: 
            
            reports_queue = f'projects/plagiarism-368919/topics/{reports_topic}'
            print(f'Publishing to reports queue {reports_queue}')
            topic_name = reports_queue.format(
                project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
                topic=reports_topic,
            )
        else: 
            print("Skipping file")
            return 
        publisher.publish(topic_name, bytes(name, 'utf-8'), fileName=name)
        print("published")
    except  Exception as e:
        print("Failed to publish", e )

