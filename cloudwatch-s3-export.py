import boto3
import math
import time
import re
from datetime import datetime, timedelta

client = boto3.client('logs')

def lambda_handler(event, context):
    group_name = []
    groupnames = []
    nDays = 1

    PreviousDate = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    deletionDate = datetime.now() - timedelta(days=nDays)
    startOfDay = deletionDate.replace(hour=0, minute=0, second=0, microsecond=0)
    endOfDay =  deletionDate.replace(hour=23, minute=59, second=59, microsecond=999999)
    print("Logs are getting exported from: ", startOfDay , " to the time ", endOfDay)

    response = client.describe_log_groups()  

    paginator = client.get_paginator('describe_log_groups')
    response_iterator = paginator.paginate()
    for response in response_iterator:
        listOfResponse=response["logGroups"]
        for result in listOfResponse:
            groupnames.append(result["logGroupName"])
            
    for groups in groupnames:
        if re.search('/search-keyword/.+', groups): 
            group_name.append(groups)
    print (group_name);        
    
    for x in group_name:
        print ("Now exporting the Group : {}".format(x))
        destPrefix = "s3bucket"+x.split('/cw-logs',1)[1]
        path = destPrefix+"/"+str(PreviousDate)
        response = client.create_export_task(
            taskName='export_task',
            logGroupName=x,
            fromTime=math.floor(startOfDay.timestamp() * 1000), 
            to=math.floor(endOfDay.timestamp() * 1000), 
            destination="",
            destinationPrefix=path
        )
        response = client.put_retention_policy(
            logGroupName=x,
            retentionInDays=30
        )
        time.sleep(15)