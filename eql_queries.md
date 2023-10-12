```
POST /winlogbeat-*/_eql/search
{
  "filter": {
    "range" : {
      "@timestamp" : {
        "gte" : "now-2w",
        "lte" :  "now"
      }
    }
  },
  "size": 50,
  "query": "<Your EQL Query Here>"
}
```

# [Basic Example Queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/eql-syntax.html#eql-how-functions-impact-search-performance)

```
sequence by agent.hostname with maxspan=30s 
  [process where process.parent.name == process.name]


sequence by agent.hostname with maxspan=30s 
  [any where network.type == "ipv4"]


sequence by agent.hostname with maxspan=30s 
  [any where process.name == "httpd.exe"]


sequence by agent.hostname with maxspan=30s 
  [file where file.extension == "txt"]
  [process where true]


sequence by agent.hostname with maxspan=30s 
  [network where file.extension == "exe"]
  [process where true]


sequence by agent.hostname with maxspan=30s 
  [authentication where event.outcome == 'failure']
  [process where true]


sequence by agent.hostname with maxspan=30s 
  [file where event.action == 'opened']
  [network where true]


sequence by agent.hostname with maxspan=30s 
  [process where event.action == 'start']
  [network where process.name == process.name]


sequence by agent.hostname with maxspan=30s 
  [file where event.action == 'creation']
  [file where event.action == 'modification']


sequence by agent.hostname with maxspan=30s 
  [process where process.parent.name == "explorer.exe"]


sequence by agent.hostname with maxspan=30s 
  [file where event.action == 'deletion']
  [process where process.name == 'empty_trash']


sequence by agent.hostname with maxspan=30s 
  [any where file.extension == "docx"]


sequence by agent.hostname with maxspan=30s 
  [authentication where event.outcome == 'failure']
  [authentication where event.outcome == 'failure']
  [user where event.action == 'user_created']


sequence by agent.hostname with maxspan=30s 
  [process where event.type == 'start']
  [network where process.name == process.name]


sequence by agent.hostname with maxspan=30s 
  [process where process.name == "suspicious.exe"]
  [file where event.action == 'deletion']


sequence by agent.hostname with maxspan=30s 
  [event where event.code == 1]
  [event where event.code == 2]


sequence by agent.hostname with maxspan=30s 
  [network where destination.ip == '192.168.1.1']
  [network where source.ip == '192.168.1.1']


sequence by agent.hostname with maxspan=30s 
  [file where event.type == 'creation']
  [file where event.type == 'modification']
  [file where event.type == 'deletion']


// Finds at least 3 failures and a success before returning a match
sequence by agent.hostname with maxspan=60s 
  [authentication where event.outcome == 'failure'] with runs=3
  [authentication where event.outcome == 'success']
  [ process where true ]
  [ process where event.code: (1, 3, 21)]



sequence by user.name
  [ process where event.type == "creation" ] by process.executable
  [ library where process.name == "regsvr32.exe" ] by dll.path with runs=3


sequence by agent.hostname with maxspan=30s 
  [network where destination.port == 22]
  [file where event.type == 'creation']


sequence by agent.hostname with maxspan=30s 
  [process where event.type == 'start']
  [network where event.type == 'connection']


sequence by agent.hostname with maxspan=30s 
  [file where event.action == 'file_write']
  [file where event.action == 'file_execute']


sequence by agent.hostname with maxspan=30s 
  [email where event.action == 'received']
  [browser where destination.domain == 'suspicious.com']


sequence by agent.hostname with maxspan=30s 
  [user where event.action == 'user_created']
  [authentication where event.outcome == 'failure'] until [authentication where event.outcome == 'success']


sequence by agent.hostname with maxspan=30s 
  [process where event.action == 'application_installed']
  [process where process.name == 'suspicious.exe']
```