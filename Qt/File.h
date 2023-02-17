#ifndef JNC_FILE_H
#define JNC_FILE_H
#include <QString>
#include <QFile>
#include <QIODeviceBase>


namespace jnc
{
    enum class OpenMode
    {
        read,
        write,
        append,
        readplus,
        writeplus,
        appendplus,
    };

    enum class ErrorCode
    {
        NoError,
        InvalidMode,
        FilePathNotExist,
        FailOpenFile,
    };

    class File
    {
    public:
        File();
        ~File();

        ErrorCode open(const QString& fileName, OpenMode mode);
        void close();

        QString read();
        void write(const QString& text);

        void seek(qint64 pos);
        qint64 tell() const;

    private:
        QFile* m_file;
    };
}

#endif // JNC_FILE_H
