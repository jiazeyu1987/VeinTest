#include "SystemCRC.h"
unsigned int SystemCRC::crcTable[256] = { 0 };

SystemCRC::SystemCRC()
{
    long lCrcTable;
    for (int i = 0; i < 256; i++)
    {
        lCrcTable = i;
        for (int j = 0; j < 8; j++)
        {
            lCrcTable = (lCrcTable >> 1) ^ ((lCrcTable & 1) ? 0xA001L : 0);
        }
        crcTable[i] = (unsigned int)lCrcTable & 0xFFFF;
    }
}

unsigned int SystemCRC::calculateCRC16(const char* reply, int replyLength) const
{
    unsigned int uCrc = 0;
    for (int m = 0; m < replyLength; m++)
    {
        uCrc = calcValue(uCrc, reply[m]);
    }
    return uCrc;
}

unsigned int SystemCRC::calcValue(unsigned int crc, int data) const
{
    crc = crcTable[(crc ^ data) & 0xFF] ^ (crc >> 8);
    return (crc & 0xFFFF);
}
