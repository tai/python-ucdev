src = """
#define CY_STRING_DESCRIPTOR_SIZE 256
#define CY_MAX_DEVICE_INTERFACE 5
#define CY_US_VERSION_MAJOR 1
#define CY_US_VERSION_MINOR 0
#define CY_US_VERSION_PATCH 0
#define CY_US_VERSION 1
#define CY_US_VERSION_BUILD 74
    typedef unsigned int UINT32;
    typedef unsigned char UINT8;
    typedef unsigned short UINT16;
    typedef char CHAR;
    typedef unsigned char UCHAR;
typedef void* CY_HANDLE;
typedef void (*CY_EVENT_NOTIFICATION_CB_FN)(UINT16 eventsNotified);
typedef struct _CY_VID_PID {
    UINT16 vid;
    UINT16 pid;
} CY_VID_PID, *PCY_VID_PID;
typedef struct _CY_LIBRARY_VERSION {
    UINT8 majorVersion;
    UINT8 minorVersion;
    UINT16 patch;
    UINT8 buildNumber;
} CY_LIBRARY_VERSION, *PCY_LIBRARY_VERSION;
typedef struct _CY_FIRMWARE_VERSION {
    UINT8 majorVersion;
    UINT8 minorVersion;
    UINT16 patchNumber;
    UINT32 buildNumber;
} CY_FIRMWARE_VERSION, *PCY_FIRMWARE_VERSION;
typedef enum _CY_DEVICE_CLASS{
    CY_CLASS_DISABLED = 0,
    CY_CLASS_CDC = 0x02,
    CY_CLASS_PHDC = 0x0F,
    CY_CLASS_VENDOR = 0xFF
} CY_DEVICE_CLASS;
typedef enum _CY_DEVICE_TYPE {
    CY_TYPE_DISABLED = 0,
    CY_TYPE_UART,
    CY_TYPE_SPI,
    CY_TYPE_I2C,
    CY_TYPE_JTAG,
    CY_TYPE_MFG
} CY_DEVICE_TYPE;
typedef enum _CY_DEVICE_SERIAL_BLOCK
{
    SerialBlock_SCB0 = 0,
    SerialBlock_SCB1,
    SerialBlock_MFG
} CY_DEVICE_SERIAL_BLOCK;
typedef struct _CY_DEVICE_INFO {
    CY_VID_PID vidPid;
    UCHAR numInterfaces;
    UCHAR manufacturerName [256];
    UCHAR productName [256];
    UCHAR serialNum [256];
    UCHAR deviceFriendlyName [256];
    CY_DEVICE_TYPE deviceType [5];
    CY_DEVICE_CLASS deviceClass [5];
    CY_DEVICE_SERIAL_BLOCK deviceBlock;
} CY_DEVICE_INFO,*PCY_DEVICE_INFO;
typedef struct _CY_DATA_BUFFER {
    UCHAR *buffer;
    UINT32 length;
    UINT32 transferCount;
} CY_DATA_BUFFER,*PCY_DATA_BUFFER;
typedef enum _CY_RETURN_STATUS{
    CY_SUCCESS = 0,
    CY_ERROR_ACCESS_DENIED,
    CY_ERROR_DRIVER_INIT_FAILED,
    CY_ERROR_DEVICE_INFO_FETCH_FAILED,
    CY_ERROR_DRIVER_OPEN_FAILED,
    CY_ERROR_INVALID_PARAMETER,
    CY_ERROR_REQUEST_FAILED,
    CY_ERROR_DOWNLOAD_FAILED,
    CY_ERROR_FIRMWARE_INVALID_SIGNATURE,
    CY_ERROR_INVALID_FIRMWARE,
    CY_ERROR_DEVICE_NOT_FOUND,
    CY_ERROR_IO_TIMEOUT,
    CY_ERROR_PIPE_HALTED,
    CY_ERROR_BUFFER_OVERFLOW,
    CY_ERROR_INVALID_HANDLE,
    CY_ERROR_ALLOCATION_FAILED,
    CY_ERROR_I2C_DEVICE_BUSY,
    CY_ERROR_I2C_NAK_ERROR,
    CY_ERROR_I2C_ARBITRATION_ERROR,
    CY_ERROR_I2C_BUS_ERROR,
    CY_ERROR_I2C_BUS_BUSY,
    CY_ERROR_I2C_STOP_BIT_SET,
    CY_ERROR_STATUS_MONITOR_EXIST
} CY_RETURN_STATUS;
typedef struct _CY_I2C_CONFIG{
    UINT32 frequency;
    UINT8 slaveAddress;
    BOOL isMaster;
    BOOL isClockStretch;
} CY_I2C_CONFIG,*PCY_I2C_CONFIG;
typedef struct _CY_I2C_DATA_CONFIG
{
    UCHAR slaveAddress;
    BOOL isStopBit;
    BOOL isNakBit;
} CY_I2C_DATA_CONFIG, *PCY_I2C_DATA_CONFIG;
typedef enum _CY_SPI_PROTOCOL {
    CY_SPI_MOTOROLA = 0,
    CY_SPI_TI,
    CY_SPI_NS
} CY_SPI_PROTOCOL;
typedef struct _CY_SPI_CONFIG
{
    UINT32 frequency;
    UCHAR dataWidth;
    CY_SPI_PROTOCOL protocol ;
    BOOL isMsbFirst;
    BOOL isMaster;
    BOOL isContinuousMode;
    BOOL isSelectPrecede;
    BOOL isCpha;
    BOOL isCpol;
}CY_SPI_CONFIG,*PCY_SPI_CONFIG;
typedef enum _CY_UART_BAUD_RATE
{
    CY_UART_BAUD_300 = 300,
    CY_UART_BAUD_600 = 600,
    CY_UART_BAUD_1200 = 1200,
    CY_UART_BAUD_2400 = 2400,
    CY_UART_BAUD_4800 = 4800,
    CY_UART_BAUD_9600 = 9600,
    CY_UART_BAUD_14400 = 14400,
    CY_UART_BAUD_19200 = 19200,
    CY_UART_BAUD_38400 = 38400,
    CY_UART_BAUD_56000 = 56000,
    CY_UART_BAUD_57600 = 57600,
    CY_UART_BAUD_115200 = 115200,
    CY_UART_BAUD_230400 = 230400,
    CY_UART_BAUD_460800 = 460800,
    CY_UART_BAUD_921600 = 921600,
    CY_UART_BAUD_1000000 = 1000000,
    CY_UART_BAUD_3000000 = 3000000,
}CY_UART_BAUD_RATE;
typedef enum _CY_UART_PARITY_MODE {
    CY_DATA_PARITY_DISABLE = 0,
    CY_DATA_PARITY_ODD,
    CY_DATA_PARITY_EVEN,
    CY_DATA_PARITY_MARK,
    CY_DATA_PARITY_SPACE
} CY_UART_PARITY_MODE;
typedef enum _CY_UART_STOP_BIT {
    CY_UART_ONE_STOP_BIT = 1,
    CY_UART_TWO_STOP_BIT
} CY_UART_STOP_BIT;
typedef enum _CY_FLOW_CONTROL_MODES {
    CY_UART_FLOW_CONTROL_DISABLE = 0,
    CY_UART_FLOW_CONTROL_DSR,
    CY_UART_FLOW_CONTROL_RTS_CTS,
    CY_UART_FLOW_CONTROL_ALL
} CY_FLOW_CONTROL_MODES;
typedef struct _CY_UART_CONFIG {
    CY_UART_BAUD_RATE baudRate;
    UINT8 dataWidth;
    CY_UART_STOP_BIT stopBits;
    CY_UART_PARITY_MODE parityMode;
    BOOL isDropOnRxErrors;
} CY_UART_CONFIG,*PCY_UART_CONFIG;
typedef enum _CY_CALLBACK_EVENTS {
    CY_UART_CTS_BIT = 0x01,
    CY_UART_DSR_BIT = 0x02,
    CY_UART_BREAK_BIT = 0x04,
    CY_UART_RING_SIGNAL_BIT = 0x08,
    CY_UART_FRAME_ERROR_BIT = 0x10,
    CY_UART_PARITY_ERROR_BIT = 0x20,
    CY_UART_DATA_OVERRUN_BIT = 0x40,
    CY_UART_DCD_BIT = 0x100,
    CY_SPI_TX_UNDERFLOW_BIT = 0x200,
    CY_SPI_BUS_ERROR_BIT = 0x400,
    CY_ERROR_EVENT_FAILED_BIT = 0x800
} CY_CALLBACK_EVENTS;
 CY_RETURN_STATUS CyLibraryInit ();
 CY_RETURN_STATUS CyLibraryExit ();
 CY_RETURN_STATUS CyGetListofDevices (
    UINT8* numDevices
    );
 CY_RETURN_STATUS CyGetDeviceInfo(
    UINT8 deviceNumber,
    CY_DEVICE_INFO *deviceInfo
    );
 CY_RETURN_STATUS CyGetDeviceInfoVidPid (
    CY_VID_PID vidPid,
    UINT8 *deviceIdList,
    CY_DEVICE_INFO *deviceInfoList,
    UINT8 *deviceCount,
    UINT8 infoListLength
    );
 CY_RETURN_STATUS CyOpen (
    UINT8 deviceNumber,
    UINT8 interfaceNum,
    CY_HANDLE *handle
    );
 CY_RETURN_STATUS CyClose (
    CY_HANDLE handle
    );
 CY_RETURN_STATUS CyCyclePort (
    CY_HANDLE handle
    );
 CY_RETURN_STATUS CySetGpioValue (
    CY_HANDLE handle,
    UINT8 gpioNumber,
    UINT8 value
    );
 CY_RETURN_STATUS CyGetGpioValue (
    CY_HANDLE handle,
    UINT8 gpioNumber,
    UINT8 *value
    );
 CY_RETURN_STATUS CySetEventNotification(
    CY_HANDLE handle,
    CY_EVENT_NOTIFICATION_CB_FN notificationCbFn
    );
 CY_RETURN_STATUS CyAbortEventNotification(
    CY_HANDLE handle
    );
 CY_RETURN_STATUS CyGetLibraryVersion (
    CY_HANDLE handle,
    PCY_LIBRARY_VERSION version
    );
 CY_RETURN_STATUS CyGetFirmwareVersion (
    CY_HANDLE handle,
    PCY_FIRMWARE_VERSION firmwareVersion
    );
 CY_RETURN_STATUS CyResetDevice (
    CY_HANDLE handle
    );
 CY_RETURN_STATUS CyProgUserFlash (
    CY_HANDLE handle,
    CY_DATA_BUFFER *progBuffer,
    UINT32 flashAddress,
    UINT32 timeout
    );
 CY_RETURN_STATUS CyReadUserFlash (
    CY_HANDLE handle,
    CY_DATA_BUFFER *readBuffer,
    UINT32 flashAddress,
    UINT32 timeout
    );
 CY_RETURN_STATUS CyGetSignature (
    CY_HANDLE handle,
    UCHAR *pSignature
    );
 CY_RETURN_STATUS CyGetUartConfig (
    CY_HANDLE handle,
    CY_UART_CONFIG *uartConfig
    );
 CY_RETURN_STATUS CySetUartConfig (
    CY_HANDLE handle,
    CY_UART_CONFIG *uartConfig
    );
 CY_RETURN_STATUS CyUartRead (
    CY_HANDLE handle,
    CY_DATA_BUFFER* readBuffer,
    UINT32 timeout
    );
 CY_RETURN_STATUS CyUartWrite (
    CY_HANDLE handle,
    CY_DATA_BUFFER* writeBuffer,
    UINT32 timeout
    );
 CY_RETURN_STATUS CyUartSetHwFlowControl(
    CY_HANDLE handle,
    CY_FLOW_CONTROL_MODES mode
    );
 CY_RETURN_STATUS CyUartGetHwFlowControl(
    CY_HANDLE handle,
    CY_FLOW_CONTROL_MODES *mode
    );
 CY_RETURN_STATUS CyUartSetRts(
    CY_HANDLE handle
    );
 CY_RETURN_STATUS CyUartClearRts(
    CY_HANDLE handle
    );
 CY_RETURN_STATUS CyUartSetDtr(
    CY_HANDLE handle
    );
 CY_RETURN_STATUS CyUartClearDtr(
    CY_HANDLE handle
    );
 CY_RETURN_STATUS CyUartSetBreak(
    CY_HANDLE handle,
    UINT16 timeout
    );
 CY_RETURN_STATUS CyGetI2cConfig (
    CY_HANDLE handle,
    CY_I2C_CONFIG *i2cConfig
    );
 CY_RETURN_STATUS CySetI2cConfig (
    CY_HANDLE handle,
    CY_I2C_CONFIG *i2cConfig
    );
 CY_RETURN_STATUS CyI2cRead (
    CY_HANDLE handle,
    CY_I2C_DATA_CONFIG *dataConfig,
    CY_DATA_BUFFER *readBuffer,
    UINT32 timeout
    );
 CY_RETURN_STATUS CyI2cWrite (
    CY_HANDLE handle,
    CY_I2C_DATA_CONFIG *dataConfig,
    CY_DATA_BUFFER *writeBuffer,
    UINT32 timeout
    );
 CY_RETURN_STATUS CyI2cReset(
                                        CY_HANDLE handle,
                                        BOOL resetMode
                                        );
 CY_RETURN_STATUS CyGetSpiConfig (
    CY_HANDLE handle,
    CY_SPI_CONFIG *spiConfig
    );
 CY_RETURN_STATUS CySetSpiConfig (
    CY_HANDLE handle,
    CY_SPI_CONFIG *spiConfig
    );
 CY_RETURN_STATUS CySpiReadWrite (
    CY_HANDLE handle,
    CY_DATA_BUFFER* readBuffer,
    CY_DATA_BUFFER* writeBuffer,
    UINT32 timeout
    );
 CY_RETURN_STATUS CyJtagEnable (
    CY_HANDLE handle
    );
 CY_RETURN_STATUS CyJtagDisable (
    CY_HANDLE handle
    );
 CY_RETURN_STATUS CyJtagWrite (
    CY_HANDLE handle,
    CY_DATA_BUFFER *writeBuffer,
    UINT32 timeout
    );
 CY_RETURN_STATUS CyJtagRead (
    CY_HANDLE handle,
    CY_DATA_BUFFER *readBuffer,
    UINT32 timeout
    );
 CY_RETURN_STATUS CyPhdcClrFeature (
        CY_HANDLE handle
        );
 CY_RETURN_STATUS CyPhdcSetFeature (
        CY_HANDLE handle
        );
 CY_RETURN_STATUS CyPhdcGetStatus (
        CY_HANDLE handle,
        UINT16 *dataStatus
        );
"""
