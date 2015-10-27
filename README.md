# eegstream
structude setting format
{
'packet': {'fmt': 'iidd' Format for struct.pack call, describes data in tuplets
  }
'data_link': [
  for pipe: 
    {'pname': 'filename.fifo' File to store pipe
    }
  ]
}
