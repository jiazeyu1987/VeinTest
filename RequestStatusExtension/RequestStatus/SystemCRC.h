#pragma once
class SystemCRC
{
public:
    SystemCRC();
    virtual ~SystemCRC() {};
    unsigned int calculateCRC16(const char* reply, int replyLength) const;

private:
    unsigned int calcValue(unsigned int crc, int data) const;
    static unsigned int crcTable[256];
};

