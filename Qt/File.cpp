#include "File.h"
#include <QDir>
#include <QTextStream>


jnc::File::File()
{
    this->m_file = new QFile;
}

jnc::File::~File()
{
    delete this->m_file;
    this->m_file = nullptr;
}

jnc::ErrorCode jnc::File::open(const QString& fileName, OpenMode mode)
{
    QDir filePath{fileName};
    if (!filePath.cdUp())
    {
        return ErrorCode::FilePathNotExist;
    }

    QIODeviceBase::OpenMode ioMode = QIODeviceBase::Text;
    switch (mode)
    {
    case OpenMode::read:
        ioMode |= QIODeviceBase::ReadOnly;
        break;
    case OpenMode::write:
        ioMode |= QIODeviceBase::WriteOnly;
        break;
    case OpenMode::append:
        ioMode |= QIODeviceBase::Append;
        break;
    case OpenMode::readplus:
        ioMode |= QIODeviceBase::ReadWrite;
        break;
    case OpenMode::writeplus:
        ioMode |= (QIODeviceBase::ReadWrite | QIODeviceBase::Truncate);
        break;
    case OpenMode::appendplus:
        ioMode |= (QIODeviceBase::ReadOnly | QIODeviceBase::Append);
        break;
    default:
        return ErrorCode::InvalidMode;
    }

    this->m_file->setFileName(fileName);
    if (!this->m_file->open(ioMode))
    {
        return ErrorCode::FailOpenFile;
    }

    return ErrorCode::NoError;
}

void jnc::File::close()
{
    this->m_file->close();
}

QString jnc::File::read()
{
    QTextStream ts{this->m_file};
    return ts.readAll();
}

void jnc::File::write(const QString& text)
{
    QTextStream ts{this->m_file};
    ts << text;
}

void jnc::File::seek(qint64 pos)
{
    this->m_file->seek(pos);
}

qint64 jnc::File::tell() const
{
    return this->m_file->pos();
}
