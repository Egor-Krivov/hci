# EEGSTREAM

Structure settings format:
```
settings = {'packet': {'fmt': fmt, 'mask': mask}, 'datalink': {'type': type, 'file': file}}
```
where:
- `fmt` describes single packet in format useful for `struct.pack` call (ex.: `'dddd'` four channels in double format each)
- `mask` describes in binary format channels to transmit via datalink (ex.: `0010` transmit only third channel)
- `type` describes data link type (ex.: `'pipe'`)
- `file` optional parameter for pipes only, describes fifo file name (ex.: `'/tmp/fifo'`)
