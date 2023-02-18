#include "Json.h"
#include "File.h"

void jnc::Json::dump(const QString& fileName, const QJsonDocument& jsonDoc)
{
    File file{};
    ErrorCode err = file.open(fileName, OpenMode::write);
    if (err != ErrorCode::NoError)
    {
        return;
    }
    file.write(jsonDoc.toJson());
    file.close();
}

QJsonDocument jnc::Json::load(const QString& fileName)
{
    File file{};
    ErrorCode err = file.open(fileName, OpenMode::read);
    if (err != ErrorCode::NoError)
    {
        return QJsonDocument{};
    }
    const QString data{file.read()};
    file.close();
    if (!data.isEmpty())
    {
        return QJsonDocument::fromJson(data.toUtf8());
    }
    else
    {
        return QJsonDocument{};
    }
}
