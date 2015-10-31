# EEGSTREAM

Structure settings format:
```
{'packet': {'format': format, 'datalink_type': datalink_type}, 'datalink': {'file': file}}
```
where:
- `format` describes single packet in format useful for `struct.pack` call (ex.: `'dddd'` four channels in double format each)
- `datalink_type` describes data link type (ex.: `'pipe'`)
- `file` optional parameter for pipes only, describes fifo file name (ex.: `'/tmp/fifo'`)
