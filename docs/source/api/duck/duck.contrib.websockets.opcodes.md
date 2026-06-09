# {py:mod}`duck.contrib.websockets.opcodes`

```{py:module} duck.contrib.websockets.opcodes
```

```{autodocx-docstring} duck.contrib.websockets.opcodes
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CloseCode <duck.contrib.websockets.opcodes.CloseCode>`
  - ```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode
    :summary:
    ```
* - {py:obj}`OpCode <duck.contrib.websockets.opcodes.OpCode>`
  - ```{autodocx-docstring} duck.contrib.websockets.opcodes.OpCode
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CONTROL_OPCODES <duck.contrib.websockets.opcodes.CONTROL_OPCODES>`
  - ```{autodocx-docstring} duck.contrib.websockets.opcodes.CONTROL_OPCODES
    :summary:
    ```
* - {py:obj}`DATA_OPCODES <duck.contrib.websockets.opcodes.DATA_OPCODES>`
  - ```{autodocx-docstring} duck.contrib.websockets.opcodes.DATA_OPCODES
    :summary:
    ```
````

### API

````{py:data} CONTROL_OPCODES
:canonical: duck.contrib.websockets.opcodes.CONTROL_OPCODES
:value: >
   ()

```{autodocx-docstring} duck.contrib.websockets.opcodes.CONTROL_OPCODES
```

````

`````{py:class} CloseCode()
:canonical: duck.contrib.websockets.opcodes.CloseCode

Bases: {py:obj}`enum.IntEnum`

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.__init__
```

````{py:attribute} ABNORMAL_CLOSURE
:canonical: duck.contrib.websockets.opcodes.CloseCode.ABNORMAL_CLOSURE
:value: >
   1006

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.ABNORMAL_CLOSURE
```

````

````{py:attribute} BAD_GATEWAY
:canonical: duck.contrib.websockets.opcodes.CloseCode.BAD_GATEWAY
:value: >
   1014

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.BAD_GATEWAY
```

````

````{py:attribute} GOING_AWAY
:canonical: duck.contrib.websockets.opcodes.CloseCode.GOING_AWAY
:value: >
   1001

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.GOING_AWAY
```

````

````{py:attribute} INTERNAL_ERROR
:canonical: duck.contrib.websockets.opcodes.CloseCode.INTERNAL_ERROR
:value: >
   1011

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.INTERNAL_ERROR
```

````

````{py:attribute} INVALID_DATA
:canonical: duck.contrib.websockets.opcodes.CloseCode.INVALID_DATA
:value: >
   1007

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.INVALID_DATA
```

````

````{py:attribute} MANDATORY_EXTENSION
:canonical: duck.contrib.websockets.opcodes.CloseCode.MANDATORY_EXTENSION
:value: >
   1010

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.MANDATORY_EXTENSION
```

````

````{py:attribute} MESSAGE_TOO_BIG
:canonical: duck.contrib.websockets.opcodes.CloseCode.MESSAGE_TOO_BIG
:value: >
   1009

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.MESSAGE_TOO_BIG
```

````

````{py:attribute} NORMAL_CLOSURE
:canonical: duck.contrib.websockets.opcodes.CloseCode.NORMAL_CLOSURE
:value: >
   1000

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.NORMAL_CLOSURE
```

````

````{py:attribute} NO_STATUS_RCVD
:canonical: duck.contrib.websockets.opcodes.CloseCode.NO_STATUS_RCVD
:value: >
   1005

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.NO_STATUS_RCVD
```

````

````{py:attribute} POLICY_VIOLATION
:canonical: duck.contrib.websockets.opcodes.CloseCode.POLICY_VIOLATION
:value: >
   1008

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.POLICY_VIOLATION
```

````

````{py:attribute} PROTOCOL_ERROR
:canonical: duck.contrib.websockets.opcodes.CloseCode.PROTOCOL_ERROR
:value: >
   1002

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.PROTOCOL_ERROR
```

````

````{py:attribute} SERVICE_RESTART
:canonical: duck.contrib.websockets.opcodes.CloseCode.SERVICE_RESTART
:value: >
   1012

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.SERVICE_RESTART
```

````

````{py:attribute} TLS_HANDSHAKE
:canonical: duck.contrib.websockets.opcodes.CloseCode.TLS_HANDSHAKE
:value: >
   1015

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.TLS_HANDSHAKE
```

````

````{py:attribute} TRY_AGAIN_LATER
:canonical: duck.contrib.websockets.opcodes.CloseCode.TRY_AGAIN_LATER
:value: >
   1013

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.TRY_AGAIN_LATER
```

````

````{py:attribute} UNSUPPORTED_DATA
:canonical: duck.contrib.websockets.opcodes.CloseCode.UNSUPPORTED_DATA
:value: >
   1003

```{autodocx-docstring} duck.contrib.websockets.opcodes.CloseCode.UNSUPPORTED_DATA
```

````

`````

````{py:data} DATA_OPCODES
:canonical: duck.contrib.websockets.opcodes.DATA_OPCODES
:value: >
   ()

```{autodocx-docstring} duck.contrib.websockets.opcodes.DATA_OPCODES
```

````

`````{py:class} OpCode()
:canonical: duck.contrib.websockets.opcodes.OpCode

Bases: {py:obj}`enum.IntEnum`

```{autodocx-docstring} duck.contrib.websockets.opcodes.OpCode
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.websockets.opcodes.OpCode.__init__
```

````{py:attribute} BINARY
:canonical: duck.contrib.websockets.opcodes.OpCode.BINARY
:value: >
   2

```{autodocx-docstring} duck.contrib.websockets.opcodes.OpCode.BINARY
```

````

````{py:attribute} CLOSE
:canonical: duck.contrib.websockets.opcodes.OpCode.CLOSE
:value: >
   8

```{autodocx-docstring} duck.contrib.websockets.opcodes.OpCode.CLOSE
```

````

````{py:attribute} CONTINUATION
:canonical: duck.contrib.websockets.opcodes.OpCode.CONTINUATION
:value: >
   0

```{autodocx-docstring} duck.contrib.websockets.opcodes.OpCode.CONTINUATION
```

````

````{py:attribute} PING
:canonical: duck.contrib.websockets.opcodes.OpCode.PING
:value: >
   9

```{autodocx-docstring} duck.contrib.websockets.opcodes.OpCode.PING
```

````

````{py:attribute} PONG
:canonical: duck.contrib.websockets.opcodes.OpCode.PONG
:value: >
   10

```{autodocx-docstring} duck.contrib.websockets.opcodes.OpCode.PONG
```

````

````{py:attribute} TEXT
:canonical: duck.contrib.websockets.opcodes.OpCode.TEXT
:value: >
   1

```{autodocx-docstring} duck.contrib.websockets.opcodes.OpCode.TEXT
```

````

`````
