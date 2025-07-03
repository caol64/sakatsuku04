# PINE：仿真器检测协议

**摘要：** 本标准介绍了 PINE (Protocol for Instrumentation of Emulators)，一个旨在用于视频游戏仿真器之间的进程间通信协议。

-----

## 1\. 引言

本标准描述了 PINE 协议（仿真器检测协议）。

该协议是为视频游戏仿真器开发的，旨在为所有仿真器提供一个一致的接口，主要有四个设计目标：

1.  **速度**
2.  **简洁性**
3.  **鲁棒性**
4.  **向后兼容性**

-----

## 2\. 通信机制

PINE 作为一种协议，需要一种与目标仿真器通信的方式。这种实现是系统特定的，目前仅对 **Linux**、**macOS** 和 **Windows** 进行了标准化。未标准化的系统仍然可以实现 PINE 协议；它们的基本要求是有一个可以打开同时连接的有效 IPC 进程。虽然没有强制规定最小值，但一个能够实现 10 个同时通信的系统将非常适合此用途。

每个 PINE 目标都必须有一个定义的 **槽 (slot)** 和 **目标名称 (target name)**。

### 2.1. 槽

PINE 实现了槽的概念以允许同时连接。它们大致可以被认为是 **TCP 端口**。它们可以设置为 0 到 65536 之间的任何数字（包括 0 和 65536）。PINE 目标有一个默认槽，以允许即插即用 (PnP)，其范围必须在 **28000-30000** 之间。这些数字必须可以手动覆盖，以允许同一软件的多个实例并发工作。

### 2.2. 目标名称

每个 PINE 目标都必须有一个设定的目标名称。这个目标名称用于区分不同的目标。例如，一个目标名称可以是 "pcsx2"。

### 2.3. 系统特定实现

#### 2.3.1. Linux

Linux 使用 **Unix 套接字**（域类型为 `SOCK_STREAM`）进行通信。
Linux 遵循 XDG 基本目录规范，因此将使用环境变量 `XDG_RUNTIME_DIR` 作为存储 Unix 套接字的文件夹。如果此变量未设置，则默认为 `/tmp`。

  * 如果使用默认槽，套接字将按以下格式命名：
      * `'目标名称 + ".sock"'`。
  * 如果指定了槽，则使用以下格式：
      * `'目标名称 + ".sock." + 槽'`。

**示例：**

  * `/run/user/1000/pcsx2.sock`: 默认槽，`XDG_RUNTIME_DIR` 已设置
  * `/tmp/pcsx2.sock.123`: 槽 123，`XDG_RUNTIME_DIR` 未设置

#### 2.3.2. MacOS

macOS 使用 **Unix 套接字**（域类型为 `SOCK_STREAM`）进行通信。
macOS 将使用环境变量 `TMPDIR` 作为存储 Unix 套接字的文件夹。如果此变量未设置，则默认为 `/tmp`。

  * 如果使用默认槽，套接字将按以下格式命名：
      * `'目标名称 + ".sock"'`。
  * 如果指定了槽，则使用以下格式：
      * `'目标名称 + ".sock." + 槽'`。

**示例：**

  * `/hello/pcsx2.sock`: 默认槽，`TMPDIR` 设置为 `hello`
  * `/tmp/pcsx2.sock.123`: 槽 123，`TMPDIR` 未设置

#### 2.3.3. Windows

Windows 使用 **TCP 套接字**进行通信。
槽用作 TCP 端口，仅监听 **localhost**。

-----

## 3\. 协议规范

PINE 是一个**无状态的二进制序列化消息协议**。
客户端（程序）发送的每个请求都将始终收到服务器（仿真器）的回复。服务器也可以发起请求（TODO: 事件），尽管它不期望任何应答。

定义了三种类型的消息：

1.  **请求**
2.  **应答**
3.  **事件**

另外，请求和应答也可以组合成**批处理命令**，以尽可能避免往返延迟。

所有 IPC 消息都以一个 `uint32_t` 类型的值开头，该值表示消息的大小，包括此字段本身。

### 3.1. 请求消息

请求消息以一个 `uint8_t` **操作码 (opcode)** 开头，后跟根据操作定义的不同参数。

**请求消息示例：**

```
+-----------+--+-----------+
|09 00 00 00|00|34 7d 34 00|
+-----------+--+-----------+
  |           |     |
  |           |     argument
  |           opcode
  message size
```

在这个例子中，这是一个操作码为 `0` 的消息（`MsgRead8`），其参数为 `0x00347D34`（它想要读取的地址）。

操作码（Operation codes）是 `uint8_t` 类型，定义了服务器必须执行的操作。其中一些具有特殊含义：

  * `FF`: 未实现
  * `F0-FE` (包含): 保留给多操作码命令
  * `D0-EF` (包含): 保留给目标特定操作

下面列出了所有标准化的请求消息及其参数和操作码：

  * **MsgRead8**
      * 读取内存位置 `mem` 的 8 字节值。
      * `opcode = 0`
      * `argument = [ uint32_t mem ];`
  * **MsgRead16**
      * 读取内存位置 `mem` 的 16 字节值。
      * `opcode = 1`
      * `argument = [ uint32_t mem ];`
  * **MsgRead32**
      * 读取内存位置 `mem` 的 32 字节值。
      * `opcode = 2`
      * `argument = [ uint32_t mem ];`
  * **MsgRead64**
      * 读取内存位置 `mem` 的 64 字节值。
      * `opcode = 3`
      * `argument = [ uint32_t mem ];`
  * **MsgWrite8**
      * 将 8 字节值 `val` 写入内存位置 `mem`。
      * `opcode = 4`
      * `argument = [ uint32_t mem, uint8_t val ];`
  * **MsgWrite16**
      * 将 16 字节值 `val` 写入内存位置 `mem`。
      * `opcode = 5`
      * `argument = [ uint32_t mem, uint16_t val ];`
  * **MsgWrite32**
      * 将 32 字节值 `val` 写入内存位置 `mem`。
      * `opcode = 6`
      * `argument = [ uint32_t mem, uint32_t val ];`
  * **MsgWrite64**
      * 将 64 字节值 `val` 写入内存位置 `mem`。
      * `opcode = 7`
      * `argument = [ uint32_t mem, uint64_t val ];`
  * **MsgVersion**
      * 获取目标的版本。
      * `opcode = 8`
      * `argument = [ ];`
  * **MsgSaveState**
      * 请求仿真器保存状态到 `sta`。
      * `opcode = 9`
      * `argument = [ uint8_t sta ];`
  * **MsgLoadState**
      * 请求仿真器加载状态 `sta`。
      * `opcode = 10`
      * `argument = [ uint8_t sta ];`
  * **MsgTitle**
      * 请求当前运行游戏的标题。
      * `opcode = 10` (注意：与 `MsgLoadState` 操作码重复，这在实际规范中可能需要澄清或更正。)
      * `argument = [ ];`
  * **MsgID**
      * 请求当前运行游戏的 ID。
      * `opcode = 11`
      * `argument = [ ];`
  * **MsgUUID**
      * 请求当前运行游戏的 UUID。
      * `opcode = 12`
      * `argument = [ ];`
  * **MsgGameVersion**
      * 请求当前运行游戏的版本。
      * `opcode = 13`
      * `argument = [ ];`
  * **MsgStatus**
      * 请求仿真器的状态。
      * `opcode = 14`
      * `argument = [ ];`

### 3.2. 应答消息

应答消息以一个 `uint8_t` **结果码 (result code)** 开头，可以是以下两个值之一：

1.  `00`: OK（成功）
2.  `FF`: FAIL（失败，表示服务器端出现故障）

结果码之后是根据操作定义的参数。

**应答消息示例：**

```
+-----------+--+--+
|06 00 00 00|00|00|
+-----------+--+--+
  |           |  |
  |           |  argument
  |           result code
  message size
```

在这个例子中，这是一个 `MsgRead8` 类型的应答消息，结果码为 `0x00`（成功），参数为 `0x00`（读取到的值）。

下面是所有可能的应答消息的文档：

  * **MsgRead8**
      * `argument = [ uint8_t val ];`
  * **MsgRead16**
      * `argument = [ uint16_t val ];`
  * **MsgRead32**
      * `argument = [ uint32_t val ];`
  * **MsgRead64**
      * `argument = [ uint64_t val ];`
  * **MsgWrite8**
      * `argument = [ ];`
  * **MsgWrite16**
      * `argument = [ ];`
  * **MsgWrite32**
      * `argument = [ ];`
  * **MsgWrite64**
      * `argument = [ ];`
  * **MsgVersion**
      * `argument = [ uint32_t size, char* version ];`
  * **MsgSaveState**
      * `argument = [ ];`
  * **MsgLoadState**
      * `argument = [ ];`
  * **MsgTitle**
      * `argument = [ uint32_t size, char* version ];`
  * **MsgID**
      * `argument = [ uint32_t size, char* version ];`
  * **MsgUUID**
      * `argument = [ uint32_t size, char* version ];`
  * **MsgGameVersion**
      * `argument = [ uint32_t size, char* version ];`
  * **MsgStatus**
      * `argument = [ uint32_t status ];`
      * `status` 可以是以下值：
        1.  `0`: 运行中 (Running)
        2.  `1`: 暂停 (Paused)
        3.  `2`: 关闭 (Shutdown)

### 3.3. 事件消息

目前，事件消息尚未实现。在本文档成为标准之前，这应该会有所改变。

### 3.4. 批处理消息

批处理消息适用于请求和应答消息。它们只是所有消息的**连接摘要**，减去了原始大小头部前言。

**请求消息的批处理示例：**

```
+-----------+--------------+--------------+
|0e 00 00 00|00 34 7d 34 00|00 34 7d 34 00|
+-----------+--------------+--------------+
  |           |              |
  |           |              消息 2
  |           消息 1
  消息大小
```

**应答消息的批处理示例：**

```
+-----------+--+-----+
|07 00 00 00|00|00|00|
+-----------+--+-----+
  |           |  | |
  |           |  | 消息 2
  |           |  消息 1
  |           结果码
  消息大小
```

由于应答消息没有标识符，并且它们的参数大小在请求时可能是未知的，因此客户端有责任根据回复的大小重新定位所有响应。
